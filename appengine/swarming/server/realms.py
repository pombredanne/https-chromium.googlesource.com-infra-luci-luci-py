# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from proto.config import realms_pb2

_PERMISSION_PREFIX = 'REALM_PERMISSION_'

def get_permission_name(enum_permission):
  """ generates Realm permission name from enum value.

  e.g. realms_pb2.REALM_PERMISSION_POOL_CREATE_TASK
       -> 'swarming.pool.createTask'

  Args:
    enum_permission: realms_pb2.RealmPermission enum value.

  Returns:
    realm_permission: Realm permission name 'swarming.<subject>.<verb>'
  """
  enum_name = realms_pb2.RealmPermission.Name(enum_permission)
  words = enum_name.replace(_PERMISSION_PREFIX, '').split('_')
  # convert first word to subject e.g. pool, task
  subject = words[0].lower()
  # convert following words to verb e.g. createTask, listBots
  verb = words[1].lower() + ''.join(map(lambda x: x.capitalize(), words[2:]))
  return 'swarming.%s.%s' % (subject, verb)
