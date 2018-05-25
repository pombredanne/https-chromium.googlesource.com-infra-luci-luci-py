#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import sys
import unittest

import service
import test_pb2  # must be imported to registeer messages
import test_prpc_pb2


class TestService(object):
  DESCRIPTION = test_prpc_pb2.TestServiceServiceDescription


class DiscoveryServiceTests(unittest.TestCase):
  def test(self):
    res = service._response_for([TestService()])
    print(res.description)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
