# coding: utf-8
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Generates statistics for the bots. Contains the backend code."""

from google.appengine.ext import ndb


### Models


class _Snapshot(ndb.Model):
  """A snapshot of statistics, to be embedded in another entity."""
  # Number of individual uploads and total amount of bytes. Same for downloads.
  uploads = ndb.IntegerProperty(default=0, indexed=False)
  uploads_bytes = ndb.IntegerProperty(default=0, indexed=False)
  downloads = ndb.IntegerProperty(default=0, indexed=False)
  downloads_bytes = ndb.IntegerProperty(default=0, indexed=False)

  # Number of /contains requests and total number of items looked up.
  contains_requests = ndb.IntegerProperty(default=0, indexed=False)
  contains_lookups = ndb.IntegerProperty(default=0, indexed=False)

  # Total number of requests to calculate QPS
  requests = ndb.IntegerProperty(default=0, indexed=False)
  # Number of non-200 requests.
  failures = ndb.IntegerProperty(default=0, indexed=False)

  def accumulate(self, rhs):
    return stats_framework.accumulate(self, rhs, [])


def _to_proto(s):
  """Shorthand to create a proto."""
  out = isolated_pb2.StatsSnapshot()
  snapshot_to_proto(s, out)
  return out


### Public API


STATS_HANDLER = stats_framework.StatisticsFramework(
      'bots', _Snapshot, _extract_snapshot_from_logs)


def cron_generate_stats():
  """Returns the number of minutes processed."""
  # TODO(maruel): https://crbug.com/864724
  return 0
