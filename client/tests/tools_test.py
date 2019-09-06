#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

# pylint: disable=missing-docstring
# pylint: disable=import-error
# pylint: disable=invalid-name

import os
import sys
import tempfile
import unittest
import ntpath
import posixpath

# Mutates sys.path.
import test_env

# third_party/
from depot_tools import auto_stub

from utils import file_path
from utils import tools


# _ACTUALLY_WINDOWS captures the windows-ness of the current platform, even
# though we mock sys.platform in the tests.
_SEP = os.path.sep
_JOIN = os.path.join
_ABSPATH = os.path.abspath

_ACTUALLY_WINDOWS = sys.platform == 'win32'


class FindExecutableTest(auto_stub.TestCase):
  """This tests the tools.find_executable function.

  All test cases and helper functions are written so that they can operate (with
  few exceptions) on all platforms that run the test. Tests which test the
  Windows behavior of find_executable must include the string "WIN" in their
  test function name.
  """

  def setUp(self):
    super(FindExecutableTest, self).setUp()
    self._orig_cwd = os.getcwd()

    self.PATH = []
    self.playground = os.path.realpath(tempfile.mkdtemp('tools_test-'))

    os.chdir(self.playground)


    is_win_test = 'WIN' in self.id()
    cross = (
      (is_win_test and not _ACTUALLY_WINDOWS) or
      (not is_win_test and _ACTUALLY_WINDOWS)
    )

    if cross:
      cross_altsep = '/' if _SEP == '\\' else '\\'
      _to_native = lambda path: path.replace(cross_altsep, _SEP)
      _to_cross = lambda path: path.replace(_SEP, cross_altsep)
    else:
      _to_native = lambda path: path
      _to_cross = lambda path: path

    self._to_cross = _to_cross

    _isfile = os.path.isfile
    self.mock(os.path, 'isfile',
              lambda path: _isfile(_to_native(path)))

    if is_win_test:
      self.mock(sys, 'platform', 'win32')
      self.mock(os.path, 'sep', '\\')
      self.mock(os.path, 'altsep', '/')
      self.mock(os.path, 'join', ntpath.join)
      self.mock(os.path, 'abspath', ntpath.abspath)
    else:
      self.mock(sys, 'platform', 'linux2')
      self.mock(os.path, 'sep', '/')
      self.mock(os.path, 'altsep', None)
      self.mock(os.path, 'join', posixpath.join)
      self.mock(os.path, 'abspath', posixpath.abspath)

    # mock os.access on windows so that the non-WIN tests correctly pass
    # os.access(..., X_OK) for just the files we mark with _touch_exe.
    if _ACTUALLY_WINDOWS:
      _executables = set()
      self.mock(os, "access", lambda path, _: path in _executables)
      self._mark_executable = _executables.add
    else:
      self._mark_executable = lambda path: os.chmod(path, 0777)
      _access = os.access
      self.mock(os, 'access',
                lambda path, mode: _access(_to_native(path), mode))

    # initial
    self._touch_exe('SYSTEM', 'python')
    self._touch_exe('SYSTEM', 'python.exe')
    self._add_PATH_abs('SYSTEM')

  def tearDown(self):
    super(FindExecutableTest, self).tearDown()

    # restore cwd
    os.chdir(self._orig_cwd)

    file_path.rmtree(self.playground)

  def _add_PATH_abs(self, *path_toks):
    self.PATH.append(self._abs(*path_toks))

  def _abs(self, *path_toks):
    return _ABSPATH(_JOIN(self.playground, *path_toks))

  def _touch(self, *path_toks):
    full = self._abs(*path_toks)
    d = os.path.dirname(full)
    if not os.path.isdir(d):
      os.makedirs(d)

    with open(full, 'w') as f:
      f.write('hi')

    return full

  def _touch_exe(self, *path_toks):
    full = self._touch(*path_toks)
    self._mark_executable(full)
    return full

  def _fe(self, cmd):
    return tools.find_executable(cmd, env={'PATH': os.pathsep.join(self.PATH)})

  def _assertCrossEqual(self, lhs, rhs):
    self.assertEqual(map(self._to_cross, lhs), rhs)

  def test_add_python(self):
    cmd = ['not_a_real_path.py']
    self._assertCrossEqual([self._abs('SYSTEM', 'python')] + cmd,
                          self._fe(cmd))

  def test_WIN_add_python(self):
    cmd = ['not_a_real_path.py']
    self._assertCrossEqual([self._abs('SYSTEM', 'python.exe')] + cmd,
                          self._fe(cmd))

  def test_missing_passthrough(self):
    cmd = ['not_a_real_path']
    self._assertCrossEqual(cmd, self._fe(cmd))

  def test_missing_abs_passthrough(self):
    cmd = [self._abs('not', 'real')]
    self._assertCrossEqual(cmd, self._fe(cmd))

  @unittest.skipIf(sys.platform == 'win32', 'posix only')
  def test_bad_permissions(self):
    cmd = ['config_file']
    os.chmod(self._touch('something', 'dir', 'config_file'), 0)
    os.chmod(self._abs('something', 'dir'), 0)
    self._add_PATH_abs('something', 'dir')
    self._assertCrossEqual(cmd, self._fe(cmd))

  def test_WIN_implicit_extension(self):
    self._assertCrossEqual([self._touch_exe('SYSTEM', 'hello.bat')],
                          self._fe(['hello']))

  def test_implicit_cwd(self):
    self._assertCrossEqual([self._touch_exe('python')],
                          self._fe(['python']))

  def test_WIN_implicit_cwd(self):
    self._assertCrossEqual([self._touch_exe('python.bat')],
                          self._fe(['python']))

  def test_relative_PATH_entry(self):
    self.PATH.insert(0, 'LOCAL')
    self._assertCrossEqual([self._touch_exe('LOCAL', 'thingy')],
                          self._fe(['thingy']))

  def test_skip_empty(self):
    self.PATH.insert(0, '')
    self._assertCrossEqual([self._abs('SYSTEM', 'python')], self._fe(['python']))

  def test_explicit_relative(self):
    self._assertCrossEqual([self._touch_exe('python')], self._fe(['./python']))

  def test_WIN_explicit_relative(self):
    self._assertCrossEqual([self._touch_exe('python.exe')], self._fe(['./python']))

  def test_explicit_relative_missing(self):
    self._assertCrossEqual(['./not_real'], self._fe(['./not_real']))


if __name__ == '__main__':
  test_env.main()
