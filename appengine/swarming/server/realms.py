# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from collections import namedtuple
import datetime
import logging

from components import auth

from proto.config import realms_pb2
from server import acl
from server import bot_management
from server import config
from server import pools_config
from server import task_scheduler
from server import task_queues

_TRACKING_BUG = 'crbug.com/1066839'


# Properties of a task that affect who can access it.
#
# Extracted either from TaskRequest or from TaskResultSummary.
TaskAccessInfo = namedtuple(
    'TaskAccessInfo',
    [
        # ID of the task. Only for error messages and logs!
        'task_id',
        # The realm the task belongs to, as "<project>:<realm>" string.
        'realm',
        # Task's pool as a string.
        'pool',
        # The bot ID the task is targeting or None.
        'bot_id',
        # auth.Identity of whoever submitted the task.
        'submitter',
    ])


def get_permission(enum_permission):
  """Generates Realm permission instance from enum value.

  e.g. realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK
       -> 'swarming.pools.createTask'

  Args:
    enum_permission: realms_pb2.RealmPermission enum value.

  Returns:
    realm_permission: an instance of auth.Permission.
  """
  enum_name = realms_pb2.RealmPermission.Name(enum_permission)
  words = enum_name.replace('REALM_PERMISSION_', '').split('_')
  # convert first word to subject e.g. pools, tasks
  subject = words[0].lower()
  # convert following words to verb e.g. createTask, listBots
  verb = words[1].lower() + ''.join(map(lambda x: x.capitalize(), words[2:]))
  return auth.Permission('swarming.%s.%s' % (subject, verb))


def is_enforced_permission(perm, pool_cfg=None):
  """Checks if the Realm permission is enforced.

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


# Realm permission checks


def check_pools_create_task(pool_cfg, enforce):
  """Checks if the caller can create the task in the pool.

  Realm permission `swarming.pools.createTask` will be checked,
  using auth.has_permission() or auth.has_permission_dryrun().

  If the realm permission check is enforced,
    It just calls auth.has_permission()

  If it's legacy-compatible,
    It calls the legacy task_scheduler.check_schedule_request_acl_caller() and
    compare the legacy result with the realm permission check using the dryrun.

  Args:
    pool_cfg: PoolCfg of the pool.
    enforce: if True enforce realm ACLs regardless of is_enforced_permission.

  Returns:
    True if used realm ACLs, False if legacy ones.

  Raises:
    auth.AuthorizationError: if the caller is not allowed to schedule the task
                             in the pool.
  """
  # 'swarming.pools.createTask'
  perm_enum = realms_pb2.REALM_PERMISSION_POOLS_CREATE_TASK
  perm = get_permission(perm_enum)

  if enforce or is_enforced_permission(perm_enum, pool_cfg):
    _check_permission(perm, [pool_cfg.realm])
    return True

  # legacy-compatible path

  # pool_cfg.realm is optional.
  if not pool_cfg.realm:
    logging.warning('%s: realm is missing in Pool "%s"', _TRACKING_BUG,
                    pool_cfg.name)

  legacy_allowed = True
  try:
    task_scheduler.check_schedule_request_acl_caller(pool_cfg)
  except auth.AuthorizationError:
    legacy_allowed = False
    raise  # re-raise the exception
  finally:
    # compare the legacy check result with realm check result if the pool realm
    # is specified.
    if pool_cfg.realm:
      auth.has_permission_dryrun(
          perm, [pool_cfg.realm], legacy_allowed, tracking_bug=_TRACKING_BUG)
  return False


def check_tasks_create_in_realm(realm, pool_cfg, enforce):
  """Checks if the caller is allowed to create a task in the realm.

  Args:
    realm: Realm that a task will be created in or None for legacy tasks.
    pool_cfg: PoolConfig of the pool where the task will run.
    enforce: if True enforce realm ACLs regardless of is_enforced_permission.

  Returns:
    True if used realm ACLs, False if legacy ones.

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  # 'swarming.tasks.createInRealm'
  perm_enum = realms_pb2.REALM_PERMISSION_TASKS_CREATE_IN_REALM
  perm = get_permission(perm_enum)

  if enforce or is_enforced_permission(perm_enum, pool_cfg):
    _check_permission(perm, [realm])
    return True

  if realm:
    # There is no existing permission that corresponds to the realm
    # permission. So always pass expected_result=True to the dryrun.
    auth.has_permission_dryrun(
        perm, [realm], expected_result=True, tracking_bug=_TRACKING_BUG)
  return False


