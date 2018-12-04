#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import logging
import os
import sys
import unittest

import test_env
test_env.setup_test_env()

import webapp2
import webtest

from components.prpc import encoding
from proto import isolated_pb2
from test_support import test_case

import handlers_prpc
import stats


def _decode(raw, dst):
  # Skip escaping characters.
  return encoding.get_decoder(encoding.Encoding.JSON)(raw[4:], dst)


def _encode(d):
  # Skip escaping characters.
  raw = encoding.get_encoder(encoding.Encoding.JSON)(d)
  #logging.info('%s', raw)
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
    self.now = datetime.datetime(2010, 1, 2, 3, 4, 5, 6)

  def _gen_stats(self):
    """Generates data for the last 10 days, last 10 hours and last 10 minutes.
    """
    # TODO(maruel): Stop accessing the DB directly. Use stats_framework_mock to
    # generate it.
    self.mock_now(self.now, 0)
    handler = stats.STATS_HANDLER
    for i in xrange(10):
      s = stats._Snapshot(requests=100 + i)
      day = (self.now - datetime.timedelta(days=i)).date()
      handler.stats_day_cls(key=handler.day_key(day), values_compressed=s).put()

    for i in xrange(10):
      s = stats._Snapshot(requests=10 + i)
      timestamp = (self.now - datetime.timedelta(hours=i))
      handler.stats_hour_cls(
          key=handler.hour_key(timestamp), values_compressed=s).put()

    for i in xrange(10):
      s = stats._Snapshot(requests=1 + i)
      timestamp = (self.now - datetime.timedelta(minutes=i))
      handler.stats_minute_cls(
          key=handler.minute_key(timestamp), values_compressed=s).put()

  def disabled_test_stats(self):
    self._gen_stats()
    response = self.app.get('/stats')
    # Just ensure something is returned.
    self.assertGreater(response.content_length, 4000)

  def test_api_stats_days(self):
    self._gen_stats()
    msg = isolated_pb2.StatsRequest()
    msg.latest.FromDatetime(self.now + datetime.timedelta(minutes=10))
    msg.resolution = isolated_pb2.MINUTE
    msg.number = 10
    raw_resp = self.app.post(
        '/prpc/isolated.Service/Stats', _encode(msg), self._headers)
    resp = isolated_pb2.StatsResponse()
    _decode(raw_resp.body, resp)

    # It's cheezy but at least it asserts that the data makes sense.
    expected = (
      u'latest {\n  seconds: 1262402040\n}\n'
      #u'measurements {\n'
      #u'  ts {\n    seconds: 1262401440\n  }\n  requests: 1\n'
      #u'}\n'
    )
    foo = (
        'google.visualization.Query.setResponse({"status":"ok","table":{"rows":'
        '[{"c":[{"v":"Date(2010,0,2)"},{"v":100},{"v":100},{"v":0},{"v":0},{"v"'
        ':0},{"v":0},{"v":0},{"v":0},{"v":0}]}],"cols":[{"type":"date","id":"ke'
        'y","label":"Day"},{"type":"number","id":"requests","label":"Total"},{"'
        'type":"number","id":"other_requests","label":"Other"},{"type":"number"'
        ',"id":"failures","label":"Failures"},{"type":"number","id":"uploads","'
        'label":"Uploads"},{"type":"number","id":"downloads","label":"Downloads'
        '"},{"type":"number","id":"contains_requests","label":"Lookups"},{"type'
        '":"number","id":"uploads_bytes","label":"Uploaded"},{"type":"number","'
        'id":"downloads_bytes","label":"Downloaded"},{"type":"number","id":"con'
        'tains_lookups","label":"Items looked up"}]},"reqId":"0","version":"0.6'
        '"});')
    self.assertEqual(expected, unicode(resp))

  def disable_test_api_stats_hours(self):
    self._gen_stats()
    # It's cheezy but at least it asserts that the data makes sense.
    expected = (
        'google.visualization.Query.setResponse({"status":"ok","table":{"rows":'
        '[{"c":[{"v":"Date(2010,0,2,3,0,0)"},{"v":10},{"v":10},{"v":0},{"v":0},'
        '{"v":0},{"v":0},{"v":0},{"v":0},{"v":0}]}],"cols":[{"type":"datetime",'
        '"id":"key","label":"Time"},{"type":"number","id":"requests","label":"T'
        'otal"},{"type":"number","id":"other_requests","label":"Other"},{"type"'
        ':"number","id":"failures","label":"Failures"},{"type":"number","id":"u'
        'ploads","label":"Uploads"},{"type":"number","id":"downloads","label":"'
        'Downloads"},{"type":"number","id":"contains_requests","label":"Lookups'
        '"},{"type":"number","id":"uploads_bytes","label":"Uploaded"},{"type":"'
        'number","id":"downloads_bytes","label":"Downloaded"},{"type":"number",'
        '"id":"contains_lookups","label":"Items looked up"}]},"reqId":"0","vers'
        'ion":"0.6"});')
    response = self.app.get(
        '/isolate/api/v1/stats/hours?duration=1&now=')
    self.assertEqual(expected, response.body)

  def disable_test_api_stats_minutes(self):
    self._gen_stats()
    # It's cheezy but at least it asserts that the data makes sense.
    expected = (
        'google.visualization.Query.setResponse({"status":"ok","table":{"rows":'
        '[{"c":[{"v":"Date(2010,0,2,3,4,0)"},{"v":1},{"v":1},{"v":0},{"v":0},{"'
        'v":0},{"v":0},{"v":0},{"v":0},{"v":0}]}],"cols":[{"type":"datetime","i'
        'd":"key","label":"Time"},{"type":"number","id":"requests","label":"Tot'
        'al"},{"type":"number","id":"other_requests","label":"Other"},{"type":"'
        'number","id":"failures","label":"Failures"},{"type":"number","id":"upl'
        'oads","label":"Uploads"},{"type":"number","id":"downloads","label":"Do'
        'wnloads"},{"type":"number","id":"contains_requests","label":"Lookups"}'
        ',{"type":"number","id":"uploads_bytes","label":"Uploaded"},{"type":"nu'
        'mber","id":"downloads_bytes","label":"Downloaded"},{"type":"number","i'
        'd":"contains_lookups","label":"Items looked up"}]},"reqId":"0","versio'
        'n":"0.6"});')
    response = self.app.get('/isolate/api/v1/stats/minutes?duration=1')
    self.assertEqual(expected, response.body)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.FATAL)
  unittest.main()
