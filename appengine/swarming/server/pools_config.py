# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Functions to fetch and parse pools.cfg file with list of pools.

See comments in proto/pools.proto for more context. Structures defined here are
used primarily by task_scheduler.check_schedule_request_acl.
"""

import collections
import random

from components import auth
from components import config
from components import utils
from components.config import validation

from proto import pools_pb2
from server import config as local_config
from server import service_accounts
from server import task_request

import swarming_rpcs


POOLS_CFG_FILENAME = 'pools.cfg'


# Validated read-only representation of one pool.
_PoolConfig = collections.namedtuple('_PoolConfig', [
  # Name of the pool.
  'name',
  # Revision of pools.cfg file this config came from.
  'rev',
  # Set of auth.Identity that can schedule jobs in the pool.
  'scheduling_users',
  # Set of group names with users that can schedule jobs in the pool.
  'scheduling_groups',
  # Map {auth.Identity of a delegatee => TrustedDelegatee tuple}.
  'trusted_delegatees',
  # Set of service account emails allowed in this pool, specified explicitly.
  'service_accounts',
  # Additional list of groups with allowed service accounts.
  'service_accounts_groups',
  # resolved TaskTemplateDeployment (optional).
  'task_template_deployment',
])

class PoolConfig(_PoolConfig):
  def apply_task_template(self, request, pool_task_template):
    """Applies any TaskTemplateDeployment to the indicated request.

    Modifies `request` in-place.

    Args:
      request (task_request.TaskProperties) - The task request to modify.
      pool_task_template (swarming_rpcs.PoolTaskTemplate) - The PoolTaskTemplate
        enum controlling application of the deployment.
    """
    assert isinstance(request, task_request.TaskRequest)
    assert isinstance(pool_task_template, swarming_rpcs.PoolTaskTemplate)

    deployment = self.task_template_deployment
    if deployment:
      deployment.apply_to_task_request(request, pool_task_template, self.rev)


# Validated read-only fields of one trusted delegation scenario.
TrustedDelegatee = collections.namedtuple('TrustedDelegatee', [
  # auth.Identity of the delegatee (the one who's minting the delegation token).
  'peer_id',
  # A set of tags to look for in the delegation token to allow the delegation.
  'required_delegation_tags',
])


# Describes how task templates apply to a pool.
_TaskTemplateDeployment = collections.namedtuple('_TaskTemplateDeployment', [
  # The TaskTemplate for prod builds (optional).
  'prod',
  # The TaskTemplate for canary builds (optional).
  'canary',
  # The chance (int [0, 9999]) of the time that the canary template should
  # be selected. Required if canary is not None. If we parse a 0 from the
  # pools.cfg, then both this and 'canary' are set to None.
  'canary_chance',
])

class TaskTemplateDeployment(_TaskTemplateDeployment):
  @classmethod
  def from_pb(cls, ctx, d, template_map):
    if not (0 <= d.canary_chance <= 9999):
      ctx.error('canary_chance out of range `[0,9999]`: %d -> %%%.2f',
                d.canary_chance, d.canary_chance/100.)
      raise InvalidTaskTemplateError()

    canary = None
    if d.HasField('canary'):
      canary = TaskTemplate.from_pb(ctx, d.canary, template_map)
    if d.canary_chance and not canary:
      ctx.error('canary_chance specified without a canary')
      raise InvalidTaskTemplateError()

    return cls(
      prod=TaskTemplate.from_pb(ctx, d.prod, template_map),
      canary=canary,
      canary_chance=d.canary_chance,
    )

  def apply_to_task_request(self, request, pool_task_template, rev):
    """Applies this deployment to the indicated request.

    Modifies `request` in-place.

    Args:
      request (task_request.TaskProperties) - The task request to modify.
      pool_task_template (swarming_rpcs.PoolTaskTemplate) - The PoolTaskTemplate
        enum controlling application of the deployment.
      rev (str) - The revision of the pools.cfg configuration we're from.
    """
    assert isinstance(request, task_request.TaskRequest)
    assert isinstance(pool_task_template, swarming_rpcs.PoolTaskTemplate)

    if pool_task_template == swarming_rpcs.PoolTaskTemplate.SKIP:
      return

    to_apply = None
    canary = False
    if pool_task_template == swarming_rpcs.PoolTaskTemplate.CANARY_NEVER:
      to_apply = self.prod
    elif pool_task_template == swarming_rpcs.PoolTaskTemplate.CANARY_PREFER:
      if self.canary:
        canary = True
        to_apply = self.canary
      else:
        to_apply = self.prod
    elif pool_task_template == swarming_rpcs.PoolTaskTemplate.AUTO:
      if self.canary_chance == 0:
        to_apply = self.prod
      else:
        canary = random.randint(0, 9999) < self.canary_chance
        to_apply = self.canary if canary else self.prod

    # This should never happen... but just in case.
    assert to_apply is not None, (
      'TaskTemplateDeployment got None template to apply to task')

    to_apply.apply_to_task_properties(request.properties)

    request.tags.append('swarming.pool.version:%s' % (rev,))
    request.tags.append('swarming.pool.template.canary:%d' % (canary,))


# A set of default task parameters to apply to tasks issued within a pool.
_TaskTemplate = collections.namedtuple('_TaskTemplate', [
  # sequence of CacheEntry.
  'cache',
  # sequence of CipdPackage.
  'cipd_package',
  # sequence of Env.
  'env',

  # An internal frozenset<str> of the transitive inclusions that went into
  # the creation of this _TaskTemplate. Users outside of this file should ignore
  # this field.
  'inclusions',
])


class InvalidTaskTemplateError(Exception):
  pass


class TaskTemplateApplicationError(Exception):
  def __init__(self, message):
    self.conflict = message
    super(TaskTemplateApplicationError, self).__init__(
      'Task defines %s which conflicts with pool task template' %
      message)


class TaskTemplate(_TaskTemplate):
  class _Intermediate(object):
    """_Intermediate represents an in-flux TaskTemplate instance, and is used
    internally by the .from_pb method to build up a finalized TaskTemplate
    instance."""
    def __init__(self, cache=None, cipd_package=None, env=None):
      self.cache = cache or {}                # name -> path
      self.cipd_package = cipd_package or {}  # (path, name) -> version
      self.env = env or {}                    # var -> (value, prefix, soft)
      self.inclusions = set()                # Set of included stuff

    def update(self, ctx, other, include_name=None):
      assert isinstance(other, TaskTemplate)

      if include_name:
        if include_name in self.inclusions:
          ctx.error('template %r included multiple times',
                    include_name.encode('utf-8'))
          raise InvalidTaskTemplateError()
        self.inclusions.add(include_name)

      for transitive_include in other.inclusions:
        if transitive_include in self.inclusions:
          ctx.error('template %r included (transitively) multiple times',
                    transitive_include.encode('utf-8'))
          raise InvalidTaskTemplateError()
        self.inclusions.add(transitive_include)

      for entry in other.cache:
        self.cache[entry.name] = entry.path

      for entry in other.cipd_package:
        self.cipd_package[(entry.path, entry.pkg)] = entry.version

      for entry in other.env:
        val, pfx, _soft = (
          self.env[entry.var] if entry.var in self.env else ('', (), False))
        self.env[entry.var] = (
          entry.value or val,
          (pfx + entry.prefix),
          entry.soft)

    def finalize(self, ctx):
      fail = [False]

      def e(*args):
        ctx.error(*args)
        fail[0] = True

      # no empty values
      for i, (name, path) in enumerate(self.cache.iteritems()):
        ident = repr(name.encode('utf-8')) if name else '#%d' % i
        with ctx.prefix('cache[%s]: ', ident):
          if not name:
            e('empty name')
          if not path:
            e('empty path')

      for i, ((path, pkg), vers) in enumerate(self.cipd_package.iteritems()):
        ident = (repr((path.encode('utf-8'), pkg.encode('utf-8')))
                 if path and pkg else '#%d' % i)
        with ctx.prefix('cipd_package[%s]: ', ident):
          if not pkg:
            e('empty pkg')
          if not vers:
            e('empty version')

      for i, (var, (value, prefix, _soft)) in enumerate(self.env.iteritems()):
        ident = repr(var.encode('utf-8')) if var else '#%d' % i
        with ctx.prefix('env[%s]: ', ident):
          if not var:
            e('empty var')
          if not value and not prefix:
            e('empty value AND prefix')

      # paths don't overlap
      paths = [] # (path, origin)
      for name, path in self.cache.iteritems():
        paths.append((path, 'cache %s' % (name,)))
      for (path, pkg), version in self.cipd_package.iteritems():
        paths.append((path, 'cipd %s %s' % (pkg, version)))
      paths.sort()
      for (a_path, a_ctx), (b_path, b_ctx) in zip(paths, paths[1:]):
        if b_path.startswith(a_path):
          if a_ctx.startswith('cipd ') and b_ctx.startswith('cipd '):
            # overlapping cipd package paths is fine
            continue
          e('%r overlaps %r', a_ctx, b_ctx)

      if fail[0]:
        raise InvalidTaskTemplateError(ctx.result())

      return TaskTemplate(
        cache = tuple(
          CacheEntry(name, path)
          for name, path in sorted(self.cache.items())),
        cipd_package = tuple(
          CipdPackage(path, pkg, version)
          for (path, pkg), version in sorted(self.cipd_package.items())),
        env = tuple(
          Env(var, value, prefix, soft)
          for var, (value, prefix, soft) in sorted(self.env.items())),
        inclusions = frozenset(self.inclusions),
      )


  @classmethod
  def from_pb(cls, ctx, t, template_map):
    """This returns a TaskTemplate from `t`, a pools_pb2.TaskTemplate, and
    `template_map`, which maps include names to TaskTemplate instances."""
    assert isinstance(t, pools_pb2.TaskTemplate)

    ret = cls._Intermediate()

    for include in t.include:
      ret.update(ctx, template_map[include], include)

    ret.update(ctx, cls._Intermediate(
      cache = {e.name: e.path for e in t.cache},
      cipd_package = {(e.path, e.pkg): e.version for e in t.cipd_package},
      env = {e.var: (e.value, tuple(e.prefix), e.soft) for e in t.env},
    ).finalize(ctx))

    return ret.finalize(ctx)

  @staticmethod
  def _overlaps_paths(needle, haystack):
    """Finds if `needle` is equal, or a subdirectory of, any of the '/'
    delimited paths in `haystatck`."""
    for path in haystack:
      if path.startswith(needle):
        return path
    return None

  def apply_to_task_properties(self, p):
    """Applies this template to the indicated properties.

    Modifies `p` in-place.

    Args:
      p (task_request.TaskProperties) - The task properties to modify.
    """
    assert isinstance(p, task_request.TaskProperties)

    for envvar in self.env:
      var = envvar.var
      if not envvar.soft:
        if var in p.env:
          raise TaskTemplateApplicationError('env[%r]' % var)
        if var in p.env_prefixes:
          raise TaskTemplateApplicationError('env_prefixes[%r]' % var)

      if envvar.value:
        p.env[var] = p.env.get(var, '') or envvar.value

      if envvar.prefix:
        new_prefix = p.env_prefixes.get(var, [])
        new_prefix.extend(envvar.prefix)
        p.env_prefixes[var] = new_prefix

    cache_map = {c.name: c.path for c in p.caches}
    paths = set(cache_map.values())
    paths.update(p.path for p in p.cipd_input.packages)
    for cache in self.cache:
      if cache.name in cache_map:
        raise TaskTemplateApplicationError('cache[%r]' % cache.name)
      overlap = self._overlaps_paths(cache.path, paths)
      if overlap:
        raise TaskTemplateApplicationError(
          'a cache or CIPD package with path %r' % (overlap,))
      p.caches.append(task_request.CacheEntry(
        name=cache.name,
        path=cache.path))

    for pkg in self.cipd_package:
      overlap = self._overlaps_paths(pkg.path, paths)
      if overlap:
        raise TaskTemplateApplicationError(
          'a cache or CIPD package with path %r' % (overlap,))
      p.cipd_input.packages.append(task_request.CipdPackage(
        path=pkg.path,
        package_name=pkg.pkg,
        version=pkg.version,
      ))


CacheEntry = collections.namedtuple('CacheEntry', ['name', 'path'])
CipdPackage = collections.namedtuple('CipdPackage', ['path', 'pkg', 'version'])
Env = collections.namedtuple('Env', ['var', 'value', 'prefix', 'soft'])


def get_pool_config(pool_name):
  """Returns PoolConfig for the given pool or None if not defined."""
  if pool_name is None:
    raise ValueError('get_pool_config called with None')
  return _fetch_pools_config().pools.get(pool_name)


def forbid_unknown_pools():
  """Returns True if the configuration forbids task in unknown pools.

  Unknown pools are pools that are not defined in pools.cfg.

  On a server without pools.cfg file, forbid_unknown_pools() returns False, to
  be backward compatible with simple Swarming deployments that don't do pool
  isolation.
  """
  return _fetch_pools_config().forbid_unknown_pools


### Private stuff.


# Parsed representation of pools.cfg ready for queries.
_PoolsCfg = collections.namedtuple('_PoolsCfg', [
  'pools',                 # dict {pool name => PoolConfig tuple}
  'forbid_unknown_pools',  # boolean, taken directly from the proto message
])


def _resolve_task_template_inclusions(ctx, task_templates):
  """Resolves all task template inclusions in the provided
  pools_pb2.TaskTemplate list.

  Returns a new dictionary with {name -> TaskTemplate} namedtuples.
  """
  template_map = {t.name: t for t in task_templates}
  if '' in template_map:
    ctx.error('one or more templates has a blank name')
    return

  if len(template_map) != len(task_templates):
    ctx.error('one or more templates has a duplicate name')
    return

  unresolved_includes = {}
  for t in task_templates:
    with ctx.prefix('template[%r]: ', t.name.encode('utf-8')):
      for inc in t.include:
        if inc not in template_map:
          ctx.error('unknown include: %r', inc.encode('utf-8'))
          return
      unresolved_includes[t.name] = set(t.include)

  resolved = {} # name -> properties for TaskTemplate

  while unresolved_includes:
    for name, includes in unresolved_includes.iteritems():
      # looking for an item in unresolved_includes without any unresolved
      # includes.
      if includes:
        continue

      with ctx.prefix('template[%r]: ', name.encode('utf-8')):
        try:
          # NOTE: template_map still has all the original include directives.
          # from_pb will use the `resolved` map to look up all of the
          # dependencies, which have been fully resolved at this point.
          resolved[name] = TaskTemplate.from_pb(
            ctx, template_map[name], resolved)
        except InvalidTaskTemplateError:
          return

      # obliterate all references to the template we just resolved
      unresolved_includes.pop(name)
      for includes in unresolved_includes.itervalues():
        includes.discard(name)

      break # back to outer loop to find the next include
    else:
      ctx.error('include cycle detected')
      return

  return resolved


def _resolve_task_template_deployments(ctx, template_map,
                                       task_template_deployments):
  ret = {}

  for i, deployment in enumerate(task_template_deployments):
    if deployment.name == "":
      ctx.error('deployment[%d]: has no name', i)
      return
    with ctx.prefix('deployment[%r]: ', deployment.name):
      try:
        ret[deployment.name] = TaskTemplateDeployment.from_pb(
          ctx, deployment, template_map)
      except InvalidTaskTemplateError:
        return

  return ret


def _resolve_deployment(ctx, pool_msg, template_map, deployment_map):
  deployment_scheme = pool_msg.WhichOneof("task_deployment_scheme")
  if deployment_scheme == "task_template_deployment":
    if pool_msg.task_template_deployment not in deployment_map:
      ctx.error('unknown deployment: %r', pool_msg.task_template_deployment)
      return
    return deployment_map[pool_msg.task_template_deployment]

  if deployment_scheme == "task_template_deployment_inline":
    try:
      return TaskTemplateDeployment.from_pb(
        ctx, pool_msg.task_template_deployment_inline, template_map)
    except InvalidTaskTemplateError:
      pass


def _to_ident(s):
  if ':' not in s:
    s = 'user:' + s
  return auth.Identity.from_bytes(s)


def _validate_ident(ctx, title, s):
  try:
    return _to_ident(s)
  except ValueError as exc:
    ctx.error('bad %s value "%s" - %s', title, s, exc)


@utils.cache_with_expiration(60)
def _fetch_pools_config():
  """Loads pools.cfg and parses it into a _PoolsCfg instance."""
  # store_last_good=True tells config components to update the config file
  # in a cron job. Here we just read from the datastore. In case it's the first
  # call ever, or config doesn't exist, it returns (None, None).
  rev, cfg = config.get_self_config(
      POOLS_CFG_FILENAME, pools_pb2.PoolsCfg, store_last_good=True)
  if not cfg:
    return _PoolsCfg({}, False)

  # The config is already validated at this point.

  fake_ctx = validation.Context()
  template_map = _resolve_task_template_inclusions(
    fake_ctx, cfg.task_template)
  deployment_map = _resolve_task_template_deployments(
    fake_ctx, template_map, cfg.task_template_deployment)

  pools = {}
  for msg in cfg.pool:
    for name in msg.name:
      pools[name] = PoolConfig(
          name=name,
          rev=rev,
          scheduling_users=frozenset(_to_ident(u) for u in msg.schedulers.user),
          scheduling_groups=frozenset(msg.schedulers.group),
          trusted_delegatees={
            _to_ident(d.peer_id): TrustedDelegatee(
                peer_id=_to_ident(d.peer_id),
                required_delegation_tags=frozenset(d.require_any_of.tag))
            for d in msg.schedulers.trusted_delegation
          },
          service_accounts=frozenset(msg.allowed_service_account),
          service_accounts_groups=tuple(msg.allowed_service_account_group),
          task_template_deployment=_resolve_deployment(
            fake_ctx, msg, template_map, deployment_map))
  return _PoolsCfg(pools, cfg.forbid_unknown_pools)


@validation.self_rule(POOLS_CFG_FILENAME, pools_pb2.PoolsCfg)
def _validate_pools_cfg(cfg, ctx):
  """Validates pools.cfg file."""

  template_map = _resolve_task_template_inclusions(
    ctx, cfg.task_template)
  deployment_map = _resolve_task_template_deployments(
    ctx, template_map, cfg.task_template_deployment)

  pools = set()
  for i, msg in enumerate(cfg.pool):
    with ctx.prefix('pool #%d (%s): ', i, '|'.join(msg.name) or 'unnamed'):
      # Validate names.
      if not msg.name:
        ctx.error('at least one pool name must be given')
      for name in msg.name:
        if not local_config.validate_dimension_value(name):
          ctx.error('bad pool name "%s", not a valid dimension value', name)
        elif name in pools:
          ctx.error('pool "%s" was already declared', name)
        else:
          pools.add(name)

      # Validate schedulers.user.
      for u in msg.schedulers.user:
        _validate_ident(ctx, 'user', u)

      # Validate schedulers.group.
      for g in msg.schedulers.group:
        if not auth.is_valid_group_name(g):
          ctx.error('bad group name "%s"', g)

      # Validate schedulers.trusted_delegation.
      seen_peers = set()
      for d in msg.schedulers.trusted_delegation:
        with ctx.prefix('trusted_delegation #%d (%s): ', i, d.peer_id):
          if not d.peer_id:
            ctx.error('"peer_id" is required')
          else:
            peer_id = _validate_ident(ctx, 'peer_id', d.peer_id)
            if peer_id in seen_peers:
              ctx.error('peer "%s" was specified twice', d.peer_id)
            elif peer_id:
              seen_peers.add(peer_id)
          for i, tag in enumerate(d.require_any_of.tag):
            if ':' not in tag:
              ctx.error('bad tag #%d "%s" - must be <key>:<value>', i, tag)

      # Validate service accounts.
      for i, account in enumerate(msg.allowed_service_account):
        if not service_accounts.is_service_account(account):
          ctx.error('bad allowed_service_account #%d "%s"', i, account)

      # Validate service account groups.
      for i, group in enumerate(msg.allowed_service_account_group):
        if not auth.is_valid_group_name(group):
          ctx.error('bad allowed_service_account_group #%d "%s"', i, group)

      _resolve_deployment(ctx, msg, template_map, deployment_map)
