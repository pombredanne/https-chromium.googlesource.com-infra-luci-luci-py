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


class _DirectoryOcclusionChecker(object):
  """A very limited filesystem hierarchy checker.

  This forms a tree, where each node is a directory. Nodes in the tree may have
  a mapping from owner claiming this directory to a series of notes
  (descriptions of /why/ this owner claims this directory).

  Paths may only ever have one owner; After adding all paths to the
  _DirectoryOcclusionChecker, call .conflicts to populate a validation.Context
  with any conflicts discovered.

  Practically, this is used to ensure that Cache directories do not overlap with
  CIPD package directives; CIPD packages may not be installed as subdirs of
  caches, and caches may not be installed as subdirs of CIPD package
  directories. Similarly, multiple caches cannot be mapped to the same
  directory.
  """
  def __init__(self, full_path=''):
    self._full_path = full_path
    self._owner_notes = collections.defaultdict(set) # owner -> set(notes)
    self._subdirs = {}

  def add(self, path, owner, note):
    """Attaches `note` to `path` with the specified `owner`.

    Args:
      path (str) - a '/'-delimited path to annotate
      owner (str) - The owning entity for this path
      note (str) - A brief description of why `owner` lays claim to `path`.
    """
    tokens = path.encode('utf-8').split('/')
    node = self
    for i, token in enumerate(tokens):
      node = node._cd(tokens[:i+1], token)
    node._owner_notes[owner].add(note)

  def conflicts(self, ctx):
    """Populates `ctx` with all violations found in this
    _DirectoryOcclusionChecker.

    This will walk the _DirectoryOcclusionChecker depth-first, pruning branches
    at the first conflict.

    Args:
      ctx (validation.Context) - Conflicts found will be reported here.

    Returns a boolean indicating if conflicts were found or not.
    """
    return self._conflicts(ctx, None)

  # internal

  def _conflicts(self, ctx, parent_owned_node):
    """Populates `ctx` with all violations found in this
    _DirectoryOcclusionChecker.

    This will walk the _DirectoryOcclusionChecker depth-first, pruning branches
    at the first conflict.

    Args:
      ctx (validation.Context) - Conflicts found will be reported here.
      parent_owned_node (cls|None) - If set, a node in the
        _DirectoryOcclusionChecker tree which is some (possibly distant) parent
        in the filesystem that has an owner set.

    Returns a boolean indicating if conflicts were found or not.
    """
    my_owners = self._owner_notes.keys()
    # multiple owners tried to claim this directory. In this case there's no
    # discernable owner for subdirectories, so return True immediately.
    if len(my_owners) > 1:
      ctx.error(
          '%r: directory has conflicting owners: %s',
          self._full_path, ' and '.join(self._descriptions()))
      return True

    # something (singluar) claimed this directory
    if len(my_owners) == 1:
      my_owner = my_owners[0]

      # some directory above us also has an owner set, check for conflicts.
      if parent_owned_node:
        if my_owner != parent_owned_node._owner():
          # We found a conflict; there's no discernible owner for
          # subdirectories, so return True immediately.
          ctx.error(
            "%s uses %r, which conflicts with %s using %r",
            self._describe_one(), self._full_path,
            parent_owned_node._describe_one(), parent_owned_node._full_path)
          return True
      else:
        # we're the first owner down this leg of the tree, so parent_owned_node
        # is now us for all subdirectories.
        parent_owned_node = self

    ret = False
    for node in self._subdirs.itervalues():
      # call _conflicts() first so that it's not short-circuited.
      ret = node._conflicts(ctx, parent_owned_node) or ret
    return ret

  def _cd(self, parts, subdir):
    """Returns a subordinate _DirectoryOcclusionChecker which represents
    changing into the given subdirectory."""
    ret = self._subdirs.get(subdir, None)
    if ret:
      return ret
    ret = _DirectoryOcclusionChecker('/'.join(parts))
    self._subdirs[subdir] = ret
    return ret

  def _descriptions(self):
    """Formats all the _owner_notes on this node into a list of strings."""
    ret = []
    for owner, notes in sorted(self._owner_notes.iteritems()):
      notes = filter(bool, notes)
      if notes:
        # "owner[note, note, note]"
        ret.append('%s%r' % (owner, sorted(notes)))
      else:
        ret.append(owner)
    return ret

  def _describe_one(self):
    """Gets the sole description for this node as a string.

    Asserts that there's exactly one owner for this node."""
    ret = self._descriptions()
    assert len(ret) == 1
    return ret[0]

  def _owner(self):
    """Gets the sole owner for this node as a string.

    Asserts that there's exactly one owner for this node."""
    assert len(self._owner_notes) == 1
    return self._owner_notes.keys()[0]


