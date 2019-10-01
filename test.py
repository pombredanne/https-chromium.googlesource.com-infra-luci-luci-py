#!/usr/bin/env python3
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Utility script to run python testsled description of test"""

import os
import subprocess
import sys

LUCI_ROOT = os.path.dirname(os.path.abspath(__file__))

INFRA_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COMMANDS = ('list', 'train', 'test', 'debug')

WIN_ENABLED_PACKAGES = []


def usage(argv):
  # TODO(jwata): update examples
  string = """Usage: %s <action> [<test names>] [<expect_tests options>]

  where <action> is one of: list, test, train, debug.

  Examples:
  Run all tests:
    ./test.py test
  Run all tests in the given package:
    ./test.py test infra
    ./test.py test appengine/cr-buildbucket
  Run all tests and generate an HTML report:
    ./test.py test infra --html-report /path/to/report/folder
  Run one given test in the infra package:
    ./test.py test infra/libs/git2/test:*testCommitBogus

  See expect_tests documentation for more details
  """ % argv[0]
  print(string)


def command_usage(command):
  args = get_executables() + [command, '--help']
  return subprocess.call(args)


def get_modules_with_coveragerc(root_module):
  """Returns submodules that have .coveragerc file present."""
  root_dir = os.path.join(LUCI_ROOT, root_module.replace('/', os.sep))
  if not os.path.isdir(root_dir):
    return []
  return [
      '%s/%s' % (root_module, d)
      for d in os.listdir(root_dir)
      if os.path.isfile(os.path.join(root_dir, d, '.coveragerc'))
  ]


def parse_argv(argv):
  if len(argv) == 1 or sys.argv[1] not in COMMANDS:
    usage(argv)
    sys.exit(1)

  command = sys.argv[1]
  args = sys.argv[2:]

  modules = []
  flags = []
  # BUG: this will append everything after the first flag to `flags`. Thus,
  # it fails to catch when (a) someone doesn't pass a directory after
  # "--html-report", nor (b) if they pass multiple directories after that
  # flag.
  for arg in args:
    if arg.startswith('-'):
      flags.append(arg)
      continue
    if flags:
      flags.append(arg)
    else:
      modules.append(arg)

  # Set up default list of packages/directories if none have been provided.
  if not modules:
    # On Windows, test only whitelisted modules.
    if sys.platform == 'win32':
      modules.extend([
          p for p in WIN_ENABLED_PACKAGES
          if os.path.isdir(os.path.join(LUCI_ROOT, p))
      ])
    else:
      modules.extend(['client'])
      modules.extend(get_modules_with_coveragerc('packages'))

    # Test shared GAE code and individual GAE apps only on 64-bit Posix. This
    # matches GAE environment. Skip this if running tests when testing
    # infra_python CIPD package integrity: the package doesn't have appengine
    # code in it.
    if os.path.isdir(os.path.join(LUCI_ROOT, 'appengine')):
      test_gae = sys.platform != 'win32' and sys.maxsize == (2**63) - 1
      if test_gae:
        modules.extend(get_modules_with_coveragerc('appengine'))

  return command, flags, modules


def get_executables():
  if sys.platform == 'win32':
    python = os.path.join(INFRA_ROOT, 'ENV', 'Scripts', 'python')
    expect_tests = os.path.join(INFRA_ROOT, 'ENV', 'Scripts', 'expect_tests')
  else:
    python = os.path.join(INFRA_ROOT, 'ENV', 'bin', 'python')
    expect_tests = os.path.join(INFRA_ROOT, 'ENV', 'bin', 'expect_tests')

  return [python, expect_tests]


def remove_orphaned_pycs():
  python = get_executables()[0]
  script = os.path.join(INFRA_ROOT, 'bootstrap', 'remove_orphaned_pycs.py')
  subprocess.check_call([python, script])


def run_command_all(command, flags, modules):
  exit_code = 0
  failed_modules = []
  for module in modules:
    _code = run_command(command, flags, module)
    if _code:
      failed_modules.append(module)
      exit_code = 1

  if exit_code:
    err_msg = '\nTests failed in modules:\n  %s' % '\n  '.join(failed_modules)
    print(err_msg)

    if '--html-report' not in flags:
      msg = """
  For detailed coverage report and per-line branch coverage,
  rerun with --html-report <dir>
      """
      print(msg)
  else:
    print('All tests passed.')

  return exit_code


def run_command(command, flags, module):
  print('Running %s...' % module)
  module_flags = flags[:]
  # Remove any test glob, which comes after semicolon (:) and convert to a path.
  module_path = module.split(':')[0].replace('/', os.sep)
  if not any(flag.startswith('--coveragerc') for flag in module_flags):
    module_coveragerc = os.path.join(INFRA_ROOT, module_path, '.coveragerc')
    module_flags.append('--coveragerc=%s' % module_coveragerc)
  if not any(flag.startswith('--html-report-subdir') for flag in module_flags):
    module_flags.append('--html-report-subdir=%s' % module_path)
  cmd = get_executables() + [command, module] + module_flags
  print(cmd)
  return subprocess.call(cmd)


def main(argv):
  command, flags, modules = parse_argv(sys.argv)

  if '--help' in flags or '-h' in flags:
    usage(argv)
    sys.exit(command_usage(command))

  remove_orphaned_pycs()

  sys.exit(run_command_all(command, flags, modules))


if __name__ == '__main__':
  main(sys.argv)
