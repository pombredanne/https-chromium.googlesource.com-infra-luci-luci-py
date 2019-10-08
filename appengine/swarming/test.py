#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import os
import sys
import logging

import six

SWARMING_DIR = os.path.dirname(os.path.abspath(__file__))
APPENGINE_DIR = os.path.dirname(SWARMING_DIR)
NOSE2_DIR = os.path.join(APPENGINE_DIR, 'third_party', 'nose2')
SWARMING_BOT_DIR = os.path.join(SWARMING_DIR, 'swarming_bot')
LUCI_DIR = os.path.dirname(os.path.dirname(SWARMING_DIR))
CLIENT_THIRDPARTY_DIR = os.path.join(LUCI_DIR, 'client', 'third_party')


def main():
  if six.PY2:
    sys.path.insert(0, APPENGINE_DIR)
    import swarming_test_env
    swarming_test_env.setup_test_env()

    sys.path.insert(0, SWARMING_BOT_DIR)
    import test_env_bot
    test_env_bot.setup_test_env()

  if six.PY3:
    # manually add depot_tools to path
    sys.path.insert(0, CLIENT_THIRDPARTY_DIR)

  from depot_tools import fix_encoding
  fix_encoding.fix_encoding()

  sys.path.insert(0, NOSE2_DIR)
  from nose2 import discover

  discover()


def _has_arg(argv, arg):
  return len([a for a in argv if arg in a]) > 0


if __name__ == '__main__':
  if not _has_arg(sys.argv, '--log-level'):
    logging.basicConfig(level=logging.CRITICAL)
  main()
