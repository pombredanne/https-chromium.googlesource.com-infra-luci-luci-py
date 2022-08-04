# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""
will be removed once all the related use be updated to server_base
"""

import httplib

from components.prpc.codes import StatusCode

  # pylint: disable=pointless-string-statement

_PRPC_TO_HTTP_STATUS = {
    StatusCode.OK: httplib.OK,
    StatusCode.CANCELLED: httplib.NO_CONTENT,
    StatusCode.INVALID_ARGUMENT: httplib.BAD_REQUEST,
    StatusCode.DEADLINE_EXCEEDED: httplib.SERVICE_UNAVAILABLE,
    StatusCode.NOT_FOUND: httplib.NOT_FOUND,
    StatusCode.ALREADY_EXISTS: httplib.CONFLICT,
    StatusCode.PERMISSION_DENIED: httplib.FORBIDDEN,
    StatusCode.RESOURCE_EXHAUSTED: httplib.SERVICE_UNAVAILABLE,
    StatusCode.FAILED_PRECONDITION: httplib.PRECONDITION_FAILED,
    StatusCode.OUT_OF_RANGE: httplib.BAD_REQUEST,
    StatusCode.UNIMPLEMENTED: httplib.NOT_IMPLEMENTED,
    StatusCode.INTERNAL: httplib.INTERNAL_SERVER_ERROR,
    StatusCode.UNAVAILABLE: httplib.SERVICE_UNAVAILABLE,
    StatusCode.UNAUTHENTICATED: httplib.UNAUTHORIZED,
}