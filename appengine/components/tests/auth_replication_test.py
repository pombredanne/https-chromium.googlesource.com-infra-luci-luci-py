#!/usr/bin/env python
# Copyright 2014 The Swarming Authors. All rights reserved.
# Use of this source code is governed by the Apache v2.0 license that can be
# found in the LICENSE file.

import datetime
import sys
import unittest

import test_env
test_env.setup_test_env()

from google.appengine.ext import ndb

from support import test_case
from components import utils

from components.auth import model
from components.auth import replication


def entity_to_dict(e):
  """Same as e.to_dict() but also adds entity key to the dict."""
  d = e.to_dict()
  d['__id__'] = e.key.id()
  d['__parent__'] = e.key.parent()
  return d


def snapshot_to_dict(snapshot):
  """AuthDBSnapshot -> dict (for comparisons)."""
  result = {
    'global_config': entity_to_dict(snapshot.global_config),
    'groups': [entity_to_dict(g) for g in snapshot.groups],
    'secrets': [entity_to_dict(s) for s in snapshot.secrets],
    'ip_whitelists': [entity_to_dict(l) for l in snapshot.ip_whitelists],
  }
  # Ensure no new keys are forgotten.
  assert len(snapshot) == len(result)
  return result


class NewAuthDBSnapshotTest(test_case.TestCase):
  """Tests for new_auth_db_snapshot function."""

  def test_empty(self):
    state, snapshot = replication.new_auth_db_snapshot()
    self.assertIsNone(state)
    expected_snapshot = {
      'global_config': {
        '__id__': 'root',
        '__parent__': None,
        'oauth_additional_client_ids': [],
        'oauth_client_id': '',
        'oauth_client_secret': ''
      },
      'groups': [],
      'secrets': [],
      'ip_whitelists': [],
    }
    self.assertEqual(expected_snapshot, snapshot_to_dict(snapshot))

  def test_non_empty(self):
    self.mock_now(datetime.datetime(2014, 1, 1, 1, 1, 1))

    state = model.AuthReplicationState(
        key=model.REPLICATION_STATE_KEY,
        primary_id='blah',
        primary_url='https://blah',
        auth_db_rev=123)
    state.put()

    global_config = model.AuthGlobalConfig(
        key=model.ROOT_KEY,
        oauth_client_id='oauth_client_id',
        oauth_client_secret='oauth_client_secret',
        oauth_additional_client_ids=['a', 'b'])
    global_config.put()

    group = model.AuthGroup(
        key=model.group_key('Some group'),
        members=[model.Identity.from_bytes('user:a@example.com')],
        globs=[model.IdentityGlob.from_bytes('user:*@example.com')],
        nested=[],
        description='Some description',
        created_by=model.Identity.from_bytes('user:creator@example.com'),
        modified_by=model.Identity.from_bytes('user:modifier@example.com'))
    group.put()

    another = model.AuthGroup(
        key=model.group_key('Another group'),
        nested=['Some group'])
    another.put()

    global_secret = model.AuthSecret(
        id='global_secret',
        parent=model.secret_scope_key('global'),
        values=['1234', '5678'],
        modified_by=model.Identity.from_bytes('user:modifier@example.com'))
    global_secret.put()

    # Local secret should not appear in a snapshot.
    local_secret = model.AuthSecret(
        id='local_secret',
        parent=model.secret_scope_key('local'),
        values=['1234', '5678'],
        modified_by=model.Identity.from_bytes('user:modifier@example.com'))
    local_secret.put()

    ip_whitelist = model.AuthIPWhitelist(
        key=model.ip_whitelist_key('bots'),
        subnets=['127.0.0.1/32'],
        description='Some description',
        created_by=model.Identity.from_bytes('user:creator@example.com'),
        modified_by=model.Identity.from_bytes('user:modifier@example.com'))
    ip_whitelist.put()

    captured_state, snapshot = replication.new_auth_db_snapshot()

    expected_state =  {
      'auth_db_rev': 123,
      'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
      'primary_id': u'blah',
      'primary_url': u'https://blah',
    }
    self.assertEqual(expected_state, captured_state.to_dict())

    expected_snapshot = {
      'global_config': {
        '__id__': 'root',
        '__parent__': None,
        'oauth_additional_client_ids': [u'a', u'b'],
        'oauth_client_id': u'oauth_client_id',
        'oauth_client_secret': u'oauth_client_secret',
      },
      'groups': [
        {
          '__id__': 'Another group',
          '__parent__': ndb.Key('AuthGlobalConfig', 'root'),
          'created_by': None,
          'created_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'description': '',
          'globs': [],
          'members': [],
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'nested': [u'Some group'],
        },
        {
          '__id__': 'Some group',
          '__parent__': ndb.Key('AuthGlobalConfig', 'root'),
          'created_by': model.Identity(kind='user', name='creator@example.com'),
          'created_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'description': u'Some description',
          'globs': [model.IdentityGlob(kind='user', pattern='*@example.com')],
          'members': [model.Identity(kind='user', name='a@example.com')],
          'modified_by': model.Identity(
              kind='user', name='modifier@example.com'),
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'nested': [],
        },
      ],
      'secrets': [
        {
          '__id__': 'global_secret',
          '__parent__': ndb.Key(
              'AuthGlobalConfig', 'root', 'AuthSecretScope', 'global'),
          'modified_by': model.Identity(
              kind='user', name='modifier@example.com'),
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'values': ['1234', '5678'],
        },
      ],
      'ip_whitelists': [
        {
          '__id__': 'bots',
          '__parent__': ndb.Key('AuthGlobalConfig', 'root'),
          'created_by': model.Identity(kind='user', name='creator@example.com'),
          'created_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'description': u'Some description',
          'modified_by': model.Identity(
              kind='user', name='modifier@example.com'),
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'subnets': ['127.0.0.1/32'],
        },
      ]
    }
    self.assertEqual(expected_snapshot, snapshot_to_dict(snapshot))


