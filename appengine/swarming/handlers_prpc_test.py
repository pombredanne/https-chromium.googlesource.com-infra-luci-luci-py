#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import os
import random
import sys
import unittest

import test_env_handlers

import webapp2
import webtest

from components.prpc import encoding
from test_support import test_case

from proto import swarming_pb2  # pylint: disable=no-name-in-module

import handlers_bot
import handlers_prpc


def _decode(raw, dst):
  # Skip escaping characters.
  assert raw[:5] == ')]}\'\n', raw[:5]
  return encoding.get_decoder(encoding.Encoding.JSON)(raw[5:], dst)


def _encode(d):
  # Skip escaping characters.
  raw = encoding.get_encoder(encoding.Encoding.JSON)(d)
  return raw[5:]


class PRPCTest(test_env_handlers.AppTestBase):
  """Tests the pRPC handlers."""
  def setUp(self):
    super(PRPCTest, self).setUp()
    # handlers_bot is necessary to create fake tasks.
    #self.app = webtest.TestApp(
    #    webapp2.WSGIApplication(handlers_bot.get_routes(), debug=True),
    #    extra_environ={
    #      'REMOTE_ADDR': self.source_ip,
    #      'SERVER_SOFTWARE': os.environ['SERVER_SOFTWARE'],
    #    })
    routes = handlers_prpc.get_routes() + handlers_bot.get_routes()
    self.app = webtest.TestApp(
        webapp2.WSGIApplication(routes, debug=True),
        extra_environ={
          'REMOTE_ADDR': self.source_ip,
          'SERVER_SOFTWARE': os.environ['SERVER_SOFTWARE'],
        },
        #extra_environ={'REMOTE_ADDR': '::ffff:127.0.0.1'},
    )
    self._headers = {
      'Content-Type': encoding.Encoding.JSON[1],
      'Accept': encoding.Encoding.JSON[1],
    }

  def test_botevents_empty(self):
    msg = swarming_pb2.BotEventsRequest(bot_id=u'id1')
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers)
    self.assertEqual(raw_resp.body, ')]}\'\n{}')

  def test_botevents_invalid_page_size(self):
    msg = swarming_pb2.BotEventsRequest(bot_id=u'id1', page_size=1001)
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers,
        expect_errors=True)
    self.assertEqual(raw_resp.status, '400 Bad Request')
    self.assertEqual(raw_resp.body, 'page_size must be between 1 and 1000')

  def test_botevents_invalid_bot_id(self):
    msg = swarming_pb2.BotEventsRequest()
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers,
        expect_errors=True)
    self.assertEqual(raw_resp.status, '400 Bad Request')
    self.assertEqual(raw_resp.body, 'specify bot_id')

  def test_botevents(self):
    # Run one task, push an event manually.
    self.mock(random, 'getrandbits', lambda _: 0x88)
    #self.mock_default_pool_acl([])

    self.set_as_bot()
    params = self.do_handshake()
    self.set_as_user()
    self.client_create_task_raw()
    self.set_as_bot()
    res = self.bot_poll(params=params)
    now_60 = self.mock_now(self.now, 60)
    response = self.bot_complete_task(task_id=res['manifest']['task_id'])
    self.assertEqual({u'must_stop': False, u'ok': True}, response)

    params['event'] = 'bot_rebooting'
    params['message'] = 'for the best'
    # TODO(maruel): https://crbug.com/913953
    response = self.post_json('/swarming/api/v1/bot/event', params)
    self.assertEqual({}, response)

    self.set_as_privileged_user()
    start = utils.datetime_to_timestamp(self.now) / 1000000.
    end = utils.datetime_to_timestamp(now_60) / 1000000.
    msg = swarming_pb2.BotEventsRequest(bot_id=u'bot1', start=start, end=end+1)
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers)
    resp = swarming_pb2.BotEventsResponse()
    _decode(raw, resp)
    dimensions = [
      {u'key': u'id', u'value': [u'bot1']},
      {u'key': u'os', u'value': [u'Amiga']},
      {u'key': u'pool', u'value': [u'default']},
    ]
    state_dict = {
      'bot_group_cfg_version': 'default',
      'running_time': 1234.,
      'sleep_streak': 0,
      'started_ts': 1410990411.111,
    }
    state = unicode(
        json.dumps(state_dict, sort_keys=True, separators=(',', ':')))
    state_dict.pop('bot_group_cfg_version')
    state_no_cfg_ver = unicode(
        json.dumps(state_dict, sort_keys=True, separators=(',', ':')))
    expected = {
      u'items': [
        {
          u'authenticated_as': u'bot:whitelisted-ip',
          u'dimensions': dimensions,
          u'event_type': u'bot_rebooting',
          u'external_ip': unicode(self.source_ip),
          u'message': u'for the best',
          u'quarantined': False,
          u'state': state,
          u'ts': fmtdate(now_60),
          u'version': unicode(self.bot_version),
        },
        {
          u'authenticated_as': u'bot:whitelisted-ip',
          u'dimensions': dimensions,
          u'event_type': u'task_completed',
          u'external_ip': unicode(self.source_ip),
          u'quarantined': False,
          u'state': state,
          u'task_id': u'5cee488008811',
          u'ts': fmtdate(now_60),
          u'version': unicode(self.bot_version),
        },
        {
          u'authenticated_as': u'bot:whitelisted-ip',
          u'dimensions': dimensions,
          u'event_type': u'request_task',
          u'external_ip': unicode(self.source_ip),
          u'quarantined': False,
          u'state': state,
          u'task_id': u'5cee488008811',
          u'ts': fmtdate(self.now),
          u'version': unicode(self.bot_version),
        },
        {
          u'authenticated_as': u'bot:whitelisted-ip',
          u'dimensions': dimensions,
          u'event_type': u'bot_connected',
          u'external_ip': unicode(self.source_ip),
          u'quarantined': False,
          u'state': state_no_cfg_ver,
          u'ts': fmtdate(self.now),
          u'version': u'123',
        },
      ],
        u'now': fmtdate(now_60),
    }
    self.assertEqual(expected, response.json)

    # Now test with a subset.
    body = message_to_dict(
        handlers_endpoints.BotEventsRequest.combined_message_class(
            bot_id='bot1', start=end, end=end+1))
    response = self.call_api('events', body=body)
    expected['items'] = expected['items'][:-2]
    self.assertEqual(expected, response.json)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.FATAL)
  unittest.main()
