#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import sys
import os
import subprocess

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def run_smoketest():
  if python3:
    print('Skipping running smoke test in Python3')
    return 0

  cmd = os.path.join(ROOT_DIR, 'local_smoke_test.py')
  print('Running smoke test: %r' % cmd)
  return subprocess.call(cmd)


def main():
  exit_code = 0

  for py3 in [False, True]:
    # smoke test
    exit_code = run_smoketest(py3) or exit_code

  return exit_code


if __name__ == '__main__':
  sys.exit(main())
