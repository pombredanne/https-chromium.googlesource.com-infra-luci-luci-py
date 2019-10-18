#!/usr/bin/env vpython
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import os
import sys

import six

from nose2 import discover

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
LUCI_DIR = os.path.dirname(THIS_DIR)
PLUGINS_DIR = os.path.join(LUCI_DIR, 'appengine', 'components',
                           'test_support', 'nose2_plugins')
THIRD_PARTY_DIR = os.path.join(THIS_DIR, 'third_party')


def main():
  plugins = []
  if six.PY3:
    plugins.append('py3filter')

  # fix_encoding
  sys.path.insert(0, THIRD_PARTY_DIR)
  from depot_tools import fix_encoding
  fix_encoding.fix_encoding()

  # add nose2 plugin dir to path
  sys.path.insert(0, PLUGINS_DIR)

  discover(plugins=plugins)


def _has_arg(argv, arg):
  return any(arg in a for a in argv)


if __name__ == '__main__':
  if not _has_arg(sys.argv, '--log-level'):
    logging.basicConfig(level=logging.CRITICAL)
  main()
