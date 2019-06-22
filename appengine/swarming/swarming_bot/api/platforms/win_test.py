#!/usr/bin/env python
# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import re
import sys
import unittest

import test_env_platforms
test_env_platforms.setup_test_env()

import win


class TestWin(unittest.TestCase):
  def test_from_cygwin_path(self):
    data = [
      ('foo', None),
      ('x:\\foo$', None),
      ('X:\\foo$', None),
      ('/cygdrive/x/foo$', 'x:\\foo$'),
    ]
    for i, (inputs, expected) in enumerate(data):
      actual = win.from_cygwin_path(inputs)
      self.assertEqual(expected, actual, (inputs, expected, actual, i))

  def test_to_cygwin_path(self):
    data = [
      ('foo', None),
      ('x:\\foo$', '/cygdrive/x/foo$'),
      ('X:\\foo$', '/cygdrive/x/foo$'),
      ('/cygdrive/x/foo$', None),
    ]
    for i, (inputs, expected) in enumerate(data):
      actual = win.to_cygwin_path(inputs)
      self.assertEqual(expected, actual, (inputs, expected, actual, i))

  def test_get_os_version_names(self):
    if sys.platform == 'win32':
      names = win.get_os_version_names()
      expected_len = 3 # names has 3 items for versions before 10/Server 2016.
      if len(names) >= 2:
        # The second item should be a raw version number.
        m = re.match(names[1], '^[0-9.]$')
        self.assertTrue(m)
        # If Windows 10/Server 2016 or later, expect four items.
        if names[1].split(u'.')[0] == u'10':
          expected_len = 4
      self.assertEqual(expected_len, len(names))
      self.assertTrue(isinstance(name, unicode) for name in names)

  def test_list_top_windows(self):
    if sys.platform == 'win32':
      win.list_top_windows()

  def test_version(self):
    m = re.search(
        win._CMD_RE, 'Microsoft Windows [version 10.0.15063]', re.IGNORECASE)
    self.assertEqual(('10.0', '15063'), m.groups())
    m = re.search(
        win._CMD_RE, 'Microsoft Windows [version 10.0.16299.19]', re.IGNORECASE)
    self.assertEqual(('10.0', '16299.19'), m.groups())


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
