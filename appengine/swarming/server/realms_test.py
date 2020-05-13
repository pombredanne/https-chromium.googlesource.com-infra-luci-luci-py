#!/usr/bin/env vpython
# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import unittest

import mock
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
      (None,),
      ('test:pool',),
  ])
  def test_can_create_task_in_pool_legacy_compatible_allowed(self, pool_realm):
    self.mock(pools_config,
              'get_pool_config', lambda _: pools_pb2.Pool(realm=pool_realm))
    self.mock(realms, 'is_enforced_permission', lambda *_: False)
    self.mock(task_scheduler, 'check_schedule_request_acl', lambda _: None)
    has_permission_dryrun_mock = mock.Mock()
    self.mock(auth, 'has_permission_dryrun', has_permission_dryrun_mock)

    task_request_mock = mock.Mock(pool='test_pool')
    allowed = realms.can_create_task_in_pool(task_request_mock)
    self.assertTrue(allowed)

    if pool_realm:
      has_permission_dryrun_mock.assert_called_once_with(
          'swarming.pools.createTask', [u'test:pool'],
          True,
          tracking_bug='crbug.com/1066839')
    else:
      has_permission_dryrun_mock.assert_not_called()

  @parameterized.expand([
      (None,),
      ('test:pool',),
  ])
  def test_can_create_task_in_pool_legacy_compatible_not_allowed(
      self, pool_realm):
    self.mock(pools_config,
              'get_pool_config', lambda _: pools_pb2.Pool(realm=pool_realm))
    self.mock(realms, 'is_enforced_permission', lambda *_: False)

    def legacy_check_func(_):
      raise auth.AuthorizationError('Not allowed.')

    self.mock(task_scheduler, 'check_schedule_request_acl', legacy_check_func)
    has_permission_dryrun_mock = mock.Mock()
    self.mock(auth, 'has_permission_dryrun', has_permission_dryrun_mock)

    task_request_mock = mock.Mock(pool='test_pool')
    with self.assertRaises(auth.AuthorizationError):
      realms.can_create_task_in_pool(task_request_mock)

    if pool_realm:
      has_permission_dryrun_mock.assert_called_once_with(
          'swarming.pools.createTask', [u'test:pool'],
          False,
          tracking_bug='crbug.com/1066839')
    else:
      has_permission_dryrun_mock.assert_not_called()

  @parameterized.expand([
      (True,),
      (False,),
  ])
  def test_can_create_task_in_pool_enforced(self, expected):
    self.mock(pools_config,
              'get_pool_config', lambda _: pools_pb2.Pool(realm='test:pool'))
    self.mock(realms, 'is_enforced_permission', lambda *_: True)
    has_permission_mock = mock.Mock(return_value=expected)
    self.mock(auth, 'has_permission', has_permission_mock)

    task_request_mock = mock.Mock(pool='test_pool')
    allowed = realms.can_create_task_in_pool(task_request_mock)
    self.assertEqual(expected, allowed)
    has_permission_mock.assert_called_once_with('swarming.pools.createTask',
                                                [u'test:pool'])


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
