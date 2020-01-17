# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Implementation of Status RPC class."""

from google.protobuf import any_pb2


class Status(Object):

  def __init__(self, code, details, error_details):
    assert code is not codes.StatusCode.OK, 'code must not be StatusCode.OK'
    assert all(isinstance(detail, any_pb2.Any) for detail in error_details), 'error_details must all be Any protos'
    self.code = code
    self.details = details
    self.error_details = error_details
