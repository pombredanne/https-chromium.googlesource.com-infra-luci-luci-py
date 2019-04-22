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


def serialize_token(tok):
  return tokens.base64_encode(tok.SerializeToString())


def seal_token(subtoken):
  serialized = subtoken.SerializeToString()
  signing_key_id, pkcs1_sha256_sig = signature.sign_blob(serialized, 0.5)
  return delegation_pb2.DelegationToken(
      serialized_subtoken=serialized,
      signer_id=model.get_service_self_identity().to_bytes(),
      signing_key_id=signing_key_id,
      pkcs1_sha256_sig=pkcs1_sha256_sig)


class SerializationTest(test_case.TestCase):
  def test_serialization_works(self):
    msg = fake_token_proto()
    tok = serialize_token(msg)
    self.assertEqual(msg, delegation.deserialize_token(tok))

  def test_deserialize_huge(self):
    msg = fake_token_proto()
    msg.serialized_subtoken = 'huge' * 10000
    tok = tokens.base64_encode(msg.SerializeToString())
    with self.assertRaises(delegation.BadTokenError):
      delegation.deserialize_token(tok)

  def test_deserialize_not_base64(self):
    msg = fake_token_proto()
    tok = serialize_token(msg)
    tok += 'not base 64'
    with self.assertRaises(delegation.BadTokenError):
      delegation.deserialize_token(tok)

  def test_deserialize_bad_proto(self):
    tok = tokens.base64_encode('not a proto')
    with self.assertRaises(delegation.BadTokenError):
      delegation.deserialize_token(tok)


class ValidationTest(test_case.TestCase):
  def test_passes_validation(self):
    tok = fake_subtoken_proto('user:abc@example.com')
    ident = delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB())
    self.assertEqual('user:abc@example.com', ident.to_bytes())

  def test_negative_validatity_duration(self):
    tok = fake_subtoken_proto('user:abc@example.com', validity_duration=-3600)
    with self.assertRaises(delegation.BadTokenError):
      delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB())

  def test_expired(self):
    now = int(utils.time_time())
    tok = fake_subtoken_proto(
        'user:abc@example.com', creation_time=now-120, validity_duration=60)
    with self.assertRaises(delegation.BadTokenError):
      delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB())

  def test_not_active_yet(self):
    now = int(utils.time_time())
    tok = fake_subtoken_proto('user:abc@example.com', creation_time=now+120)
    with self.assertRaises(delegation.BadTokenError):
      delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB())

  def test_allowed_clock_drift(self):
    now = utils.utcnow()
    self.mock_now(now)
    tok = fake_subtoken_proto('user:abc@example.com')
    # Works -29 sec before activation.
    self.mock_now(now, -29)
    self.assertTrue(delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB()))
    # Doesn't work before that.
    self.mock_now(now, -31)
    with self.assertRaises(delegation.BadTokenError):
      delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB())

  def test_expiration_moment(self):
    now = utils.utcnow()
    self.mock_now(now)
    tok = fake_subtoken_proto('user:abc@example.com', validity_duration=3600)
    # Active at now + 3599.
    self.mock_now(now, 3599)
    self.assertTrue(delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB()))
    # Expired at now + 3601.
    self.mock_now(now, 3601)
    with self.assertRaises(delegation.BadTokenError):
      delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB())

  def test_subtoken_services(self):
    tok = fake_subtoken_proto(
        'user:abc@example.com', services=['service:app-id'])
    # Passes.
    self.mock(
        model, 'get_service_self_identity',
        lambda: model.Identity.from_bytes('service:app-id'))
    self.assertTrue(delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB()))
    # Fails.
    self.mock(
        model, 'get_service_self_identity',
        lambda: model.Identity.from_bytes('service:another-app-id'))
    with self.assertRaises(delegation.BadTokenError):
      delegation.check_subtoken(tok, FAKE_IDENT, api.AuthDB())

  def test_subtoken_audience(self):
    auth_db = api.AuthDB(groups=[model.AuthGroup(
      id='abc', members=[model.Identity.from_bytes('user:b@b.com')],
    )])
    tok = fake_subtoken_proto(
          'user:abc@example.com', audience=['user:a@a.com', 'group:abc'])
    # Works.
    make_id = model.Identity.from_bytes
    self.assertTrue(
        delegation.check_subtoken(tok, make_id('user:a@a.com'), auth_db))
    self.assertTrue(
        delegation.check_subtoken(tok, make_id('user:b@b.com'), auth_db))
    # Other ids are rejected.
    with self.assertRaises(delegation.BadTokenError):
      delegation.check_subtoken(tok, make_id('user:c@c.com'), auth_db)


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
    self.mock(delegation, '_urlfetch_async', lambda  **_k: res)

    with self.assertRaises(delegation.DelegationTokenCreationError):
      delegation.delegate(
        audience=['*'],
        services=['*'],
        token_server_url='https://example.com')

  def test_http_403(self):
    res = ndb.Future()
    res.set_result(self.Response(403, 'Not authorized'))
    self.mock(delegation, '_urlfetch_async', lambda  **_k: res)

    with self.assertRaises(delegation.DelegationAuthorizationError):
      delegation.delegate(
        audience=['*'],
        services=['*'],
        token_server_url='https://example.com')


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
