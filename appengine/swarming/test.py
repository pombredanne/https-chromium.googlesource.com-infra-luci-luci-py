#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import os
import sys
import logging

SWARMING_DIR = os.path.dirname(os.path.abspath(__file__))
APPENGINE_DIR = os.path.dirname(SWARMING_DIR)
APPENGINE_THIRD_PARTY_DIR = os.path.join(APPENGINE_DIR, 'third_party')
SWARMING_BOT_DIR = os.path.join(SWARMING_DIR, 'swarming_bot')


def main():
  discover()


if __name__ == '__main__':
  sys.path.insert(0, APPENGINE_DIR)
  sys.path.insert(0, SWARMING_BOT_DIR)

  import swarming_test_env
  swarming_test_env.setup_test_env()

  import test_env_bot
  test_env_bot.setup_test_env()

  from depot_tools import fix_encoding
  fix_encoding.fix_encoding()

  sys.path.insert(0, APPENGINE_THIRD_PARTY_DIR)
  from nose2 import discover

  logging.basicConfig(level=logging.CRITICAL)
  main()
