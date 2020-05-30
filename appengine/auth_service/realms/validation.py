# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Validation of realms.cfg config files."""

from components import auth
from components.config import validation

from proto import realms_config_pb2

from realms import common
from realms import permissions


# TODO(vadimsh): Figure out how to handle deletion of roles and permissions.
# Right now deleting a role/permission would result in all configs that use it
# to become invalid. Maybe instead of deleting roles we could mark them as
# deprecated, which should trigger validation warnings (not errors) when a
# config is referring to such role/permission. Eventually, once there are no
# such warnings anymore, the role/permission can be deleted for real.


def register():
  """Register the config validation hook."""
  # pylint: disable=unused-variable
  @validation.project_config_rule(
      common.cfg_path(), realms_config_pb2.RealmsCfg)
  def validate_realms_cfg(cfg, ctx):
    validate_realms_cfg_with_db(permissions.db(), cfg, ctx)


def validate_realms_cfg_with_db(db, cfg, ctx):
  """Validates realms.cfg config file with the given roles DB.

  Extracted from validate_realms_cfg for easier testing.
  """
  custom_roles_map = validate_custom_roles_list(db, cfg.custom_roles, ctx)
  validate_realms_list(db, cfg.realms, custom_roles_map, ctx)


def validate_custom_roles_list(db, roles, ctx):
  """Validates a list of realms_config_pb2.CustomRole, converts it to a map."""
  all_custom_roles = set(r.name for r in roles)
  graph = {}  # custom role name => set of custom roles it `extends` from

  for i, role in enumerate(roles):
    with ctx.prefix('Custom role #%d ("%s"): ', i+1, role.name):
      if not role.name.startswith(permissions.CUSTOM_ROLE_PREFIX):
        ctx.error('name should start with "%s"', permissions.CUSTOM_ROLE_PREFIX)
        continue
      if role.name in graph:
        ctx.error('a custom role with this name was already defined')
        continue

      # All referenced permissions must be known.
      for perm in role.permissions:
        validate_permission(db, perm, ctx)

      # Validate `extends` relations, build an adjacency map for the graph cycle
      # check below.
      parent_custom_roles = set()
      for parent in role.extends:
        good = validate_role_ref(db, parent, all_custom_roles, ctx)
        if parent.startswith(permissions.CUSTOM_ROLE_PREFIX) and good:
          if parent in parent_custom_roles:
            ctx.error('the role "%s" is extended from more than once', parent)
          else:
            parent_custom_roles.add(parent)
      graph[role.name] = parent_custom_roles

  # Make traversal order deterministic.
  graph = {k: sorted(v) for k, v in graph.items()}

  valid = {}
  cyclic = set()
  for name, role in sorted(graph.items()):
    if name in cyclic:
      continue  # already found it to be a part of a cycle, don't report again
    cycle = find_cycle(name, graph)
    if cycle:
      ctx.error(
          'Custom role "%s" cyclically extends itself: %s',
          name, ' -> '.join('"%s"' % node for node in cycle))
      cyclic.update(cycle)
    else:
      valid[name] = role

  return valid


def validate_permission(db, perm, ctx):
  """Emits errors if the permission is not defined."""
  if perm not in db.permissions:
    ctx.error(
        'permission "%s" is not defined in permissions DB ver "%s"',
        perm, db.revision)


def validate_role_ref(db, name, custom_roles, ctx):
  """Emits errors and returns False if the role name is unrecognized."""
  if name.startswith(permissions.BUILTIN_ROLE_PREFIX):
    if name.startswith(permissions.INTERNAL_ROLE_PREFIX):
      ctx.error(
          'the role "%s" is an internal role, it can\'t be used in the config',
          name)
      return False
    if name in db.roles:
      return True
    ctx.error(
        'referencing a role "%s" not defined in permissions DB ver "%s"',
        name, db.revision)
    return False

  if name.startswith(permissions.CUSTOM_ROLE_PREFIX):
    if name in custom_roles:
      return True
    ctx.error(
        'referencing a role "%s" not defined in the realms config', name)
    return False

  ctx.error(
      'bad role reference "%s": must be either some predefined '
      'role ("%s..."), or a custom role defined somewhere in this '
      'file ("%s...")',
      name, permissions.BUILTIN_ROLE_PREFIX, permissions.CUSTOM_ROLE_PREFIX)
  return False