def check_tasks_act_as(task_request, pool_cfg, enforce):
  """Checks if the task service account is allowed to run in the task realm.

  Realm permission `swarming.tasks.actAs` will be checked,
  using auth.has_permission() or auth.has_permission_dryrun().

  If the realm permission check is enforced,
    It just calls auth.has_permission()

  If it's legacy-compatible,
    It calls task_scheduler.check_schedule_request_acl_service_account()
    and compare the legacy result with the realm permission check using
    the dryrun.

  Args:
    task_request: TaskRequest entity to be scheduled.
    pool_cfg: PoolConfig of the pool where the task will run.
    enforce: if True enforce realm ACLs regardless of is_enforced_permission.

  Returns:
    True if used realm ACLs, False if legacy ones.

  Raises:
    auth.AuthorizationError: if the service account is not allowed to run
                             in the task realm.
  """
  perm_enum = realms_pb2.REALM_PERMISSION_TASKS_ACT_AS
  perm = get_permission(perm_enum)
  identity = auth.Identity(auth.IDENTITY_USER, task_request.service_account)

  if enforce or is_enforced_permission(perm_enum, pool_cfg):
    _check_permission(perm, [task_request.realm], identity)
    return True

  # legacy-compatible path

  legacy_allowed = True

  try:
    # ACL check
    task_scheduler.check_schedule_request_acl_service_account(task_request)
  except auth.AuthorizationError:
    legacy_allowed = False
    raise  # re-raise the exception
  finally:
    if task_request.realm:
      auth.has_permission_dryrun(
          perm, [task_request.realm],
          legacy_allowed,
          identity=identity,
          tracking_bug=_TRACKING_BUG)
  return False


# Handler permission checks


def check_bot_get_acl(bot_id):
  """Checks if the caller is allowed to get the bot.

  Checks if the caller has global permission using acl.can_view_bot().

  If the caller doesn't have any global permissions,
    It checks realm permission 'swarming.pools.listBots'.
    The caller is required to have the permission in *any* pools.

  Args:
    bot_id: ID of the bot.

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  if acl.can_view_bot():
    return
  _check_bot_acl(realms_pb2.REALM_PERMISSION_POOLS_LIST_BOTS, bot_id)


def check_bot_tasks_acl(bot_id):
  """Checks if the caller is allowed to get the tasks assigned to the bot.

  Checks if the caller has global permission using acl.can_view_all_tasks().

  If the caller doesn't have any global permissions,
    It checks realm permission 'swarming.pools.listTasks'.
    The caller is required to have the permission in *any* pools.

  Args:
    bot_id: ID of the bot.

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  if acl.can_view_all_tasks():
    return
  _check_bot_acl(realms_pb2.REALM_PERMISSION_POOLS_LIST_TASKS, bot_id)


def check_bot_terminate_acl(bot_id):
  """Checks if the caller is allowed to terminate the bot.

  Checks if the caller has global permission using acl.can_edit_bot().

  If the caller doesn't have any global permissions,
    It checks realm permission 'swarming.pools.terminateBot'.
    The caller is required to have the permissions in *any* pools.

  Args:
    bot_id: ID of the bot.

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  if acl.can_edit_bot():
    return
  _check_bot_acl(realms_pb2.REALM_PERMISSION_POOLS_TERMINATE_BOT, bot_id)


def check_bot_delete_acl(bot_id):
  """Checks if the caller is allowed to delete the bot.

  Checks if the caller has global permission using acl.can_delete_bot().

  If the caller doesn't have any global permissions,
    It checks realm permission 'swarming.pools.deleteBot'.
    The caller is required to have the permissions in *any* pools.

  Args:
    bot_id: ID of the bot.

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  if acl.can_delete_bot():
    return
  _check_bot_acl(realms_pb2.REALM_PERMISSION_POOLS_DELETE_BOT, bot_id)


