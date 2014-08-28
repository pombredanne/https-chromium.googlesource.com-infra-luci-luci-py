#!/usr/bin/env python
# Copyright 2013 The Swarming Authors. All rights reserved.
# Use of this source code is governed by the Apache v2.0 license that can be
# found in the LICENSE file.

import datetime
import logging
import os
import sys
import time
import unittest
import urllib

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import test_env
test_env.setup_test_env()

# From components/third_party/
import webtest

from google.appengine.ext import ndb

from components import datastore_utils
from components import template
from components import utils
from support import test_case

import acl
import gcs
import handlers_backend
import handlers_frontend
import model
import stats

# Access to a protected member _XXX of a client class
# pylint: disable=W0212


def hash_item(content):
  h = model.get_hash_algo('default')
  h.update(content)
  return h.hexdigest()


def gen_item(content):
  """Returns data to send to /pre-upload to upload 'content'."""
  return {
    'h': hash_item(content),
    'i': 0,
    's': len(content),
  }


class MainTest(test_case.TestCase):
  """Tests the handlers."""
  APP_DIR = ROOT_DIR

  def setUp(self):
    """Creates a new app instance for every test case."""
    super(MainTest, self).setUp()
    self.testbed.init_user_stub()

    # When called during a taskqueue, the call to get_app_version() may fail so
    # pre-fetch it.
    version = utils.get_app_version()
    self.mock(utils, 'get_task_queue_host', lambda: version)
    self.source_ip = '127.0.0.1'
    self.app_frontend = webtest.TestApp(
        handlers_frontend.create_application(debug=True),
        extra_environ={'REMOTE_ADDR': self.source_ip})
    # This is awkward but both the frontend and backend applications uses the
    # same template variables.
    template.reset()
    self.app_backend = webtest.TestApp(
        handlers_backend.create_application(debug=True),
        extra_environ={'REMOTE_ADDR': self.source_ip})
    # Tasks are enqueued on the backend.
    self.app = self.app_backend

  def tearDown(self):
    template.reset()
    super(MainTest, self).tearDown()

  def whitelist_self(self):
    acl.WhitelistedIP(
        id=acl._ip_to_str(*acl._parse_ip(self.source_ip)),
        ip=self.source_ip).put()

  def mock_acl_checks(self):
    known_groups = (
      acl.READERS_GROUP,
      acl.WRITERS_GROUP,
    )
    self.mock(
        handlers_frontend.auth,
        'is_group_member',
        lambda group: group in known_groups)

  def handshake(self):
    self.whitelist_self()
    self.mock_acl_checks()
    data = {
      'client_app_version': '0.2',
      'fetcher': True,
      'protocol_version': handlers_frontend.ISOLATE_PROTOCOL_VERSION,
      'pusher': True,
    }
    req = self.app_frontend.post_json('/content-gs/handshake', data)
    return urllib.quote(req.json['access_token'])

  def mock_delete_files(self):
    deleted = []
    def delete_files(bucket, files, ignore_missing=False):
      # pylint: disable=W0613
      self.assertEquals('isolateserver-dev', bucket)
      deleted.extend(files)
      return []
    self.mock(gcs, 'delete_files', delete_files)
    return deleted

  def put_content(self, url, content):
    """Simulare isolateserver.py archive."""
    req = self.app_frontend.put(
        url, content_type='application/octet-stream', params=content)
    self.assertEqual(200, req.status_code)
    self.assertEqual({'entry':{}}, req.json)

  # Test cases.

  def test_pre_upload_ok(self):
    req = self.app_frontend.post_json(
        '/content-gs/pre-upload/a?token=%s' % self.handshake(),
        [gen_item('foo')])
    self.assertEqual(1, len(req.json))
    self.assertEqual(2, len(req.json[0]))
    # ['url', None]
    self.assertTrue(req.json[0][0])
    self.assertEqual(None, req.json[0][1])

  def test_pre_upload_invalid_namespace(self):
    req = self.app_frontend.post_json(
        '/content-gs/pre-upload/[?token=%s' % self.handshake(),
        [gen_item('foo')],
        expect_errors=True)
    self.assertTrue(
        'Invalid namespace; allowed keys must pass regexp "[a-z0-9A-Z\-._]+"' in
        req.body)

  def test_upload_tag_expire(self):
    # Complete integration test that ensures tagged items are properly saved and
    # non tagged items are dumped.
    # Use small objects so it doesn't exercise the GS code path.
    deleted = self.mock_delete_files()
    items = ['bar', 'foo']
    now = datetime.datetime(2012, 01, 02, 03, 04, 05, 06)
    self.mock(utils, 'utcnow', lambda: now)
    self.mock(ndb.DateTimeProperty, '_now', lambda _: now)
    self.mock(ndb.DateProperty, '_now', lambda _: now.date())

    r = self.app_frontend.post_json(
        '/content-gs/pre-upload/default?token=%s' % self.handshake(),
        [gen_item(i) for i in items])
    self.assertEqual(len(items), len(r.json))
    self.assertEqual(0, len(list(model.ContentEntry.query())))

    for content, urls in zip(items, r.json):
      self.assertEqual(2, len(urls))
      self.assertEqual(None, urls[1])
      self.put_content(urls[0], content)
    self.assertEqual(2, len(list(model.ContentEntry.query())))
    expiration = 7*24*60*60
    self.assertEqual(0, self.execute_tasks())

    # Advance time, tag the first item.
    now += datetime.timedelta(seconds=2*expiration)
    self.assertEqual(
        datetime.datetime(2012, 01, 16, 03, 04, 05, 06), utils.utcnow())
    r = self.app_frontend.post_json(
        '/content-gs/pre-upload/default?token=%s' % self.handshake(),
        [gen_item(items[0])])
    self.assertEqual(200, r.status_code)
    self.assertEqual([None], r.json)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(2, len(list(model.ContentEntry.query())))

    # 'bar' was kept, 'foo' was cleared out.
    headers = {'X-AppEngine-Cron': 'true'}
    resp = self.app_backend.get(
        '/internal/cron/cleanup/trigger/old', headers=headers)
    self.assertEqual(200, resp.status_code)
    self.assertEqual([None], r.json)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(1, len(list(model.ContentEntry.query())))
    self.assertEqual('bar', model.ContentEntry.query().get().content)

    # Advance time and force cleanup. This deletes 'bar' too.
    now += datetime.timedelta(seconds=2*expiration)
    headers = {'X-AppEngine-Cron': 'true'}
    resp = self.app_backend.get(
        '/internal/cron/cleanup/trigger/old', headers=headers)
    self.assertEqual(200, resp.status_code)
    self.assertEqual([None], r.json)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(0, len(list(model.ContentEntry.query())))

    # Advance time and force cleanup.
    now += datetime.timedelta(seconds=2*expiration)
    headers = {'X-AppEngine-Cron': 'true'}
    resp = self.app_backend.get(
        '/internal/cron/cleanup/trigger/old', headers=headers)
    self.assertEqual(200, resp.status_code)
    self.assertEqual([None], r.json)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(0, len(list(model.ContentEntry.query())))

    # All items expired are tried to be deleted from GS. This is the trade off
    # between having to fetch the items vs doing unneeded requests to GS for the
    # inlined objects.
    expected = sorted('default/' + hash_item(i) for i in items)
    self.assertEqual(expected, sorted(deleted))

  def test_ancestor_assumption(self):
    prefix = '1234'
    suffix = 40 - len(prefix)
    c = model.new_content_entry(model.entry_key('n', prefix + '0' * suffix))
    self.assertEqual(0, len(list(model.ContentEntry.query())))
    c.put()
    self.assertEqual(1, len(list(model.ContentEntry.query())))

    c = model.new_content_entry(model.entry_key('n', prefix + '1' * suffix))
    self.assertEqual(1, len(list(model.ContentEntry.query())))
    c.put()
    self.assertEqual(2, len(list(model.ContentEntry.query())))

    actual_prefix = c.key.parent().id()
    k = datastore_utils.shard_key(
        actual_prefix, len(actual_prefix), 'ContentShard')
    self.assertEqual(2, len(list(model.ContentEntry.query(ancestor=k))))

  def test_trim_missing(self):
    deleted = self.mock_delete_files()
    def gen_file(i, t=0):
      return (i, gcs.cloudstorage.GCSFileStat(i, 100, 'etag', t))
    mock_files = [
        # Was touched.
        gen_file('d/' + '0' * 40),
        # Is deleted.
        gen_file('d/' + '1' * 40),
        # Too recent.
        gen_file('d/' + '2' * 40, time.time() - 60),
    ]
    self.mock(gcs, 'list_files', lambda _: mock_files)

    model.ContentEntry(key=model.entry_key('d', '0' * 40)).put()
    headers = {'X-AppEngine-Cron': 'true'}
    resp = self.app_backend.get(
        '/internal/cron/cleanup/trigger/trim_lost', headers=headers)
    self.assertEqual(200, resp.status_code)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(['d/' + '1' * 40], deleted)

  def test_verify(self):
    # Upload a file larger than MIN_SIZE_FOR_DIRECT_GS and ensure the verify
    # task works.
    data = '0' * handlers_frontend.MIN_SIZE_FOR_DIRECT_GS
    req = self.app_frontend.post_json(
        '/content-gs/pre-upload/default?token=%s' % self.handshake(),
        [gen_item(data)])
    self.assertEqual(1, len(req.json))
    self.assertEqual(2, len(req.json[0]))
    # ['url', 'url']
    self.assertTrue(req.json[0][0])
    # Fake the upload by calling the second function.
    self.mock(gcs, 'get_file_info', lambda _b, _f: gcs.FileInfo(size=len(data)))
    req = self.app_frontend.post(req.json[0][1], '')

    self.mock(gcs, 'read_file', lambda _b, _f: [data])
    self.assertEqual(1, self.execute_tasks())

    # Assert the object is still there.
    self.assertEqual(1, len(list(model.ContentEntry.query())))

  def test_verify_corrupted(self):
    # Upload a file larger than MIN_SIZE_FOR_DIRECT_GS and ensure the verify
    # task works.
    data = '0' * handlers_frontend.MIN_SIZE_FOR_DIRECT_GS
    req = self.app_frontend.post_json(
        '/content-gs/pre-upload/default?token=%s' % self.handshake(),
        [gen_item(data)])
    self.assertEqual(1, len(req.json))
    self.assertEqual(2, len(req.json[0]))
    # ['url', 'url']
    self.assertTrue(req.json[0][0])
    # Fake the upload by calling the second function.
    self.mock(gcs, 'get_file_info', lambda _b, _f: gcs.FileInfo(size=len(data)))
    req = self.app_frontend.post(req.json[0][1], '')

    # Fake corruption
    data_corrupted = '1' * handlers_frontend.MIN_SIZE_FOR_DIRECT_GS
    self.mock(gcs, 'read_file', lambda _b, _f: [data_corrupted])
    deleted = self.mock_delete_files()
    self.assertEqual(1, self.execute_tasks())

    # Assert the object is gone.
    self.assertEqual(0, len(list(model.ContentEntry.query())))
    self.assertEqual(['default/' + hash_item(data)], deleted)

  def _gen_stats(self):
    # Generates data for the last 10 days, last 10 hours and last 10 minutes.
    # TODO(maruel): Stop accessing the DB directly. Use stats_framework_mock to
    # generate it.
    now = datetime.datetime(2010, 1, 2, 3, 4, 5, 6)
    self.mock_now(now, 0)
    handler = stats.STATS_HANDLER
    for i in xrange(10):
      s = stats._Snapshot(requests=100 + i)
      day = (now - datetime.timedelta(days=i)).date()
      handler.stats_day_cls(key=handler.day_key(day), values_compressed=s).put()

    for i in xrange(10):
      s = stats._Snapshot(requests=10 + i)
      timestamp = (now - datetime.timedelta(hours=i))
      handler.stats_hour_cls(
          key=handler.hour_key(timestamp), values_compressed=s).put()

    for i in xrange(10):
      s = stats._Snapshot(requests=1 + i)
      timestamp = (now - datetime.timedelta(minutes=i))
      handler.stats_minute_cls(
          key=handler.minute_key(timestamp), values_compressed=s).put()

  def test_stats(self):
    self._gen_stats()
    response = self.app_frontend.get('/stats')
    # Just ensure something is returned.
    self.assertGreater(response.content_length, 4000)

  def test_api_stats_days(self):
    self._gen_stats()
    # It's cheezy but at least it asserts that the data makes sense.
    expected = (
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
    response = self.app_frontend.get('/isolate/api/v1/stats/days?duration=1')
    self.assertEqual(expected, response.body)

  def test_api_stats_hours(self):
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
    response = self.app_frontend.get(
        '/isolate/api/v1/stats/hours?duration=1&now=')
    self.assertEqual(expected, response.body)

  def test_api_stats_minutes(self):
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
    response = self.app_frontend.get('/isolate/api/v1/stats/minutes?duration=1')
    self.assertEqual(expected, response.body)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.FATAL)
  unittest.main()
