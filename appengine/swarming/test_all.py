#!/usr/bin/env python

import sys
import os
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_unittests(start_dir, attrs, python3):
  # vpython
  vpython = 'vpython'
  if python3:
    vpython += '3'

  # test.py
  testpy = os.path.join(ROOT_DIR, 'test.py')

  # filtering attributes
  if not attrs:
    attrs = ['!no_run']
  else:
    attrs.append('!no_run')
  attrs_opt = ','.join(attrs)

  cmd = [vpython, testpy, '-v', '-A', attrs_opt, '-s', start_dir]

  if python3:
    cmd.append('--python3')

  print('Running test script: %r' % cmd)
  return subprocess.call(cmd)


def run_smoketest(python3=False):
  if python3:
    print('Skipping running smoke test in Python3')
    return 0

  cmd = os.path.join(ROOT_DIR, 'local_smoke_test.py')
  print('Running smoke test: %r' % cmd)
  return subprocess.call(cmd)


def main():
  exit_code = 0

  start_dirs = ['.', './swarming_bot']

  for py3 in [False, True]:
    # unittests
    for start_dir in start_dirs:
      s_dir = os.path.join(ROOT_DIR, start_dir)
      exit_code = run_unittests(s_dir, ['!run_later'], py3) or exit_code
      exit_code = run_unittests(s_dir, ['run_later'], py3) or exit_code

    # smoke test
    exit_code = run_smoketest(py3) or exit_code

  return exit_code

if __name__ == '__main__':
  sys.exit(main())
