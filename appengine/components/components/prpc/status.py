# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Implementation of Status RPC class."""


class Status(Object):

  def __init__(self, code, details, details_object):
    assert code is not codes.StatusCode.OK, 'code must not be StatusCode.OK'
    assert code in codes.ALL_CODES, '%r is not StatusCode.*' % (code,)
    self.code = code
    self.details = details
    self.details_object = details_object
