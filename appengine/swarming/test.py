#!/usr/bin/env python

import os
import sys
import logging

SWARMING_DIR = os.path.dirname(os.path.abspath(__file__))
APPENGINE_DIR = os.path.dirname(SWARMING_DIR)
APPENGINE_THIRD_PARTY_DIR = os.path.join(APPENGINE_DIR, 'third_party')
SWARMING_BOT_DIR = os.path.join(SWARMING_DIR, 'swarming_bot')

def main():
  runner = unittest.TextTestRunner()

  # loader = unittest.TestLoader()
  # tests = loader.discover('./', pattern='*_test.py')
  # runner.run(tests)

  loader = unittest.TestLoader()
  swarming_bot_tests = loader.discover('./swarming_bot', pattern='*_test.py')
  for t in swarming_bot_tests:
    import pdb; pdb.set_trace()
    runner.run(t)

  # loader = unittest.TestLoader()
  # server_tests = loader.discover('./server', pattern='*_test.py')
  # runner.run(server_tests)

if __name__ == '__main__':
  sys.path.insert(0, SWARMING_BOT_DIR)
  sys.path.insert(0, APPENGINE_DIR)

  import test_env_bot
  test_env_bot.setup_test_env()

  # from utils import tools
  # tools.disable_cache = True

  from depot_tools import fix_encoding
  fix_encoding.fix_encoding()

  sys.path.insert(0, APPENGINE_THIRD_PARTY_DIR)
  import unittest2 as unittest

  unittest.TestCase.maxDiff = None
  logging.basicConfig(level=logging.CRITICAL)
  main()
