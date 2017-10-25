#!/usr/bin/env python
# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import math
import os
import re
import socket
import subprocess
import sys
import time
import unittest

import test_env_api
test_env_api.setup_test_env()

from api import platforms
from depot_tools import auto_stub
from utils import file_path

# Disable caching before importing os_utilities.
from utils import tools
tools.cached = lambda func: func

import os_utilities


class TestOsUtilities(auto_stub.TestCase):
  def test_get_os_name(self):
    expected = (u'Linux', u'Mac', u'Raspbian', u'Ubuntu', u'Windows')
    self.assertIn(os_utilities.get_os_name(), expected)

  def test_get_cpu_type(self):
    actual = os_utilities.get_cpu_type()
    if actual == u'x86':
      return
    self.assertTrue(actual.startswith(u'arm'), actual)

  def test_get_cpu_bitness(self):
    expected = (u'32', u'64')
    self.assertIn(os_utilities.get_cpu_bitness(), expected)

  def test_get_cpu_dimensions(self):
    values = os_utilities.get_cpu_dimensions()
    self.assertGreater(len(values), 1)

  def test_parse_intel_model(self):
    examples = [
     ('Intel(R) Core(TM) i5-5200U CPU @ 2.20GHz', 'i5-5200U'),
     ('Intel(R) Core(TM) i7-2635QM CPU @ 2.00GHz', 'i7-2635QM'),
     ('Intel(R) Core(TM) i7-4578U CPU @ 3.00GHz', 'i7-4578U'),
     ('Intel(R) Core(TM)2 Duo CPU     P8600  @ 2.40GHz', 'P8600'),
     ('Intel(R) Core(TM) i7-4870HQ CPU @ 2.50GHz', 'i7-4870HQ'),
     ('Intel(R) Core(TM) i7-6700T CPU @ 2.80GHz', 'i7-6700T'),
     ('Intel(R) Pentium(R) CPU  N3710  @ 1.60GHz', 'N3710'),
     ('Intel(R) Xeon(R) CPU E3-1220 V2 @ 3.10GHz', 'E3-1220 V2'),
     ('Intel(R) Xeon(R) CPU E3-1230 v3 @ 3.30GHz', 'E3-1230 v3'),
     ('Intel(R) Xeon(R) CPU E5-2670 0 @ 2.60GHz', 'E5-2670'),
     ('Intel(R) Xeon(R) CPU E5-2697 v2 @ 2.70GHz', 'E5-2697 v2'),
     # As generated by platforms.gce.get_cpuinfo():
     ('Intel(R) Xeon(R) CPU Sandy Bridge GCE', 'Sandy Bridge GCE'),
     ('Intel(R) Xeon(R) CPU @ 2.30GHz', None),
    ]
    for i, expected in examples:
      actual = os_utilities._parse_intel_model(i)
      self.assertEqual(expected, actual)

  def test_get_ip(self):
    ip = os_utilities.get_ip()
    self.assertNotEqual('127.0.0.1', ip)
    ipv4 = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    ipv6 = r'^%s$' % ':'.join([r'[0-9a-f]{1,4}'] * 8)
    self.assertTrue(re.match(ipv4, ip) or re.match(ipv6, ip), ip)

  def test_get_num_processors(self):
    self.assertGreater(os_utilities.get_num_processors(), 0)

  def test_get_physical_ram(self):
    self.assertGreater(os_utilities.get_physical_ram(), 0)

  def test_get_disks_info(self):
    info = os_utilities.get_disks_info()
    self.assertGreater(len(info), 0)
    root_path = u'C:\\' if sys.platform == 'win32' else u'/'
    root = info[root_path]
    # Round the same way.
    free_disk = round(
        float(file_path.get_free_space(root_path)) / 1024. / 1024., 1)
    delta = math.fabs(free_disk - root['free_mb'])
    # Check that they are mostly equal. There can be some gitter as there is
    # disk I/O during the two calls.
    self.assertLess(delta, 2., (delta, free_disk, root['free_mb']))

  def test_get_gpu(self):
    actual = os_utilities.get_gpu()
    self.assertTrue(actual is None or actual)

  def test_get_dimensions(self):
    dimensions = os_utilities.get_dimensions()
    for key, values in dimensions.iteritems():
      self.assertIsInstance(key, unicode)
      self.assertIsInstance(values, list)
      for value in values:
        self.assertIsInstance(value, unicode)
    actual = set(dimensions)
    # Only set when the process is running in a properly configured GUI context.
    actual.discard(u'locale')
    # Only set on GCE.
    actual.discard(u'image')
    actual.discard(u'machine_type')
    actual.discard(u'zone')
    # Only set on Mac.
    actual.discard(u'hidpi')
    # Only set on Windows.
    actual.discard(u'integrity')
    # Only set on machines with SSD
    if sys.platform in ('darwin', 'linux2'):
      actual.discard(u'ssd')
    expected = {u'cores', u'cpu', u'gpu', u'id', u'os', u'pool', u'python'}
    if sys.platform in ('linux2'):
      actual.discard(u'kvm')
    if sys.platform == 'darwin':
      expected.add(u'mac_model')
      expected.add(u'xcode_version')
    self.assertEqual(expected, actual)

  def test_override_id_via_env(self):
    mock_env = os.environ.copy()
    mock_env['SWARMING_BOT_ID'] = 'customid'
    self.mock(os, 'environ', mock_env)
    dimensions = os_utilities.get_dimensions()
    self.assertIsInstance(dimensions[u'id'], list)
    self.assertEqual(len(dimensions[u'id']), 1)
    self.assertIsInstance(dimensions[u'id'][0], unicode)
    self.assertEqual(dimensions[u'id'][0], u'customid')

  def test_get_state(self):
    actual = os_utilities.get_state()
    actual.pop('temp', None)
    expected = {
      u'audio', u'caches', u'cost_usd_hour', u'cpu_name', u'cwd', u'disks',
      u'env', u'gpu', u'ip', u'hostname', u'nb_files_in_temp', u'pid',
      u'python', u'ram', u'running_time', u'ssd', u'started_ts', u'uptime',
      u'user',
    }
    if sys.platform in ('cygwin', 'win32'):
      expected.add(u'cygwin')
    if sys.platform == 'darwin':
      expected.add(u'xcode')
    if sys.platform == 'win32':
      expected.add(u'integrity')
    if u'quarantined' in actual:
      self.fail(actual[u'quarantined'])
    self.assertEqual(expected, set(actual))

  def test_get_hostname_gce_docker(self):
    self.mock(platforms, 'is_gce', lambda: True)
    self.mock(os.path, 'isfile', lambda _: True)
    self.mock(socket, 'getfqdn', lambda: 'dockerhost')
    self.assertEqual(os_utilities.get_hostname(), 'dockerhost')

  def test_get_hostname_gce_nodocker(self):
    self.mock(platforms, 'is_gce', lambda: True)
    self.mock(os.path, 'isfile', lambda _: False)
    self.mock(platforms.gce, 'get_metadata',
              lambda: {'instance': {'hostname': 'gcehost'}})
    self.assertEqual(os_utilities.get_hostname(), 'gcehost')

  def test_get_hostname_nogce(self):
    self.mock(platforms, 'is_gce', lambda: False)
    self.mock(os.path, 'isfile', lambda _: False)
    self.mock(socket, 'getfqdn', lambda: 'somehost')
    self.assertEqual(os_utilities.get_hostname(), 'somehost')

  def test_get_hostname_macos(self):
    self.mock(platforms, 'is_gce', lambda: False)
    self.mock(os.path, 'isfile', lambda _: False)
    self.mock(socket, 'getfqdn', lambda: 'somehost.in-addr.arpa')
    self.mock(socket, 'gethostname', lambda: 'somehost')
    self.assertEqual(os_utilities.get_hostname(), 'somehost')

  def test_setup_auto_startup_win(self):
    # TODO(maruel): Figure out a way to test properly.
    pass

  def test_setup_auto_startup_osx(self):
    # TODO(maruel): Figure out a way to test properly.
    pass

  def test_host_reboot(self):
    class Foo(Exception):
      pass

    def raise_exception(x):
      raise x

    self.mock(subprocess, 'check_call', lambda _: None)
    self.mock(time, 'sleep', lambda _: raise_exception(Foo()))
    self.mock(logging, 'error', lambda *_: None)
    with self.assertRaises(Foo):
      os_utilities.host_reboot()

  def test_host_reboot_and_return(self):
    self.mock(subprocess, 'check_call', lambda _: None)
    self.assertIs(True, os_utilities.host_reboot_and_return())

  def test_host_reboot_and_return_with_message(self):
    self.mock(subprocess, 'check_call', lambda _: None)
    self.assertIs(True, os_utilities.host_reboot_and_return(message='Boo'))

  def test_host_reboot_with_timeout(self):
    self.mock(subprocess, 'check_call', lambda _: None)
    self.mock(logging, 'error', lambda *_: None)

    now = [0]
    def mock_sleep(dt):
      now[0] += dt
    self.mock(time, 'sleep', mock_sleep)
    self.mock(time, 'time', lambda: now[0])

    self.assertFalse(os_utilities.host_reboot(timeout=60))
    self.assertEqual(time.time(), 60)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.ERROR)
  unittest.main()
