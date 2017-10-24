#!/usr/bin/env python
# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Triggers a task that can be used to debug another task."""

import argparse
import json
import os
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def collect(swarming, taskid):
  cmd = [
      sys.executable, 'swarming.py', 'query', '-S', swarming,
      'task/%s/request' % taskid,
  ]
  try:
    return json.loads(subprocess.check_output(cmd, cwd=ROOT_DIR))
  except subprocess.CalledProcessError:
    print >> sys.stderr, (
        'Are you sure the task ID and swarming server is valid?')
    sys.exit(1)


def convert_to_debug(task):
  # TODO(maruel): Fetch isolated, extract command, embed in script here:
  original = get_swarming_args_from_task(task)
  task['command'] = ['python', '-c', 'print \'hello world\'']
  task.pop('extra_args', None)


def get_swarming_args_from_task(task):
  """Extracts the original command from a task."""
  args = []
  return args


def trigger(swarming, task):
  cmd = [
    sys.executable, 'swarming.py', 'trigger', '-S', swarming,
    '-S', swarming,
    '--hard-timeout', str(10*60), '--task-name', 'Debug',
    '--raw-cmd',
    '-s', task['properties']['inputs_ref']['isolated'],
    '-I',  task['properties']['inputs_ref']['isolatedserver'],
    '--namespace',  task['properties']['inputs_ref']['namespace'],
    #'--cipd-package',
    #'--named-cache',
  ]
  for i in task['properties']['dimensions']:
    cmd.extend(('-d', i['key'], i['value']))
  for i in task['properties'].get('env', []):
    cmd.extend(('--env', i['key'], i['value']))
  cmd.append('--')
  cmd.extend(task['command'])
  try:
    return subprocess.call(cmd, cwd=ROOT_DIR)
  except KeyboardInterrupt:
    return 0


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('taskid')
  parser.add_argument(
        '-S', '--swarming',
        metavar='URL', default=os.environ.get('SWARMING_SERVER', ''),
        help='Swarming server to use')
  args = parser.parse_args()

  task = collect(args.swarming, args.taskid)
  convert_to_debug(task)
  trigger(args.swarming, task)
  return 0


if __name__ == '__main__':
  sys.exit(main())
