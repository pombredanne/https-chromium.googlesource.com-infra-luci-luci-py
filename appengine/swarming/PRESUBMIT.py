# Copyright 2013 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Top-level presubmit script for swarming-server.

See http://dev.chromium.org/developers/how-tos/depottools/presubmit-scripts for
details on the presubmit API built into gclient.
"""


def CommonChecks(input_api, output_api):
  output = []
  def join(*args):
    return input_api.os_path.join(input_api.PresubmitLocalPath(), *args)

  black_list = list(input_api.DEFAULT_BLACK_LIST) + [
      r'ui2/node_modules/.*',
      r'ui2/nodejs/.*',
      r'.*_pb2\.py$',
      r'.*_pb2_grpc\.py$',
  ]
  disabled_warnings = [
    'relative-import',
  ]
  output.extend(input_api.canned_checks.RunPylint(
      input_api, output_api,
      black_list=black_list,
      disabled_warnings=disabled_warnings))

  test_directories = [
    input_api.PresubmitLocalPath(),
    join('server'),
    join('swarming_bot'),
    join('swarming_bot', 'api'),
    join('swarming_bot', 'api', 'platforms'),
    join('swarming_bot', 'bot_code'),
  ]

  blacklist = [
    # Never run the remote_smoke_test automatically. Should instead be run after
    # uploading a server instance.
    r'^remote_smoke_test\.py$'
  ]

  # adding python path to env
  swarming_root = input_api.PresubmitLocalPath()
  swarming_bot_path = input_api.os_path.join(swarming_root, 'swarming_bot')
  env = EnvAddingPythonPath(input_api, [swarming_bot_path])

  tests = []
  for directory in test_directories:
    tests.extend(
        input_api.canned_checks.GetUnitTestsInDirectory(
            input_api, output_api,
            directory,
            whitelist=[r'.+_test\.py$'],
            blacklist=blacklist,
            env=env))
  output.extend(input_api.RunTests(tests, parallel=True))
  return output


def EnvAddingPythonPath(input_api, extra_python_paths):
  # Copy the system path to the environment so pylint can find the right
  # imports.
  input_api.logging.debug(
      '  with extra PYTHONPATH: %r' % extra_python_paths)
  env = input_api.environ.copy()
  import sys
  env['PYTHONPATH'] = input_api.os_path.pathsep.join(
      extra_python_paths + sys.path).encode('utf8')
  return env


# pylint: disable=unused-argument
def CheckChangeOnUpload(input_api, output_api):
  return []


def CheckChangeOnCommit(input_api, output_api):
  return CommonChecks(input_api, output_api)
