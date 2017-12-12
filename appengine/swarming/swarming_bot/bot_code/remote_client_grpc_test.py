#!/usr/bin/env python
# Copyright 2016 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import time
import unittest

import test_env_bot_code
test_env_bot_code.setup_test_env()

from depot_tools import auto_stub
import remote_client_grpc

from google.protobuf import empty_pb2


class FakeGrpcProxy(object):

  def __init__(self, testobj):
    self._testobj = testobj

  @property
  def prefix(self):
    return 'inst'

  def call_unary(self, name, request):
    return self._testobj._handle_call(name, request)


class TestRemoteClientGrpc(auto_stub.TestCase):

  def setUp(self):
    super(TestRemoteClientGrpc, self).setUp()
    self._num_sleeps = 0

    def fake_sleep(_time):
      self._num_sleeps += 1

    self.mock(time, 'sleep', fake_sleep)
    self._client = remote_client_grpc.RemoteClientGrpc('', FakeGrpcProxy(self))
    self._expected = []
    self._error_codes = []

  def _handle_call(self, method, request):
    """This is called by FakeGrpcProxy to implement fake calls."""
    # Pop off the first item on the list
    self.assertTrue(self._expected)
    expected, self._expected = self._expected[0], self._expected[1:]
    # Each element of the "expected" array should be a 3-tuple:
    #    * The name of the method (eg 'TaskUpdate')
    #    * The proto request
    #    * The proto response
    self.assertEqual(method, expected[0])
    self.assertEqual(str(request), str(expected[1]))
    return expected[2]

  def test_handshake(self):
    """Tests the handshake proto."""
    attrs = {
        'version': '123',
        'dimensions': {
            'id': ['robocop'],
            'pool': ['swimming'],
            'mammal': ['ferrett', 'wombat'],
        },
        'state': {},
    }

    msg_req = remote_client_grpc.bots_pb2.CreateBotSessionRequest()
    msg_req.parent = 'inst'
    session = msg_req.bot_session
    session.bot_id = 'robocop'
    session.status = remote_client_grpc.bots_pb2.OK
    session.version = '123'
    worker = session.worker
    wp = worker.properties.add()
    wp.key = 'pool'
    wp.value = 'swimming'
    dev = worker.devices.add()
    dev.handle = 'robocop'
    dp1 = dev.properties.add()
    dp1.key = 'mammal'
    dp1.value = 'ferrett'
    dp2 = dev.properties.add()
    dp2.key = 'mammal'
    dp2.value = 'wombat'

    # Create proto response, overriding the pool
    msg_rsp = remote_client_grpc.bots_pb2.BotSession()
    msg_rsp.CopyFrom(msg_req.bot_session)
    msg_rsp.worker.properties[0].value = 'dead'

    # Execute call and verify response
    expected_call = ('CreateBotSession', msg_req, msg_rsp)
    self._expected.append(expected_call)
    response = self._client.do_handshake(attrs)
    self.assertEqual(response, {
        'bot_version': u'123',
        'bot_group_cfg': {
            'dimensions': {
                u'pool': [u'dead'],
            },
        },
        'bot_group_cfg_version': 1,
    })

  def test_poll_accept_task(self):
    """Tests the bot accepts a task before returning the manifest."""
    attrs = {
        'version': '123',
        'dimensions': {
            'id': ['robocop'],
        },
        'state': {},
    }

    session = remote_client_grpc.bots_pb2.BotSession()
    session.bot_id = 'robocop'
    session.version = '123'
    session.name = 'projects/project_id/botsessions/bot_sessions'
    session.status = remote_client_grpc.bots_pb2.OK
    worker = session.worker
    dev = worker.devices.add()
    dev.handle = 'robocop'
    self._client._session = remote_client_grpc.bots_pb2.BotSession()

    # Case: UpdateBotSession returns no leases.
    self._client._session.CopyFrom(session)
    req = remote_client_grpc.bots_pb2.UpdateBotSessionRequest()
    req.name = session.name
    req.bot_session.CopyFrom(session)
    resp = remote_client_grpc.bots_pb2.BotSession()
    resp.CopyFrom(session)
    expected_call = ('UpdateBotSession', req, resp)
    # Expect the second UpdateBotSession is not called. Otherwise, assertEqual
    # in _handle_call should fail.
    self._expected = [expected_call, ('UpdateBotSession', None, None)]
    cmd, value = self._client.poll(attrs)
    # Expect it returns ('sleep', 1)
    self.assertEqual(cmd, 'sleep')
    self.assertEqual(value, 1)

    # Case: UpdateBotSession returns admin lease.
    # TODO(huangwe): Consider accepting admin lease as well.
    self._client._session.CopyFrom(session)
    req = remote_client_grpc.bots_pb2.UpdateBotSessionRequest()
    req.name = session.name
    req.bot_session.CopyFrom(session)
    resp = remote_client_grpc.bots_pb2.BotSession()
    resp.CopyFrom(session)
    lease = resp.leases.add()
    lease.state = remote_client_grpc.bots_pb2.PENDING
    lease.assignment = 'abc'
    admin_lease = remote_client_grpc.bots_pb2.AdminTemp()
    admin_lease.command = remote_client_grpc.bots_pb2.AdminTemp.BOT_UPDATE
    lease.inline_assignment.Pack(admin_lease)
    expected_call = ('UpdateBotSession', req, resp)
    # Expect the second UpdateBotSession is not called. Otherwise, assertEqual
    # in _handle_call should fail.
    self._expected = [expected_call, ('UpdateBotSession', None, None)]
    cmd, _ = self._client.poll(attrs)
    self.assertEqual(cmd, 'update')

    # Case: UpdateBotSession returns task lease.
    self._client._session.CopyFrom(session)
    req1 = remote_client_grpc.bots_pb2.UpdateBotSessionRequest()
    req1.name = session.name
    req1.bot_session.CopyFrom(session)
    resp1 = remote_client_grpc.bots_pb2.BotSession()
    resp1.CopyFrom(session)
    lease1 = resp1.leases.add()
    lease1.state = remote_client_grpc.bots_pb2.PENDING
    lease1.assignment = 'def'
    command = remote_client_grpc.command_pb2.CommandTask()
    f = command.inputs.files.add()
    f.hash = 'adsfafasf'
    f.size_bytes = 60
    task_lease = remote_client_grpc.tasks_pb2.Task()
    task_lease.description.Pack(command)
    lease1.inline_assignment.Pack(task_lease)

    req2 = remote_client_grpc.bots_pb2.UpdateBotSessionRequest()
    req2.name = session.name
    req2.bot_session.CopyFrom(session)
    lease2 = req2.bot_session.leases.add()
    lease2.CopyFrom(lease1)
    lease2.state = remote_client_grpc.bots_pb2.ACTIVE
    # Expect the second UpdateBotSession is called.
    self._expected = [('UpdateBotSession', req1, resp1),
                      ('UpdateBotSession', req2, '')]

    def _stdout_resource_name_from_ids(_self, _bot_id, _task_id):
      return ''
    self.mock(remote_client_grpc.RemoteClientGrpc,
              '_stdout_resource_name_from_ids', _stdout_resource_name_from_ids)
    cmd, _ = self._client.poll(attrs)
    self.assertEqual(cmd, 'run')

  def test_post_bot_event(self):
    """Tests post_bot_event function."""
    self._client._session = remote_client_grpc.bots_pb2.BotSession()
    self._client._session.status = remote_client_grpc.bots_pb2.OK

    message = 'some message'
    msg_req = remote_client_grpc.bots_pb2.PostBotEventTempRequest()
    msg_req.name = self._client._session.name
    msg_req.bot_session_temp.CopyFrom(self._client._session)
    msg_req.msg = message

    # Post an error message.
    msg_req.type = remote_client_grpc.bots_pb2.PostBotEventTempRequest.ERROR
    expected_call = ('PostBotEventTemp', msg_req, empty_pb2.Empty())
    self._expected.append(expected_call)
    self._client.post_bot_event('bot_error', message, {})
    self.assertEqual(self._client._session.status,
                     remote_client_grpc.bots_pb2.OK)

    # Post a rebooting message.
    msg_req.type = remote_client_grpc.bots_pb2.PostBotEventTempRequest.INFO
    msg_req.bot_session_temp.status = remote_client_grpc.bots_pb2.HOST_REBOOTING
    expected_call = ('PostBotEventTemp', msg_req, empty_pb2.Empty())
    self._expected.append(expected_call)
    self._client.post_bot_event('bot_rebooting', message, {})
    self.assertEqual(self._client._session.status,
                     remote_client_grpc.bots_pb2.HOST_REBOOTING)

    # Post a shutdown message.
    msg_req.type = remote_client_grpc.bots_pb2.PostBotEventTempRequest.INFO
    msg_req.bot_session_temp.status = \
        remote_client_grpc.bots_pb2.BOT_TERMINATING
    expected_call = ('PostBotEventTemp', msg_req, empty_pb2.Empty())
    self._expected.append(expected_call)
    self._client.post_bot_event('bot_shutdown', message, {})
    self.assertEqual(self._client._session.status,
                     remote_client_grpc.bots_pb2.BOT_TERMINATING)


if __name__ == '__main__':
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.TestCase.maxDiff = None
  unittest.main()
