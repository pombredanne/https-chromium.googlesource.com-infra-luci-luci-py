#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import collections
import datetime
import time
import json
import sys
import unittest

from test_support import test_env
test_env.setup_test_env()

from google.appengine.ext import ndb

from components import utils
from components.auth import exceptions
from components.auth import project_tokens
from components.auth import service_account
from components.auth import model

from test_support import test_case


class CreateTokenTest(test_case.TestCase):

  Response = collections.namedtuple('Response', ['status_code', 'content'])

  def test_success(self):
    self.mock_now(datetime.datetime(2015, 1, 1))

    def totimestamp(datetimeobj):
      return int(time.mktime(datetimeobj.timetuple()))

    @ndb.tasklet
    def urlfetch(url, payload, **_rest):
      urlfetch.called = True
      self.assertEqual(
          url,
          'https://tokens.example.com/prpc/tokenserver.minter.TokenMinter/'
              'MintProjectToken')
      payload = json.loads(payload)
      self.assertEqual(payload, urlfetch.expected_payload)
      expiry = utils.utcnow() + datetime.timedelta(seconds=1800)
      res = {
        'access_token': 'deadbeef',
        'service_account_email': 'foo@bar.com',
        'expiry': totimestamp(expiry),
      }

      raise ndb.Return(
          self.Response(200, json.dumps(res, sort_keys=True)))

    urlfetch.expected_payload = {
      u'luci_project': u'test-project',
      u'oauth_scope': [
        u'https://www.googleapis.com/auth/cloud-platform',
      ],
      u'min_validity_duration': 300,
      u'audit_tags': [],
    }

    urlfetch.called = False

    self.mock(service_account, '_urlfetch_async', urlfetch)

    model.AuthReplicationState(
        key=model.replication_state_key(),
        primary_url='https://auth.example.com',
        primary_id='example-app-id',
    ).put()
    model.AuthGlobalConfig(
      key=model.root_key(),
      token_server_url='https://tokens.example.com',
    ).put()

    args = {
      'project_id': 'test-project',
      'oauth_scopes': [
        u'https://www.googleapis.com/auth/cloud-platform',
      ],
      'min_validity_duration_sec': 300,
      'auth_request_func': service_account.authenticated_request_async,
    }
    result = project_tokens.project_token(**args)
    self.assertTrue(urlfetch.called)
    self.assertEqual(result.token, 'deadbeef')
    self.assertEqual(
        result.expiry,
        totimestamp(utils.utcnow() + datetime.timedelta(seconds=1800)))

    # Get from cache.
    urlfetch.called = False
    project_tokens.project_token(**args)
    self.assertFalse(urlfetch.called)

    # Get from cache with larger validity duration.
    urlfetch.called = False
    args['min_validity_duration_sec'] = 1200
    urlfetch.expected_payload[u'min_validity_duration'] = 1200
    result = project_tokens.project_token(**args)
    self.assertTrue(urlfetch.called)
    self.assertEqual(result.token, 'deadbeef')
    self.assertEqual(
        result.expiry,
        totimestamp(utils.utcnow() + datetime.timedelta(seconds=1800)))
    self.assertTrue(urlfetch.called)

  def test_http_500(self):
    res = ndb.Future()
    res.set_result(self.Response(500, 'Server internal error'))
    self.mock(service_account, '_urlfetch_async', lambda  **_k: res)

    with self.assertRaises(exceptions.TokenCreationError):
      project_tokens.project_token(
        project_id = 'luci-project',
        oauth_scopes=['https://www.googleapis.com/auth/cloud-platform'],
        auth_request_func=service_account.authenticated_request_async,
        min_validity_duration_sec=5*60,
        tags=None,
        token_server_url='https://example.com')

  def test_http_403(self):
    res = ndb.Future()
    res.set_result(self.Response(403, 'Not authorized'))
    self.mock(service_account, '_urlfetch_async', lambda  **_k: res)

    with self.assertRaises(exceptions.TokenAuthorizationError):
      project_tokens.project_token(
        project_id=['test-project'],
        oauth_scopes=['https://www.googleapis.com/auth/cloud-platform'],
        auth_request_func=service_account.authenticated_request_async,
        min_validity_duration_sec=5*60,
        tags=None,
        token_server_url='https://example.com')


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