def can_terminate_bot(bot_id):
  """Checks if the caller is allowed to terminate the bot.

  Args:
    bot_id: ID of the bot.

  Returns:
    allowed: True if allowed, False otherwise.
  """
  if not bot_id:
    return acl.can_edit_bot()

  try:
    check_bot_terminate_acl(bot_id)
    return True
  except auth.AuthorizationError:
    return False


def can_delete_bot(bot_id):
  """Checks if the caller is allowed to delete the bot.

  Args:
    bot_id: ID of the bot.

  Returns:
    allowed: True if allowed, False otherwise.
  """
  if not bot_id:
    return acl.can_delete_bot()

  try:
    check_bot_delete_acl(bot_id)
    return True
  except auth.AuthorizationError:
    return False


def can_delete_bots(pools):
  """Checks if the caller is allowed to delete bots in the pools.

  Args:
    pools: List of pools.

  Returns:
    allowed: True if allowed, False otherwise.
  """
  if not pools:
    return acl.can_delete_bot()

  try:
    _check_pools_filters_acl(realms_pb2.REALM_PERMISSION_POOLS_DELETE_BOT,
                             pools)
    return True
  except auth.AuthorizationError:
    return False


def check_bots_list_acl(pools):
  """Checks if the caller is allowed to list or count bots.

  Checks if the caller has global permission using acl.can_view_bot().

  If the caller doesn't have any global permissions,
    It checks realm permission 'swarming.pools.listBots'.
    The caller is required to specify a pool dimension, and have the permission
    in *all* pools.

  Args:
    pools: List of pools for filtering.

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  if acl.can_view_bot():
    return
  _check_pools_filters_acl(realms_pb2.REALM_PERMISSION_POOLS_LIST_BOTS, pools)


def can_list_bots(pool):
  """Checks if the caller is allowed to list tasks of the pool.

  Args:
    pool: Pool name

  Returns:
    allowed: True if allowed, False otherwise.
  """
  if acl.can_view_bot():
    return True
  pool_cfg = pools_config.get_pool_config(pool)
  if not pool_cfg:
    logging.warning('Pool "%s" not found', pool)
    return False

  try:
    _check_permission(
        get_permission(realms_pb2.REALM_PERMISSION_POOLS_LIST_BOTS),
        [pool_cfg.realm])
    return True
  except auth.AuthorizationError:
    return False


def task_access_info_from_request(task_request):
  """Extracts information for task ACL check from TaskRequest."""
  return TaskAccessInfo(task_id=task_request.task_id,
                        realm=task_request.realm,
                        pool=task_request.pool,
                        bot_id=task_request.bot_id,
                        submitter=task_request.authenticated)


def check_task_get_acl(access_info):
  """Checks if the caller is allowed to get the task entities.

  Checks if the caller has global permission using acl.can_view_all_tasks().

  If the caller doesn't have any global permissions, checks if the caller has
  'swarming.tasks.get' in the task realm or 'swarming.pools.listTasks' in a
  realm associated with either the task pool or the bot pool the task was
  assigned to.

  Args:
    access_info: An instance of TaskAccessInfo extracted from TaskRequest or
        TaskResultSummary via task_access_info_from_*(...).

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  assert isinstance(access_info, TaskAccessInfo)
  if auth.get_current_identity() == access_info.submitter:
    return
  if acl.can_view_all_tasks():
    return
  _check_task_acl(access_info, realms_pb2.REALM_PERMISSION_TASKS_GET,
                  realms_pb2.REALM_PERMISSION_POOLS_LIST_TASKS)


