#!/usr/bin/env vpython3
# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import io
import logging
import sys
import textwrap
import unittest

import mock

import test_env_platforms
test_env_platforms.setup_test_env()

from depot_tools import auto_stub
from utils import tools

if sys.platform == 'linux':
  import linux


# pylint: disable=line-too-long
EXYNOS_CPU_INFO = r"""
Processor : ARMv7 Processor rev 4 (v7l)
processor : 0
BogoMIPS  : 1694.10

processor : 1
BogoMIPS  : 1694.10

Features  : swp half thumb fastmult vfp edsp thumbee neon vfpv3 tls vfpv4 idiva idivt
CPU implementer : 0x41
CPU architecture: 7
CPU variant : 0x0
CPU part  : 0xc0f
CPU revision  : 4

Hardware  : SAMSUNG EXYNOS5 (Flattened Device Tree)
Revision  : 0000
Serial    : 0000000000000000
"""


CAVIUM_CPU_INFO = r"""
processor : 0
BogoMIPS  : 200.00
Features  : fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics
CPU implementer : 0x43
CPU architecture: 8
CPU variant : 0x1
CPU part  : 0x0a1
CPU revision  : 1

processor : 1
BogoMIPS  : 200.00
Features  : fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics
CPU implementer : 0x43
CPU architecture: 8
CPU variant : 0x1
CPU part  : 0x0a1
CPU revision  : 1
"""


MIPS64_CPU_INFO = r"""
chrome-bot@build23-b3:/tmp/1$ cat /proc/cpuinfo
system type             : Unsupported Board (CN6120p1.1-1000-NSP)
machine                 : Unknown
processor               : 0
cpu model               : Cavium Octeon II V0.1
BogoMIPS                : 2000.00
wait instruction        : yes
microsecond timers      : yes
tlb_entries             : 128
extra interrupt vector  : yes
hardware watchpoint     : yes, count: 2, address/irw mask: [0x0ffc, 0x0ffb]
isa                     : mips2 mips3 mips4 mips5 mips64r2
ASEs implemented        :
shadow register sets    : 1
kscratch registers      : 3
package                 : 0
core                    : 0
VCED exceptions         : not available
VCEI exceptions         : not available

processor               : 1
cpu model               : Cavium Octeon II V0.1
BogoMIPS                : 2000.00
wait instruction        : yes
microsecond timers      : yes
tlb_entries             : 128
extra interrupt vector  : yes
hardware watchpoint     : yes, count: 2, address/irw mask: [0x0ffc, 0x0ffb]
isa                     : mips2 mips3 mips4 mips5 mips64r2
ASEs implemented        :
shadow register sets    : 1
kscratch registers      : 3
package                 : 0
core                    : 1
VCED exceptions         : not available
VCEI exceptions         : not available
"""


@unittest.skipUnless(sys.platform == 'linux', 'linux only test')
class TestCPUInfo(auto_stub.TestCase):

  def setUp(self):
    super(TestCPUInfo, self).setUp()
    tools.clear_cache_all()

  def tearDown(self):
    super(TestCPUInfo, self).tearDown()
    tools.clear_cache_all()

  def get_cpuinfo(self, text):
    self.mock(linux, '_read_cpuinfo', lambda: text)
    return linux.get_cpuinfo()

  def test_get_cpuinfo_exynos(self):
    self.assertEqual(
        {
            'flags': [
                'edsp',
                'fastmult',
                'half',
                'idiva',
                'idivt',
                'neon',
                'swp',
                'thumb',
                'thumbee',
                'tls',
                'vfp',
                'vfpv3',
                'vfpv4',
            ],
            'model': (0, 3087, 4),
            'name':
            'SAMSUNG EXYNOS5',
            'revision':
            '0000',
            'serial':
            '',
            'vendor':
            'ARMv7 Processor rev 4 (v7l)',
        }, self.get_cpuinfo(EXYNOS_CPU_INFO))

  def test_get_cpuinfo_cavium(self):
    self.assertEqual(
        {
            'flags': [
                'aes',
                'asimd',
                'atomics',
                'crc32',
                'evtstrm',
                'fp',
                'pmull',
                'sha1',
                'sha2',
            ],
            'model': (1, 161, 1),
            'vendor':
            'N/A',
        }, self.get_cpuinfo(CAVIUM_CPU_INFO))

  def test_get_cpuinfo_mips(self):
    self.assertEqual(
        {
            'flags': ['mips2', 'mips3', 'mips4', 'mips5', 'mips64r2'],
            'name': 'Cavium Octeon II V0.1',
        }, self.get_cpuinfo(MIPS64_CPU_INFO))

  def test_get_num_processors(self):
    self.assertTrue(linux.get_num_processors() != 0)


