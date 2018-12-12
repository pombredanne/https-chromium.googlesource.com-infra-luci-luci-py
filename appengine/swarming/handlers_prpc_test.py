#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import os
import sys
import unittest

import test_env_handlers

import webapp2
import webtest

from components.prpc import encoding
from test_support import test_case

from proto import swarming_pb2  # pylint: disable=no-name-in-module

import handlers_prpc


def _decode(raw, dst):
  # Skip escaping characters.
  assert raw[:5] == ')]}\'\n', raw[:5]
  return encoding.get_decoder(encoding.Encoding.JSON)(raw[5:], dst)


def _encode(d):
  # Skip escaping characters.
  raw = encoding.get_encoder(encoding.Encoding.JSON)(d)
  assert raw[:5] == ')]}\'\n', raw[:5]
  return raw[5:]


class PRPCTest(test_env_handlers.AppTestBase):
  """Tests the pRPC handlers."""
  def setUp(self):
    super(PRPCTest, self).setUp()
    routes = handlers_prpc.get_routes()
    self.app = webtest.TestApp(
        webapp2.WSGIApplication(routes, debug=True),
        extra_environ={
          'REMOTE_ADDR': self.source_ip,
          'SERVER_SOFTWARE': os.environ['SERVER_SOFTWARE'],
        },
    )
    self._headers = {
      'Content-Type': encoding.Encoding.JSON[1],
      'Accept': encoding.Encoding.JSON[1],
    }

  def test_botevents(self):
    msg = swarming_pb2.BotEventsRequest()
    raw_resp = self.app.post(
        '/prpc/swarming.BotAPI/Events', _encode(msg), self._headers,
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
