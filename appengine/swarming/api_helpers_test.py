#!/usr/bin/env vpython
# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
import datetime
import os
import logging
import sys
import unittest

import swarming_test_env
swarming_test_env.setup_test_env()
import test_env_handlers

import webapp2
import webtest

from google.appengine.api import memcache
from google.appengine.ext import ndb

import api_helpers
from components import auth
from components import auth_testing
from components import utils
import handlers_exceptions
from proto.config import config_pb2
from server import acl
from server import config
from server import pools_config
from server import realms
from server import service_accounts
from server import task_request
from server import task_result
from server import task_queues
from test_support import test_case
import handlers_bot


class TestProcessTaskRequest(test_case.TestCase):

  def setUp(self):
    super(TestProcessTaskRequest, self).setUp()
    now = datetime.datetime(2019, 01, 02, 03)
    test_case.mock_now(self, now, 0)

    self._known_pools = None

  def basic_task_request(self):
    return task_request.TaskRequest(
        name='ChickenTask',
        realm='farm:chicken',
        created_ts=utils.utcnow(),
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=task_request.TaskProperties(
                    command=['print', 'chicken'],
                    execution_timeout_secs=120,
                    dimensions_data={
                        u'chicken': [u'egg1', u'egg2'],
                        u'pool': [u'default']
                    }))
        ])

  def test_process_task_request_BadRequest(self):
    tr = task_request.TaskRequest(
        created_ts=utils.utcnow(),
        task_slices=[
            task_request.TaskSlice(
                properties=task_request.TaskProperties(
                    dimensions_data={u'chicken': [u'egg1', u'egg2']}))
        ])

    # Catch init_new_request() ValueError exceptions.
    with self.assertRaisesRegexp(handlers_exceptions.BadRequestException,
                                 'missing expiration_secs'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)
    tr.task_slices[0].expiration_secs = 60

    # Catch datastore.BadValueErrors.
    with self.assertRaisesRegexp(handlers_exceptions.BadRequestException,
                                 'name is missing'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)
    tr = self.basic_task_request()

    # Catch no such pool.
    with self.assertRaisesRegexp(handlers_exceptions.PermissionException,
                                 'No such pool'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)

    # Catch inconsistent enabling of realms and resultDB.
    self.mock(realms, 'check_tasks_create_in_realm', lambda *_: False)
    self.mock_pool_config('default')
    tr.resultdb = task_request.ResultDBCfg(enable=True)
    with self.assertRaisesRegexp(handlers_exceptions.BadRequestException,
                                 'ResultDB is enabled, but realm is not'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)

  def test_process_task_request(self):
    self.mock_pool_config('default')
    tr = self.basic_task_request()

    expected_tr = self.basic_task_request()
    task_request.init_new_request(expected_tr,
                                  acl.can_schedule_high_priority_tasks(),
                                  task_request.TEMPLATE_AUTO)
    expected_tr.realms_enabled = True

    self.mock(realms, 'check_tasks_create_in_realm', lambda *_: True)
    self.mock(realms, 'check_pools_create_task', lambda *_: True)

    api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)
    self.assertEqual(expected_tr, tr)

  def test_process_task_request_service_account(self):
    self.mock_pool_config('default')

    tr = self.basic_task_request()
    tr.service_account = 'service-account@example.com'

    expected_tr = self.basic_task_request()
    expected_tr.service_account = 'service-account@example.com'
    task_request.init_new_request(expected_tr,
                                  acl.can_schedule_high_priority_tasks(),
                                  task_request.TEMPLATE_AUTO)
    expected_tr.realms_enabled = True

    self.mock(realms, 'check_tasks_create_in_realm', lambda *_: True)
    self.mock(realms, 'check_pools_create_task', lambda *_: True)
    self.mock(realms, 'check_tasks_act_as', lambda *_: True)
    self.mock(service_accounts, 'has_token_server', lambda: True)

    api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)

    self.assertEqual(expected_tr, tr)

  def test_process_task_request_service_account_legacy(self):
    self.mock_pool_config('default')

    tr = self.basic_task_request()
    tr.service_account = 'service-account@example.com'

    expected_tr = self.basic_task_request()
    expected_tr.service_account = 'service-account@example.com'
    task_request.init_new_request(expected_tr,
                                  acl.can_schedule_high_priority_tasks(),
                                  task_request.TEMPLATE_AUTO)
    expected_tr.realms_enabled = False
    expected_tr.service_account_token = 'tok'

    self.mock(realms, 'check_tasks_create_in_realm', lambda *_: False)
    self.mock(realms, 'check_pools_create_task', lambda *_: True)
    self.mock(realms, 'check_tasks_act_as', lambda *_: True)
    self.mock(service_accounts, 'has_token_server', lambda: True)
    self.mock(service_accounts, 'get_oauth_token_grant', lambda **_: 'tok')

    api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)

    self.assertEqual(expected_tr, tr)

  def mock_pool_config(self, name):

    def mocked_get_pool_config(pool):
      if pool == name:
        return pools_config.init_pool_config(
            name=name,
            rev='rev',
        )
      return None

    self.mock(pools_config, 'get_pool_config', mocked_get_pool_config)


class TestFetchTasks(test_env_handlers.AppTestBase):

  def setUp(self):
    super(TestFetchTasks, self).setUp()
    self.app = webtest.TestApp(
        webapp2.WSGIApplication(handlers_bot.get_routes(), debug=True),
        extra_environ={
            'REMOTE_ADDR': self.source_ip,
            'SERVER_SOFTWARE': os.environ['SERVER_SOFTWARE'],
        },
    )
    now = datetime.datetime(2019, 01, 02, 03)
    test_case.mock_now(self, now, 0)

  def _mock_enqueue_task_async(self, allowed_queues):

    def mocked_enqueue_task_async(url, queue_name, payload):
      if queue_name not in allowed_queues:
        self.fail(url)
      if queue_name == 'rebuild-task-cache':
        return task_queues.rebuild_task_cache_async(payload)
      self.fail(url)

    self.mock(utils, 'enqueue_task_async', mocked_enqueue_task_async)

  def _mock_enqueue_task(self, allowed_queues):

    def mocked_enqueue_task(url, queue_name, **kwargs):
      del kwargs
      if queue_name in allowed_queues:
        return True
      self.fail(url)

    self.mock(utils, 'enqueue_task', mocked_enqueue_task)

  def test_fetch_tasks(self):
    self._mock_enqueue_task_async(['rebuild-task-cache'])
    self.mock_default_pool_acl([])

    # Create two tasks, one COMPLETED, one PENDING
    self.set_as_bot()
    params = self.do_handshake()
    self.bot_poll(params=params)
    self.set_as_user()

    # first request
    _, first_id = self.client_create_task_raw(
        name='first',
        tags=['project:yay', 'commit:post'],
        properties=dict(idempotent=True))
    self.set_as_bot()
    self._mock_enqueue_task(['cancel-children-tasks'])
    self.bot_run_task()

    # Clear cache to test fetching from datastore path.
    ndb.get_context().clear_cache()
    memcache.flush_all()

    # second request
    self.set_as_user()
    _, second_id = self.client_create_task_raw(
        name='second',
        user='jack@localhost',
        tags=['project:yay', 'commit:pre'])

    results = api_helpers.fetch_tasks([first_id, second_id, '1d69b9f088008810'])

    self.assertEqual(results[0].state, task_result.State.COMPLETED)
    self.assertEqual(results[0].task_id, first_id)
    self.assertEqual(results[1].state, task_result.State.PENDING)
    self.assertEqual(results[1].task_id, second_id)
    self.assertIsNone(results[2])


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
