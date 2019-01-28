#!/usr/bin/env python
# coding=utf-8
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import os
import tempfile
import unittest
import sys

BASE_DIR = os.path.dirname(os.path.abspath(
    __file__.decode(sys.getfilesystemencoding())))
ROOT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, 'third_party'))

FILE_PATH = os.path.abspath(__file__.decode(sys.getfilesystemencoding()))

from depot_tools import fix_encoding
from utils import file_path
from utils import fs


def write_content(filepath, content):
  with fs.open(filepath, 'wb') as f:
    f.write(content)


class FSTest(unittest.TestCase):
  def setUp(self):
    super(FSTest, self).setUp()
    self._tempdir = None

  def tearDown(self):
    try:
      if self._tempdir:
        file_path.rmtree(self._tempdir)
    finally:
      super(FSTest, self).tearDown()

  @property
  def tempdir(self):
    if not self._tempdir:
      self._tempdir = tempfile.mkdtemp(prefix=u'fs_test')
    return self._tempdir

  def test_symlink_relative(self):
    filepath = os.path.join(self.tempdir, 'file')
    dirpath = os.path.join(self.tempdir, 'dir')
    write_content(filepath, 'hello')
    os.mkdir(dirpath)

    linkfile = os.path.join(self.tempdir, 'lf')
    linkdir = os.path.join(self.tempdir, 'ld')
    fs.symlink('file', linkfile)
    fs.symlink('dir', linkdir)
    self.assertEqual('file', fs.readlink(linkfile))
    self.assertEqual('dir', fs.readlink(linkdir))

  def test_symlink_absolute(self):
    filepath = os.path.join(self.tempdir, 'file')
    dirpath = os.path.join(self.tempdir, 'dir')
    write_content(filepath, 'hello')
    os.mkdir(dirpath)

    linkfile = os.path.join(self.tempdir, 'lf')
    linkdir = os.path.join(self.tempdir, 'ld')
    fs.symlink(filepath, linkfile)
    fs.symlink(dirpath, linkdir)
    self.assertEqual(filepath, fs.readlink(linkfile))
    self.assertEqual(dirpath, fs.readlink(linkdir))


if __name__ == '__main__':
  fix_encoding.fix_encoding()
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.ERROR)
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
