#!/usr/bin/env vpython
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import logging
import os
import random
import sys
import unittest
import json
import cgi
import mock
from parameterized import parameterized

import test_env_handlers

import webapp2
import webtest

from test_support import test_case

from components.prpc import encoding
from components import auth

from proto.api import swarming_api_pb2

from server import bot_management
from server import acl

import handlers_bot
import handlers_prpc
import message_conversion_prpc

import google.protobuf as proto


# 2010-01-02T03:04:05Z
def fmtdate(d, fmt='%Y-%m-%dT%H:%M:%SZ'):
  """Formats a datetime.datetime instance to the format generated by the API.
  API datetime responses return at UTC+0 hence the Z at the end."""
  return unicode(d.strftime(fmt))


def _decode(raw, dst):
  assert raw[:5] == ')]}\'\n', raw[:5]
  return encoding.get_decoder(encoding.Encoding.JSON)(raw[5:], dst)


def _decode_dict(dct, out):
  return proto.json_format.ParseDict(dct, out)


def _encode(d):
  raw = encoding.get_encoder(encoding.Encoding.JSON)(d)
  assert raw[:5] == ')]}\'\n', raw[:5]
  return raw[5:]


def _bot_event(event_type, bot_id, **kwargs):
  args = {
      'authenticated_as': 'bot:whitelisted-ip',
      'dimensions': {
          u'id': [bot_id],
          u'pool': [u'default']
      },
      'external_ip': '8.8.4.4',
      'state': {
          'ram': 65
      },
      'version': '123456789',
      'quarantined': False,
      'maintenance_msg': None,
      'task_id': None,
      'task_name': None,
      'register_dimensions': event_type.startswith('request_')
  }
  args.update(kwargs)
  return bot_management.bot_event(event_type, bot_id, **args)


class PrpcTest(test_env_handlers.AppTestBase):
  no_run = 1
  service = None

  def apply_defaults_for_run_result(self, result):
    """Returns a serialized swarming_rpcs.TaskResult initialized from a
    TaskRunResult.

    To be used for expectations.
    """
    result.bot_dimensions.extend([
        swarming_api_pb2.StringListPair(key='id', value=['bot1']),
        swarming_api_pb2.StringListPair(key='os', value=['Amiga']),
        swarming_api_pb2.StringListPair(key='pool', value=['default'])
    ])
    result.bot_id = 'bot1'
    result.bot_version = self.bot_version
    result.costs_usd.extend([0.0])
    result.current_task_slice = 0
    result.failure = False
    result.internal_failure = False
    result.name = 'job1'
    result.run_id = '5cee488008811'
    result.server_versions.extend(['v1a'])
    result.state = swarming_api_pb2.TaskState.RUNNING
    result.task_id = '5cee488008811'
    return result

  def gen_perf_stats_prpc(self, stats):
    """Returns a serialized swarming_rpcs.PerformanceStats.

    To be used for expectations.
    """
    stats.bot_overhead = 0.1
    stats.cache_trim.duration = 0.1
    stats.isolated_download.duration = 1.0
    stats.isolated_download.initial_size = 100000
    stats.isolated_download.initial_number_items = 10
    stats.isolated_download.items_cold = b'x\234\023\001\000\000\025\000\025'
    stats.isolated_download.items_hot = b'x\234\223\343\002\000\000H\000)'
    stats.isolated_download.num_items_cold = 1
    stats.isolated_download.total_bytes_items_cold = 20
    stats.isolated_download.num_items_hot = 2
    stats.isolated_download.total_bytes_items_hot = 70

    stats.isolated_upload.duration = 2.0
    stats.isolated_upload.items_cold = b'x\234cdT\003\000\000.\000)'
    stats.isolated_upload.items_hot = b'x\234cdd\324\007\000\000<\0003'
    stats.isolated_upload.num_items_cold = 3
    stats.isolated_upload.total_bytes_items_cold = 43
    stats.isolated_upload.num_items_hot = 4
    stats.isolated_upload.total_bytes_items_hot = 56

    stats.cleanup.duration = 0.1
    stats.package_installation.duration = 3.0
    stats.named_caches_install.duration = 0.1
    stats.named_caches_uninstall.duration = 0.1

  def post_prpc(self, rpc, request, expect_errors=False):
    assert self.service, "Child classes must define service"

    return self.app.post('/prpc/%s/%s' % (self.service, rpc),
                         _encode(request),
                         self._headers,
                         expect_errors=expect_errors)


