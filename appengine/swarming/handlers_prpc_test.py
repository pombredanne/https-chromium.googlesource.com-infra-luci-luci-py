#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import logging
import sys
import unittest

import test_env
test_env.setup_test_env()

import webapp2
import webtest

from components.prpc import encoding
from test_support import test_case

from proto import swarming_pb2  # pylint: disable=no-name-in-module

import handlers_prpc


def _decode(raw, dst):
  # Skip escaping characters.
  return encoding.get_decoder(encoding.Encoding.JSON)(raw[4:], dst)


def _encode(d):
  # Skip escaping characters.
  raw = encoding.get_encoder(encoding.Encoding.JSON)(d)
  return raw[4:]


class PRPCTest(test_case.TestCase):
  """Tests the pRPC handlers."""
  APP_DIR = test_env.APP_DIR

  def setUp(self):
    super(PRPCTest, self).setUp()
    self.app = webtest.TestApp(
        webapp2.WSGIApplication(handlers_prpc.get_routes(), debug=True),
        extra_environ={'REMOTE_ADDR': '::ffff:127.0.0.1'},
    )
    self._headers = {
      'Content-Type': encoding.Encoding.JSON[1],
      'Accept': encoding.Encoding.JSON[1],
    }

  def test_botevents(self):
    msg = swarming_pb2.BotEventsRequest()
    raw_resp = self.app.post(
        '/prpc/swarming.Swarming/BotEvents', _encode(msg), self._headers,
        expect_errors=True)
    self.assertEqual(raw_resp.status, '501 Not Implemented')
    self.assertEqual(raw_resp.body, ')]}\'\n{}')


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.FATAL)
  unittest.main()
