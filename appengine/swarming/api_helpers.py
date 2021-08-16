# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

""" """


def process_task_request(tr, template_apply):
    # type: (task_request.TaskRequest) -> None

    task_request.init_new_request(tr, acl.can_schedule_high_priority_tasks(), template_apply)

    for task_slice in tr.task_slices:
        apply_server_property_defaults(task_slice.properties)


    try:
        # We need to call the ndb.Model pre-put check earlier because the
        # following checks assume that the request itself is valid and could crash
        # otherwise.
        tr.pre_put_hook()
    except (datastore_errors.BadValueError, TypeError, ValueError) as e:
        logging.warning('Incorrect new task request', exc_info=True)
        raise BadTaskRequestException


    # Retrieve pool_cfg, and check the existence.
    pool_cfg = pools_config.get_pool_config(tr.pool)
    if not pool_cfg:
        logging.warning('Pool "%s" is not in pools.cfg', tr.pool)
        # TODO(crbug.com/1086058): It currently returns 403 Forbidden, but
        # should return 400 BadRequest or 422 Unprocessable Entity, instead.
        raise auth.AuthorizationError(
            'Can\'t submit tasks to pool "%s", not defined in pools.cfg' % tr.pool)

    # TODO(crbug.com/1109378): Check ACLs before calling init_new_request to
    # avoid leaking information about pool templates to unauthorized callers.

    # If the task request supplied a realm it means the task is in a realm-aware
    # mode and it wants *all* realm ACLs to be enforced. Otherwise assume
    # the task runs in pool_cfg.default_task_realm and enforce only permissions
    # specified in enforced_realm_permissions pool config (using legacy ACLs
    # for the rest). This should simplify the transition to realm ACLs.
    # Enforce realm acls.
    enforce_realms_acl = False
    if tr.realm:
        logging.info('Using task realm %r', tr.realm)
        enforce_realms_acl = True
    elif pool_cfg.default_task_realm:
        logging.info('Using default_task_realm %r', pool_cfg.default_task_realm)
        tr.realm = pool_cfg.default_task_realm
    else:
        logging.info('Not using realms')

    # Warn if the pool has realms configured, but the task is using old ACLs.
    if pool_cfg.realm and not tr.realm:
      logging.warning(
          'crbug.com/1066839: %s: %r is not using realms',
          pool, tr.name)

    # Realm permission 'swarming.pools.createInRealm' checks if the
    # caller is allowed to create a task in the task realm.
    tr.realms_enabled = realms.check_tasks_create_in_realm(
        tr.realm, pool_cfg, enforce_realms_acl)

    # Realm permission 'swarming.pools.create' checks if the caller is allowed
    # to create a task in the pool.
    realms.check_pools_create_task(pool_cfg, enforce_realms_acl)


    # If the request has a service account email, check if the service account
    # is allowed to run.
    if service_accounts_utils.is_service_account(tr.service_account):
      if not service_accounts.has_token_server():
          raise BadTaskRequestException(
              'This Swarming server doesn\'t support task service accounts '
              'because Token Server URL is not configured')
      # Realm permission 'swarming.tasks.actAs' checks if the service account is
      # allowed to run in the task realm.
      realms.check_tasks_act_as(tr, pool_cfg, enforce_realms_acl)

      # If using legacy ACLs for service accounts, use the legacy mechanism to
      # mint oauth token as well. Note that this path will be deprecated after
      # migration to MintServiceAccountToken rpc which accepts realm.
      # It contacts the token server to generate "OAuth token grant" (or grab a
      # cached one). By doing this we check that the given service account usage
      # is allowed by the token server rules at the time the task is posted.
      # This check is also performed later (when running the task), when we get
      # the actual OAuth access token.
      if not tr.realms_enabled:
        max_lifetime_secs = tr.max_lifetime_secs
        duration = datetime.timedelta(seconds=max_lifetime_secs)
        tr.service_account_token = (
            service_accounts.get_oauth_token_grant(
                service_account=tr.service_account,
                validity_duration=duration))



class InvalidTaskRequestException(Exception):
    """The TaskRequest is invalid."""
    pass
