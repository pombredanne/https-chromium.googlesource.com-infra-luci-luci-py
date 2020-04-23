#!/usr/bin/env python
# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Prints out attributes as generated by ../swarming_bot/api/os_utilities.py.
"""

import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
  """Prints out the output of get_dimensions() and get_state()."""
  sys.path.insert(0, os.path.join(ROOT_DIR, 'swarming_bot'))
  import test_env_bot
  test_env_bot.setup_test_env()
  from api import os_utilities
  from api import platforms

  # Pass an empty tag, so pop it up since it has no significance.
  devices = None
  if sys.platform.startswith('linux'):
    devices = platforms.android.get_devices(None)
    if devices:
      try:
        data = {
            u'dimensions':
                os_utilities.get_dimensions_all_devices_android(devices),
            u'state': os_utilities.get_state_all_devices_android(devices),
        }
      finally:
        platforms.android.close_devices(devices)
  if not devices:
    data = {
        u'dimensions': os_utilities.get_dimensions(),
        u'state': os_utilities.get_state(),
    }

  json.dump(data, sys.stdout, indent=2, sort_keys=True, separators=(',', ': '))
  print('')
  return 0


if __name__ == '__main__':
  sys.exit(main())