K8S_CGROUP = """
8:freezer:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
7:blkio:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
6:net_cls:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
5:memory:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
4:cpu,cpuacct:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
3:cpuset:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
2:devices:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
1:name=systemd:/k8s.io/baa2c4c148cc83e36b7f14fe9145c58b742c82b244f77e32cda50cf8f26a27a5
"""

NO_K8S_CGROUP = """
11:blkio:/init.scope
10:devices:/init.scope
9:memory:/init.scope
8:perf_event:/
7:cpuset:/
6:net_cls,net_prio:/
5:freezer:/
4:rdma:/
3:cpu,cpuacct:/init.scope
2:pids:/init.scope
1:name=systemd:/init.scope
0::/init.scope
"""


@unittest.skipUnless(sys.platform == 'linux', 'linux only test')
class TestDocker(auto_stub.TestCase):

  def setUp(self):
    super(TestDocker, self).setUp()
    tools.clear_cache_all()

  def tearDown(self):
    super(TestDocker, self).tearDown()
    tools.clear_cache_all()

  def get_inside_docker(self, text):
    self.mock(linux, '_read_cgroup', lambda: text)
    return linux.get_inside_docker()

  def test_get_inside_docker_k8s(self):
    self.assertEqual('stock', self.get_inside_docker(K8S_CGROUP))

  def test_get_inside_docker_no_k8s(self):
    self.assertEqual(None, self.get_inside_docker(NO_K8S_CGROUP))


@unittest.skipUnless(sys.platform == 'linux', 'linux only test')
class TestLinux(auto_stub.TestCase):

  def setUp(self):
    super(TestLinux, self).setUp()
    tools.clear_cache_all()
    self.mock_check_output = mock.patch('subprocess.check_output').start()

  def tearDown(self):
    super(TestLinux, self).tearDown()
    mock.patch.stopall()
    tools.clear_cache_all()

  def test_get_ssd(self):
    self.mock_check_output.return_value = textwrap.dedent("""\
      NAME    ROTA
      nvme0n1    0
    """)
    self.assertEqual(linux.get_ssd(), ('nvme0n1',))

  def test_get_gpu(self):
    # pylint: disable=line-too-long
    self.mock_check_output.return_value = textwrap.dedent("""\
      18:00.0 "VGA compatible controller [0300]" "NVIDIA Corporation [10de]" "GP107GL [Quadro P1000] [1cb1]" -ra1 "NVIDIA Corporation [10de]" "GP107GL [Quadro P1000] [11bc]"
    """).encode()
    with mock.patch('builtins.open', mock.mock_open(read_data='440.82')):
      self.assertEqual(linux.get_gpu(),
                       (['10de', '10de:1cb1', '10de:1cb1-440.82'
                        ], ['Nvidia GP107GL [Quadro P1000] 440.82']))

  def test_get_intel_version(self):
    self.mock_check_output.return_value = textwrap.dedent("""\
      Version: 1.2.3
    """).encode()
    self.assertEqual(linux._get_intel_version(), '1.2.3')

  def test_get_device_tree_compatible(self):
    with mock.patch('builtins.open') as mock_open:
      mock_open.return_value = io.BytesIO(b'foo,bar')
      self.assertEqual(linux.get_device_tree_compatible(),
                       sorted(['foo', 'bar']))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