class TaskTemplateDeployment(_TaskTemplateDeployment):
  @classmethod
  def from_pb(cls, ctx, d, template_map):
    if not (0 <= d.canary_chance <= 9999):
      ctx.error(
          'canary_chance out of range `[0,9999]`: %d -> %%%.2f',
          d.canary_chance, d.canary_chance/100.)
      raise InvalidTaskTemplateError()

    prod = None
    if d.HasField('prod'):
      prod = TaskTemplate.from_pb(ctx, d.prod, template_map)

    canary = None
    if d.HasField('canary'):
      canary = TaskTemplate.from_pb(ctx, d.canary, template_map)
    if d.canary_chance and not canary:
      ctx.error('canary_chance specified without a canary')
      raise InvalidTaskTemplateError()

    return cls(
      prod=prod,
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
  def __init__(
      self, message,
      fmt='Task defines %s which conflicts with pool task template'):
    self.conflict = message
    super(TaskTemplateApplicationError, self).__init__(fmt % message)


class TaskTemplate(_TaskTemplate):
  class _Intermediate(object):
    """_Intermediate represents an in-flux TaskTemplate instance.

    This is used internally by the .from_pb method to build up a finalized
    TaskTemplate instance."""
    def __init__(self, ctx, t=None):
      if t is None:
        t = pools_pb2.TaskTemplate()
      assert isinstance(t, pools_pb2.TaskTemplate)

      fail = [False]
      def e(*args):
        fail[0] = True
        ctx.error(*args)

      self.cache = {}
      for i, ce in enumerate(t.cache):
        name, path = ce.name, ce.path
        ident = repr(name.encode('utf-8')) if name else '#%d' % i
        with ctx.prefix('cache[%s]: ', ident):
          if not name:
            e('empty name')
          if not path:
            e('empty path')
        self.cache[name] = path

      self.cipd_package = {}
      for i, cp in enumerate(t.cipd_package):
        path, pkg, version = cp.path, cp.pkg, cp.version
        ident = (
            repr((path.encode('utf-8'), pkg.encode('utf-8')))
            if path and pkg else '#%d' % i)
        with ctx.prefix('cipd_package[%s]: ', ident):
          if not pkg:
            e('empty pkg')
          if not version:
            e('empty version')
        self.cipd_package[(path, pkg)] = version

      self.env = {}
      for i, env in enumerate(t.env):
        var, value, prefix, soft = env.var, env.value, env.prefix, env.soft
        ident = repr(var.encode('utf-8')) if var else '#%d' % i
        with ctx.prefix('env[%s]: ', ident):
          if not var:
            e('empty var')
          if not value and not prefix:
            e('empty value AND prefix')
        self.env[var] = (value, tuple(prefix), soft)

      if fail[0]:
        raise InvalidTaskTemplateError(ctx.result())

      # We don't need to initialize this here, update() will adjust this as it
      # processes includes.
      self.inclusions = set()

    def update(self, ctx, other, include_name=None):
      assert isinstance(other, TaskTemplate)

      if include_name:
        if include_name in self.inclusions:
          ctx.error(
              'template %r included multiple times',
              include_name.encode('utf-8'))
          raise InvalidTaskTemplateError()
        self.inclusions.add(include_name)

      for transitive_include in other.inclusions:
        if transitive_include in self.inclusions:
          ctx.error(
              'template %r included (transitively) multiple times',
              transitive_include.encode('utf-8'))
          raise InvalidTaskTemplateError()
        self.inclusions.add(transitive_include)

      for entry in other.cache:
        self.cache[entry.name] = entry.path

      for entry in other.cipd_package:
        self.cipd_package[(entry.path, entry.pkg)] = entry.version

      for entry in other.env:
        val, pfx = '', ()
        if entry.var in self.env:
          val, pfx, _ = self.env[entry.var]
        self.env[entry.var] = (
          entry.value or val,
          (pfx + entry.prefix),
          entry.soft)

    def finalize(self, ctx):
      doc = _DirectoryOcclusionChecker()
      for (path, pkg), version in self.cipd_package.iteritems():
        # all cipd packages are considered compatible in terms of paths: it's
        # totally legit to install many packages in the same directory. Thus we
        # set the owner for all cipd packages to 'cipd'.
        doc.add(path, 'cipd', '%s:%s' % (pkg.encode('utf-8'),
                                         version.encode('utf-8')))

      for name, path in self.cache.iteritems():
        # caches are all unique; they can't overlap. Thus, we give each of them
        # a unique (via the cache name) owner.
        doc.add(path, 'cache %r' % name.encode('utf-8'), '')

      if doc.conflicts(ctx):
        raise InvalidTaskTemplateError(ctx.result())

      return TaskTemplate(
        cache=tuple(
            CacheEntry(name, path)
            for name, path in sorted(self.cache.items())),
        cipd_package=tuple(
            CipdPackage(path, pkg, version)
            for (path, pkg), version in sorted(self.cipd_package.items())),
        env=tuple(
            Env(var, value, prefix, soft)
            for var, (value, prefix, soft) in sorted(self.env.items())),
        inclusions=frozenset(self.inclusions),
      )

  @classmethod
  def from_pb(cls, ctx, t, template_map):
    """This returns a TaskTemplate from `t` and `template_map`.

    Args:
      ctx (validation.Context) - The validation context.
      t (pools_pb2.TaskTemplate) - The proto TaskTemplate message to convert.
      template_map (dict[str,TaskTemplate]) - The map of all the parsed
        includable TaskTemplate messages.

    Returns a TaskTemplate object (this class).

    Raises InvalidTaskTemplateError if there was an issue; all error messages
    are reported via ctx.
    """
    assert isinstance(t, pools_pb2.TaskTemplate)

    ret = cls._Intermediate(ctx)

    for include in t.include:
      ret.update(ctx, template_map[include], include)

    ret.update(ctx, cls._Intermediate(ctx, t).finalize(ctx))

    return ret.finalize(ctx)

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
        if var in (p.env or {}):
          raise TaskTemplateApplicationError('env[%r]' % var.encode('utf-8'))
        if var in (p.env_prefixes or {}):
          raise TaskTemplateApplicationError(
              'env_prefixes[%r]' % var.encode('utf-8'))

      if envvar.value:
        p.env = {} if p.env is None else p.env
        p.env[var] = p.env.get(var, '') or envvar.value

      if envvar.prefix:
        p.env_prefixes = {} if p.env_prefixes is None else p.env_prefixes
        p.env_prefixes[var] = list(envvar.prefix) + p.env_prefixes.get(var, [])

    reserved_cache_names = set()
    doc = _DirectoryOcclusionChecker()
    # add all task template paths
    for cache in self.cache:
      reserved_cache_names.add(cache.name)
      doc.add(
          cache.path, 'task template cache %r' % cache.name.encode('utf-8'),
          '')
    for cp in self.cipd_package:
      doc.add(
          cp.path, 'task template cipd',
          '%s:%s' % (cp.pkg.encode('utf-8'), cp.version.encode('utf-8')))

    # add all task paths, avoiding spurious initializations in the underlying
    # TaskProperties (repeated fields auto-initialize to [] when looped over)
    for cache in (p.caches or ()):
      if cache.name in reserved_cache_names:
        raise TaskTemplateApplicationError(
            'cache[%r]' % cache.name.encode('utf-8'))
      doc.add(
          cache.path, 'task cache %r' % cache.name.encode('utf-8'), '')
    for cp in (p.cipd_input.packages or () if p.cipd_input else ()):
      doc.add(
          cp.path, 'task cipd',
          '%s:%s' % (
              cp.package_name.encode('utf-8'), cp.version.encode('utf-8')))

    ctx = validation.Context()
    if doc.conflicts(ctx):
      raise TaskTemplateApplicationError(
          '\n'.join(m.text for m in ctx.result().messages), fmt='%s')

    for cache in self.cache:
      p.caches.append(task_request.CacheEntry(
          name=cache.name, path=cache.path))

    if self.cipd_package:
      # Only initialize TaskProperties.cipd_input if we have something to add
      p.cipd_input = p.cipd_input or task_request.CipdInput()
      for cp in self.cipd_package:
        p.cipd_input.packages.append(task_request.CipdPackage(
            package_name=cp.pkg, path=cp.path, version=cp.version))


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


def _resolve_task_template_deployments(
    ctx, template_map, task_template_deployments):
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


def _resolve_deployment(
    ctx, pool_msg, template_map, deployment_map):
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
