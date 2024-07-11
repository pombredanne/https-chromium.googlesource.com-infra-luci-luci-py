# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Android specific utility functions.

This file serves as an API to bot_config.py. bot_config.py can be replaced on
the server to allow additional server-specific functionality.
"""

import collections
import logging
import os
import re
import time

try:
  from adb import adb_protocol
  from adb import common
  from adb.contrib import adb_commands_safe
  from adb.contrib import high
  from adb.contrib import parallel

  # The main switch that can easily be temporarily increased to INFO or even
  # DEBUG when needed by simply pushing a new tainted swarming server version.
  # This helps quickly debugging issues. On the other hand, even INFO level is
  # quite verbose so keep it at WARNING by default.
  LEVEL = logging.WARNING
  adb_commands_safe._LOG.setLevel(LEVEL)
  adb_protocol._LOG.setLevel(LEVEL)
  common._LOG.setLevel(LEVEL)
  high._LOG.setLevel(LEVEL)
except OSError:
  # This can fail on macOS if libusb-1.0.dylib is not installed.
  pass

from api.platforms import gce

# This list of third party apps embedded in the base OS image varies from
# version to version.
KNOWN_APPS = frozenset([
    'android',
    'android.autoinstalls.config.google.nexus',
    'com.frogmind.badland',
    'com.hp.android.printservice',
    'com.huawei.callstatisticsutils',
    'com.huawei.entitlement',
    'com.huawei.mmitest',
    'com.huawei.sarcontrolservice',
    'com.lge.HiddenMenu',
    'com.lge.SprintHiddenMenu',
    'com.lge.entitlement',
    'com.lge.lifetimer',
    'com.lge.update',
    'com.mediatek.fmradio',
    'com.mediatek.lbs.em2.ui',
    'com.motorola.android.buacontactadapter',
    'com.motorola.appdirectedsmsproxy',
    'com.motorola.entitlement',
    'com.motorola.motocit',
    'com.motorola.motosignature.app',
    'com.motorola.triggerenroll',
    'com.motorola.triggertrainingservice',
    'com.nuance.xt9.input',
    'com.nvidia.NvCPLSvc',
    'com.nvidia.NvCPLUpdater',
    'com.nvidia.benchmarkblocker',
    'com.nvidia.blakepairing',
    'com.nvidia.feedback',
    'com.nvidia.nvcecservice',
    'com.nvidia.nvgamecast',
    'com.nvidia.osc',
    'com.nvidia.ota',
    'com.nvidia.shield.nvcustomize',
    'com.nvidia.shield.welcome',
    'com.nvidia.shieldservice',
    'com.nvidia.stats',
    'com.nvidia.tegraprofiler.security',
    'com.nvidia.tegrazone3',
    'com.plexapp.android',
    'com.qti.qualcomm.datastatusnotification',
    'com.qualcomm.atfwd',
    'com.qualcomm.cabl',
    'com.qualcomm.embms',
    'com.qualcomm.qcrilmsgtunnel',
    'com.qualcomm.qti.rcsbootstraputil',
    'com.qualcomm.qti.rcsimsbootstraputil',
    'com.qualcomm.shutdownlistner',
    'com.qualcomm.timeservice',
    'com.quicinc.cne.CNEService',
    'com.quickoffice.android',
    'com.redbend.vdmc',
    'com.verizon.omadm',
    'com.vzw.apnservice',
    'com.yodo1.crossyroad',
    'jp.co.omronsoft.iwnnime.ml',
    'jp.co.omronsoft.iwnnime.ml.kbd.white',
    'org.codeaurora.ims',
    'org.simalliance.openmobileapi.service',
])

# Grabs the key/value pair list from lines such as:
# Temperature{mValue=25.6, mType=0, mName=AP, mStatus=0}
THERMALSERVICE_TEMPERATURE_REGEX = re.compile(r'^Temperature\{(.*)\}$')


def get_unknown_apps(device):
  return [
      p for p in device.GetPackages() or []
      if (not p.startswith(('com.android.',
                            'com.google.')) and p not in KNOWN_APPS)
  ]


def initialize(pub_key, priv_key):
  return high.Initialize(pub_key, priv_key)


# TODO(bpastene): Remove bot arg when call site has been updated.
def get_devices(bot=None, endpoints=None, enable_resets=False):
  # pylint: disable=unused-argument
  devices = []
  if not gce.is_gce():
    devices += high.GetLocalDevices(
        b'swarming', 10000, 10000, as_root=False, enable_resets=enable_resets)

  if endpoints:
    devices += high.GetRemoteDevices(
        b'swarming', endpoints, 10000, 10000, as_root=False)

  return devices


def close_devices(devices):
  return high.CloseDevices(devices)


def kill_adb():
  return adb_commands_safe.KillADB()


def get_dimensions(devices):
  """Returns the default dimensions for an host with multiple android devices.
  """
  dimensions = {}
  start = time.time()
  # Each key in the following dict is a dimension and its value is the list of
  # all possible device properties that can define that dimension.
  # TODO(bpastene) Make sure all the devices use the same board and OS.
  # product.device should be read (and listed) first, that is, before
  # build.product because the latter is deprecated.
  # https://android.googlesource.com/platform/build/+/b0dfb70381b729cd652a8e07b087bbb2e332e8cc/tools/buildinfo.sh
  dimension_properties = {
      'device_abi': ['product.cpu.abi'],
      'device_os': ['build.id'],
      'device_os_flavor': ['product.brand', 'product.system.brand'],
      'device_os_type': ['build.type'],
      'device_os_version': ['build.version.release'],
      'device_type': ['product.device', 'build.product', 'product.board'],
  }
  for dim in dimension_properties:
    dimensions[dim] = set()

  dimensions['android'] = []
  for device in devices:
    properties = device.cache.build_props
    if properties:
      for dim, props in dimension_properties.items():
        for prop in props:
          real_prop = 'ro.' + prop
          if real_prop in properties:
            p = properties[real_prop].strip()
            if p and p not in dimensions[dim]:
              dimensions[dim].add(p)
              # In the past, we would break here to have only one device_type.
              # This can be re-introduced if needed, but for some devices
              # (e.g. 2017 NVidia Shield, aka darcy) there are different values
              # for product.device and build.product (e.g. darcy and foster
              # [the device_type of the 2015 Shield]). Rather than knowing
              # which of the three keys is "correct", just report all of them.
      # Only advertize devices that can be used.
      dimensions['android'].append(device.serial)

      # Update device OS for Android Go Wembley devices to the version we
      # install, which is Android U as of now
      if 'wembley_2GB' in dimensions.get('device_type', []):
        dimensions['device_os'] = {
            key
            for key in dimensions.get('device_os', [])
            if key.lower() != 'master'
        }
        dimensions['device_os'].add('Android U')

  # Add the first character of each device_os to the dimension.
  android_vers = {
      os[0]
      for os in dimensions.get('device_os', []) if os and os[0].isupper()
  }
  dimensions['device_os'] = dimensions['device_os'].union(android_vers)

  # Add all prefixes of complex OS versions like 8.1.0
  device_os_version = dimensions.get('device_os_version', set())
  if device_os_version:
    vers = next(iter(device_os_version))
    vers_prefixes = [vers[0:i.start()] for i in re.finditer('\.', vers)]
    dimensions['device_os_version'] = dimensions['device_os_version'].union(
        vers_prefixes)

  dimensions['android'].sort()
  for dim in dimension_properties:
    if not dimensions[dim]:
      del dimensions[dim]
    else:
      dimensions[dim] = sorted(dimensions[dim])

  # Tweaks the 'product.brand' prop to be a little more readable.
  if dimensions.get('device_os_flavor'):

    def _fix_flavor(flavor):
      flavor = flavor.lower()
      # Non-aosp stock android is reported as 'google'. Other OEMs that ship
      # their own images are free to report what they want. (eg: Nvidia Shield
      # is reported as 'NVIDIA'.
      return 'aosp' if flavor == 'android' else flavor

    dimensions['device_os_flavor'] = list(
        map(_fix_flavor, dimensions['device_os_flavor']))

  nb_android = len(dimensions['android'])
  dimensions['android_devices'] = list(
      map(str, range(nb_android, max(0, nb_android - 4), -1)))

  # TODO(maruel): Add back once dimensions limit is figured out and there's a
  # need.
  del dimensions['android']

  # Trim 'os' to reduce the number of dimensions and not run tests by accident
  # on it.
  dimensions['os'] = ['Android']

  logging.info(
      'get_dimensions() (device part) took %gs' %
      round(time.time() - start, 1))

  def _get_package_versions(package):
    versions = set()
    for device in devices:
      version = device.GetPackageVersion(package)
      if version:
        versions.add(version)
    return sorted(versions)

  # Add gms core and Playstore versions
  dimensions['device_gms_core_version'] = (
      _get_package_versions('com.google.android.gms') or ['unknown'])
  dimensions['device_playstore_version'] = (
      _get_package_versions('com.android.vending') or ['unknown'])

  return dimensions


def get_state(devices):
  """Returns state information about all the devices connected to the host.
  """
  keys = ('board.platform', 'build.product', 'build.fingerprint', 'build.id',
          'build.type', 'build.version.release', 'build.version.sdk',
          'product.board', 'product.cpu.abi', 'product.device')

  def fn(device):
    if not device.is_valid or device.failure:
      return {'state': device.failure or 'unavailable'}
    properties = device.cache.build_props
    if not properties:
      return {'state': 'unavailable'}
    no_sd_card = properties.get('ro.product.model', '') in ['Chromecast']
    temperature_data = device.GetTemperatures()
    if not temperature_data:
      temperature_data = _get_fallback_temperature_data(device)
    return {
        'battery':
        device.GetBattery(),
        'build': {
            key: properties.get('ro.' + key, '<missing>')
            for key in keys
        },
        'cpu':
        device.GetCPUScale(),
        'disk':
        device.GetDisk(),
        'imei':
        device.GetIMEI(),
        'ip':
        device.GetIPs(),
        'max_uid':
        device.GetLastUID(),
        'mem':
        device.GetMemInfo(),
        'other_packages':
        get_unknown_apps(device),
        'port_path':
        device.port_path,
        'processes':
        device.GetProcessCount(),
        'state':
        ('available' if no_sd_card or device.IsFullyBooted()[0] else 'booting'),
        'temp':
        temperature_data,
        'uptime':
        device.GetUptime(),
    }

  start = time.time()
  state = {
      'devices': {
          device.serial: out
          for device, out in zip(devices, parallel.pmap(fn, devices))
      }
  }
  logging.info(
      'get_state() (device part) took %gs' %
      round(time.time() - start, 1))
  return state


def _get_fallback_temperature_data(device):
  """Returns fallback temperature data if the default path does not work.

  Args:
    device: The device to get temperature data from.

  Returns:
    A dict mapping temperature sensor names to temperatures in Celsius. May be
    empty if data is not available.
  """
  temperature_data = {}
  # dumpsys thermalservice is only expected to work on Android 10 and above.
  if int(device.cache.build_props.get('ro.build.version.sdk', 0)) < 29:
    return temperature_data

  dumpsys_output = device.Dumpsys('thermalservice')
  if not dumpsys_output:
    logging.warning(
        'Failed to run "dumpsys thermalservice" during fallback temperature '
        'collection')
    return temperature_data

  temperature_data = _parse_thermalservice_output(dumpsys_output)

  return temperature_data


def _parse_thermalservice_output(output):
  temperature_data = {}

  # Parse the temperature data from the block of lines such as:
  # Current temperatures from HAL:
  #      Temperature{mValue=25.6, mType=0, mName=AP, mStatus=0}
  #      Temperature{mValue=23.8, mType=2, mName=BAT, mStatus=0}
  #      ...
  in_temperature_block = False
  for line in output.splitlines():
    line = line.strip()
    # Ignore any blank lines.
    if not line:
      continue
    if line.startswith('Current temperatures'):
      in_temperature_block = True
      continue
    if not in_temperature_block:
      continue

    if not line.startswith('Temperature{'):
      break

    match = THERMALSERVICE_TEMPERATURE_REGEX.match(line)
    if not match:
      logging.warning('Unable to find expected temperature data in line %r',
                      line)
      continue
    key_value_list = match.group(1)
    sensor_name = None
    sensor_value = None
    for key_value_pair in key_value_list.split(','):
      key_value_pair = key_value_pair.strip()
      key, value = key_value_pair.split('=', maxsplit=1)
      if key == 'mValue':
        try:
          sensor_value = float(value)
        except ValueError:
          logging.warning('Unable to parse float from %r', value)
          break
      elif key == 'mName':
        sensor_name = value

    # This will also drop the data if the sensor value is 0, which is what we
    # want since that's indicative of the sensor not providing useful data. This
    # can happen during normal operation.
    if sensor_name and sensor_value:
      temperature_data[sensor_name] = sensor_value

  if not temperature_data:
    logging.warning('Did not find any data using fallback temperature path')

  return temperature_data
