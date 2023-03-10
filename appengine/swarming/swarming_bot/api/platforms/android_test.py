#!/usr/bin/env vpython3
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import unittest

import test_env_platforms
test_env_platforms.setup_test_env()

if sys.platform == 'linux':
  import android


GMS_PACKAGE = 'com.google.android.gms'
PLAYSTORE_PACKAGE = 'com.android.vending'


@unittest.skipUnless(sys.platform == 'linux', 'Android tests run only on linux')
class TestGetDimensions(unittest.TestCase):

  def empty_object(self):
    return lambda: None

  def mock_android_device(self, build_props, serial, package_versions):
    cache = self.empty_object()
    setattr(cache, 'build_props', build_props)
    base = self.empty_object()
    setattr(base, 'cache', cache)
    setattr(base, 'serial', serial)
    setattr(base, 'GetPackageVersion', lambda p: package_versions[p])

    return base

  def get_mock_nvidia_shield(self):
    return self.mock_android_device({
        'ro.product.brand':
            'NVIDIA',
        'ro.board.platform':
            'tegra',
        'ro.build.fingerprint': ('NVIDIA/darcy/darcy:7.0/NRD90M/'
                                 '1915764_848.4973:user/release-keys'),
        'ro.build.id':
            'NRD90M',
        'ro.build.product':
            'foster',
        'ro.build.version.sdk':
            '24',
        'ro.product.board':
            '',
        'ro.product.cpu.abi':
            'arm64-v8a',
        'ro.product.device':
            'darcy'
    }, 'mock_nvidia_shield', {
        GMS_PACKAGE: None,
        PLAYSTORE_PACKAGE: None
    })

  def get_mock_nexus5x(self):
    return self.mock_android_device({
        'ro.product.brand':
            'google',
        'ro.board.platform':
            'msm8992',
        'ro.build.fingerprint': ('google/bullhead/bullhead:6.0.1/'
                                 'MMB29Q/2480792:userdebug/dev-keys'),
        'ro.build.id':
            'MMB29Q',
        'ro.build.product':
            'bullhead',
        'ro.build.type':
            'userdebug',
        'ro.build.version.sdk':
            '23',
        'ro.product.board':
            'bullhead',
        'ro.product.cpu.abi':
            'arm64-v8a',
        'ro.product.device':
            'bullhead'
    }, 'mock_nexus5x', {
        GMS_PACKAGE: '8.1.86',
        PLAYSTORE_PACKAGE: '1.2.3'
    })

  def get_mock_pixel2xl(self):
    return self.mock_android_device({
        'ro.product.brand':
            'google',
        'ro.build.fingerprint': ('google/taimen/taimen:9/PPR1.180610.009/'
                                 '4898911:userdebug/dev-keys'),
        'ro.build.id':
            'PPR1.180610.009',
        'ro.build.product':
            'taimen',
        'ro.build.type':
            'userdebug',
        'ro.build.version.sdk':
            '28',
        'ro.product.cpu.abi':
            'arm64-v8a',
        'ro.product.device':
            'taimen'
    }, 'mock_nexus5x', {
        GMS_PACKAGE: '12.8.62',
        PLAYSTORE_PACKAGE: '1.2.3'
    })

  def get_mock_galaxyS6(self):
    return self.mock_android_device({
        'ro.product.brand':
            'Samsung',
        'ro.board.platform':
            'exynos5',
        'ro.build.fingerprint': ('samsung/zerofltetmo/zerofltetmo:7.0/'
                                 'NRD90M/G920TUVU5FQK1:user/release-keys'),
        'ro.build.id':
            'NRD90M',
        'ro.build.product':
            'zerofltetmo',
        'ro.build.type':
            'user',
        'ro.build.version.sdk':
            '24',
        'ro.product.board':
            'universal7420',
        'ro.product.cpu.abi':
            'arm64-v8a',
        'ro.product.device':
            'zerofltetmo'
    }, 'mock_galaxyS6', {
        GMS_PACKAGE: '11.5.09',
        PLAYSTORE_PACKAGE: '1.2.3'
    })

  def get_mock_wembley(self):
    return self.mock_android_device(
        {
            'ro.product.brand': 'google',
            'ro.build.id': 'Master',
            'ro.build.product': 'wembley_2GB',
            'ro.build.type': 'userdebug',
            'ro.build.version.sdk': '34',
            'ro.product.device': 'wembley_2GB'
        }, 'mock_wembley', {
            GMS_PACKAGE: '22.26.15',
            PLAYSTORE_PACKAGE: '1.2.3'
        })

  def get_mock_wembley_uppercase(self):
    return self.mock_android_device(
        {
            'ro.product.brand': 'google',
            'ro.build.id': 'MASTER',
            'ro.build.product': 'wembley_2GB',
            'ro.build.type': 'userdebug',
            'ro.build.version.sdk': '34',
            'ro.product.device': 'wembley_2GB'
        }, 'mock_wembley', {
            GMS_PACKAGE: '22.26.15',
            PLAYSTORE_PACKAGE: '1.2.3'
        })

  def test_wembley_get_dimensions(self):
    wembley_result = {
        'android_devices': ['1'],
        'device_gms_core_version': ['22.26.15'],
        'device_os': ['A', 'Android U'],
        'device_os_flavor': ['google'],
        'device_os_type': ['userdebug'],
        'device_playstore_version': ['1.2.3'],
        'device_type': ['wembley_2GB'],
        'os': ['Android'],
    }
    self.assertEqual(wembley_result,
                     android.get_dimensions([self.get_mock_wembley()]))
    self.assertEqual(
        wembley_result,
        android.get_dimensions([self.get_mock_wembley_uppercase()]))

  def test_shield_get_dimensions(self):
    self.assertEqual(
        {
            'android_devices': ['1'],
            'device_abi': ['arm64-v8a'],
            'device_gms_core_version': ['unknown'],
            'device_os': ['N', 'NRD90M'],
            'device_os_flavor': ['nvidia'],
            'device_playstore_version': ['unknown'],
            'device_type': ['darcy', 'foster'],
            'os': ['Android'],
        }, android.get_dimensions([self.get_mock_nvidia_shield()]))

  def test_nexus5x_get_dimensions(self):
    self.assertEqual(
        {
            'android_devices': ['1'],
            'device_abi': ['arm64-v8a'],
            'device_gms_core_version': ['8.1.86'],
            'device_os': ['M', 'MMB29Q'],
            'device_os_flavor': ['google'],
            'device_os_type': ['userdebug'],
            'device_playstore_version': ['1.2.3'],
            'device_type': ['bullhead'],
            'os': ['Android'],
        }, android.get_dimensions([self.get_mock_nexus5x()]))

  def test_pixel2xl_get_dimensions(self):
    self.assertEqual(
        {
            'android_devices': ['1'],
            'device_abi': ['arm64-v8a'],
            'device_gms_core_version': ['12.8.62'],
            'device_os': ['P', 'PPR1.180610.009'],
            'device_os_flavor': ['google'],
            'device_os_type': ['userdebug'],
            'device_playstore_version': ['1.2.3'],
            'device_type': ['taimen'],
            'os': ['Android'],
        }, android.get_dimensions([self.get_mock_pixel2xl()]))

  def test_galaxyS6_get_dimensions(self):
    self.assertEqual(
        {
            'android_devices': ['1'],
            'device_abi': ['arm64-v8a'],
            'device_gms_core_version': ['11.5.09'],
            'device_os': ['N', 'NRD90M'],
            'device_os_flavor': ['samsung'],
            'device_os_type': ['user'],
            'device_playstore_version': ['1.2.3'],
            'device_type': ['universal7420', 'zerofltetmo'],
            'os': ['Android'],
        }, android.get_dimensions([self.get_mock_galaxyS6()]))