def validate_realms_list(db, realms, custom_roles_map, ctx):
  """Validates a list of realms_config_pb2.Realm."""
  all_realms = set(r.name for r in realms)
  graph = {}  # realm name => set of realms it `extends` from

  for i, realm in enumerate(realms):
    with ctx.prefix('Realm #%d ("%s"): ', i+1, realm.name):
      if not validate_realm_name(realm.name, ctx):
        continue
      if realm.name in graph:
        ctx.error('a realm with this name was already defined')
        continue

      # Bindings must refer to known roles.
      for j, binding in enumerate(realm.bindings):
        with ctx.prefix('binding #%d (role "%s") - ', j+1, binding.role):
          validate_binding(db, binding, custom_roles_map, ctx)

      # The root realm can't have any parents, it makes a cycle.
      if realm.name == common.ROOT_REALM:
        if realm.extends:
          ctx.error('the root realm must not use `extends`')
        graph[realm.name] = set()
        continue

      # Validate format of `extends` relations, build an adjacency map for the
      # graph cycle check below.
      parent_realms = set()
      for parent in realm.extends:
        if parent not in all_realms:
          ctx.error('extending from an undefined realm "%s"', parent)
        elif parent in parent_realms:
          ctx.error('the realm "%s" is extended from more than once', parent)
        else:
          parent_realms.add(parent)
      graph[realm.name] = parent_realms

  # Make traversal order deterministic.
  graph = {k: sorted(v) for k, v in graph.items()}

  cyclic = set()
  for name in sorted(graph):
    if name in cyclic:
      continue  # already found it to be a part of a cycle, don't report again
    cycle = find_cycle(name, graph)
    if cycle:
      ctx.error(
          'Realm "%s" cyclically extends itself: %s',
          name, ' -> '.join('"%s"' % node for node in cycle))
      cyclic.update(cycle)


def validate_realm_name(name, ctx):
  """Emits errors and returns False if the realm name is malformed."""
  if name.startswith('@'):
    if name == common.ROOT_REALM or name == common.LEGACY_REALM:
      return True
    ctx.error(
        'unknown special realm name, only "%s" and "%s" are allowed',
        common.ROOT_REALM, common.LEGACY_REALM)
    return False
  if not common.REALM_NAME_RE.match(name):
    ctx.error('the name must match "%s"', common.REALM_NAME_RE.pattern)
    return False
  return True


def validate_binding(db, binding, custom_roles_map, ctx):
  """Emits errors if the binding is invalid."""
  validate_role_ref(db, binding.role, custom_roles_map, ctx)
  for p in binding.principals:
    if p.startswith('group:'):
      group = p[len('group:'):]
      if not auth.is_valid_group_name(group):
        ctx.error('invalid group name: "%s"', group)
    else:
      try:
        auth.Identity.from_bytes(p)
      except ValueError:
        ctx.error('invalid principal format: "%s"', p)


def find_cycle(start, graph):
  """Finds a path from `start` to itself in a directed graph.

  Note that if the graph has other cycles (that don't have `start` as a hop),
  they are ignored.

  Args:
    start: str name of the node to start.
    graph: {str => iterable of str} is adjacency map that defines the graph.

  Returns:
    A list or str with nodes that form a cycle or None if there's no cycle.
    When not None, the first and the last elements are always `start`.

  Raises:
    KeyError if there's a reference to a node that is not in the `graph` map.
  """
  explored = set()  # set of roots of totally explored subgraphs
  visiting = []     # stack of nodes currently being traversed

  def visit(node):
    if node in explored:
      return False  # been there, no cycles there that have `start` in them

    if node in visiting:
      # Found a cycle that starts and ends with `node`. Return True if it is
      # "start -> ... -> start" cycle or False if is some "inner" cycle. We are
      # not interested in the latter.
      return node == start

    visiting.append(node)
    for edge in graph[node]:
      if visit(edge):
        return True  # found a cycle!

    popped = visiting.pop()
    assert popped == node
    explored.add(node)  # don't visit this subgraph ever again

    return False

  if not visit(start):
    return None

  visiting.append(start)  # close the loop
  return visiting
