#!/usr/bin/env vpython
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import os
import sys

import six

from test_support import parallel_test_runner, sequential_test_runner

SWARMING_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
  return run_tests_parralel() or run_tests_sequential()


def run_tests_parralel():
  # TODO(jwata): delete this adhoc path insertion
  # after fixing swarming_test_env.setup_test_env
  if six.PY2:
    import swarming_test_env
    swarming_test_env.setup_test_env()

  # append attribute filter option "--attribute '!no_run'"
  # https://nose2.readthedocs.io/en/latest/plugins/attrib.html
  sys.argv.extend(['--attribute', '!no_run'])

  # execute test runner
  return parallel_test_runner.run_tests(python3=six.PY3)


def run_tests_sequential():
  # These tests need to be run as executable
  # because they don't pass when running in parallel
  # or run via test runner
  abs_path = lambda f: os.path.join(SWARMING_DIR, f)
  test_cmds = [
      # TODO(crbug.com/10569967)
      # handlers_bot_test.py failing with unknown bot_id errors
      [abs_path('handlers_bot_test.py')],
      [abs_path('handlers_backend_test.py')],
      [abs_path('handlers_endpoints_test.py')],
      [abs_path('handlers_prpc_test.py')],
      [abs_path('server/bot_groups_config_test.py')],
      [abs_path('server/resultdb_test.py')],
      [abs_path('local_smoke_test.py')],
  ]

  # execute test runner
  return sequential_test_runner.run_tests(test_cmds, python3=six.PY3)


if __name__ == '__main__':
  sys.exit(main())
