#!/usr/bin/env vpython
# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import unittest

import swarming_test_env
swarming_test_env.setup_test_env()

from google.appengine.ext import ndb

from test_support import test_case

import backend_conversions
from server import task_result

from infra import init_python_pb2  # pylint: disable=unused-import
from go.chromium.org.luci.buildbucket.proto import taskbackend_service_pb2


class TestBackendConversions(test_case.TestCase):

  def test_compute_task_slices(self):
    expected_slices = []
    self.assertEqual(expected_slices,
                     backend_conversions._compute_task_slices(run_task_req))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
