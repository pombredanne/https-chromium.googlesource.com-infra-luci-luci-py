# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Expansion of realms_config.Realm into the flat form."""

import collections

from components.auth import model
from components.auth.proto import realms_pb2
from components.config import validation as cfg_validation

from proto import realms_config_pb2

from realms import common
from realms import permissions
from realms import validation


def expand_realms(db, project_id, realms_cfg):
  """Expands realms_config.RealmsCfg into a flat realms_pb2.Realms.

  The returned realms_pb2.Realms contains realms and permissions of a single
  project only. Permissions not mentioned in the project's realms are omitted.
  All realms_pb2.Permission message have permission names only (no metadata).

  All such realms_pb2.Realms messages for all projects (plus a list of all
  permissions with all their metadata) can be merged together into a final
  universal realms_pb2.Realms by merge_realms().

  Args:
    db: a permissions.DB instance with current permissions and roles.
    project_id: ID of a LUCI project to use a prefix in realm names.
    realms_cfg: an instance of realms_config.RealmsCfg to expand.

  Returns:
    realms_pb2.Realms with expanded realms.

  Raises:
    ValueError if the given realms doesn't pass validation.
  """
  # The server code could have changed since the config passed the validation
  # and it may not be valid anymore. Verify it still is. The code below depends
  # crucially on the validity of configs (in particular absence of cycles).
  ctx = cfg_validation.Context.raise_on_error()
  validation.validate_realms_cfg_with_db(db, realms_cfg, ctx)

  # A lazy populated {role -> tuple of permissions} mapping.
  roles_expansion = RolesExpansion(db, realms_cfg.custom_roles)
  # A helper to traverse the realms graph.
  realms_expansion = RealmsExpansion(roles_expansion, realms_cfg.realms)

  # Visit all realms and build preliminary lists of bindings as pairs of
  # (a permission tuple, a list of principals who have them). This populates
  # `roles` with permissions that are actually in use, thus we should finish
  # this first pass before we can proceed.
  realms = []  # [(name, (permissions tuple, principals list))]
  for name in realms_expansion.names:
    # Build a mapping from a principal to the permissions set they have.
    principal_to_perms = collections.defaultdict(set)
    for principal, perms in realms_expansion.elementary_bindinds(name):
      principal_to_perms[principal].update(perms)
    # Combine entries with the same set of permissions into one.
    perms_to_principals = collections.defaultdict(list)
    for principal, perms in principal_to_perms.items():
      perms_to_principals[tuple(sorted(perms))].append(principal)
    realms.append((name, perms_to_principals.items()))

  # We now know all permissions ever used by all realms. Convert them into the
  # realm_pb2 form by sorting alphabetically. Keep the mapping between old and
  # new indexes, to be able to change indexes in permission sets.
  perms, index_map = roles_expansion.sorted_permissions()

  # Build the final "deterministic" form of all realms by relabeling permissions
  # according to the index_map and by sorting stuff.
  return realms_pb2.Realms(
      api_version=model.REALMS_API_VERSION,
      permissions=[realms_pb2.Permission(name=p) for p in perms],
      realms=[
          realms_pb2.Realm(
              name='%s/%s' % (project_id, name),
              bindings=to_normalized_bindings(perms_to_principals, index_map),
          )
          for name, perms_to_principals in realms
      ])


