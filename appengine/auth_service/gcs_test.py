#!/usr/bin/env vpython
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import unittest

import test_env
test_env.setup_test_env()

from test_support import test_case

from components import net

from proto import config_pb2
import acl
import config
import gcs


class GCSTest(test_case.TestCase):
  def setUp(self):
    super(GCSTest, self).setUp()

    self.expected_update_calls = 0

    self.requests = []
    def _net_request(**kwargs):
      self.requests.append(kwargs)
    self.mock(net, 'request', _net_request)

    self.mock(gcs, '_multipart_payload_boundary', lambda: 'BOUNDARY')

  def tearDown(self):
    try:
      self.assertEqual(0, self.expected_update_calls)
    finally:
      super(GCSTest, self).tearDown()

  def mock_update_gcs_acls(self):
    def _update_gcs_acls():
      self.assertGreater(self.expected_update_calls, 0)
      self.expected_update_calls -= 1
    self.mock(gcs, '_update_gcs_acls', _update_gcs_acls)

  def expect_update_gcs_acls(self):
    self.expected_update_calls += 1

  def mock_config(self, **kwargs):
    settings = config_pb2.SettingsCfg(**kwargs)
    self.mock(config, 'get_settings', lambda: settings)

  def test_authorize_and_deauthorize(self):
    self.mock_update_gcs_acls()

    email = 'a@example.com'

    # Add.
    self.assertFalse(gcs.is_authorized_reader(email))
    self.expect_update_gcs_acls()
    gcs.authorize_reader(email)
    self.assertTrue(gcs.is_authorized_reader(email))

    # Remove.
    self.expect_update_gcs_acls()
    gcs.deauthorize_reader(email)
    self.assertFalse(gcs.is_authorized_reader(email))

  def test_max_acl_entries_limit(self):
    self.mock_update_gcs_acls()

    # Fill up to the limit.
    for i in range(gcs._MAX_ACL_ENTRIES):
      self.expect_update_gcs_acls()
      gcs.authorize_reader('%d@example.com' % i)

    # Readding already existing entry is fine.
    self.expect_update_gcs_acls()
    gcs.authorize_reader('0@example.com')

    # Adding a new one is not fine.
    with self.assertRaises(gcs.Error):
      gcs.authorize_reader('more@example.com')

  def test_revoke_stale_authorization(self):
    self.mock_update_gcs_acls()

    emails = ['a@example.com', 'b@example.com', 'keep@example.com']
    for email in emails:
      self.expect_update_gcs_acls()
      gcs.authorize_reader(email)
    self.assertEqual(emails, gcs._list_authorized_readers())

    # Only keep@... is still authorized.
    self.mock(acl, 'is_trusted_service', lambda i: i.name == 'keep@example.com')

    # Should remove non-authorized emails and update GCS ACLs (once).
    self.expect_update_gcs_acls()
    gcs.revoke_stale_authorization()
    self.assertEqual(['keep@example.com'], gcs._list_authorized_readers())

  def test_upload_auth_db(self):
    self.mock_update_gcs_acls()
    self.mock_config(auth_db_gs_path='bucket/dir')
    self.assertTrue(gcs.is_upload_enabled())

    for email in ['a@example.com', 'b@example.com']:
      self.expect_update_gcs_acls()
      gcs.authorize_reader(email)

    gcs.upload_auth_db('signed blob', 'revision json')

    # Should upload two files and set ACLs to match authorized readers.
    self.assertEqual(2, len(self.requests))
    self.assertEqual({
        'deadline': 30,
        'headers': {'Content-Type': 'multipart/related; boundary=BOUNDARY'},
        'method': 'POST',
        'params': {'uploadType': 'multipart'},
        'payload': '\r\n'.join([
            '--BOUNDARY',
            'Content-Type: application/json; charset=UTF-8',
            '',
            '{"acl":[{"entity":"user-a@example.com","role":"READER"},'
                + '{"entity":"user-b@example.com","role":"READER"}],'
                + '"name":"dir/latest.db"}',
            '--BOUNDARY',
            'Content-Type: application/protobuf',
            '',
            'signed blob',
            '--BOUNDARY--',
            '',
        ]),
        'scopes': ['https://www.googleapis.com/auth/cloud-platform'],
        'url': u'https://www.googleapis.com/upload/storage/v1/b/bucket/o',
    }, self.requests[0])

    self.assertEqual({
        'deadline': 30,
        'headers': {'Content-Type': 'multipart/related; boundary=BOUNDARY'},
        'method': 'POST',
        'params': {'uploadType': 'multipart'},
        'payload': '\r\n'.join([
            '--BOUNDARY',
            'Content-Type: application/json; charset=UTF-8',
            '',
            '{"acl":[{"entity":"user-a@example.com","role":"READER"},'
                + '{"entity":"user-b@example.com","role":"READER"}],'
                + '"name":"dir/latest.json"}',
            '--BOUNDARY',
            'Content-Type: application/json',
            '',
            'revision json',
            '--BOUNDARY--',
            '',
        ]),
        'scopes': ['https://www.googleapis.com/auth/cloud-platform'],
        'url': u'https://www.googleapis.com/upload/storage/v1/b/bucket/o',
    }, self.requests[1])

  def test_update_gcs_acls(self):
    self.mock_config(auth_db_gs_path='bucket/dir')
    self.assertTrue(gcs.is_upload_enabled())

    gcs.authorize_reader('a@example.com')

    self.assertEqual(2, len(self.requests))
    self.assertEqual({
        'deadline': 30,
        'headers': {'Content-Type': 'application/json; charset=UTF-8'},
        'method': 'PUT',
        'payload': '{"acl":[{"entity":"user-a@example.com","role":"READER"}],'
            + '"contentType":"application/protobuf"}',
        'scopes': ['https://www.googleapis.com/auth/cloud-platform'],
        'url': u'https://www.googleapis.com/storage/v1/b/bucket/'
            + 'o/dir%2Flatest.db',
    }, self.requests[0])
    self.assertEqual({
        'deadline': 30,
        'headers': {'Content-Type': 'application/json; charset=UTF-8'},
        'method': 'PUT',
        'payload': '{"acl":[{"entity":"user-a@example.com","role":"READER"}],'
            + '"contentType":"application/json"}',
        'scopes': ['https://www.googleapis.com/auth/cloud-platform'],
        'url': u'https://www.googleapis.com/storage/v1/b/bucket/'
            + 'o/dir%2Flatest.json',
    }, self.requests[1])


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.FATAL)
  unittest.main()
