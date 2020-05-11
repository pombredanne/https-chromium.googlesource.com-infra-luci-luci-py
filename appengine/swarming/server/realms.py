# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from proto.config import realms_pb2

PERMISSIONS = {
    realms_pb2.REALM_PERMISSION_UNSPECIFIED: 'swarming.unspecified',
    realms_pb2.REALM_PERMISSION_POOL_CREATE_TASK: 'swarming.pool.createTask',
}
