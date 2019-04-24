#!/usr/bin/env python
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import collections
import datetime
import json
import sys
import unittest

from test_support import test_env
test_env.setup_test_env()

from google.appengine.ext import ndb

from components import utils
from components.auth import api
from components.auth import project_tokens
from components.auth import model
from components.auth import signature
from components.auth import tokens

from test_support import test_case


class CreateTokenTest(test_case.TestCase):

  Response = collections.namedtuple('Response', ['status_code', 'content'])

  def test_success(self):
    self.mock_now(datetime.datetime(2015, 1, 1))

    @ndb.tasklet
    def urlfetch(url, payload, **_rest):
      urlfetch.called = True
      self.assertEqual(
          url,
          'https://tokens.example.com/prpc/tokenserver.minter.TokenMinter/'
              'MintDelegationToken')
      payload = json.loads(payload)
      self.assertEqual(payload, urlfetch.expected_payload)
      res = {
        'token': 'deadbeef',
        'serviceVersion': 'app-id/version-id',
        'delegationSubtoken': {
          'kind': 'BEARER_DELEGATION_TOKEN',
          'validityDuration': payload['validityDuration'],
          'subtokenId': '12345',
        },
      }
      raise ndb.Return(
          self.Response(200, ")]}'\n" + json.dumps(res, sort_keys=True)))

    urlfetch.expected_payload = {
      u'audience': [
        u'REQUESTOR',
        u'group:g',
        u'user:a1@example.com',
        u'user:a2@example.com',
      ],
      u'services': [u'https://example.com', u'service:1', u'service:2'],
      u'delegatedIdentity': u'user:i@example.com',
      u'tags': [u'a:b', u'c:d'],
      u'validityDuration': 3000,
    }
    urlfetch.called = False

    self.mock(delegation, '_urlfetch_async', urlfetch)

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
      'audience': [
        'user:a1@example.com',
        model.Identity('user', 'a2@example.com'),
        'group:g',
        'REQUESTOR',
      ],
      'services': [
        'service:1',
        model.Identity('service', '2'),
        'https://example.com',
      ],
      'max_validity_duration_sec': 3000,
      'impersonate': model.Identity('user', 'i@example.com'),
      'tags': ['c:d', 'a:b'],
    }
    result = delegation.delegate(**args)
    self.assertTrue(urlfetch.called)
    self.assertEqual(result.token, 'deadbeef')
    self.assertEqual(
        result.expiry, utils.utcnow() + datetime.timedelta(seconds=3000))

    # Get from cache.
    urlfetch.called = False
    delegation.delegate(**args)
    self.assertFalse(urlfetch.called)

    # Get from cache with larger validity duration.
    urlfetch.called = False
    args['min_validity_duration_sec'] = 5000
    args['max_validity_duration_sec'] = 5000
    urlfetch.expected_payload['validityDuration'] = 5000
    result = delegation.delegate(**args)
    self.assertTrue(urlfetch.called)
    self.assertEqual(result.token, 'deadbeef')
    self.assertEqual(
        result.expiry, utils.utcnow() + datetime.timedelta(seconds=5000))
    self.assertTrue(urlfetch.called)

  def test_http_500(self):
    res = ndb.Future()
    res.set_result(self.Response(500, 'Server internal error'))
    self.mock(project_tokens, '_urlfetch_async', lambda  **_k: res)

    with self.assertRaises(project_tokens.ProjectTokenCreationError):
      project_tokens.project_token(
        oauth_scopes=[''],
        min_validity_duration_sec=5*60,
        tags=None,
        token_server_url='https://example.com')

  def test_http_403(self):
    res = ndb.Future()
    res.set_result(self.Response(403, 'Not authorized'))
    self.mock(project_tokens, '_urlfetch_async', lambda  **_k: res)

    with self.assertRaises(project_tokens.ProjectTokenAuthorizationError):
      project_tokens.project_token(
        oauth_scopes=[''],
        min_validity_duration_sec=5*60,
        tags=None,
        token_server_url='https://example.com')


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
