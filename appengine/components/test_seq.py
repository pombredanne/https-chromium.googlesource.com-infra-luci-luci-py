#!/usr/bin/env vpython
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import os
import subprocess
import sys

import six

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_test(test_file, python3=False):
  if python3 and not _has_py3_shebang(test_file):
    print('Skipping test in python3: %s' % test_file)
    return 0, True

  # vpython
  vpython = 'vpython'
  if python3:
    vpython += '3'

  cmd = [vpython, os.path.join(ROOT_DIR, test_file), '-v']

  print('Running test script: %r' % cmd)
  return subprocess.call(cmd), False


def _has_py3_shebang(path):
  with open(path, 'r') as f:
    maybe_shebang = f.readline()
  return maybe_shebang.startswith('#!') and 'python3' in maybe_shebang


def main():
  # These tests need to run as executable
  # because they don't pass when running in parallel
  # or run via test runner
  test_files = [
      'components/auth/delegation_test.py',
      'components/auth/project_tokens_test.py',
      'components/endpoints_webapp2/discovery_test.py',
  ]

  run_cnt = 0
  skipped_tests = []
  failed_tests = []
  for test_file in test_files:
    _exit_code, skipped = run_test(test_file, python3=six.PY3)
    if skipped:
      skipped_tests.append(test_file)
      continue

    if _exit_code:
      failed_tests.append(test_file)

    run_cnt += 1

  print('\n-------------------------------------------------------------------')
  print('Ran %d test files, Skipped %d test files' % (run_cnt,
                                                      len(skipped_tests)))

  if len(skipped_tests) > 0:
    print('\nSkipped tests:')
    for t in skipped_tests:
      print(' - %s' % t)

  if len(failed_tests) > 0:
    print('\nFailed tests:')
    for t in failed_tests:
      print(' - %s' % t)
    print('\nFAILED')
    return 1

  print('\nOK')
  return 0


if __name__ == '__main__':
  sys.exit(main())
