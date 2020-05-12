# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

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


def can_create_task_in_pool(task_request):
  pool = task_request.pool
  pool_cfg = pools_config.get_pool_config(pool)

  # 'swarming.pools.createTask'
  perm = get_permission_name(realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK)

  if is_enforced_permission(realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK,
                            pool_cfg):
    # check only Realm ACLs.
    return auth.has_permission(perm, [pools_cfg.realm])

  legacy_check_result = True
  try:
    task_scheduler.check_schedule_request_ack(task_request)
  except auth.AuthorizationError:
    legacy_check_result = False
    raise
  finally:
    if pool_cfg.realm:
      auth.has_permission_dryrun(
          perm, [pools_cfg.realm],
          legach_check_result,
          tracking_bug='crbug.com/1066839')
    else:
      logging.warning('crbug.com/1066839: missing pool realm. pool: %s', pool)

  return legacy_check_result
