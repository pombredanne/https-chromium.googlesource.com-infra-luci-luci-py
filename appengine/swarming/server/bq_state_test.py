#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import unittest

import test_env
test_env.setup_test_env()

from google.protobuf import struct_pb2

from test_support import test_case

from server import bq_state


class BotManagementTest(test_case.TestCase):
  APP_DIR = test_env.APP_DIR

  def test_all_apis_are_tested(self):
    actual = frozenset(i[5:] for i in dir(self) if i.startswith('test_'))
    # Contains the list of all public APIs.
    expected = frozenset(
        i for i in dir(bq_state)
        if i[0] != '_' and hasattr(getattr(bq_state, i), 'func_name'))
    missing = expected - actual
    self.assertFalse(missing)

  def test_cron_trigger_tasks(self):
    # TODO(maruel): Will be deleted.
    pass

  def test_send_to_bq_empty(self):
    # Empty, nothing is done. No need to mock the HTTP client.
    self.assertEqual(0, bq_state.send_to_bq('foo', []))

  def test_send_to_bq(self):
    payloads = []
    def json_request(url, method, payload, scopes, deadline):
      self.assertEqual(
          'https://www.googleapis.com/bigquery/v2/projects/sample-app/datasets/'
            'swarming/tables/foo/insertAll',
          url)
      payloads.append(payload)
      self.assertEqual('POST', method)
      self.assertEqual(bq_state.bqh.INSERT_ROWS_SCOPE, scopes)
      self.assertEqual(600, deadline)
      return {'insertErrors': []}
    self.mock(bq_state.net, 'json_request', json_request)

    rows = [
        ('key1', struct_pb2.Struct()),
        ('key2', struct_pb2.Struct()),
    ]
    self.assertEqual(0, bq_state.send_to_bq('foo', rows))
    expected = [
      {
        'ignoreUnknownValues': False,
        'kind': 'bigquery#tableDataInsertAllRequest',
        'skipInvalidRows': True,
      },
    ]
    actual_rows = payloads[0].pop('rows')
    self.assertEqual(expected, payloads)
    self.assertEqual(2, len(actual_rows))

  def test_send_to_bq_fail(self):
    # Test the failure code path.
    payloads = []
    def json_request(url, method, payload, scopes, deadline):
      self.assertEqual(
          'https://www.googleapis.com/bigquery/v2/projects/sample-app/datasets/'
            'swarming/tables/foo/insertAll',
          url)
      first = not payloads
      payloads.append(payload)
      self.assertEqual('POST', method)
      self.assertEqual(bq_state.bqh.INSERT_ROWS_SCOPE, scopes)
      self.assertEqual(600, deadline)
      # Return an error on the first call.
      if first:
        return {
          'insertErrors': [
            {
              'index': 0,
              'errors': [
                {
                  'reason': 'sadness',
                  'message': 'Oh gosh',
                },
              ],
            },
          ],
        }
      return {'insertErrors': []}
    self.mock(bq_state.net, 'json_request', json_request)

    rows = [
        ('key1', struct_pb2.Struct()),
        ('key2', struct_pb2.Struct()),
    ]
    self.assertEqual(1, bq_state.send_to_bq('foo', rows))

    self.assertEqual(2, len(payloads), payloads)
    expected = {
      'ignoreUnknownValues': False,
      'kind': 'bigquery#tableDataInsertAllRequest',
      'skipInvalidRows': True,
    }
    actual_rows = payloads[0].pop('rows')
    self.assertEqual(expected, payloads[0])
    self.assertEqual(2, len(actual_rows))

    expected = {
      'ignoreUnknownValues': False,
      'kind': 'bigquery#tableDataInsertAllRequest',
      'skipInvalidRows': True,
    }
    actual_rows = payloads[1].pop('rows')
    self.assertEqual(expected, payloads[1])
    self.assertEqual(1, len(actual_rows))


if __name__ == '__main__':
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.ERROR)
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
