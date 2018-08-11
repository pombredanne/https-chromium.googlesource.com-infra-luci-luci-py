# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Generates statistics for the bots. Contains the backend code."""

from google.appengine.ext import ndb

from components import stats_framework
from components import utils


# Class has no __init__ method - pylint: disable=W0232


### Models


class _BotSnapshot(ndb.Model):
  """A snapshot of statistics, to be embedded in another entity."""
  # Each of the state. The sum should hopefully be equal to the number of bots
  # known, divided by the amount of time this represents in minutes.
  idle = ndb.FloatProperty(default=0, indexed=False)
  busy = ndb.FloatProperty(default=0, indexed=False)
  dead = ndb.FloatProperty(default=0, indexed=False)
  maintenance = ndb.FloatProperty(default=0, indexed=False)
  # This only includes the bots that were not dead, not in maintenance.
  quarantined = ndb.FloatProperty(default=0, indexed=False)
  # TODO(maruel): Fill.
  rebooting = ndb.FloatProperty(default=0, indexed=False)
  # TODO(maruel): Fill.
  overhead = ndb.FloatProperty(default=0, indexed=False)

  def accumulate(self, rhs):
    return stats_framework.accumulate(self, rhs, [])


### Private code


def _generate_stats_bots(start_time, end_time):
  """Returns a _Snapshot filled with the events for the specified interval.
  """
  values = _Snapshot()
  return values


### Public API


STATS_HANDLER = stats_framework.StatisticsFramework(
    'stats_bot', _Snapshot, _generate_stats_bots)


# Action to log.
STORE, RETURN, LOOKUP, DUPE = range(4)


def add_entry(action, number, where):
  """Formatted statistics log entry so it can be processed for daily stats.

  The format is simple enough that it doesn't require a regexp for faster
  processing.
  """
  stats_framework.add_entry(
      '%s; %d; %s' % (_ACTION_NAMES[action], number, where))


def generate_stats():
  """Returns the number of minutes processed."""
  return STATS_HANDLER.process_next_chunk(stats_framework.TOO_RECENT)

