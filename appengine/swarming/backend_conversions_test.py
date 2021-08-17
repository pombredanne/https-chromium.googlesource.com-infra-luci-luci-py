#!/usr/bin/env vpython
# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import unittest
import sys
import posixpath
import copy

import swarming_test_env
swarming_test_env.setup_test_env()

from google.appengine.ext import ndb

from test_support import test_case

import backend_conversions
from server import task_request

from google.protobuf import struct_pb2
from google.protobuf import duration_pb2
from google.protobuf import timestamp_pb2

from proto.api.internal.bb import backend_pb2
from proto.api.internal.bb import common_pb2
from proto.api.internal.bb import swarming_bb_pb2


class TestBackendConversions(test_case.TestCase):

  def test_compute_task_slices(self):
    exec_secs = 180
    grace_secs = 60

    base_slice = task_request.TaskSlice(
        wait_for_capacity=True,
        properties=task_request.TaskProperties(
            caches=[
                task_request.CacheEntry(
                    path=posixpath.join(backend_conversions._CACHE_DIR,
                                        'path_1'),
                    name='name_1'),
                task_request.CacheEntry(
                    path=posixpath.join(backend_conversions._CACHE_DIR,
                                        'path_2'),
                    name='name_2'),
            ],
            execution_timeout_secs=exec_secs,
            grace_period_secs=grace_secs,
        ),
    )

    slice_1 = task_request.TaskSlice(
        expiration_secs=60, properties=copy.deepcopy(base_slice.properties))
    slice_1.properties.dimensions_data = {
        u'caches': [u'name_2'],
        u'required-1': [u'req-1', u'req-1-2'],
        u'required-2': [u'req-2'],
        u'optional-1': [u'opt-1'],
        u'optional-2': [u'opt-2'],
        u'optional-3': [u'opt-3']
    }

    slice_2 = task_request.TaskSlice(
        expiration_secs=120, properties=copy.deepcopy(base_slice.properties))
    slice_2.properties.dimensions_data = {
        u'caches': [u'name_2'],
        u'required-1': [u'req-1', u'req-1-2'],
        u'required-2': [u'req-2'],
        u'optional-1': [u'opt-1'],
        u'optional-2': [u'opt-2']
    }

    base_slice.expiration_secs = 60  # minimum allowed is 60s
    base_slice.properties.dimensions_data = {
        u'required-1': [u'req-1', u'req-1-2'],
        u'required-2': [u'req-2']
    }

    expected_slices = [slice_1, slice_2, base_slice]

    run_task_req = backend_pb2.RunTaskRequest(
        backend_config=struct_pb2.Struct(
            fields={'wait_for_capacity': struct_pb2.Value(bool_value=True)}),
        caches=[
            swarming_bb_pb2.CacheEntry(name='name_1', path='path_1'),
            swarming_bb_pb2.CacheEntry(
                name='name_2',
                path='path_2',
                wait_for_warm_cache=duration_pb2.Duration(seconds=180))
        ],
        grace_period=duration_pb2.Duration(seconds=grace_secs),
        execution_timeout=duration_pb2.Duration(seconds=exec_secs),
        start_deadline=timestamp_pb2.Timestamp(seconds=60 * 10),
        dimensions=[
            common_pb2.RequestedDimension(key='required-1', value='req-1'),
            common_pb2.RequestedDimension(
                key='optional-1',
                value='opt-1',
                expiration=duration_pb2.Duration(seconds=180)),
            common_pb2.RequestedDimension(
                key='optional-2',
                value='opt-2',
                expiration=duration_pb2.Duration(seconds=180)),
            common_pb2.RequestedDimension(
                key='optional-3',
                value='opt-3',
                expiration=duration_pb2.Duration(seconds=60)),
            common_pb2.RequestedDimension(key='required-2', value='req-2'),
            common_pb2.RequestedDimension(key='required-1', value='req-1-2')
        ])

    self.assertEqual(expected_slices,
                     backend_conversions._compute_task_slices(run_task_req))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
