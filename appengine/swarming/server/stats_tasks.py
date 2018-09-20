# coding: utf-8
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Generates statistics for the tasks. Contains the backend code."""

from google.appengine.ext import ndb

from components import stats_framework
from server import task_request
from server import task_result


### Models


class _TasksPoolSnapshot(ndb.Model):
  """Snapshot of statistics for tasks in a pool, to be embedded in
  _TasksSnapshot.
  """
  # The pool's name.
  name = ndb.StringProperty()

  # Events
  created = ndb.IntegerProperty(default=0)
  deduped = ndb.IntegerProperty(default=0)
  started = ndb.IntegerProperty(default=0)
  completed = ndb.IntegerProperty(default=0)
  completed_success = ndb.IntegerProperty(default=0)
  completed_failure = ndb.IntegerProperty(default=0)
  canceled = ndb.IntegerProperty(default=0)
  killed = ndb.IntegerProperty(default=0)
  expired = ndb.IntegerProperty(default=0)
  internal_failure = ndb.IntegerProperty(default=0)

  # task•second.
  pending_secs = ndb.FloatProperty(default=0.)
  running_secs = ndb.FloatProperty(default=0.)
  deduped_secs = ndb.FloatProperty(default=0.)

  # waiting_times (?)
  # execution_times (?)

  def accumulate(self, rhs):
    return stats_framework.accumulate(self, rhs, ['name'])


class _TasksSnapshot(ndb.Model):
  """snapshot of tasks statistics, to be embedded in stats_framework."""
  pools = ndb.LocalStructuredProperty(_TasksPoolSnapshot)


### Private code


def _generate_stats_tasks(start_time, end_time):
  """Returns a _TasksSnapshot filled with the events for the specified interval.
  """
  pools = {}
  cls = task_result.TaskResultSummary

  # created
  for result in cls.query(cls.created_ts >= start_time):
    if result.created_ts >= end_time:
      break
    pools.setdefault(result.pool, set()).add(result)

  # started
  for result in cls.query(cls.started_ts >= start_time):
    if result.started_ts >= end_time:
      break
    pools.setdefault(result.pool, set()).add(result)

  # completed, completed_success, completed_failure, deduped
  for result in cls.query(cls.completed_ts >= start_time):
    if result.completed_ts >= end_time:
      break
    pools.setdefault(result.pool, set()).add(result)

  # canceled, killed, expired, internal_failure
  for result in cls.query(cls.abandonned_ts >= start_time):
    if result.abandonned_ts >= end_time:
      break
    pools.setdefault(result.pool, set()).add(result)

  s = _TasksSnapshot()
  for pool in pools:
    sp = _TasksPoolSnapshot(name=pool)
    if start_time <= sp.created_ts < end_time:
      sp.created += 1
    if start_time <= sp.created_ts < end_time:
      sp.started += 1
    if start_time <= sp.completed_ts < end_time:
      if sp.state == task_result.State.DEDUPED:
        sp.deduped += 1
      else:
        sp.completed += 1
        if not sp.failure:
          sp.completed_success += 1
        else:
          sp.completed_failure += 1
    if start_time <= sp.abandonned_ts < end_time:
      if sp.state == task_result.State.CANCELED:
        sp.canceled += 1
      elif sp.state == task_result.State.KILLED:
        sp.killed += 1
      elif sp.state == task_result.State.EXPIRED:
        sp.expired += 1
      elif sp.state == task_result.State.BOT_DIED:
        sp.internal_failure += 1
    s.pools.append(sp)

  # TODO(maruel): Calculate these.
  #pending_secs
  #running_secs
  #deduped_secs

  s.pools.sort(key=lambda x: x.name)
  return s


### Public API


STATS_HANDLER = stats_framework.StatisticsFramework(
    'stats_tasks', _TasksSnapshot, _generate_stats_tasks)


def cron_generate_stats():
  """Returns the number of minutes processed."""
  # We optimistically hope that DB queries are consistent after 1 minute. This
  # is not true all the time, but good enough.
  return STATS_HANDLER.process_next_chunk(1)
