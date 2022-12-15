# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import collections
import copy
import inspect
import itertools
import threading
import time

from google.protobuf import message
from infra_libs.ts_mon.common import errors
import six


def default_modify_fn(name):
  def _modify_fn(value, delta):
    if delta < 0:
      raise errors.MonitoringDecreasingValueError(name, None, delta)
    return value + delta
  return _modify_fn


class MetricStore(object):
  """A place to store values for each metric.

  Several methods take "a normalized field tuple".  This is a tuple of
  (key, value) tuples sorted by key.  (The reason this is given as a tuple
  instead of a dict is because tuples are hashable and can be used as dict keys,
  dicts can not).

  The MetricStore is also responsible for keeping the start_time of each metric.
  This is what goes into the start_timestamp_us field in the MetricsData proto
  for cumulative metrics and distributions, and helps Monarch identify when a
  counter was reset.  This is the MetricStore's job because an implementation
  might share counter values across multiple instances of a task (like on
  Appengine), so the start time must be associated with that value so that it
  can be reset for all tasks at once when the value is reset.

  External metric stores (like those backed by memcache) may be cleared (either
  wholly or partially) at any time.  When this happens the MetricStore *must*
  generate a new start_time for all the affected metrics.

  Metrics can specify their own explicit start time if they are mirroring the
  value of some external counter that started counting at a known time.

  Otherwise the MetricStore's time_fn (defaults to time.time()) is called the
  first time a metric is set or incremented, or after it is cleared externally.
  """

  def __init__(self, state, time_fn=None):
    self._state = state
    self._time_fn = time_fn or time.time

  def get(self, name, fields, target_fields, default=None):
    """Fetches the current value for the metric.

    Args:
      name (string): the metric's name.
      fields (tuple): a normalized field tuple.
      target_fields (dict or None): target fields to override.
      default: the value to return if the metric has no value of this set of
          field values.
    """
    raise NotImplementedError

  def get_all(self):
    """Returns an iterator over all the metrics present in the store.

    The iterator yields 5-tuples:
      (target, metric, start_time, end_time, field_values)
    """
    raise NotImplementedError

  def set(self, name, fields, target_fields, value, enforce_ge=False):
    """Sets the metric's value.

    Args:
      name: the metric's name.
      fields: a normalized field tuple.
      target_fields (dict or None): target fields to override.
      value: the new value for the metric.
      enforce_ge: if this is True, raise an exception if the new value is
          less than the old value.

    Raises:
      MonitoringDecreasingValueError: if enforce_ge is True and the new value is
          smaller than the old value.
    """
    raise NotImplementedError

  def incr(self, name, fields, target_fields, delta, modify_fn=None):
    """Increments the metric's value.

    Args:
      name: the metric's name.
      fields: a normalized field tuple.
      target_fields (dict or None): target fields to override.
      delta: how much to increment the value by.
      modify_fn: this function is called with the original value and the delta
          as its arguments and is expected to return the new value.  The
          function must be idempotent as it may be called multiple times.
    """
    raise NotImplementedError

  def reset_for_unittest(self, name=None):
    """Clears the values metrics.  Useful in unittests.

    Args:
      name: the name of an individual metric to reset, or if None resets all
        metrics.
    """
    raise NotImplementedError


