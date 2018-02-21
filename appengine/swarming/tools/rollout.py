#!/usr/bin/env python
# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Rolls out new versions safely to AppEngine."""

import argparse
import json
import os
import subprocess
import sys
import time


HERE = os.path.dirname(__file__)

parser = argparse.ArgumentParser()
parser.add_argument('-A', '--application', default='chromium-swarm-dev')
parser.add_argument('-S', '--services',
                    default=('default', 'backend'),
                    nargs='+')
parser.add_argument('--canary-percentage', default=10, type=int)
parser.add_argument('--canary-seconds', default=5 * 60, type=int)
parser.add_argument('--health-check-tool',
                    default=os.path.join(HERE, 'health_check'))
parser.add_argument('--rollback', default=False, action='store_true')
parser.add_argument('version', nargs='?')


MAX_CANARY_PERCENTAGE = 50
assert MAX_CANARY_PERCENTAGE <= 50, \
    'infer_rollout_state_from_splits will not work'


class InvalidStateError(ValueError):
  """
  Error representing when the state is in an invalid state for the
  automation to act on.

  This should result in the automation taking no action, or alerting a human to
  fix the state.
  """
  pass


def sleep(total_seconds, max_sleep_seconds=1):
  """Reliably sleep for a period of time.

  Args:
    total_seconds: The number of seconds to sleep.
    max_sleep_seconds: Maximum time to call time.sleep() with.

  Yields:
    a float indicating approximate progress through the sleep
  """
  start = time.time()
  end = start + total_seconds
  while True:
    now = time.time() - start
    delta = total_seconds - now
    if delta <= 0:
      break
    yield now / float(total_seconds)
    time.sleep(min(max_sleep_seconds, delta))
  yield 1.0


def draw_progress_bar(fraction, f=sys.stderr):
  _, columns = subprocess.check_output(['stty', 'size']).split()
  columns = int(columns)
  if columns < 2:
    return
  columns -= 2

  n = int(columns * fraction)
  bar = '[' + '*' * n + '.' * (columns - n) + ']'

  clear = '\x1b[G'
  f.write(clear + bar)
  f.flush()


def get_traffic_split(application, service):
  output = subprocess.check_output([
      'gcloud',
      '--project=' + application,
      'app', 'services', 'describe', service,
      '--format=json',
  ])
  desc = json.loads(output)
  return desc['split']


def set_traffic_splits(application, services, split):
  subprocess.check_call([
      'gcloud',
      '--quiet',
      '--project=' + application,
      'app', 'services', 'set-traffic',
      '--splits=' + split,
      '--split-by=cookie',
  ] + list(services))


def infer_rollout_state_from_splits(splits_by_service):
  """
  Given traffic splits for the application's services, figure out what state
  the rollout is in.

  Args:
    splits_by_service: Dictionary mapping services to their traffic splits.

  Returns:
    A tuple of (current_version, new_version).
    If there is not currently a rollout in progress, new_version will be None.

  Raises:
    InvalidStateError: The traffic splits are not in an expected state.
  """
  unallocated_versions = set()
  unallocated_services = []

  versions = None
  previous_split_services = []

  for service, split in splits_by_service.iteritems():
    allocations = split['allocations']

    if len(allocations) == 1:
      # Add this version to a set of versions we'll figure out later.
      unallocated_versions.update(allocations)
      unallocated_services.append(service)

    elif len(allocations) == 2:
      # Sort the versions by the amount of traffic they serve.
      expected_versions = tuple(sorted(allocations,
                                       key=lambda k: (allocations[k], k),
                                       reverse=True))

      # If we haven't seen a traffic split before, use this one.
      if versions is None:
        versions = expected_versions
      # If we have, the split should have the same versions.
      elif versions != expected_versions:
        raise InvalidStateError(
            'Service %s conflicts with traffic splits on services %s: '
            'expected %s, got %s' %
            (service, previous_split_services, versions, expected_versions))

      previous_split_services.append(service)

    else:
      raise InvalidStateError(
          'Traffic to service %s is split in an unexpected way: %s' %
          (service, split))

  if len(unallocated_versions) > 2:
    raise InvalidStateError(
        'Too many differing versions in services %s: %s' %
        (unallocated_services, unallocated_versions))

  # There are no traffic splits, so figure out the state just from
  # unallocated_versions.
  if versions is None:
    # If there are no versions, then uhhh, we didn't find anything.
    if not unallocated_versions:
      raise InvalidStateError('No versions found?')

    unallocated_versions = tuple(sorted(unallocated_versions))

    # If there's just one, it's easy.
    if len(unallocated_versions) == 1:
      return unallocated_versions[0], None
    # If there are two, then assume lexicographical ordering for the rollout.
    assert type(unallocated_versions) is tuple
    assert len(unallocated_versions) == 2
    return unallocated_versions

  # There was a traffic split, so we should only see versions from that split.
  unexpected_versions = unallocated_versions - set(versions)
  if unexpected_versions:
    raise InvalidStateError(
        'Services %s had unexpected versions: expected %s, got %s' %
        (unallocated_services, versions, unexpected_versions))

  return versions


def get_inferred_rollout_state(application, services):
  # TODO(flowblok): parallelise this
  splits_by_service = {
      service: get_traffic_split(application, service)
      for service in services
  }
  return infer_rollout_state_from_splits(splits_by_service)


def check_health(version, args):
  rv = subprocess.call([
      args.health_check_tool,
      args.application,
      version,
  ])
  return rv == 0

def rollforward(version, args):
  if not 0 <= args.canary_percentage < MAX_CANARY_PERCENTAGE:
    raise InvalidStateError(
        '--canary-percentage must be < %s' % MAX_CANARY_PERCENTAGE)

  # Figure out what the current / new versions are.
  current_version, new_version = get_inferred_rollout_state(args.application,
                                                            args.services)

  if new_version is not None and new_version != version:
    # Nope, not doing that.
    raise InvalidStateError(
        'Already rolling out %s, refusing to roll out %s.' %
        (new_version, version))

  # Rename some variables so below is more readable.
  new_version = version
  del version

  # Canary a fraction of the traffic on the new version.
  canary = args.canary_percentage
  non_canary = 100 - canary
  split = '{current_version}={non_canary},{new_version}={canary}'.format(
      **locals())
  set_traffic_splits(args.application, args.services, split)

  # Start measuring the canary soak time from now.
  canary_soak_sleep = sleep(args.canary_seconds)
  next(canary_soak_sleep)

  if not check_health(new_version, args):
    print 'Failed health check, rolling back.'
    return rollback(args, current_version)

  print 'Waiting for canary to soak...'
  for progress in canary_soak_sleep:
    draw_progress_bar(progress)

  # Make the new version default.
  split = '{new_version}=1'.format(**locals())
  set_traffic_splits(args.application, args.services, split)


def rollback(args, version=None):
  if version is None:
    # Figure out what the current / new versions are.
    current_version, new_version = get_inferred_rollout_state(args.application,
                                                              args.services)
    if new_version is None:
      # There's no rollout in progress, nothing to do.
      return
    version = current_version

  # Roll back to the current version.
  split = '{version}=1'.format(**locals())
  set_traffic_splits(args.application, args.services, split)


def main():
  args = parser.parse_args()

  if args.version is not None:
    if args.rollback:
      print >> sys.stderr, 'Cannot specify both version and --rollback.'
      return 1
    rollforward(args.version, args=args)

  else:
    if not args.rollback:
      print >> sys.stderr, 'Neither version nor --rollback was specified.'
      return 1
    rollback(args=args)

  return 0


if __name__ == '__main__':
  sys.exit(main())
