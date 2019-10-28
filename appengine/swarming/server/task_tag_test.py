#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import os
import sys
import unittest

import test_env
test_env.setup_test_env()

from google.appengine.api import datastore_errors

from server import task_tag
from test_support import test_case


class TaskTagApiTest(test_case.TestCase):

  def test_all_apis_are_tested(self):
    # Ensures there's a test for each public API.
    module = task_tag
    expected = frozenset(
        i for i in dir(module)
        if i[0] != '_' and hasattr(getattr(module, i), 'func_name'))
    missing = expected - frozenset(
        i[5:] for i in dir(self) if i.startswith('test_'))
    self.assertFalse(missing)

  def test_add_label_value(self):
    task_tag.add_label_value('foo', 'bar').get_result()
    task_tag.add_label_value('a' * 500, 'bar').get_result()
    task_tag.add_label_value('foo', 'a' * 500).get_result()

    with self.assertRaises(ValueError):
      task_tag.add_label_value('', 'bar').get_result()
    with self.assertRaises(ValueError):
      task_tag.add_label_value('a' * 501, 'bar').get_result()

    with self.assertRaises(ValueError):
      task_tag.add_label_value('foo', '').get_result()
    with self.assertRaises(ValueError):
      task_tag.add_label_value('foo', 'a' * 501).get_result()

  def test_yield_labels(self):
    task_tag.add_label_value('foo', '1').get_result()
    task_tag.add_label_value('bar', '2').get_result()
    task_tag.add_label_value('third key', '3 foo').get_result()
    self.assertEqual(['bar', 'foo', 'third key'], list(task_tag.yield_labels()))

  def test_yield_label_values(self):
    task_tag.add_label_value('foo', '1').get_result()
    task_tag.add_label_value('foo', '2').get_result()
    task_tag.add_label_value('foo', '3 foo').get_result()
    task_tag.add_label_value('bar', 'other').get_result()
    self.assertEqual(['1', '2', '3 foo'],
                     list(task_tag.yield_label_values('foo')))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.ERROR)
  unittest.main()
