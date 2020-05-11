#!/usr/bin/env vpython3
# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import unittest

from test_support import test_case

from proto.config import realms_pb2
import realms


class RealmsTest(test_case.TestCase):

  def test_permission_names(self):
    self.assertEqual(
        'swarming.pool.createTask',
        realms.PERMISSIONS[realms_pb2.REALM_PERMISSION_POOL_CREATE_TASK])


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
