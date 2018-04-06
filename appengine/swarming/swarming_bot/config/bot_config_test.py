#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import hashlib
import struct
import unittest

class Test(unittest.TestCase):
  def test_fudge(self):
    # This assumes little endian.
    f = 1. + (6e-6 * struct.unpack('h', '\xff\x8f')[0])
    self.assertEqual(0.827962, f)
    f = 1. + (6e-6 * struct.unpack('h', '\xff\x7f')[0])
    self.assertEqual(1.196602, f)


if __name__ == '__main__':
  unittest.main()
