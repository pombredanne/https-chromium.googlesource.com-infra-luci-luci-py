#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

# pylint: disable=missing-docstring
# pylint: disable=import-error
# pylint: disable=invalid-name

import errno
import os
import shutil
import sys
import tempfile
import unittest

# Mutates sys.path.
import test_env

from utils import tools


class FindExecutableTest(unittest.TestCase):
  def setUp(self):
    super(FindExecutableTest, self).setUp()
    self._orig_platform = sys.platform
    self._orig_cwd = os.getcwd()

    self.PATH = []
    self.playground = os.path.realpath(os.path.abspath(tempfile.mkdtemp()))

    # mocks so that both win and non-win tests can run on all platforms
    os.chdir(self.playground)
    if sys.platform == 'win32':
      self._orig_access = os.access
      self._executables = set()
      os.access = lambda path, _: path in self._executables
    sys.platform = 'win32' if 'win' in self.id() else 'posix'

    # initial
    self._touch_exe('SYSTEM', 'python')
    self._touch_exe('SYSTEM', 'python.exe')
    self._add_PATH('SYSTEM')

  def tearDown(self):
    super(FindExecutableTest, self).tearDown()

    # restore mocks
    sys.platform = self._orig_platform
    if sys.platform == 'win32':
      os.access = self._orig_access
    os.chdir(self._orig_cwd)

    if sys.platform != 'win32':
      for dirpath, dirnames, filenames in os.walk(self.playground):
        for itm in dirnames + filenames:
          os.chmod(os.path.join(dirpath, itm), 0777)

    shutil.rmtree(self.playground)

  def _add_PATH(self, *path_toks):
    self.PATH.append(self._abs(*path_toks))

  def _abs(self, *path_toks):
    return os.path.abspath(os.path.join(self.playground, *path_toks))

  def _touch(self, *path_toks):
    if len(path_toks) > 1:
      try:
        os.makedirs(self._abs(*path_toks[:-1]))
      except OSError as ex:
        if ex.errno != errno.EEXIST:
          raise

    full = self._abs(*path_toks)
    with open(full, 'w') as f:
      f.write('hi')

    return full

  def _touch_exe(self, *path_toks):
    full = self._touch(*path_toks)
    if self._orig_platform == 'win32':
      self._executables.add(full)
    else:
      os.chmod(full, 0777)
    return full

  def _fe(self, cmd, implicit_cwd_in_path=True):
    return tools.find_executable(
        list(cmd), implicit_cwd_in_path=implicit_cwd_in_path,
        env={'PATH': os.pathsep.join(self.PATH)})

  def test_add_python(self):
    cmd = ['not_a_real_path.py']
    self.assertItemsEqual([self._abs('SYSTEM', 'python')] + cmd,
                          self._fe(cmd))

  def test_win_add_python(self):
    cmd = ['not_a_real_path.py']
    self.assertItemsEqual([self._abs('SYSTEM', 'python.exe')] + cmd,
                          self._fe(cmd))

  def test_missing_passthrough(self):
    cmd = ['not_a_real_path']
    self.assertItemsEqual(cmd, self._fe(cmd))

  def test_missing_abs_passthrough(self):
    cmd = [self._abs('not', 'real')]
    self.assertItemsEqual(cmd, self._fe(cmd))

  @unittest.skipIf(sys.platform == 'win32', 'posix only')
  def test_bad_permissions(self):
    cmd = ['config_file']
    os.chmod(self._touch('something', 'dir', 'config_file'), 0)
    os.chmod(self._abs('something', 'dir'), 0)
    self._add_PATH('something', 'dir')
    self.assertItemsEqual(cmd, self._fe(cmd))

  def test_win_implicit_extension(self):
    self._touch_exe('SYSTEM', 'hello.bat')
    self.assertItemsEqual([self._abs('SYSTEM', 'hello.bat')],
                          self._fe(['hello']))

  def test_implicit_cwd(self):
    self._touch_exe('python')
    self.assertItemsEqual([self._abs('python')], self._fe(['python']))

  def test_win_implicit_cwd(self):
    self._touch_exe('python.bat')
    self.assertItemsEqual([self._abs('python.bat')], self._fe(['python']))

  def test_non_implicit_cwd(self):
    self._touch_exe('python')
    self.assertItemsEqual([self._abs('SYSTEM', 'python')],
                          self._fe(['python'], implicit_cwd_in_path=False))

  def test_win_non_implicit_cwd(self):
    self._touch_exe('python.exe')
    self.assertItemsEqual([self._abs('SYSTEM', 'python.exe')],
                          self._fe(['python'], implicit_cwd_in_path=False))

  def test_non_implicit_cwd_skip_empty(self):
    self.PATH.insert(0, '')
    self._touch_exe('python')
    self.assertItemsEqual([self._abs('SYSTEM', 'python')],
                          self._fe(['python'], implicit_cwd_in_path=False))

  def test_explicit_relative(self):
    self._touch_exe('python')
    self.assertItemsEqual([self._abs('python')],
                          self._fe(['./python'], implicit_cwd_in_path=False))

  def test_explicit_relative_missing(self):
    self.assertItemsEqual(['./not_real'],
                          self._fe(['./not_real'], implicit_cwd_in_path=False))

if __name__ == '__main__':
  test_env.main()
