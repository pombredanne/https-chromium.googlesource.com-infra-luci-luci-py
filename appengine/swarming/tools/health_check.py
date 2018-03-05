#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Check the health of a Swarming version."""

import argparse
import collections
import functools
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(__file__)
SWARMING_TOOL = os.path.join(HERE, '..', '..', '..', 'client', 'swarming.py')


def retry_exception(exc_type, max_attempts, delay):
  def deco(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
      for _ in range(max_attempts):
        try:
          return fn(*args, **kwargs)
        except exc_type:
          time.sleep(delay)
    return wrapper
  return deco


@retry_exception(ValueError, 1, 10)
def pick_best_pool(url, server_version):
  """Pick the best pool to run the health check task on.

  Asks the specified swarming server for a list of all bots, filters those
  running the specified server version, and returns the pool with the most bots
  in it.

  Args:
    url: The swarming server to query.
    server_version: Which server version to filter bots by.

  Returns:
    A string indicating the best pool to run the health check task on.
  """
  # The output of this command looks like:
  #   bot-name
  #     {"dimension": ["value", ...], ...}
  #     task: ...
  # but the last line is optional.
  output = subprocess.check_output([
      SWARMING_TOOL, 'bots',
      '-S', url,
  ])

  pool_counts = collections.Counter()
  previous_line_was_bot_name = False
  for line in output.split('\n'):
    if previous_line_was_bot_name:
      dimensions = json.loads(line)
      if server_version in dimensions.get('server_version', []):
        pool_counts.update(dimensions.get('pool', []))
    previous_line_was_bot_name = not line.startswith(' ')

  if not pool_counts:
    raise ValueError('No bots are running server_version=%s' % server_version)

  return pool_counts.most_common(1)[0][0]


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('application')
  parser.add_argument('server_version')
  args = parser.parse_args()

  url = 'https://{server_version}-dot-{application}.appspot.com'.format(
      application=args.application,
      server_version=args.server_version)
  print 'Swarming server:', url

  print 'Finding best pool to use'
  pool = pick_best_pool(url, args.server_version)

  print 'Scheduling no-op task'
  rv = subprocess.call([
      SWARMING_TOOL, 'run',
      '-S', url,
      '--expiration', '120',
      '--hard-timeout', '120',
      '-d', 'pool', pool,
      '-d', 'server_version', args.server_version,
      '--raw-cmd', '--', 'python', '-c', 'pass'])
  if rv != 0:
    print>>sys.stderr, 'Failed to run no-op task'
    return 2
  return 0


if __name__ == '__main__':
  sys.exit(main())
