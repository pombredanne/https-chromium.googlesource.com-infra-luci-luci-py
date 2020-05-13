#!/usr/bin/env vpython
# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import collections
import logging
import mock
import sys
import unittest

from parameterized import parameterized

import test_env
test_env.setup_test_env()

from components import auth
from components import utils
from test_support import test_case

from proto.config import config_pb2
from proto.config import pools_pb2
from proto.config import realms_pb2
from server import config
from server import pools_config
from server import realms
from server import task_scheduler


def get_mock(name, **kwargs):
  klass = collections.namedtuple(name, kwargs.keys())
  return klass(**kwargs)


class RealmsTest(test_case.TestCase):

  def setUp(self):
    super(RealmsTest, self).setUp()
    utils.clear_cache(config.settings)

  def tearDown(self):
    super(RealmsTest, self).tearDown()
    utils.clear_cache(config.settings)

  def test_get_permission_names(self):
    self.assertEqual(
        'swarming.pools.createTask',
        realms.get_permission_name(
            realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK))

  @parameterized.expand([
      # should return False if the permissiion is not configured in settings.cfg
      # and in pools.cfg.
      (
          False,
          config_pb2.SettingsCfg(),
          pools_pb2.Pool(),
      ),
      # should return True if the permission is enforced in the pool.
      (
          True,
          config_pb2.SettingsCfg(),
          pools_pb2.Pool(enforced_realm_permissions=[
              realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK
          ])
      ),
      # return True if the permission is enforced globally.
      (
          True,
          config_pb2.SettingsCfg(
              auth=config_pb2.AuthSettings(enforced_realm_permissions=[
                  realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK
          ])),
          pools_pb2.Pool()
      ),
  ])
  def test_is_enforced_permission(self, expected, settings_cfg, pool_cfg):
    self.mock(config, '_get_settings', lambda: (None, settings_cfg))
    self.assertEqual(expected, realms.is_enforced_permission(
        realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK, pool_cfg))

  @parameterized.expand([
      (True, None, False),
      (False, None, False),
      (True, 'test:pool', True),
      (False, 'test:pool', True),
  ])
  def test_can_create_task_in_pool_legacy_compatible(self, legacy_allowed,
                                                     pool_realm,
                                                     should_call_realm_check):
    task_request_mock = get_mock('TaskRequest', pool='test_pool')
    pool_cfg_mock = pools_pb2.Pool(realm=pool_realm)
    self.mock(pools_config, 'get_pool_config', lambda _: pool_cfg_mock)
    self.mock(realms, 'is_enforced_permission', lambda *_: False)

    # mock legacy check function
    if legacy_allowed:
      legacy_check_func = lambda _: None
    else:

      def legacy_check_func(_):
        raise auth.AuthorizationError('Not allowed.')

    self.mock(task_scheduler, 'check_schedule_request_acl', legacy_check_func)

    has_permission_dryrun_mock = mock.Mock()
    self.mock(auth, 'has_permission_dryrun', has_permission_dryrun_mock)

    if legacy_allowed:
      ret = realms.can_create_task_in_pool(task_request_mock)
      self.assertTrue(ret)
    else:
      with self.assertRaises(auth.AuthorizationError):
        realms.can_create_task_in_pool(task_request_mock)

    if should_call_realm_check:
      has_permission_dryrun_mock.assert_called_once_with(
          'swarming.pools.createTask',
          [u'test:pool'],
          legacy_allowed,
          tracking_bug='crbug.com/1066839'
      )
    else:
      has_permission_dryrun_mock.assert_not_called()

  @parameterized.expand([
      (True,),
      (False,),
  ])
  def test_can_create_task_in_pool_enforced(self, realm_allowed):
    task_request_mock = get_mock('TaskRequest', pool='test_pool')
    pool_cfg_mock = pools_pb2.Pool(realm='test:pool')
    self.mock(pools_config, 'get_pool_config', lambda _: pool_cfg_mock)
    self.mock(realms, 'is_enforced_permission', lambda _pool, _cfg: True)

    has_permission_mock = mock.Mock(return_value=realm_allowed)
    self.mock(auth, 'has_permission', has_permission_mock)

    self.assertEqual(realm_allowed,
                     realms.can_create_task_in_pool(task_request_mock))
    has_permission_mock.assert_called_once_with(
        'swarming.pools.createTask', [u'test:pool'])


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
