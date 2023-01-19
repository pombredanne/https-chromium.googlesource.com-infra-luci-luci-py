#!/usr/bin/env vpython
# Copyright 2023 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import logging
import mock
import unittest
import sys

import swarming_test_env
swarming_test_env.setup_test_env()

from test_support import test_case

from server import bot_management

import api_common


def _bot_event(bot_id=None,
               external_ip='8.8.4.4',
               authenticated_as=None,
               dimensions=None,
               state=None,
               version=u"12345",
               quarantined=False,
               maintenance_msg=None,
               task_id=None,
               task_name=None,
               register_dimensions=False,
               **kwargs):
  """Calls bot_management.bot_event with default arguments."""
  if not bot_id:
    bot_id = u'id1'
  if not dimensions:
    dimensions = {
        u'id': [bot_id],
        u'os': [u'Ubuntu', u'Ubuntu-16.04'],
        u'pool': [u'default'],
    }
  if not authenticated_as:
    authenticated_as = u'bot:%s.domain' % bot_id
  return bot_management.bot_event(bot_id=bot_id,
                                  external_ip=external_ip,
                                  authenticated_as=authenticated_as,
                                  dimensions=dimensions,
                                  state=state or {'ram': 65},
                                  version=version,
                                  quarantined=quarantined,
                                  maintenance_msg=maintenance_msg,
                                  task_id=task_id,
                                  task_name=task_name,
                                  register_dimensions=register_dimensions,
                                  **kwargs)


class ApiCommonTest(test_case.TestCase):
  APP_DIR = swarming_test_env.APP_DIR

  def test_race_condition_handling_get_bot(self):
    """Tests a specific race condition described http://go/crb/1407381

    It simulates the race condition by patching the first call to
    `bot_management.get_info_key` in `api_common.get_bot` to also write a
    "bot_connected" event. This would simulate a `bot/handshake` happening after
    the first read of `bot_info` but before the read of `bot_event` in
    `bot_management.get_events_query`
    """
    self.mock_now(datetime.datetime(2010, 1, 2, 3, 4, 5, 6))
    bot_id = 'bot1'
    _bot_event(bot_id=bot_id, event_type='bot_connected')
    expected_bot = bot_management.get_info_key(bot_id).get()
    bot_management.get_info_key(bot_id).delete()
    get_bot = bot_management.get_info_key
    with mock.patch('server.bot_management.get_info_key',
                    new_callable=mock.Mock) as m:

      def side_effect(bot_id):
        # changing the side effect to be the unpatched
        # bot_management.get_info_key means that the side_effect_once function
        # will only be run a single time before reverting to normal
        # bot_management.get_info_key
        m.side_effect = get_bot
        bot = get_bot(bot_id=bot_id)
        _bot_event(bot_id=bot_id, event_type='bot_connected')
        # due to setup the first call to get_bot should return nothing
        self.assertNone(bot)
        return bot

      m.side_effect = side_effect
      bot, deleted = api_common.get_bot(bot_id)
      self.assertFalse(deleted)
      self.assertEqual(expected_bot, bot)


if __name__ == '__main__':
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.ERROR)
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