class RolesExpansion(object):
  """Keeps track of permissions and `role => [permission]` expansions.

  Permissions are represented internally as integers to speed up set operations.
  The mapping from a permission to a corresponding integer is lazily-built and
  should be considered arbitrary (it depends on the order of method calls). It
  doesn't matter since in the end we relabel all permissions according to their
  indexes in the sorted list of permissions.

  Should be used only with validated realms_config_pb2.RealmsCfg, may recurse
  infinitely or raise random exceptions otherwise.
  """

  def __init__(self, db, custom_roles):
    self._db = db
    self._custom_roles = {r.name: r for r in custom_roles}
    self._permissions = {}  # permission name => its index
    self._roles = {}  # role name => set indexes of permissions

  def permission(self, name):
    """Returns an index that represents the given permission string."""
    idx = self._permissions.get(name)
    if idx is None:
      idx = len(self._permissions)
      self._permissions[name] = idx
    return idx

  def permissions(self, iterable):
    """Returns a tuple of indexes of corresponding permission strings."""
    return tuple(self.permission(p) for p in iterable)

  def role(self, role):
    """Returns an unsorted tuple of indexes of permissions of the role."""
    perms = self._roles.get(role)
    if perms is not None:
      return perms

    if role.startswith(permissions.BUILTIN_ROLE_PREFIX):
      perms = self.permissions(self._db.roles[role].permissions)
    elif role.startswith(permissions.CUSTOM_ROLE_PREFIX):
      custom_role = self._custom_roles[role]
      perms = set(self.permissions(custom_role.permissions))
      for parent in custom_role.extends:
        perms.update(self.role(parent))
      perms = tuple(perms)
    else:
      raise AssertionError('Impossible role %s' % (role,))

    self._roles[role] = perms
    return perms

  def sorted_permissions(self):
    """Returns a sorted list of permission and a old->new index mapping list.

    See to_normalized_bindings below for how it is used.
    """
    perms = sorted(self._permissions)
    mapping = [None]*len(perms)
    for new_idx, p in enumerate(perms):
      old_idx = self._permissions[p]
      mapping[old_idx] = new_idx
    return perms, mapping


class RealmsExpansion(object):
  """Helper to traverse the realm inheritance graph."""

  def __init__(self, roles, realms):
    self._roles = roles
    self._realms = {r.name: r for r in realms}
    if common.ROOT_REALM not in self._realms:
      self._realms[common.ROOT_REALM] = default_root()

  @property
  def names(self):
    """Returns a sorted list of names of all realms, including @root."""
    return sorted(self._realms)

  def elementary_bindinds(self, realm):
    """Yields pairs of (principal, permissions tuple) that define a realm.

    Returns a lot of duplicates. It's the caller's job to skip them.
    """
    r = self._realms[realm]

    for b in r.bindings:
      perms = self._roles.role(b.role)  # the tuple of permissions of the role
      for principal in b.principals:
        yield principal, perms

    for parent in r.extends:
      if parent == common.ROOT_REALM:
        continue  # will explicitly visit it later
      for principal, perms in self.elementary_bindinds(parent):
        yield principal, perms

    # All realms except the root itself inherit from @root.
    if realm != common.ROOT_REALM:
      for principal, perms in self.elementary_bindinds(common.ROOT_REALM):
        yield principal, perms


def default_root():
  """A root realm to use if not explicitly defined in the config."""
  return realms_config_pb2.Realm(name=common.ROOT_REALM)


def to_normalized_bindings(perms_to_principals, index_map):
  """Produces a sorted list of normalized realms_pb2.Binding.

  Bindings are given as `perms_to_principals` list of (tuple of permissions,
  list of principals) pairs. Permissions are specified through their internal
  indexes as produced by RolesExpansion. We should convert them into "public"
  ones (the ones that correspond to the sorted permissions list in the
  realms_pb2.Realms proto). The mapping from an old to a new index is given
  by: `new = index_map[old]`.

  Args:
    perms_to_principals: a list of (tuple of permissions, list of principals).
    index_map: defines how to remap permission indexes (old -> new).

  Returns:
    A sorted list of realm_pb2.Binding.
  """
  # Remap and sort the list of permissions, sort the list of principals.
  normalized = (
      (sorted(index_map[idx] for idx in permset), sorted(principals))
      for permset, principals in perms_to_principals
  )
  return [
      realms_pb2.Binding(permissions=permset, principals=principals)
      for permset, principals in sorted(normalized, key=lambda x: x[0])
  ]