@unittest.skipUnless(sys.platform == 'linux', 'Android tests run only on linux')
class TestGetState(unittest.TestCase):
  def empty_object(self):
    return lambda: None

  def mock_android_device(self, serial, build_props, mock_props, mock_methods):
    base = self.empty_object()
    setattr(base, 'serial', serial)
    cache = self.empty_object()
    setattr(cache, 'build_props', build_props)
    setattr(base, 'cache', cache)
    for key, value in mock_props.items():
      setattr(base, key, value)
    for key, value in mock_methods.items():
      setattr(base, key, lambda v=value: v)

    return base

  def test_invalid_device(self):
    device = self.mock_android_device(
        serial='device_serial',
        build_props={},
        mock_props={
            'is_valid': False,
            'failure': None,
        },
        mock_methods={},
    )
    expected_state = {
        'devices': [{
            'serial': 'device_serial',
            'state': 'unavailable',
        }],
    }
    self.assertEqual(expected_state, android.get_state([device]))

  def test_failed_device(self):
    device = self.mock_android_device(
        serial='device_serial',
        build_props={},
        mock_props={
            'is_valid': True,
            'failure': 'I am failed',
        },
        mock_methods={},
    )
    expected_state = {
        'devices': [{
            'serial': 'device_serial',
            'state': 'I am failed',
        }],
    }
    self.assertEqual(expected_state, android.get_state([device]))

  def test_no_prop_device(self):
    device = self.mock_android_device(
        serial='device_serial',
        build_props={},
        mock_props={
            'is_valid': True,
            'failure': None,
        },
        mock_methods={},
    )
    expected_state = {
        'devices': [{
            'serial': 'device_serial',
            'state': 'unavailable',
        }],
    }
    self.assertEqual(expected_state, android.get_state([device]))

  def test_available_device(self):
    device = self.mock_android_device(
        serial='device_serial',
        build_props={
            "ro.board.platform": "platform",
            "ro.build.fingerprint": "fingerprint",
            "ro.build.id": "PQ3A.190801.002",
            "ro.build.product": "sailfish",
            "ro.build.type": "userdebug",
            "ro.build.version.sdk": "28",
            "ro.product.board": "board",
            "ro.product.cpu.abi": "arm64-v8a",
            "ro.product.device": "sailfish",
        },
        mock_props={
            'is_valid': True,
            'failure': None,
            'port_path': '1/89',
        },
        mock_methods = {
            'GetPackages': ['com.chromium.abc'],
            'GetBattery': {'level': 90},
            'GetCPUScale': {'governor': 'powersave'},
            'GetDisk': {'data': {'free_mb': 1024}},
            'GetIMEI': "12345",
            'GetIPs': ['0.0.0.5'],
            'GetLastUID': 19999,
            'GetMemInfo': {'avail': 1024},
            'GetProcessCount': 2,
            'IsFullyBooted': [True, None],
            'GetTemperatures': {'battery': 22.7},
            'GetUptime': 1000.1,
        },
    )
    expected_state = {
        'devices': [{
            'serial': 'device_serial',
            'battery': {'level': 90},
            'build': {
                "board.platform": "platform",
                "build.fingerprint": "fingerprint",
                "build.id": "PQ3A.190801.002",
                "build.product": "sailfish",
                "build.type": "userdebug",
                "build.version.sdk": "28",
                "product.board": "board",
                "product.cpu.abi": "arm64-v8a",
                "product.device": "sailfish",
            },
            'cpu': {'governor': 'powersave'},
            'disk': {'data': {'free_mb': 1024}},
            'imei': "12345",
            'ip': ['0.0.0.5'],
            'max_uid': 19999,
            'mem': {'avail': 1024},
            'other_packages': ['com.chromium.abc'],
            'port_path': '1/89',
            'processes': 2,
            'state': 'available',
            'temp': {'battery': 22.7},
            'uptime': 1000.1,
        }],
    }
    self.assertEqual(expected_state, android.get_state([device]))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
