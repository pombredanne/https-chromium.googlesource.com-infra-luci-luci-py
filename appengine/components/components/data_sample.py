# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Framework to handle statistical data samples."""

import itertools

from google.appengine.ext import ndb

from components import datastore_utils


class DataSamples(ndb.Model):
  """Value series for sampling.

  Keeps the raw values compressed. Since the sample size can become large, it
  can save significant space and increase the amount of samples that can be kept
  in a single entity. Keeping the values sorted likely helps with compression
  ratio.

  TODO(maruel): Evaluate better compression mechanisms, for example
  delta-encoding.
  """
  values = datastore_utils.GradientEncodedSortedVectorProperty(compressed=True)

  @property
  def sample_size(self):
    return len(self.values)

  @property
  def average(self):
    if not self.sample_size:
      return None
    return sum(self.values) / self.sample_size

  @property
  def percentile_25(self):
    return value_millicille(self.values, 250)

  @property
  def median(self):
    return value_millicille(self.values, 500)

  @property
  def percentile_95(self):
    return value_millicille(self.values, 950)

  @property
  def percentile_99(self):
    return value_millicille(self.values, 990)

  @property
  def percentile_99_9(self):
    return value_millicille(self.values, 999)


class DataSampled(ndb.Model):
  """Samples at 25%, median, 95%, 99% and 99.9% of a value series.

  Stores the raw data off this entity.
  """
  source_keys = ndb.KeyProperty(kind=DataSamples, indexed=False, repeated=True)

  # Keep the precalculated data.
  sample_size = ndb.IntegerProperty(default=0, indexed=False)
  average = ndb.FloatProperty(default=0., indexed=False)
  percentile_25 = ndb.FloatProperty(default=0., indexed=False)
  median = ndb.FloatProperty(default=0., indexed=False)
  percentile_95 = ndb.FloatProperty(default=0., indexed=False)
  percentile_99 = ndb.FloatProperty(default=0., indexed=False)
  percentile_99_9 = ndb.FloatProperty(default=0., indexed=False)

  def accumulate(self, rhs):
    # This function is DB intensive, especially at the Day level, where it will
    # fetch 60*24 = 1440 entities.
    self.source_keys.extend(rhs.source_keys)
    # The important part here is only keep the statistically important values.
    # This is the last 10%, 10% around the median, 10% around the 25th
    # percentile. The 10% is actually a factor of how many values are being
    # added. For example, if the first series has 1000 elements and the second
    # 100, the function must determine which elements to keep.
    # It's be around 300 elements.
    # For 10000 elements, it is still around 300 elements, depending on the
    # confidence level.
    sample = DataSamples(
        values=itertools.chain_from_iterables(
            d.values for d in ndb.get_multi(self.source_keys)))
    # Copy the data over.
    self.sample_size = sample.sample_size
    self.average = sample.average
    self.percentile_25 = sample.percentile_25
    self.median = sample.median
    self.percentile_95 = sample.percentile_95
    self.percentile_99 = sample.percentile_99
    self.percentile_99_9 = sample.percentile_99_9


def value_millicille(series, location):
  """Returns the value at location in a series where X is in /1000.

  Median is 500, 95% percentile is 950, 99% percentile is 990, etc.
  """
  if not series:
    return None
  number = len(series)

  # Is it precise or not. If not, average two values. For percentile near the
  # edge, expect some variation.
  index = int(round(number / 1000. * location + 0.5))
  return series[index]
