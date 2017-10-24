#!/usr/bin/env python
# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Triggers a task that can be used to debug another task."""

import argparse
import os
import sys


def collect(swarming, taskid):
  return {}


def mutate(task):
  pass


def trigger(task):
  try:
    pass
  except KeyboardInterrupt:
    pass


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('taskid')
  parser.add_argument(
        '-S', '--swarming',
        metavar='URL', default=os.environ.get('SWARMING_SERVER', ''),
        help='Swarming server to use')
  args = parser.parse_args()

  task = collect(args.swarming, args.taskid)
  mutate(task)
  trigger(task)
  return 0


if __name__ == '__main__':
  sys.exit(main())