class SnapshotToProtoConversionTest(test_case.TestCase):
  """Tests for entities <-> proto conversion."""

  def assert_serialization_works(self, snapshot):
    """Ensures AuthDBSnapshot == AuthDBSnapshot -> proto -> AuthDBSnapshot."""
    roundtrip = replication.proto_to_auth_db_snapshot(
        replication.auth_db_snapshot_to_proto(snapshot))
    self.assertEqual(snapshot_to_dict(snapshot), snapshot_to_dict(roundtrip))

  def test_empty(self):
    """Serializing empty snapshot."""
    snapshot = replication.AuthDBSnapshot(
        model.AuthGlobalConfig(key=model.ROOT_KEY), [], [], [])
    self.assert_serialization_works(snapshot)

  def test_global_config_serialization(self):
    """Serializing snapshot with non-trivial AuthGlobalConfig."""
    snapshot = replication.AuthDBSnapshot(
        model.AuthGlobalConfig(
            key=model.ROOT_KEY,
            oauth_client_id='some-client-id',
            oauth_client_secret='some-client-secret',
            oauth_additional_client_ids=['id1', 'id2']),
        [], [], [])
    self.assert_serialization_works(snapshot)

  def test_group_serialization(self):
    """Serializing snapshot with non-trivial AuthGroup."""
    group = model.AuthGroup(
        key=model.group_key('some-group'),
        members=[
          model.Identity.from_bytes('user:punch@example.com'),
          model.Identity.from_bytes('user:judy@example.com'),
        ],
        globs=[model.IdentityGlob.from_bytes('user:*@example.com')],
        nested=['Group A', 'Group B'],
        description='Blah blah blah',
        created_ts=utils.utcnow(),
        created_by=model.Identity.from_bytes('user:creator@example.com'),
        modified_ts=utils.utcnow(),
        modified_by=model.Identity.from_bytes('user:modifier@example.com'),
    )
    snapshot = replication.AuthDBSnapshot(
        model.AuthGlobalConfig(key=model.ROOT_KEY), [group], [], [])
    self.assert_serialization_works(snapshot)

  def test_secret_serialization(self):
    """Serializing snapshot with non-trivial AuthSecret."""
    secret = model.AuthSecret(
        id='secret key',
        parent=model.secret_scope_key('global'),
        values=['\x00' * 100, ''],
        modified_ts=utils.utcnow(),
        modified_by=model.Identity.from_bytes('user:modifier@example.com'))
    snapshot = replication.AuthDBSnapshot(
        model.AuthGlobalConfig(key=model.ROOT_KEY), [], [secret], [])
    self.assert_serialization_works(snapshot)

  def test_ip_whitelist_serialization(self):
    """Serializing snapshot with non-trivial IP whitelist."""
    ip_whitelist = model.AuthIPWhitelist(
        key=model.ip_whitelist_key('bots'),
        subnets=['127.0.0.1/32'],
        description='Blah blah blah',
        created_ts=utils.utcnow(),
        created_by=model.Identity.from_bytes('user:creator@example.com'),
        modified_ts=utils.utcnow(),
        modified_by=model.Identity.from_bytes('user:modifier@example.com'),
    )
    snapshot = replication.AuthDBSnapshot(
        model.AuthGlobalConfig(key=model.ROOT_KEY), [], [], [ip_whitelist])
    self.assert_serialization_works(snapshot)