def check_task_cancel_acl(access_info):
  """Checks if the caller is allowed to cancel the task.

  Checks if the caller has global permission using acl.can_edit_one_task().

  If the caller doesn't have any global permissions, checks if the caller has
  'swarming.tasks.cancel' in the task realm or 'swarming.pools.cancelTask' in
  a realm associated with either the task pool or the bot pool the task was
  assigned to.

  Args:
    access_info: An instance of TaskAccessInfo extracted from TaskRequest or
        TaskResultSummary via task_access_info_from_*(...).

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  assert isinstance(access_info, TaskAccessInfo)
  if auth.get_current_identity() == access_info.submitter:
    return
  if acl.can_edit_one_task():
    return
  _check_task_acl(access_info, realms_pb2.REALM_PERMISSION_TASKS_CANCEL,
                  realms_pb2.REALM_PERMISSION_POOLS_CANCEL_TASK)


def can_cancel_task(access_info):
  """Checks if the caller is allowed to cancel the task.

  Args:
    access_info: An instance of TaskAccessInfo extracted from TaskRequest or
        TaskResultSummary via task_access_info_from_*(...).

  Returns:
    allowed: True if allowed, False otherwise.
  """
  try:
    check_task_cancel_acl(access_info)
    return True
  except auth.AuthorizationError:
    return False


def check_tasks_list_acl(pools):
  """Checks if the caller is allowed to list or count tasks.

  Checks if the caller has global permission using acl.can_view_all_tasks().

  If the caller doesn't have any global permissions,
    It checks realm permission 'swarming.pools.listTasks'.
    The caller is required to specify pools, and have the permission
    in *all* pools.

  Args:
    pools: List of pools for filtering.

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  if acl.can_view_all_tasks():
    return
  _check_pools_filters_acl(realms_pb2.REALM_PERMISSION_POOLS_LIST_TASKS, pools)


def can_list_tasks(pool):
  """Checks if the caller is allowed to list tasks of the pool.

  Args:
    pool: Pool name

  Returns:
    allowed: True if allowed, False otherwise.
  """
  if acl.can_view_all_tasks():
    return True

  pool_cfg = pools_config.get_pool_config(pool)
  if not pool_cfg:
    logging.warning('Pool "%s" not found', pool)
    return False

  try:
    _check_permission(
        get_permission(realms_pb2.REALM_PERMISSION_POOLS_LIST_TASKS),
        [pool_cfg.realm])
    return True
  except auth.AuthorizationError:
    return False


def check_tasks_cancel_acl(pools):
  """Checks if the caller is allowed to cancel tasks.

  Checks if the caller has global permission using acl.can_edit_all_tasks().

  If the caller doesn't have any global permissions,
    It checks realm permission 'swarming.pools.cancelTask'.
    The caller is required to specify pools, and have *all* permissions of
    the pools.

  Args:
    pools: List of pools for filtering.

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  if acl.can_edit_all_tasks():
    return
  _check_pools_filters_acl(realms_pb2.REALM_PERMISSION_POOLS_CANCEL_TASK, pools)


def can_cancel_tasks(pools):
  """Checks if the caller is allowed to cancel tasks.

  Args:
    pools: List of pools for filtering.

  Returns:
    allowed: True if allowed, False otherwise.
  """
  try:
    check_tasks_cancel_acl(pools)
    return True
  except auth.AuthorizationError:
    return False


# Private section


def _check_permission(perm, realms, identity=None):
  """Checks if the caller has the realm permission.

  Args:
    perm: An instance of auth.Permission.
    realms: List of realms.
    identity: An instance of auth.Identity to check permission.
              default is auth.get_current_identity().

  Returns:
    None

  Raises:
    auth.AuthorizationError: if the caller is not allowed or realm is missing.
  """

  # Remove None from list
  realms = [r for r in realms if r]

  if not identity:
    identity = auth.get_current_identity()

  if not realms:
    raise auth.AuthorizationError('Realm is missing')

  if not auth.has_permission(perm, realms, identity=identity):
    logging.warning(
        '[realms] %s "%s" does not have permission "%s" in any realms %s',
        identity.kind, identity.name, perm.name, realms)
    raise auth.AuthorizationError('%s "%s" does not have permission "%s"' %
                                  (identity.kind, identity.name, perm.name))
  logging.info('[realms] %s "%s" has permission "%s" in any realms %s',
               identity.kind, identity.name, perm.name, realms)


def _bot_pool_realms(bot_id):
  """Returns realms of all pools the bot belongs to.

  Returns:
    A list of realms. It is empty if the bot doesn't exist or has no pools
    associated with it.
  """
  realms = []
  for p in bot_management.get_bot_pools(bot_id):
    pool_cfg = pools_config.get_pool_config(p)
    if not pool_cfg:
      logging.warning('Bot pool is missing. pool: %s, bot: %s', p, bot_id)
    elif not pool_cfg.realm:
      logging.warning('Bot pool has no realm. pool: %s, bot: %s', p, bot_id)
    else:
      realms.append(pool_cfg.realm)
  return realms


def _check_pools_filters_acl(perm_enum, pools):
  """Checks if the caller has the permission in the specified pools.

  The caller needs to have the permission in *all* pools.

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  # Pool dimension is required if the caller doesn't have global permission.
  if not pools:
    raise auth.AuthorizationError('No pool is specified')

  perm = get_permission(perm_enum)

  # the caller needs to have all permissions of the pools.
  for p in pools:
    pool_cfg = pools_config.get_pool_config(p)
    if not pool_cfg:
      raise auth.AuthorizationError(
          'No such pool or no permission to use it: %s' % p)

    _check_permission(perm, [pool_cfg.realm])


