# coding: utf-8
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Generates statistics for the bots. Contains the backend code."""

from google.appengine.ext import ndb

from components import stats_framework


### Models


class _BotsPoolSnapshot(ndb.Model):
  """Snapshot of statistics for bots in a pool, to be embedded in _BotsSnapshot.
  """
  # The pool's name.
  name = ndb.StringProperty()

  # Events. See bot_management.BotEvent.ALLOWED_EVENTS
  # A bot connected.
  connection = ndb.IntegerProperty(default=0)
  # A bot reported an error.
  error = ndb.IntegerProperty(default=0)
  # A bot was leased via Machine Provider.
  leased = ndb.IntegerProperty(default=0)
  # A bot was terminated via the terminate API.
  terminate = ndb.IntegerProperty(default=0)
  # A bot rebooted.
  reboot = ndb.IntegerProperty(default=0)
  # A bot updated.
  update = ndb.IntegerProperty(default=0)
  # A bot shutdown for another reason that terminate, reboot or update.
  shutdown = ndb.IntegerProperty(default=0)

  # Each bot·second state. The sum should hopefully be equal to the number of
  # bots known, divided by the amount of time this represents in seconds.
  idle_secs = ndb.FloatProperty(default=0.)
  busy_secs = ndb.FloatProperty(default=0.)
  dead_secs = ndb.FloatProperty(default=0.)
  maintenance_secs = ndb.FloatProperty(default=0.)
  # This only includes the bots that were not dead nor in maintenance.
  quarantined_secs = ndb.FloatProperty(default=0.)
  rebooting_secs = ndb.FloatProperty(default=0.)
  overhead_secs = ndb.FloatProperty(default=0.)

  def accumulate(self, rhs):
    return stats_framework.accumulate(self, rhs, ['name'])


class _BotsSnapshot(ndb.Model):
  """Snapshot of bots statistics, to be embedded in stats_framework."""
  pools = ndb.LocalStructuredProperty(_BotsPoolSnapshot)


### Private code


def _generate_stats_bots(start_time, end_time):
  """Returns a _BotsSnapshot filled with the events for the specified interval.

  The time spent by each bot is reconstructed by the closest BotEvent found.
  """
  # We need to figure out all bots that existed during this time frame!
  # 20000 bots / 10 minutes = 33 bots/s.
  pools = {}
  for bot in bot_management.BotInfo.query():
    pools.setdefault(bot.pool, []).append(bot)

  #for bot in bot_management.BotEvent.query(
  #    bot_management.BotEvent.ts < end_time):
  #  pools.setdefault(bot.pool, []).append(bot)

  s = _BotsSnapshot()
  for pool, bots in pools.iteritems():
    sp = _BotsPoolSnapshot(name=pool)
    sp.idle = 2
    s.pools.append(sp)
  s.pools.sort(key=lambda x: x.name)
  return s


### Public API


STATS_HANDLER = stats_framework.StatisticsFramework(
    'stats_bot', _BotsSnapshot, _generate_stats_bots)


def cron_generate_stats():
  """Returns the number of minutes processed."""
  return STATS_HANDLER.process_next_chunk(
      config.settings().bot_death_timeout_secs / 60 + 1)