class ReplaceAuthDbTest(test_case.TestCase):
  """Tests for replace_auth_db function."""

  @staticmethod
  def configure_as_replica(auth_db_rev=0, modified_ts=None):
    state = model.AuthReplicationState(
         key=model.REPLICATION_STATE_KEY,
         primary_id='primary',
         primary_url='https://primary',
         auth_db_rev=auth_db_rev,
         modified_ts=modified_ts)
    state.put()

  def test_works(self):
    self.mock_now(datetime.datetime(2014, 1, 1, 1, 1, 1))
    self.configure_as_replica(0)

    # Prepare auth db state.
    model.AuthGlobalConfig(
        key=model.ROOT_KEY,
        oauth_client_id='oauth_client_id',
        oauth_client_secret='oauth_client_secret',
        oauth_additional_client_ids=['a', 'b']).put()

    def group(name, **kwargs):
      return model.AuthGroup(key=model.group_key(name), **kwargs)
    group('Modify').put()
    group('Delete').put()
    group('Keep').put()

    def secret(name, scope, **kwargs):
      return model.AuthSecret(
          id=name, parent=model.secret_scope_key(scope), **kwargs)
    secret('modify', 'global').put()
    secret('delete', 'global').put()
    secret('keep', 'global').put()
    secret('local', 'local').put()

    # TODO(vadimsh): Add more cases when 'new_auth_db_snapshot' doesn't hardcode
    # 'bots' anymore.
    def ip_whitelist(name, **kwargs):
      return model.AuthIPWhitelist(key=model.ip_whitelist_key(name), **kwargs)
    ip_whitelist('bots').put()

    # Prepare snapshot.
    snapshot = replication.AuthDBSnapshot(
        global_config=model.AuthGlobalConfig(
            key=model.ROOT_KEY,
            oauth_client_id='another_oauth_client_id',
            oauth_client_secret='another_oauth_client_secret',
            oauth_additional_client_ids=[]),
        groups=[
          group('New'),
          group('Modify', description='blah'),
          group('Keep'),
        ],
        secrets=[
          secret('new', 'global'),
          secret('modify', 'global', values=['1234']),
          secret('keep', 'global'),
        ],
        ip_whitelists=[
          ip_whitelist('bots', subnets=['127.0.0.1/32']),
        ])

    # Push it.
    updated, state = replication.replace_auth_db(
        auth_db_rev=1234,
        modified_ts=datetime.datetime(2014, 1, 1, 1, 1, 1),
        snapshot=snapshot)
    self.assertTrue(updated)
    expected_state = {
      'auth_db_rev': 1234,
      'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
      'primary_id': u'primary',
      'primary_url': u'https://primary',
    }
    self.assertEqual(expected_state, state.to_dict())

    # Verify expected Auth db state.
    current_state, current_snapshot = replication.new_auth_db_snapshot()
    self.assertEqual(expected_state, current_state.to_dict())

    expected_auth_db = {
      'global_config': {
        '__id__': 'root',
        '__parent__': None,
        'oauth_additional_client_ids': [],
        'oauth_client_id': u'another_oauth_client_id',
        'oauth_client_secret': u'another_oauth_client_secret'},
      'groups': [
        {
          '__id__': 'Keep',
          '__parent__': ndb.Key('AuthGlobalConfig', 'root'),
          'created_by': None,
          'created_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'description': '',
          'globs': [],
          'members': [],
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'nested': [],
        },
        {
          '__id__': 'Modify',
          '__parent__': ndb.Key('AuthGlobalConfig', 'root'),
          'created_by': None,
          'created_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'description': u'blah',
          'globs': [],
          'members': [],
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'nested': [],
        },
        {
          '__id__': 'New',
          '__parent__': ndb.Key('AuthGlobalConfig', 'root'),
          'created_by': None,
          'created_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'description': '',
          'globs': [],
          'members': [],
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'nested': [],
        },
      ],
      'secrets': [
        {
          '__id__': 'keep',
          '__parent__': ndb.Key(
              'AuthGlobalConfig', 'root', 'AuthSecretScope', 'global'),
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'values': [],
        },
        {
          '__id__': 'modify',
          '__parent__': ndb.Key(
              'AuthGlobalConfig', 'root', 'AuthSecretScope', 'global'),
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'values': ['1234'],
        },
        {
          '__id__': 'new',
          '__parent__': ndb.Key(
              'AuthGlobalConfig', 'root', 'AuthSecretScope', 'global'),
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'values': [],
        },
      ],
      'ip_whitelists': [
        {
          '__id__': 'bots',
          '__parent__': ndb.Key('AuthGlobalConfig', 'root'),
          'created_by': None,
          'created_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'description': '',
          'modified_by': None,
          'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
          'subnets': ['127.0.0.1/32'],
        },
      ],
    }
    self.assertEqual(expected_auth_db, snapshot_to_dict(current_snapshot))

    # Ensure local secret was left intact.
    local_secrets = model.AuthSecret.query(
        ancestor=model.secret_scope_key('local'))
    expected_local_secrets = [
      {
        '__id__': 'local',
        '__parent__': ndb.Key(
            'AuthGlobalConfig', 'root', 'AuthSecretScope', 'local'),
        'modified_by': None,
        'modified_ts': datetime.datetime(2014, 1, 1, 1, 1, 1),
        'values': [],
      },
    ]
    self.assertEqual(
        expected_local_secrets, [entity_to_dict(s) for s in local_secrets])

  def test_old_rev(self):
    """Refuses to push with old auth_db revision."""
    self.configure_as_replica(123, datetime.datetime(2000, 1, 1, 1, 1, 1))
    updated, state = replication.replace_auth_db(
        auth_db_rev=123,
        modified_ts=datetime.datetime(2014, 1, 1, 1, 1, 1),
        snapshot=replication.AuthDBSnapshot(
            model.AuthGlobalConfig(key=model.ROOT_KEY), [], [], []))
    self.assertFalse(updated)
    # Old modified_ts, update is not applied.
    expected_state = {
      'auth_db_rev': 123,
      'modified_ts': datetime.datetime(2000, 1, 1, 1, 1, 1),
      'primary_id': u'primary',
      'primary_url': u'https://primary',
    }
    self.assertEqual(expected_state, state.to_dict())


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
