# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""This is simple wrapper of MacOS.Error or OSError for macos."""

import six

if six.PY3:
  import re
  # Extract 43 from error like 'Mac Error -43'
  _mac_error_re = re.compile('^MAC Error -(\d+)$')

  Error = OSError

  def get_errno(e):
    m = _mac_error_re.match(e.args[0])
    if not m:
      return None
    return -int(m.groups()[0])
else:
  import MacOS
  Error = MacOS.Error

  def get_errno(e):
    return e.args[0]
