#!/usr/bin/env vpython
# Copyright 2016 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import unittest
import datetime

import swarming_test_env
swarming_test_env.setup_test_env()

import api_helpers
from components import auth
from components import auth_testing
from components import utils
from server import config
from server import pools_config
from server import service_accounts
from server import realms
from test_support import test_case

from proto.config import config_pb2

from server import acl
from server import task_request


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

  def test_process_task_request_BadTaskRequest(self):
    tr = task_request.TaskRequest(
        created_ts=utils.utcnow(),
        task_slices=[
            task_request.TaskSlice(
                properties=task_request.TaskProperties(
                    dimensions_data={u'chicken': [u'egg1', u'egg2']}))
        ])

    # Catch init_new_request() exceptions.
    with self.assertRaisesRegexp(api_helpers.BadTaskRequestException,
                                 'missing expiration_secs'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)
    tr.task_slices[0].expiration_secs = 60

    # Catch get_pool_config() exceptions.
    with self.assertRaisesRegexp(api_helpers.BadTaskRequestException,
                                 'get_pool_config called with None'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)
    tr.task_slices[0].properties.dimensions_data.update({u'pool': [u'pool-a']})

    # Catch no such pool.
    with self.assertRaisesRegexp(api_helpers.BadTaskRequestException,
                                 'Pool "pool-a" not found.'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)
    tr.task_slices[0].properties.dimensions_data.update({u'pool': [u'default']})
    mock_pool_config(self, 'default')

    # Catch _pre_put_hook errors.
    with self.assertRaisesRegexp(api_helpers.BadTaskRequestException,
                                 'name is missing'):
      api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)

  def test_process_task_request(self):
    mock_pool_config(self, 'default')
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
    mock_pool_config(self, 'default')

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
    mock_pool_config(self, 'default')

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


def mock_pool_config(test,
                     name,
                     scheduling_users=None,
                     scheduling_groups=None,
                     trusted_delegatees=None,
                     service_accounts=None,
                     service_accounts_groups=None,
                     external_schedulers=None):

  def mocked_get_pool_config(pool):
    if pool == name:
      return pools_config.init_pool_config(
          name=name,
          rev='rev',
          scheduling_users=frozenset(scheduling_users or []),
          scheduling_groups=frozenset(scheduling_groups or []),
          trusted_delegatees={
              peer: pools_config.TrustedDelegatee(peer, frozenset(tags))
              for peer, tags in (trusted_delegatees or {}).items()
          },
          service_accounts=frozenset(service_accounts or []),
          service_accounts_groups=tuple(service_accounts_groups or []),
          external_schedulers=external_schedulers,
      )
    return None

  test.mock(pools_config, 'get_pool_config', mocked_get_pool_config)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
