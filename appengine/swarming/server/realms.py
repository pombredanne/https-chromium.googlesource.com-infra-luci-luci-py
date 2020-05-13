# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging

from components import auth

from proto.config import realms_pb2
from server import config
from server import pools_config
from server import task_scheduler


def get_permission_name(enum_permission):
  """ Generates Realm permission name from enum value.

  e.g. realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK
       -> 'swarming.pools.createTask'

  Args:
    enum_permission: realms_pb2.RealmPermission enum value.

  Returns:
    realm_permission: Realm permission name 'swarming.<subject>.<verb>'
  """
  enum_name = realms_pb2.RealmPermission.Name(enum_permission)
  words = enum_name.replace('REALM_PERMISSION_', '').split('_')
  # convert first word to subject e.g. pools, tasks
  subject = words[0].lower()
  # convert following words to verb e.g. createTask, listBots
  verb = words[1].lower() + ''.join(map(lambda x: x.capitalize(), words[2:]))
  return 'swarming.%s.%s' % (subject, verb)


def is_enforced_permission(perm, pool_cfg=None):
  """ Checks if the Realm permission is enforced.

  Checks if the permission is specified in `enforced_realm_permissions`
  in settings.cfg or pools.cfg for the pool.

  Args:
    perm: realms_pb2.RealmPermission enum value.
    pool_cfg: PoolConfig of the pool

  Returns:
    bool: True if it's enforced, False if it's legacy-compatible.
  """
  if pool_cfg and perm in pool_cfg.enforced_realm_permissions:
    return True
  return perm in config.settings().auth.enforced_realm_permissions


def check_pools_create_task(task_request):
  """Checks if the caller can create the task in the pool.

  If the realm permission check is enforced,
    just call auth.has_permission()

  If it's legacy-compatible,
    call the legacy task_scheduler.check_schedule_request_acl() and compare
    the legacy result with the realm permission check using
    auth.has_permission_dryrun()
    Note that the legacy check function raises exception, which also will be
    re-raised from this function.

  Args:
    task_request: TaskRequest

  Returns:
    None

  Raises:
    auth.AuthorizationError
  """
  pool = task_request.pool
  pool_cfg = pools_config.get_pool_config(pool)

  if not pool_cfg:
    logging.warning('Pool "%s" is not in pools.cfg', pool)
    # Unknown pools are forbidden.
    raise auth.AuthorizationError('Pool "%s" not defined in pools.cfg' % pool)

  # check enforcement
  is_enforced = is_enforced_permission(
      realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK, pool_cfg)

  # check if realm is configured for the pool.
  if not pool_cfg.realm:
    err_msg = 'realm is missing in Pool "%s"' % pool
    if is_enforced:
      # realm is required in this path.
      raise auth.AuthorizationError(err_msg)
    else:
      logging.warning('crbug.com/1066839: %s', err_msg)

  # 'swarming.pools.createTask'
  perm = get_permission_name(realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK)

  if is_enforced:
    # check only Realm ACLs.
    if not auth.has_permission(perm, [pool_cfg.realm]):
      raise auth.AuthorizationError(
          'User "%s" is not allowed to schedule tasks in the pool "%s", '
          'see pools.cfg' % (auth.get_current_identity().to_bytes(), pool))
    return

  legacy_allowed = True
  try:
    task_scheduler.check_schedule_request_acl_caller(pool, pool_cfg)
  except auth.AuthorizationError:
    legacy_allowed = False
    raise  # re-raise the exception
  finally:
    if pool_cfg.realm:
      auth.has_permission_dryrun(
          perm, [pool_cfg.realm],
          legacy_allowed,
          tracking_bug='crbug.com/1066839')
