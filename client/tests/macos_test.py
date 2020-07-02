#!/usr/bin/env vpython3
# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import unittest

import six

# Mutates sys.path.
import test_env

from utils import macos


class MacosTest(unittest.TestCase):

  @unittest.skipIf(six.PY2, 'this is only for python3')
  def test_get_errno(self):
    self.assertEqual(macos.get_errno(OSError('MAC Error -43')), -43)


if __name__ == '__main__':
  test_env.main()