def _check_bot_acl(perm_enum, bot_id):
  """Checks if the caller is allowed to access the resource associated with
  the bot.

  The caller needs to have the permission in *any* pools the bot belong to.

  Raises:
    auth.AuthorizationError: if the caller is not allowed.
  """
  bot_realms = _bot_pool_realms(bot_id)
  if not bot_realms:
    raise auth.AuthorizationError(
        'No such bot or no permission to use it: %s.' % bot_id)
  _check_permission(get_permission(perm_enum), bot_realms)


def _check_task_acl(access_info, task_perm_enum, pool_perm_enum):
  """Checks if the caller has `task_perm_enum` permission in the task realm or
  `pool_perm_enum` permission in a realm associated with either the task pool
  or a bot pool of the bot the task was assigned to.

  The idea is that the caller can either "own" the task or "own" the bot pool it
  was scheduled to run on. If the caller "owns" the task, they will get access
  through  `task_perm_enum` in the tasks realm. If the caller "owns" the pool,
  they will get access through `pool_perm_enum` in the pool realm.

  Args:
    access_info: An instance of TaskAccessInfo.
    task_perm_enum: realms_pb2.RealmPermission enum value.
    pool_perm_enum: realms_pb2.RealmPermission enum value.

  Raises:
    auth.AuthorizationError if the call is not allowed.
  """
  task_perm = get_permission(task_perm_enum)
  pool_perm = get_permission(pool_perm_enum)

  # First check the task realm permission, it is the fastest check.
  task_realm = access_info.realm
  if task_realm and auth.has_permission(task_perm, [task_realm]):
    return

  # Next check the pool permission of the pool the task was scheduled in. This
  # is also relatively fast, since it hits the local config cache.
  if access_info.pool:
    pool_cfg = pools_config.get_pool_config(access_info.pool)
    if not pool_cfg:
      logging.warning('Task pool is missing. pool: %s', access_info.pool)
    elif not pool_cfg.realm:
      logging.warning('Task pool has no realm. pool: %s', access_info.pool)
    elif auth.has_permission(pool_perm, [pool_cfg.realm]):
      return

  # Finally check the pool permission of all the pools (usually one) in bot
  # dimensions. This is slow, since we need to fetch bot dimensions from the
  # datastore. For that reason we do it last.
  if access_info.bot_id:
    bot_realms = _bot_pool_realms(access_info.bot_id)
    if bot_realms and auth.has_permission(pool_perm, bot_realms):
      return

  raise auth.AuthorizationError('Task "%s" is not accessible' %
                                access_info.task_id)
