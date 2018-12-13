#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import logging
import os
import random
import sys
import unittest

import test_env_handlers

import webapp2
import webtest

from google.appengine.ext import ndb

from components import utils
from components.prpc import encoding

from proto import swarming_pb2  # pylint: disable=no-name-in-module
from server import task_queues

import handlers_bot
import handlers_prpc


def _decode(raw, dst):
  # Skip escaping characters.
  assert raw[:5] == ')]}\'\n', raw[:5]
  return encoding.get_decoder(encoding.Encoding.JSON)(raw[5:], dst)


def _encode(d):
  # Skip escaping characters.
  raw = encoding.get_encoder(encoding.Encoding.JSON)(d)
  assert raw[:5] == ')]}\'\n', raw[:5]
  return raw[5:]


class PRPCTest(test_env_handlers.AppTestBase):
  """Tests the pRPC handlers."""
  def setUp(self):
    super(PRPCTest, self).setUp()
    # handlers_bot is necessary to run fake tasks.
    routes = handlers_prpc.get_routes() + handlers_bot.get_routes()
    self.app = webtest.TestApp(
        webapp2.WSGIApplication(routes, debug=True),
        extra_environ={
          'REMOTE_ADDR': self.source_ip,
          'SERVER_SOFTWARE': os.environ['SERVER_SOFTWARE'],
        },
    )
    self._headers = {
      'Content-Type': encoding.Encoding.JSON[1],
      'Accept': encoding.Encoding.JSON[1],
    }
    self._enqueue_task_orig = self.mock(
        utils, 'enqueue_task', self._enqueue_task)
    self.now = datetime.datetime(2010, 1, 2, 3, 4, 5)
    self.mock_now(self.now)
    self.mock_default_pool_acl([])

  @ndb.non_transactional
  def _enqueue_task(self, url, queue_name, **kwargs):
    if queue_name == 'rebuild-task-cache':
      # Call directly into it.
      self.assertEqual(True, task_queues.rebuild_task_cache(kwargs['payload']))
      return True
    if queue_name == 'pubsub':
      return True
    self.fail(url)
    return False

  def test_botevents_empty(self):
    msg = swarming_pb2.BotEventsRequest(bot_id=u'id1')
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers)
    self.assertEqual(raw_resp.body, ')]}\'\n{}')

  def test_botevents_invalid_page_size(self):
    msg = swarming_pb2.BotEventsRequest(bot_id=u'id1', page_size=-1)
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers,
        expect_errors=True)
    self.assertEqual(raw_resp.status, '400 Bad Request')
    self.assertEqual(raw_resp.body, 'page_size must be positive')

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

    self.set_as_bot()
    params = self.do_handshake()
    self.set_as_user()
    self.client_create_task_raw()
    self.set_as_bot()
    res = self.bot_poll(params=params)
    now_60 = self.mock_now(self.now, 60)
    # Large page_size is automatically reduced.
    response = self.bot_complete_task(task_id=res['manifest']['task_id'])
    self.assertEqual({u'must_stop': False, u'ok': True}, response)

    params['event'] = 'bot_rebooting'
    params['message'] = 'for the best'
    # TODO(maruel): https://crbug.com/913953
    response = self.post_json('/swarming/api/v1/bot/event', params)
    self.assertEqual({}, response)

    self.set_as_privileged_user()
    msg = swarming_pb2.BotEventsRequest(bot_id=u'bot1', page_size=1001)
    msg.start_time.FromDatetime(self.now)
    msg.end_time.FromDatetime(now_60 + datetime.timedelta(seconds=1))
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers)
    resp = swarming_pb2.BotEventsResponse()
    _decode(raw_resp.body, resp)

    expected = ur"""events {
  event_time {
    seconds: 1262401505
  }
  bot {
    bot_id: "bot1"
    dimensions {
      key: "id"
      values: "bot1"
    }
    dimensions {
      key: "os"
      values: "Amiga"
    }
    dimensions {
      key: "pool"
      values: "default"
    }
    info {
      raw {
        fields {
          key: "bot_group_cfg_version"
          value {
            string_value: "default"
          }
        }
        fields {
          key: "running_time"
          value {
            number_value: 1234.0
          }
        }
        fields {
          key: "sleep_streak"
          value {
            number_value: 0
          }
        }
        fields {
          key: "started_ts"
          value {
            number_value: 1410990411.11
          }
        }
      }
      version: "a5d3d1f287ed010ccfe16c496b9423d9f322737c98a793d8fb97c9a67c312314"
      external_ip: "192.168.2.2"
      authenticated_as: "bot:whitelisted-ip"
    }
  }
  event: BOT_REBOOTING_HOST
  event_msg: "for the best"
}
events {
  event_time {
    seconds: 1262401505
  }
  bot {
    bot_id: "bot1"
    status: BUSY
    current_task_id: "5cee488008811"
    dimensions {
      key: "id"
      values: "bot1"
    }
    dimensions {
      key: "os"
      values: "Amiga"
    }
    dimensions {
      key: "pool"
      values: "default"
    }
    info {
      raw {
        fields {
          key: "bot_group_cfg_version"
          value {
            string_value: "default"
          }
        }
        fields {
          key: "running_time"
          value {
            number_value: 1234.0
          }
        }
        fields {
          key: "sleep_streak"
          value {
            number_value: 0
          }
        }
        fields {
          key: "started_ts"
          value {
            number_value: 1410990411.11
          }
        }
      }
      version: "a5d3d1f287ed010ccfe16c496b9423d9f322737c98a793d8fb97c9a67c312314"
      external_ip: "192.168.2.2"
      authenticated_as: "bot:whitelisted-ip"
    }
  }
  event: TASK_COMPLETED
}
events {
  event_time {
    seconds: 1262401445
  }
  bot {
    bot_id: "bot1"
    status: BUSY
    current_task_id: "5cee488008811"
    dimensions {
      key: "id"
      values: "bot1"
    }
    dimensions {
      key: "os"
      values: "Amiga"
    }
    dimensions {
      key: "pool"
      values: "default"
    }
    info {
      raw {
        fields {
          key: "bot_group_cfg_version"
          value {
            string_value: "default"
          }
        }
        fields {
          key: "running_time"
          value {
            number_value: 1234.0
          }
        }
        fields {
          key: "sleep_streak"
          value {
            number_value: 0
          }
        }
        fields {
          key: "started_ts"
          value {
            number_value: 1410990411.11
          }
        }
      }
      version: "a5d3d1f287ed010ccfe16c496b9423d9f322737c98a793d8fb97c9a67c312314"
      external_ip: "192.168.2.2"
      authenticated_as: "bot:whitelisted-ip"
    }
  }
  event: INSTRUCT_START_TASK
}
events {
  event_time {
    seconds: 1262401445
  }
  bot {
    bot_id: "bot1"
    dimensions {
      key: "id"
      values: "bot1"
    }
    dimensions {
      key: "os"
      values: "Amiga"
    }
    dimensions {
      key: "pool"
      values: "default"
    }
    info {
      raw {
        fields {
          key: "running_time"
          value {
            number_value: 1234.0
          }
        }
        fields {
          key: "sleep_streak"
          value {
            number_value: 0
          }
        }
        fields {
          key: "started_ts"
          value {
            number_value: 1410990411.11
          }
        }
      }
      version: "123"
      external_ip: "192.168.2.2"
      authenticated_as: "bot:whitelisted-ip"
    }
  }
  event: BOT_NEW_SESSION
}
"""
    self.assertEqual(expected, unicode(resp))

    # Now test with a subset.
    msg = swarming_pb2.BotEventsRequest(bot_id=u'bot1')
    msg.start_time.FromDatetime(now_60)
    msg.end_time.FromDatetime(now_60 + datetime.timedelta(seconds=1))
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers)
    resp = swarming_pb2.BotEventsResponse()
    _decode(raw_resp.body, resp)

if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.FATAL)
  unittest.main()