class BotServicePrpcTest(PrpcTest):
  """Tests the pRPC handlers."""
  def setUp(self):
    super(BotServicePrpcTest, self).setUp()
    self.service = "swarming_api.v1.Bot"
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
    self.now = datetime.datetime(2010, 1, 2, 3, 4, 5)
    self.mock_now(self.now)
    self.mock_default_pool_acl([])
    self.mock_tq_tasks()

  def test_bot_get(self):
    self.set_as_bot()
    self.do_handshake()
    self.set_as_privileged_user()
    request = swarming_api_pb2.BotRequest(bot_id="bot1", )
    resp = self.post_prpc("GetBot", request)
    actual_info = swarming_api_pb2.BotInfo()
    _decode(resp.body, actual_info)
    expected = message_conversion_prpc.bot_info_to_proto(
        bot_management.get_info_key('bot1').get())
    self.assertEqual(expected, actual_info)

  def test_bot_in_maintenance(self):
    self.set_as_privileged_user()
    _bot_event('request_sleep', 'bot1', maintenance_msg='boiling water')
    request = swarming_api_pb2.BotRequest(bot_id="bot1", )
    resp = self.post_prpc("GetBot", request)
    actual_info = swarming_api_pb2.BotInfo()
    _decode(resp.body, actual_info)
    expected = message_conversion_prpc.bot_info_to_proto(
        bot_management.get_info_key('bot1').get())
    self.assertTrue(actual_info.maintenance_msg)
    self.assertEqual(expected, actual_info)

  def test_bot_get_not_found(self):
    self.set_as_privileged_user()
    request = swarming_api_pb2.BotRequest(bot_id="bot1", )
    resp = self.post_prpc("GetBot", request, expect_errors=True)
    self.assertEqual(resp.status, '404 Not Found')
    self.assertEqual(resp.body, 'bot not found')

  def test_get_deleted_bot(self):
    bot_id = "bot1"
    _bot_event('bot_connected', bot_id=bot_id, state={'foo': 0})
    self.set_as_admin()
    request = swarming_api_pb2.BotRequest(bot_id=bot_id, )
    resp = self.post_prpc("DeleteBot", request)
    expected = swarming_api_pb2.DeletedResponse(deleted=True)
    actual = swarming_api_pb2.DeletedResponse(deleted=True)
    _decode(resp.body, actual)
    self.assertEqual(expected, actual)

    # Now check whether the bot still exists, it will return not found
    request = swarming_api_pb2.BotRequest(bot_id=bot_id, )
    resp = self.post_prpc("GetBot", request)
    self.assertEqual(resp.status, '200 OK')
    ghost_bot = swarming_api_pb2.BotInfo()
    _decode(resp.body, ghost_bot)
    self.assertTrue(ghost_bot.deleted)

  def test_unauthorized_bot_not_found(self):
    self.set_as_anonymous()
    request = swarming_api_pb2.BotRequest(bot_id="bot1", )
    resp = self.post_prpc("GetBot", request, expect_errors=True)
    self.assertEqual(resp.status, '403 Forbidden')
    self.assertEqual(resp.body, 'Access is denied.')

  @parameterized.expand([
      'GetBot',
      'ListBotEvents',
  ])
  def test_get_ok_realm(self, api):
    # non-privileged user with realm permission.
    self.mock_auth_db([auth.Permission('swarming.pools.listBots')])
    self.set_as_user()

    _bot_event('bot_connected', bot_id='id1')
    resp = self.post_prpc(api,
                          swarming_api_pb2.BotRequest(bot_id='id1'),
                          expect_errors=True)
    self.assertEqual(resp.status, '403 Forbidden')

  @parameterized.expand([
      'GetBot',
      'ListBotEvents',
  ])
  def test_get_forbidden(self, api):
    self.mock_auth_db([])

    # non-privileged user with no realm permission.
    self.set_as_user()

    # alive bot
    _bot_event('bot_connected', bot_id='id1')
    resp = self.post_prpc(api,
                          swarming_api_pb2.BotRequest(bot_id='id1'),
                          expect_errors=True)
    self.assertEqual(resp.status, '403 Forbidden')

    # deleted bot
    with mock.patch('server.acl._is_admin', return_value=True):
      self.post_prpc('DeleteBot', swarming_api_pb2.BotRequest(bot_id='id1'))
    resp = self.post_prpc(api,
                          swarming_api_pb2.BotRequest(bot_id='id1'),
                          expect_errors=True)
    self.assertEqual(resp.status, '403 Forbidden')

  def test_delete_ok(self):
    """Assert that delete finds and deletes a bot."""
    self.set_as_admin()
    self.mock(acl, '_is_admin', lambda *_args, **_kwargs: True)
    state = {
        'dict': {
            'random': 'values'
        },
        'float': 0.,
        'list': ['of', 'things'],
        'str': u'uni',
    }
    _bot_event('request_sleep', bot_id='id1', state=state)

    # delete the bot
    resp = self.post_prpc('DeleteBot',
                          swarming_api_pb2.BotRequest(bot_id='id1'))
    actual = swarming_api_pb2.DeletedResponse()
    _decode(resp.body, actual)
    self.assertEqual(swarming_api_pb2.DeletedResponse(deleted=True), actual)

    # is it gone?
    resp = self.post_prpc('DeleteBot',
                          swarming_api_pb2.BotRequest(bot_id='id1'),
                          expect_errors=True)
    self.assertEqual(resp.status, '404 Not Found')

  def test_events(self):
    # Run one task, push an event manually.
    second = datetime.timedelta(seconds=1)
    self.mock(random, 'getrandbits', lambda _: 0x88)
    first_ticker = test_case.Ticker(self.now, datetime.timedelta(seconds=1))
    t1 = self.mock_now(first_ticker())

    self.set_as_bot()
    params = self.do_handshake()
    t2 = self.mock_now(first_ticker())

    self.bot_poll(params=params)
    self.set_as_user()
    self.client_create_task_raw()
    self.set_as_bot()
    t3 = self.mock_now(first_ticker())

    res = self.bot_poll(params=params)
    now_60 = first_ticker.last() + datetime.timedelta(seconds=60)
    second_ticker = test_case.Ticker(now_60, datetime.timedelta(seconds=1))
    t4 = self.mock_now(second_ticker())

    resp = self.bot_complete_task(task_id=res['manifest']['task_id'])
    self.assertEqual({u'must_stop': False, u'ok': True}, resp)
    params['event'] = 'bot_rebooting'
    params['message'] = 'for the best'
    t5 = self.mock_now(second_ticker())

    resp = self.post_json('/swarming/api/v1/bot/event', params)
    self.assertEqual({}, resp)
    start = first_ticker.first()
    end = second_ticker.last()
    self.set_as_privileged_user()
    request = swarming_api_pb2.BotEventsRequest(bot_id="bot1", limit=200)
    request.start.FromDatetime(start)
    request.end.FromDatetime(end + second)
    resp = self.post_prpc("ListBotEvents", request)
    dimensions = [
        {
            u'key': u'id',
            u'value': [u'bot1']
        },
        {
            u'key': u'os',
            u'value': [u'Amiga']
        },
        {
            u'key': u'pool',
            u'value': [u'default']
        },
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
    items = [
        {
            u'authenticated_as': u'bot:whitelisted-ip',
            u'dimensions': dimensions,
            u'event_type': u'bot_rebooting',
            u'external_ip': unicode(self.source_ip),
            u'message': u'for the best',
            u'quarantined': False,
            u'state': state,
            u'ts': fmtdate(t5),
            u'version': unicode(self.bot_version),
        },
        {
            u'authenticated_as': u'bot:whitelisted-ip',
            u'dimensions': dimensions,
            u'event_type': u'task_completed',
            u'external_ip': unicode(self.source_ip),
            u'quarantined': False,
            u'state': state,
            u'task_id': res['manifest']['task_id'],
            u'ts': fmtdate(t4),
            u'version': unicode(self.bot_version),
        },
        {
            u'authenticated_as': u'bot:whitelisted-ip',
            u'dimensions': dimensions,
            u'event_type': u'request_task',
            u'external_ip': unicode(self.source_ip),
            u'quarantined': False,
            u'state': state,
            u'task_id': res['manifest']['task_id'],
            u'ts': fmtdate(t3),
            u'version': unicode(self.bot_version),
        },
        {
            u'authenticated_as': u'bot:whitelisted-ip',
            u'dimensions': dimensions,
            u'event_type': u'request_sleep',
            u'external_ip': unicode(self.source_ip),
            u'quarantined': False,
            u'state': state,
            u'ts': fmtdate(t2),
            u'version': unicode(self.bot_version),
        },
        {
            u'authenticated_as': u'bot:whitelisted-ip',
            u'dimensions': dimensions,
            u'event_type': u'bot_connected',
            u'external_ip': unicode(self.source_ip),
            u'quarantined': False,
            u'state': state_no_cfg_ver,
            u'ts': fmtdate(t1),
            u'version': u'123',
        },
    ]
    expected = swarming_api_pb2.BotEventsResponse()
    _decode_dict(dict(items=items), expected)
    actual = swarming_api_pb2.BotEventsResponse()
    _decode(resp.body, actual)

    # Now test with a subset.
    start = second_ticker.first()
    end = second_ticker.last()
    request = swarming_api_pb2.BotEventsRequest(bot_id="bot1", limit=200)
    request.start.FromDatetime(start)
    request.end.FromDatetime(end + second)
    _encode(request)
    resp = self.post_prpc("ListBotEvents", request)
    actual = swarming_api_pb2.BotEventsResponse()
    _decode(resp.body, actual)

    # actual.items[:] converts to a list so it can be compared with expected
    # items
    self.assertEqual(expected.items[:2], actual.items[:])

  def test_terminate_admin(self):
    self.set_as_bot()
    self.bot_poll()
    self.mock(random, 'getrandbits', lambda _: 0x88)

    self.set_as_admin()
    request = swarming_api_pb2.BotRequest(bot_id="bot1")
    resp = self.post_prpc('TerminateBot', request)
    actual = swarming_api_pb2.TerminateResponse()
    _decode(resp.body, actual)
    expected = swarming_api_pb2.TerminateResponse(task_id='5cee488008810')
    self.assertEqual(expected, actual)

  def test_terminate_privileged_user(self):
    self.set_as_bot()
    self.bot_poll()
    self.mock(random, 'getrandbits', lambda _: 0x88)

    self.set_as_privileged_user()
    request = swarming_api_pb2.BotRequest(bot_id="bot1")
    resp = self.post_prpc('TerminateBot', request)
    actual = swarming_api_pb2.TerminateResponse()
    _decode(resp.body, actual)
    expected = swarming_api_pb2.TerminateResponse(task_id='5cee488008810')
    self.assertEqual(expected, actual)

  def test_terminate_user(self):
    self.set_as_bot()
    self.bot_poll()
    self.mock(random, 'getrandbits', lambda _: 0x88)

    # without realm permission.
    self.set_as_user()
    self.mock_auth_db([])
    request = swarming_api_pb2.BotRequest(bot_id="bot1")
    resp = self.post_prpc('TerminateBot', request, expect_errors=True)
    expected = cgi.escape(
        'user "user@example.com" does not have '
        'permission "swarming.pools.terminateBot"',
        quote=True)
    self.assertEqual(expected, resp.body)

    # give permission.
    self.mock_auth_db([auth.Permission('swarming.pools.terminateBot')])
    request = swarming_api_pb2.BotRequest(bot_id="bot1")
    resp = self.post_prpc('TerminateBot', request)
    actual = swarming_api_pb2.TerminateResponse()
    _decode(resp.body, actual)
    expected = swarming_api_pb2.TerminateResponse(task_id='5cee488008810')
    self.assertEqual(expected, actual)

  def test_tasks_ok(self):
    """Asserts that tasks produces bot information."""
    self.mock(random, 'getrandbits', lambda _: 0x88)

    self.set_as_bot()
    self.bot_poll()
    self.set_as_user()
    self.client_create_task_raw()
    self.set_as_bot()
    res = self.bot_poll()
    response = self.bot_complete_task(task_id=res['manifest']['task_id'])
    self.assertEqual({u'must_stop': False, u'ok': True}, response)

    now_1 = self.mock_now(self.now, 1)
    self.mock(random, 'getrandbits', lambda _: 0x55)
    self.set_as_user()
    self.client_create_task_raw(name='philbert')
    self.set_as_bot()
    res = self.bot_poll()
    response = self.bot_complete_task(exit_code=1,
                                      task_id=res['manifest']['task_id'])
    self.assertEqual({u'must_stop': False, u'ok': True}, response)

    start = self.now + datetime.timedelta(seconds=0.5)
    end = now_1 + datetime.timedelta(seconds=0.5)

    self.set_as_privileged_user()
    request = swarming_api_pb2.BotTasksRequest()
    request.bot_id = 'bot1'
    request.start.FromDatetime(start)
    request.end.FromDatetime(end)
    request.sort = swarming_api_pb2.TaskQuery.Sort.CREATED_TS
    request.state = swarming_api_pb2.TaskQuery.State.ALL
    request.include_performance_stats = True
    request.limit = 100
    response = self.post_prpc('ListBotTasks', request)
    actual = swarming_api_pb2.TaskListResponse()
    _decode(response.body, actual)

    expected = swarming_api_pb2.TaskResultResponse()
    self.apply_defaults_for_run_result(expected)
    expected.bot_idle_since_ts.FromDatetime(now_1)
    expected.completed_ts.FromDatetime(now_1)
    expected.modified_ts.FromDatetime(now_1)
    expected.started_ts.FromDatetime(now_1)
    expected.created_ts.FromDatetime(now_1)
    expected.duration = 0.1
    expected.name = 'philbert'
    expected.exit_code = 1
    expected.failure = True
    expected.run_id = '5cee870005511'
    expected.state = swarming_api_pb2.TaskState.COMPLETED
    expected.task_id = '5cee870005511'
    expected.costs_usd[:] = [0.1]
    self.gen_perf_stats_prpc(expected.performance_stats)
    self.assertEqual(expected, actual.items[0])

    for sort in (swarming_api_pb2.TaskQuery.Sort.COMPLETED_TS,
                 swarming_api_pb2.TaskQuery.Sort.STARTED_TS):
      request = swarming_api_pb2.BotTasksRequest()
      request.bot_id = 'bot1'
      request.sort = sort
      request.state = swarming_api_pb2.TaskQuery.State.ALL
      request.include_performance_stats = True
      request.limit = 100
      response = self.post_prpc('ListBotTasks', request)
      self.assertEqual(response.status, '200 OK')


class TaskServicePrpcTest(PrpcTest):
  def setUp(self):
    super(TaskServicePrpcTest, self).setUp()
    self.service = "swarming_api.v1.Task"
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
    self.now = datetime.datetime(2010, 1, 2, 3, 4, 5)
    self.mock_now(self.now)
    self.mock_default_pool_acl([])
    self.mock_tq_tasks()

  def test_result_unknown(self):
    """Asserts that result raises 404 for unknown task IDs."""
    self.set_as_privileged_user()
    resp = self.post_prpc(
        'GetResult',
        swarming_api_pb2.TaskIdWithPerfRequest(task_id='12310'),
        expect_errors=True)
    self.assertEqual(resp.status, '404 Not Found')

  def test_result_long(self):
    """Asserts that result raises 400 for wildly invalid task IDs."""
    self.set_as_privileged_user()
    resp = self.post_prpc(
        'GetResult',
        swarming_api_pb2.TaskIdWithPerfRequest(task_id='12310' * 10),
        expect_errors=True)
    self.assertEqual(resp.status, '400 Bad Request')

  def test_result_ok(self):
    """Asserts that result produces a result entity."""
    self.mock(random, 'getrandbits', lambda _: 0x88)
    self.set_as_bot()
    self.bot_poll()

    # pending task
    self.set_as_user()
    _, task_id = self.client_create_task_raw()
    response = self.post_prpc(
        'GetResult', swarming_api_pb2.TaskIdWithPerfRequest(task_id=task_id))
    expected = swarming_api_pb2.TaskResultResponse()
    expected.created_ts.FromDatetime(self.now)
    expected.modified_ts.FromDatetime(self.now)
    expected.failure = False
    expected.internal_failure = False
    expected.name = 'job1'
    expected.server_versions[:] = ['v1a']
    expected.state = swarming_api_pb2.TaskState.PENDING
    expected.tags[:] = [
        u'a:tag',
        u'authenticated:user:user@example.com',
        u'os:Amiga',
        u'pool:default',
        u'priority:20',
        u'realm:none',
        u'service_account:none',
        u'swarming.pool.template:none',
        u'swarming.pool.version:pools_cfg_rev',
        u'user:joe@localhost',
    ]
    expected.task_id = '5cee488008810'
    expected.user = 'joe@localhost'

    actual = swarming_api_pb2.TaskResultResponse()
    _decode(response.body, actual)
    self.assertEqual(expected, actual)

    # no bot started: running task
    run_id = task_id[:-1] + '1'
    response = self.post_prpc(
        'GetResult',
        swarming_api_pb2.TaskIdWithPerfRequest(task_id=run_id),
        expect_errors=True)
    self.assertEqual(response.status, '404 Not Found')

    # run as bot
    self.set_as_bot()
    self.bot_poll()

    self.set_as_user()
    response = self.post_prpc(
        'GetResult', swarming_api_pb2.TaskIdWithPerfRequest(task_id=run_id))
    expected = swarming_api_pb2.TaskResultResponse()
    self.apply_defaults_for_run_result(expected)
    expected.bot_idle_since_ts.FromDatetime(self.now)
    expected.created_ts.FromDatetime(self.now)
    expected.modified_ts.FromDatetime(self.now)
    expected.started_ts.FromDatetime(self.now)
    expected.current_task_slice = 0
    actual = swarming_api_pb2.TaskResultResponse()
    _decode(response.body, actual)
    self.assertEqual(expected, actual)

  def test_result_completed_task(self):
    """Tests that completed tasks are correctly reported."""
    self.set_as_bot()
    self.bot_poll()
    self.set_as_user()
    self.client_create_task_raw()
    self.set_as_bot()
    task_id = self.bot_run_task()
    # First ask without perf metadata.
    self.set_as_user()
    response = self.post_prpc(
        'GetResult',
        swarming_api_pb2.TaskIdWithPerfRequest(task_id=task_id,
                                               include_performance_stats=True))

    expected = swarming_api_pb2.TaskResultResponse()
    self.apply_defaults_for_run_result(expected)
    self.gen_perf_stats_prpc(expected.performance_stats)
    expected.bot_idle_since_ts.FromDatetime(self.now)
    expected.completed_ts.FromDatetime(self.now)
    expected.modified_ts.FromDatetime(self.now)
    expected.created_ts.FromDatetime(self.now)
    expected.started_ts.FromDatetime(self.now)
    expected.state = swarming_api_pb2.TaskState.COMPLETED
    expected.costs_usd[:] = [0.1]
    expected.run_id = task_id
    expected.task_id = task_id
    expected.duration = 0.1
    actual = swarming_api_pb2.TaskResultResponse()
    _decode(response.body, actual)
    self.assertEqual(expected, actual)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.FATAL)
  unittest.main()