class _TargetFieldsValues(object):
  """Holds all values for a single metric.

  Values are keyed by metric fields and target fields (which override the
  default target fields configured globally for the process).
  """

  def __init__(self):
    # {normalized_target_fields: {normalized_metric_fields: value}}
    self._values = collections.defaultdict(dict)
    self._start_times = collections.defaultdict(dict)

  def gen_key(self, target_fields):
    if not isinstance(target_fields, message.Message):
      # It's a dict. Canonicalise its items.
      return tuple(sorted(six.iteritems(target_fields)))

    # It's a protobuf. Serialise its values.
    # The zeroth element is the target type.
    values = [type(target_fields)]
    for field in target_fields.DESCRIPTOR.fields:
      name = field.name
      value = getattr(target_fields, name)
      values.append(value)
    return tuple(values)

  def _get_target_values(self, target_fields):
    # Normalize the target fields by converting them into a hashable tuple.
    if not target_fields:
      target_fields = {}
    return self._values[self.gen_key(target_fields)]

  def _get_target_start_times(self, target_fields):
    # Normalize the target fields by converting them into a hashable tuple.
    if not target_fields:
      target_fields = {}
    return self._start_times[self.gen_key(target_fields)]

  def get_value(self, fields, target_fields, default=None):
    return self._get_target_values(target_fields).get(
        fields, default)

  def set_value(self, fields, target_fields, value, time_fn=None):
    self._get_target_values(target_fields)[fields] = value
    start_time = time_fn() if time_fn else time.time()
    # If fields does not exist in dict, set to start_time
    self._get_target_start_times(target_fields).setdefault(fields, start_time)

  def iter_targets(self, default_target):
    targets = self.iter_targets_with_start_times(default_target)
    for target, fields_values, _ in targets:
      yield target, fields_values

  def iter_targets_with_start_times(self, default_target):
    for target_fields, fields_values in six.iteritems(self._values):
      if target_fields:
        if inspect.isclass(target_fields[0]):
          # It's a target type plus serialised values.
          # Output the tuple as is.
          target = target_fields
        else:
          target = copy.copy(default_target)
          target.update({k: v for k, v in target_fields})
      else:
        target = default_target
      yield target, fields_values, self._start_times[target_fields]

  def __deepcopy__(self, memo_dict):
    ret = _TargetFieldsValues()
    ret._start_times = copy.deepcopy(self._start_times, memo_dict)
    ret._values = copy.deepcopy(self._values, memo_dict)
    return ret


class InProcessMetricStore(MetricStore):
  """A thread-safe metric store that keeps values in memory."""

  def __init__(self, state, time_fn=None):
    super(InProcessMetricStore, self).__init__(state, time_fn=time_fn)

    self._values = {}
    self._thread_lock = threading.Lock()

  def _entry(self, name):
    if name not in self._values:
      self._reset(name)

    return self._values[name]

  def get(self, name, fields, target_fields, default=None):
    return self._entry(name).get_value(fields, target_fields, default)

  def iter_field_values(self, name):
    return itertools.chain.from_iterable(
        six.iteritems(x)
        for _, x in self._entry(name).iter_targets(self._state.target))

  def get_all(self):
    # Make a copy of the metric values in case another thread (or this
    # generator's consumer) modifies them while we're iterating.
    with self._thread_lock:
      values = copy.deepcopy(self._values)
    end_time = self._time_fn()

    for name, metric_values in six.iteritems(values):
      if name not in self._state.metrics:
        continue
      targets = metric_values.iter_targets_with_start_times(
          self._state.target)
      for target, fields_values, start_times in targets:
        yield (target, self._state.metrics[name], start_times, end_time,
               fields_values)

  def set(self, name, fields, target_fields, value, enforce_ge=False):
    with self._thread_lock:
      if enforce_ge:
        old_value = self._entry(name).get_value(fields, target_fields, 0)
        if value < old_value:
          raise errors.MonitoringDecreasingValueError(name, old_value, value)

      self._entry(name).set_value(fields, target_fields, value, self._time_fn)

  def incr(self, name, fields, target_fields, delta, modify_fn=None):
    if delta < 0:
      raise errors.MonitoringDecreasingValueError(name, None, delta)

    if modify_fn is None:
      modify_fn = default_modify_fn(name)

    with self._thread_lock:
      self._entry(name).set_value(fields, target_fields, modify_fn(
          self.get(name, fields, target_fields, 0), delta), self._time_fn)

  def reset_for_unittest(self, name=None):
    if name is not None:
      self._reset(name)
    else:
      for name in self._values.keys():
        self._reset(name)

  def _reset(self, name):
    self._values[name] = _TargetFieldsValues()
