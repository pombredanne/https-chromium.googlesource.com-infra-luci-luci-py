#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import os
import sys
import time
import unittest

import rollout

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENT_DIR = os.path.join(os.path.dirname(os.path.dirname(APP_DIR)), 'client')
sys.path.insert(0, CLIENT_DIR)

from third_party.depot_tools import auto_stub


class RolloutSleepTest(auto_stub.TestCase):
  def setUp(self):
    super(RolloutSleepTest, self).setUp()
    self.sleeps = []
    self.mock(time, 'sleep', self.sleeps.append)
    self.mock(time, 'time', self.time_time)

  def time_time(self):
    # start at some arbitrary point in time
    now = 0x123456789
    # add the time slept
    for i, seconds in enumerate(self.sleeps):
      now += seconds
      # and some forwards and backwards jitter
      now += i * 0.001 * (-1) ** i
    return now

  def round_numbers(self, items, ndigits):
    return [round(n, ndigits) for n in items]

  def test_sleep_zero_seconds(self):
    progress = list(rollout.sleep(0))
    self.assertEqual([], self.sleeps)
    self.assertListEqual([1.0], progress)

  def test_sleep_point_five_seconds(self):
    progress = list(rollout.sleep(0.5))
    self.assertEqual([0.5], self.round_numbers(self.sleeps, 4))
    self.assertListEqual([0.0, 1.0], self.round_numbers(progress, 4))

  def test_sleep_two_point_six_seconds(self):
    progress = list(rollout.sleep(2.6))
    self.assertEqual([1, 1, 0.601], self.round_numbers(self.sleeps, 4))
    self.assertListEqual([0.0, 0.3846, 0.7688, 1.0],
                         self.round_numbers(progress, 4))

  def test_sleep_five_seconds(self):
    progress = []
    s = rollout.sleep(5)

    # the initial iteration doesn't sleep
    progress.append(next(s))
    self.assertEqual([], self.sleeps)

    # sleep a second
    progress.append(next(s))
    self.assertEqual([1], self.sleeps)

    # finish the sleep
    progress.extend(s)
    self.assertEqual([1, 1, 1, 1, 1], self.sleeps)
    self.assertListEqual([0.0, 0.2, 0.3998, 0.6002, 0.7996, 1.0],
                         self.round_numbers(progress, 4))


class RolloutTest(unittest.TestCase):
  def setUp(self):
    super(RolloutTest, self).setUp()

  def test_infer_rollout_state_from_splits(self):
    self.longMessage = True

    tests = [
        {
            'name': 'two stable versions',
            'splits_by_service': {
                'aaa': {'allocations': {'1000-foo': 1}},
                'bbb': {'allocations': {'1000-foo': 1}},
            },
            'expected': ('1000-foo', None),
        },
        {
            'name': 'one rollout',
            'splits_by_service': {
                'aaa': {'allocations': {'1000-foo': .9, '2000-bar': .1}},
            },
            'expected': ('1000-foo', '2000-bar'),
        },
        {
            'name': 'parallel rollouts',
            'splits_by_service': {
                'aaa': {'allocations': {'1000-foo': .9, '2000-bar': .1}},
                'bbb': {'allocations': {'1000-foo': .6, '2000-bar': .4}},
            },
            'expected': ('1000-foo', '2000-bar'),
        },
        {
            'name': 'two different versions',
            'splits_by_service': {
                'aaa': {'allocations': {'1000-foo': 1}},
                'bbb': {'allocations': {'2000-bar': 1}},
            },
            'expected': ('1000-foo', '2000-bar'),
        },
        {
            'name': 'no versions',
            'splits_by_service': {},
            'expected': rollout.InvalidStateError,
        },
        {
            'name': 'three different versions',
            'splits_by_service': {
                'aaa': {'allocations': {'1000-foo': 1}},
                'bbb': {'allocations': {'2000-bar': 1}},
                'ccc': {'allocations': {'3000-eep': 1}},
            },
            'expected': rollout.InvalidStateError,
        },
        {
            'name': 'conflicting rollouts',
            'splits_by_service': {
                'aaa': {'allocations': {'1000-foo': .4, '2000-bar': .6}},
                'bbb': {'allocations': {'1000-foo': .4, '3000-eep': .6}},
            },
            'expected': rollout.InvalidStateError,
        },
        {
            'name': 'rollout with too many allocations',
            'splits_by_service': {
                'aaa': {'allocations': {
                    '1000-foo': .4,
                    '2000-bar': .3,
                    '3000-eep': .3
                }},
            },
            'expected': rollout.InvalidStateError,
        },
        {
            'name': 'version conflicting with rollout',
            'splits_by_service': {
                'aaa': {'allocations': {'1000-foo': .4, '2000-bar': .6}},
                'bbb': {'allocations': {'3000-eep': 1}}
            },
            'expected': rollout.InvalidStateError,
        },
    ]

    for test in tests:
      try:
        result = rollout.infer_rollout_state_from_splits(
            test['splits_by_service'])
      except rollout.InvalidStateError:
        if test['expected'] is rollout.InvalidStateError:
          continue
        raise
      self.assertEqual(test['expected'], result, test['name'])


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL,
      format='%(levelname)-7s %(filename)s:%(lineno)3d %(message)s')
  unittest.main()
