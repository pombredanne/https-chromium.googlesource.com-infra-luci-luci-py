#!/usr/bin/env vpython
# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import sys
import threading
import unittest

from six.moves import queue
import mock

from test_support import test_env
test_env.setup_test_env()

from google.appengine import runtime
from google.appengine.ext import ndb

from components.auth import api
from components.auth import config
from components.auth import ipaddr
from components.auth import model
from components.auth import realms
from components.auth import replication
from components.auth.proto import replication_pb2
from components.auth.proto import security_config_pb2
from components import utils
from test_support import test_case


def new_auth_db(
      replication_state=None,
      global_config=None,
      groups=None,
      ip_whitelist_assignments=None,
      ip_whitelists=None,
      internal_service_regexp=None,
      additional_client_ids=None
  ):
  global_config = global_config or model.AuthGlobalConfig()
  global_config.security_config = security_config_blob(internal_service_regexp)
  return api.AuthDB.from_entities(
      replication_state=replication_state or model.AuthReplicationState(),
      global_config=global_config,
      groups=groups or [],
      ip_whitelist_assignments=(
          ip_whitelist_assignments or model.AuthIPWhitelistAssignments()),
      ip_whitelists=ip_whitelists or [],
      additional_client_ids=additional_client_ids or [])


def security_config_blob(regexps=None):
  regexps = regexps or ['(.*-dot-)?internal\\.example\\.com']
  msg = security_config_pb2.SecurityConfig(internal_service_regexp=regexps)
  return msg.SerializeToString()


class AuthDBTest(test_case.TestCase):
  """Tests for AuthDB class."""

  def setUp(self):
    super(AuthDBTest, self).setUp()
    self.mock(api.logging, 'warning', lambda *_args: None)
    self.mock(api.logging, 'error', lambda *_args: None)

  def test_get_group(self):
    g = model.AuthGroup(
      key=model.group_key('group'),
      members=[
        model.Identity.from_bytes('user:b@example.com'),
        model.Identity.from_bytes('user:a@example.com'),
      ],
      globs=[model.IdentityGlob.from_bytes('user:*')],
      nested=['blah'],
      created_by=model.Identity.from_bytes('user:x@example.com'),
      created_ts=datetime.datetime(2014, 1, 2, 3, 4, 5),
      modified_by=model.Identity.from_bytes('user:y@example.com'),
      modified_ts=datetime.datetime(2015, 1, 2, 3, 4, 5))

    db = new_auth_db(groups=[g])

    # Unknown group.
    self.assertIsNone(db.get_group('blah'))

    # Known group.
    from_cache = db.get_group('group')
    self.assertEqual(from_cache.key, g.key)

    # Members list is sorted.
    self.assertEqual(from_cache.members, [
      model.Identity.from_bytes('user:a@example.com'),
      model.Identity.from_bytes('user:b@example.com'),
    ])

    # Fields that are know to be different.
    exclude = ['members', 'auth_db_rev', 'auth_db_prev_rev']
    self.assertEqual(
        from_cache.to_dict(exclude=exclude),
        g.to_dict(exclude=exclude))

  def test_is_group_member(self):
    # Test identity.
    joe = model.Identity(model.IDENTITY_USER, 'joe@example.com')

    # Group that includes joe via glob.
    with_glob = model.AuthGroup(id='WithGlob')
    with_glob.globs.append(
        model.IdentityGlob(model.IDENTITY_USER, '*@example.com'))

    # Group that includes joe via explicit listing.
    with_listing = model.AuthGroup(id='WithListing')
    with_listing.members.append(joe)

    # Group that includes joe via nested group.
    with_nesting = model.AuthGroup(id='WithNesting')
    with_nesting.nested.append('WithListing')

    # Creates AuthDB with given list of groups and then runs the check.
    is_member = (lambda groups, ident, group:
        new_auth_db(groups=groups).is_group_member(group, ident))

    # Wildcard group includes everyone (even anonymous).
    self.assertTrue(is_member([], joe, '*'))
    self.assertTrue(is_member([], model.Anonymous, '*'))

    # An unknown group includes nobody.
    self.assertFalse(is_member([], joe, 'Missing'))
    self.assertFalse(is_member([], model.Anonymous, 'Missing'))

    # Globs are respected.
    self.assertTrue(is_member([with_glob], joe, 'WithGlob'))
    self.assertFalse(is_member([with_glob], model.Anonymous, 'WithGlob'))

    # Members lists are respected.
    self.assertTrue(is_member([with_listing], joe, 'WithListing'))
    self.assertFalse(is_member([with_listing], model.Anonymous, 'WithListing'))

    # Nested groups are respected.
    self.assertTrue(is_member([with_nesting, with_listing], joe, 'WithNesting'))
    self.assertFalse(
        is_member([with_nesting, with_listing], model.Anonymous, 'WithNesting'))

  def test_list_group(self):
    def list_group(groups, group, recursive):
      l = new_auth_db(groups=groups).list_group(group, recursive)
      return api.GroupListing(
          sorted(l.members), sorted(l.globs), sorted(l.nested))

    grp_1 = model.AuthGroup(id='1')
    grp_1.members.extend([
      model.Identity(model.IDENTITY_USER, 'a@example.com'),
      model.Identity(model.IDENTITY_USER, 'b@example.com'),
    ])
    grp_1.globs.extend([
      model.IdentityGlob(model.IDENTITY_USER, '*@a.example.com'),
      model.IdentityGlob(model.IDENTITY_USER, '*@b.example.com'),
    ])

    grp_2 = model.AuthGroup(id='2')
    grp_2.nested.append('1')
    grp_2.members.extend([
      # Specify 'b' again, even though it's in a nested group.
      model.Identity(model.IDENTITY_USER, 'b@example.com'),
      model.Identity(model.IDENTITY_USER, 'c@example.com'),
    ])
    grp_2.globs.extend([
      # Specify '*@b.example.com' again, even though it's in a nested group.
      model.IdentityGlob(model.IDENTITY_USER, '*@b.example.com'),
      model.IdentityGlob(model.IDENTITY_USER, '*@c.example.com'),
    ])

    # Unknown group.
    empty = api.GroupListing([], [], [])
    self.assertEqual(empty, list_group([grp_1, grp_2], 'blah', False))
    self.assertEqual(empty, list_group([grp_1, grp_2], 'blah', True))

    # Non recursive.
    expected = api.GroupListing(
        members=[
          model.Identity(model.IDENTITY_USER, 'b@example.com'),
          model.Identity(model.IDENTITY_USER, 'c@example.com'),
        ],
        globs=[
          model.IdentityGlob(model.IDENTITY_USER, '*@b.example.com'),
          model.IdentityGlob(model.IDENTITY_USER, '*@c.example.com'),
        ],
        nested=['1'])
    self.assertEqual(expected, list_group([grp_1, grp_2], '2', False))

    # Recursive.
    expected = api.GroupListing(
        members=[
          model.Identity(model.IDENTITY_USER, 'a@example.com'),
          model.Identity(model.IDENTITY_USER, 'b@example.com'),
          model.Identity(model.IDENTITY_USER, 'c@example.com'),
        ],
        globs=[
          model.IdentityGlob(model.IDENTITY_USER, '*@a.example.com'),
          model.IdentityGlob(model.IDENTITY_USER, '*@b.example.com'),
          model.IdentityGlob(model.IDENTITY_USER, '*@c.example.com'),
        ],
        nested=['1'])
    self.assertEqual(expected, list_group([grp_1, grp_2], '2', True))

  def test_nested_groups_cycle(self):
    # Groups that nest each other.
    group1 = model.AuthGroup(id='Group1')
    group1.nested.append('Group2')
    group2 = model.AuthGroup(id='Group2')
    group2.nested.append('Group1')

    # Collect warnings.
    warnings = []
    self.mock(api.logging, 'warning', lambda msg, *_args: warnings.append(msg))

    # This should not hang, but produce error message.
    auth_db = new_auth_db(groups=[group1, group2])
    self.assertFalse(
        auth_db.is_group_member('Group1', model.Anonymous))
    self.assertEqual(1, len(warnings))
    self.assertTrue('Cycle in a group graph' in warnings[0])

  def test_not_real_nested_group_cycle_aka_issue_251(self):
    # See https://github.com/luci/luci-py/issues/251.
    #
    # B -> A, C -> [B, A]. When traversing C, A is seen twice, and this is fine.
    group_A = model.AuthGroup(id='A')
    group_B = model.AuthGroup(id='B')
    group_C = model.AuthGroup(id='C')

    group_B.nested = ['A']
    group_C.nested = ['A', 'B']

    db = new_auth_db(groups=[group_A, group_B, group_C])

    # 'is_group_member' must not report 'Cycle in a group graph' warning.
    warnings = []
    self.mock(api.logging, 'warning', lambda msg, *_args: warnings.append(msg))
    self.assertFalse(db.is_group_member('C', model.Anonymous))
    self.assertFalse(warnings)

  def test_is_allowed_oauth_client_id(self):
    global_config = model.AuthGlobalConfig(
        oauth_client_id='1',
        oauth_additional_client_ids=['2', '3'])
    auth_db = new_auth_db(
        global_config=global_config,
        additional_client_ids=['local'])
    self.assertFalse(auth_db.is_allowed_oauth_client_id(None))
    self.assertTrue(auth_db.is_allowed_oauth_client_id('1'))
    self.assertTrue(auth_db.is_allowed_oauth_client_id('2'))
    self.assertTrue(auth_db.is_allowed_oauth_client_id('3'))
    self.assertTrue(auth_db.is_allowed_oauth_client_id('local'))
    self.assertTrue(
        auth_db.is_allowed_oauth_client_id(api.API_EXPLORER_CLIENT_ID))
    self.assertFalse(auth_db.is_allowed_oauth_client_id('4'))

  def test_fetch_auth_db_lazy_bootstrap(self):
    # Don't exist before the call.
    self.assertFalse(model.root_key().get())

    # Run bootstrap.
    api._lazy_bootstrap_ran = False
    api.fetch_auth_db()

    # Exist now.
    self.assertTrue(model.root_key().get())

    # Simulate datastore wipe which can happen in tests, verify fetch_auth_db
    # still works. It hits slightly different code path since wiping datastore
    # doesn't reset _lazy_bootstrap_ran global var.
    model.root_key().delete()
    api.fetch_auth_db()

  def run_auth_db_fetch_test(self, setup_cb):
    now = utils.utcnow()
    ident = model.Identity.from_bytes('user:a@example.com')

    # Client IDs callback. Disable config.ensure_configured() since it overrides
    # _additional_client_ids_cb after we mock it.
    self.mock(config, 'ensure_configured', lambda: None)
    self.mock(api, '_additional_client_ids_cb', lambda: ['', 'cb_client_id'])
    self.mock(api, 'get_web_client_id', lambda: 'web_client_id')

    # Create AuthGlobalConfig.
    global_config = model.AuthGlobalConfig(key=model.root_key())
    global_config.oauth_client_id = '1'
    global_config.oauth_client_secret = 'secret'
    global_config.oauth_additional_client_ids = ['2', '3']
    global_config.security_config = security_config_blob()
    global_config.token_server_url = 'token_server_url'
    global_config.put()

    # What we expect to see in the AuthDB.
    expected_groups = {}

    def add_group(name, members, globs, nested, owners):
      expected_groups[name] = (
          frozenset(members),
          tuple(model.IdentityGlob.from_bytes(g) for g in globs),
          tuple(nested),
          owners,
      )
      model.AuthGroup(
          key=model.group_key(name),
          members=[model.Identity.from_bytes(m) for m in members],
          globs=[model.IdentityGlob.from_bytes(g) for g in globs],
          nested=nested,
          owners=owners,
          created_ts=now,
          created_by=ident,
          modified_ts=now,
          modified_by=ident,
      ).put()

    # Create a bunch of groups.
    add_group(
        name='Group A',
        members=['user:a@example.com', 'user:b@example.com'],
        globs=['user:*@example.com'],
        nested=['Group B', 'Group C'],
        owners='Group A')
    add_group(
        name='Group B',
        members=['user:c@example.com'],
        globs=['user:*@example.com'],
        nested=[],
        owners='Group A')
    add_group(
        name='Group C',
        members=[],
        globs=[],
        nested=[],
        owners='Group C')

    # And a bunch IP whitelist.
    model.AuthIPWhitelistAssignments(
        key=model.ip_whitelist_assignments_key(),
        assignments=[
            model.AuthIPWhitelistAssignments.Assignment(
                identity=model.Anonymous,
                ip_whitelist='some ip whitelist',
                created_ts=now,
                created_by=ident,
                comment='comment',
            ),
        ],
    ).put()

    model.AuthIPWhitelist(
        key=model.ip_whitelist_key('some ip whitelist'),
        subnets=['127.0.0.1/32'],
        description='description',
        created_ts=now,
        created_by=ident,
        modified_ts=now,
        modified_by=ident,
    ).put()
    model.AuthIPWhitelist(
        key=model.ip_whitelist_key('bots'),
        subnets=['127.0.0.1/32'],
        description='description',
        created_ts=now,
        created_by=ident,
        modified_ts=now,
        modified_by=ident,
    ).put()

    if setup_cb:
      setup_cb()

    # Verify all the stuff above ends up in the auth_db.
    auth_db = api.fetch_auth_db()

    # global_config and additional_client_ids_cb
    self.assertEqual('token_server_url', auth_db.token_server_url)
    self.assertEqual(('1', 'secret', ['2', '3']), auth_db.get_oauth_config())
    self.assertTrue(auth_db.is_allowed_oauth_client_id('1'))
    self.assertTrue(auth_db.is_allowed_oauth_client_id('cb_client_id'))
    self.assertTrue(auth_db.is_allowed_oauth_client_id('web_client_id'))
    self.assertFalse(auth_db.is_allowed_oauth_client_id(''))

    # Groups.
    self.assertEqual(
        expected_groups,
        {
            name: (g.members, g.globs, g.nested, g.owners)
            for name, g in auth_db._groups.items()
        })

    # IP whitelists and whitelist assignments.
    self.assertEqual(
        {model.Anonymous: 'some ip whitelist'},
        auth_db._ip_whitelist_assignments)
    self.assertEqual(
        {'bots': ['127.0.0.1/32'], 'some ip whitelist': ['127.0.0.1/32']},
        auth_db._ip_whitelists)

    return auth_db

  def test_fetch_auth_db_from_entities(self):
    auth_db = self.run_auth_db_fetch_test(None)
    self.assertEqual('from_entities', auth_db._from_what)

  def test_fetch_auth_db_from_snapshot(self):
    PRIMARY_ID = 'primary_id'
    PRIMARY_URL = 'https://primary_url'
    AUTH_DB_REV = 12345

    def setup_snapshot():
      # Create AuthDB snapshot entities from existing "detailed" entities in
      # the datastore.
      _, snap = replication.new_auth_db_snapshot()
      # Switch into Replica mode, store the snapshot.
      model.AuthReplicationState(
          key=model.replication_state_key(),
          primary_id=PRIMARY_ID,
          primary_url=PRIMARY_URL,
          auth_db_rev=AUTH_DB_REV,
          shard_ids=replication.store_sharded_auth_db(
              auth_db=replication.auth_db_snapshot_to_proto(snap),
              primary_url=PRIMARY_URL,
              auth_db_rev=AUTH_DB_REV,
              shard_size=100,
          ),
      ).put()

    auth_db = self.run_auth_db_fetch_test(setup_snapshot)

    self.assertEqual('from_proto', auth_db._from_what)
    self.assertEqual(PRIMARY_ID, auth_db.primary_id)
    self.assertEqual(PRIMARY_URL, auth_db.primary_url)
    self.assertEqual(AUTH_DB_REV, auth_db.auth_db_rev)

  def test_get_secret_bootstrap(self):
    # Mock AuthSecret.bootstrap to capture calls to it.
    original = api.model.AuthSecret.bootstrap
    calls = []
    @classmethod
    def mocked_bootstrap(cls, name):
      calls.append(name)
      result = original(name)
      result.values = ['123']
      return result
    self.mock(api.model.AuthSecret, 'bootstrap', mocked_bootstrap)

    auth_db = new_auth_db()
    got = auth_db.get_secret(api.SecretKey('some_secret'))
    self.assertEqual(['123'], got)
    self.assertEqual(['some_secret'], calls)

  def test_is_in_ip_whitelist(self):
    auth_db = new_auth_db(ip_whitelists=[
        model.AuthIPWhitelist(
            key=model.ip_whitelist_key('l'),
            subnets=['127.0.0.1', '192.168.0.0/24']),
    ])
    test = lambda ip: auth_db.is_in_ip_whitelist('l', ipaddr.ip_from_string(ip))
    self.assertTrue(test('127.0.0.1'))
    self.assertTrue(test('192.168.0.0'))
    self.assertTrue(test('192.168.0.9'))
    self.assertTrue(test('192.168.0.255'))
    self.assertFalse(test('192.168.1.0'))
    self.assertFalse(test('192.1.0.0'))

  @staticmethod
  def make_auth_db_with_ip_whitelist():
    """AuthDB with a@example.com assigned IP whitelist '127.0.0.1/32'."""
    return new_auth_db(
      ip_whitelists=[
        model.AuthIPWhitelist(
          key=model.ip_whitelist_key('some ip whitelist'),
          subnets=['127.0.0.1/32'],
        ),
        model.AuthIPWhitelist(
          key=model.ip_whitelist_key('bots'),
          subnets=['192.168.1.1/32', '::1/32'],
        ),
      ],
      ip_whitelist_assignments=model.AuthIPWhitelistAssignments(
        assignments=[
          model.AuthIPWhitelistAssignments.Assignment(
            identity=model.Identity(model.IDENTITY_USER, 'a@example.com'),
            ip_whitelist='some ip whitelist',)
        ],
      ),
    )

  def test_verify_ip_whitelisted_ok(self):
    # Should not raise: IP is whitelisted.
    ident = model.Identity(model.IDENTITY_USER, 'a@example.com')
    self.make_auth_db_with_ip_whitelist().verify_ip_whitelisted(
        ident, ipaddr.ip_from_string('127.0.0.1'))

  def test_verify_ip_whitelisted_not_whitelisted(self):
    with self.assertRaises(api.AuthorizationError):
      self.make_auth_db_with_ip_whitelist().verify_ip_whitelisted(
          model.Identity(model.IDENTITY_USER, 'a@example.com'),
          ipaddr.ip_from_string('192.168.0.100'))

  def test_verify_ip_whitelisted_not_assigned(self):
    # Should not raise: whitelist is not required for another_user@example.com.
    ident = model.Identity(model.IDENTITY_USER, 'another_user@example.com')
    self.make_auth_db_with_ip_whitelist().verify_ip_whitelisted(
        ident, ipaddr.ip_from_string('192.168.0.100'))

  def test_verify_ip_whitelisted_missing_whitelist(self):
    auth_db = new_auth_db(
      ip_whitelist_assignments=model.AuthIPWhitelistAssignments(
        assignments=[
          model.AuthIPWhitelistAssignments.Assignment(
            identity=model.Identity(model.IDENTITY_USER, 'a@example.com'),
            ip_whitelist='missing ip whitelist',)
        ],
      ),
    )
    with self.assertRaises(api.AuthorizationError):
      auth_db.verify_ip_whitelisted(
          model.Identity(model.IDENTITY_USER, 'a@example.com'),
          ipaddr.ip_from_string('127.0.0.1'))

  def test_is_internal_domain(self):
    auth_db = new_auth_db(internal_service_regexp=[
        '(.*-dot-)?a-int\\.example\\.com',
        '(.*-dot-)?b-int\\.example\\.com',
    ])
    self.assertTrue(auth_db.is_internal_domain('a-int.example.com'))
    self.assertTrue(auth_db.is_internal_domain('b-int.example.com'))
    self.assertTrue(auth_db.is_internal_domain('z-dot-a-int.example.com'))
    self.assertTrue(auth_db.is_internal_domain('z-dot-b-int.example.com'))
    self.assertFalse(auth_db.is_internal_domain('int.example.com'))
    self.assertFalse(auth_db.is_internal_domain('a-int.example'))
    self.assertFalse(auth_db.is_internal_domain('dot-a-int.example.com'))


def mock_replication_state(auth_db_rev):
  return model.AuthReplicationState(
      key=model.replication_state_key(),
      primary_id='primary-id',
      auth_db_rev=auth_db_rev)


class TestAuthDBCache(test_case.TestCase):
  """Tests for process-global and request-local AuthDB cache."""

  def setUp(self):
    super(TestAuthDBCache, self).setUp()
    api.reset_local_state()

  def set_time(self, ts):
    """Mocks time.time() to return |ts|."""
    self.mock(api.time, 'time', lambda: ts)

  def set_fetched_auth_db(self, auth_db):
    """Mocks fetch_auth_db to return |auth_db|."""
    def mock_fetch_auth_db(known_auth_db=None):
      if (known_auth_db is not None and
          auth_db.auth_db_rev == known_auth_db.auth_db_rev):
        return known_auth_db
      return auth_db
    self.mock(api, 'fetch_auth_db', mock_fetch_auth_db)

  def test_get_request_cache_different_threads(self):
    """Ensure get_request_cache() respects multiple threads."""
    # Runs in its own thread.
    def thread_proc():
      request_cache = api.reinitialize_request_cache()
      self.assertTrue(request_cache)
      # Returns same object in a context of a same request thread.
      self.assertTrue(api.get_request_cache() is request_cache)
      return request_cache

    # Launch two threads running 'thread_proc', wait for them to stop, collect
    # whatever they return.
    results_queue = queue.Queue()
    threads = [
        threading.Thread(target=lambda: results_queue.put(thread_proc()))
        for _ in range(2)
    ]
    for t in threads:
      t.start()
    results = [results_queue.get(timeout=1) for _ in range(len(threads))]

    # Different threads use different RequestCache objects.
    self.assertTrue(results[0] is not results[1])

  def test_get_request_cache_different_requests(self):
    """Ensure get_request_cache() returns new object for a new request."""
    # Grab request cache for 'current' request.
    request_cache = api.reinitialize_request_cache()

    # Track calls to 'close'.
    close_calls = []
    self.mock(request_cache, 'close', lambda: close_calls.append(1))

    # Should return a new instance of request cache now.
    self.assertTrue(api.reinitialize_request_cache() is not request_cache)
    # Old one should have been closed.
    self.assertEqual(1, len(close_calls))

  def test_get_process_auth_db_expiration(self):
    """Ensure get_process_auth_db() respects expiration."""
    # Prepare several instances of AuthDB to be used in mocks.
    auth_db_v0 = new_auth_db(replication_state=mock_replication_state(0))
    auth_db_v1 = new_auth_db(replication_state=mock_replication_state(1))

    # Fetch initial copy of AuthDB.
    self.set_time(0)
    self.set_fetched_auth_db(auth_db_v0)
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # It doesn't expire for some time.
    self.set_time(api.get_process_cache_expiration_sec() - 1)
    self.set_fetched_auth_db(auth_db_v1)
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # But eventually it does.
    self.set_time(api.get_process_cache_expiration_sec() + 1)
    self.set_fetched_auth_db(auth_db_v1)
    self.assertEqual(auth_db_v1, api.get_process_auth_db())

  def test_get_process_auth_db_known_version(self):
    """Ensure get_process_auth_db() respects entity group version."""
    # Prepare several instances of AuthDB to be used in mocks.
    auth_db_v0 = new_auth_db(replication_state=mock_replication_state(0))
    auth_db_v0_again = new_auth_db(replication_state=mock_replication_state(0))

    # Fetch initial copy of AuthDB.
    self.set_time(0)
    self.set_fetched_auth_db(auth_db_v0)
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # Make cache expire, but setup fetch_auth_db to return a new instance of
    # AuthDB, but with same entity group version. Old known instance of AuthDB
    # should be reused.
    self.set_time(api.get_process_cache_expiration_sec() + 1)
    self.set_fetched_auth_db(auth_db_v0_again)
    self.assertTrue(api.get_process_auth_db() is auth_db_v0)

  def test_get_process_auth_db_multithreading(self):
    """Ensure get_process_auth_db() plays nice with multiple threads."""

    def run_in_thread(func):
      """Runs |func| in a parallel thread, returns future (as Queue)."""
      result = queue.Queue()
      thread = threading.Thread(target=lambda: result.put(func()))
      thread.start()
      return result

    # Prepare several instances of AuthDB to be used in mocks.
    auth_db_v0 = new_auth_db(replication_state=mock_replication_state(0))
    auth_db_v1 = new_auth_db(replication_state=mock_replication_state(1))

    # Run initial fetch, should cache |auth_db_v0| in process cache.
    self.set_time(0)
    self.set_fetched_auth_db(auth_db_v0)
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # Make process cache expire.
    self.set_time(api.get_process_cache_expiration_sec() + 1)

    # Start fetching AuthDB from another thread, at some point it will call
    # 'fetch_auth_db', and we pause the thread then and resume main thread.
    fetching_now = threading.Event()
    auth_db_queue = queue.Queue()

    def mock_fetch_auth_db(**_kwargs):
      fetching_now.set()
      return auth_db_queue.get()
    self.mock(api, 'fetch_auth_db', mock_fetch_auth_db)
    future = run_in_thread(api.get_process_auth_db)

    # Wait for internal thread to call |fetch_auth_db|.
    fetching_now.wait()

    # Ok, now main thread is unblocked, while internal thread is blocking on a
    # artificially slow 'fetch_auth_db' call. Main thread can now try to get
    # AuthDB via get_process_auth_db(). It should get older stale copy right
    # away.
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # Finish background 'fetch_auth_db' call by returning 'auth_db_v1'.
    # That's what internal thread should get as result of 'get_process_auth_db'.
    auth_db_queue.put(auth_db_v1)
    self.assertEqual(auth_db_v1, future.get())

    # Now main thread should get it as well.
    self.assertEqual(auth_db_v1, api.get_process_auth_db())

  def test_get_process_auth_db_exceptions(self):
    """Ensure get_process_auth_db() handles DB exceptions well."""
    # Prepare several instances of AuthDB to be used in mocks.
    auth_db_v0 = new_auth_db(replication_state=mock_replication_state(0))
    auth_db_v1 = new_auth_db(replication_state=mock_replication_state(1))

    # Fetch initial copy of AuthDB.
    self.set_time(0)
    self.set_fetched_auth_db(auth_db_v0)
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # Make process cache expire.
    self.set_time(api.get_process_cache_expiration_sec() + 1)

    # Emulate an exception in fetch_auth_db.
    def mock_fetch_auth_db(**_kwargs):
      raise runtime.DeadlineExceededError()
    self.mock(api, 'fetch_auth_db', mock_fetch_auth_db)

    # Capture calls to logging.exception.
    logger_calls = []
    self.mock(api.logging, 'exception', lambda *_args: logger_calls.append(1))

    # Propagates the exception, releases the fetch lock.
    with self.assertRaises(runtime.DeadlineExceededError):
      api.get_process_auth_db()

    # Make fetch_auth_db to work again. Verify get_process_auth_db() works too.
    self.set_fetched_auth_db(auth_db_v1)
    self.assertEqual(auth_db_v1, api.get_process_auth_db())

  def test_get_latest_auth_db(self):
    """Ensure get_latest_auth_db "rushes" cached AuthDB update."""
    auth_db_v0 = new_auth_db(replication_state=mock_replication_state(0))
    auth_db_v1 = new_auth_db(replication_state=mock_replication_state(1))

    # Fetch initial copy of AuthDB.
    self.set_time(0)
    self.set_fetched_auth_db(auth_db_v0)
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # Rig up fetch_auth_db to return a newer version.
    self.set_fetched_auth_db(auth_db_v1)

    # 'get_process_auth_db' still returns the cached one.
    self.assertEqual(auth_db_v0, api.get_process_auth_db())

    # But 'get_latest_auth_db' returns a new one and updates the cached copy.
    self.assertEqual(auth_db_v1, api.get_latest_auth_db())
    self.assertEqual(auth_db_v1, api.get_process_auth_db())

  def test_get_request_auth_db(self):
    """Ensure get_request_auth_db() caches AuthDB in request cache."""
    api.reinitialize_request_cache()

    # 'get_request_auth_db()' returns whatever get_process_auth_db() returns
    # when called for a first time.
    self.mock(api, 'get_process_auth_db', lambda: 'fake')
    self.assertEqual('fake', api.get_request_auth_db())

    # But then it caches it locally and reuses local copy, instead of calling
    # 'get_process_auth_db()' all the time.
    self.mock(api, 'get_process_auth_db', lambda: 'another-fake')
    self.assertEqual('fake', api.get_request_auth_db())

  def test_warmup(self):
    """Ensure api.warmup() fetches AuthDB into process-global cache."""
    self.assertFalse(api._auth_db)
    api.warmup()
    self.assertTrue(api._auth_db)


class ApiTest(test_case.TestCase):
  """Test for publicly exported API."""

  def setUp(self):
    super(ApiTest, self).setUp()
    api.reset_local_state()

  def test_get_current_identity_unitialized(self):
    """If request cache is not initialized, returns Anonymous."""
    self.assertEqual(api.get_current_identity(), model.Anonymous)

  def test_get_current_identity(self):
    """Ensure get_current_identity returns whatever was put in request cache."""
    ident = model.Identity.from_bytes('user:abc@example.com')
    api.get_request_cache().current_identity = ident
    self.assertEqual(ident, api.get_current_identity())

  def test_require_decorator_ok(self):
    """@require calls the callback and then decorated function."""
    callback_calls = []
    def require_callback():
      callback_calls.append(1)
      return True

    @api.require(require_callback)
    def allowed(*args, **kwargs):
      return (args, kwargs)

    self.assertEqual(((1, 2), {'a': 3}), allowed(1, 2, a=3))
    self.assertEqual(1, len(callback_calls))

  def test_require_decorator_fail(self):
    """@require raises exception and doesn't call decorated function."""
    forbidden_calls = []

    @api.require(lambda: False)
    def forbidden():
      forbidden_calls.append(1)

    with self.assertRaises(api.AuthorizationError):
      forbidden()
    self.assertFalse(forbidden_calls)

  def test_require_decorator_error_msg(self):
    @api.require(lambda: False, 'Forbidden!')
    def forbidden():
      pass

    with self.assertRaisesRegexp(api.AuthorizationError, 'Forbidden!'):
      forbidden()

  def test_require_decorator_nesting_ok(self):
    """Permission checks are called in order."""
    calls = []
    def check(name):
      calls.append(name)
      return True

    @api.require(lambda: check('A'))
    @api.require(lambda: check('B'))
    def allowed(arg):
      return arg

    self.assertEqual('value', allowed('value'))
    self.assertEqual(['A', 'B'], calls)

  def test_require_decorator_nesting_first_deny(self):
    """First deny raises AuthorizationError."""
    calls = []
    def check(name, result):
      calls.append(name)
      return result

    forbidden_calls = []

    @api.require(lambda: check('A', False))
    @api.require(lambda: check('B', True))
    def forbidden(arg):
      forbidden_calls.append(1)

    with self.assertRaises(api.AuthorizationError):
      forbidden('value')
    self.assertFalse(forbidden_calls)
    self.assertEqual(['A'], calls)

  def test_require_decorator_nesting_non_first_deny(self):
    """Non-first deny also raises AuthorizationError."""
    calls = []
    def check(name, result):
      calls.append(name)
      return result

    forbidden_calls = []

    @api.require(lambda: check('A', True))
    @api.require(lambda: check('B', False))
    def forbidden(arg):
      forbidden_calls.append(1)

    with self.assertRaises(api.AuthorizationError):
      forbidden('value')
    self.assertFalse(forbidden_calls)
    self.assertEqual(['A', 'B'], calls)

  def test_require_decorator_on_method(self):
    calls = []
    def checker():
      calls.append(1)
      return True

    class Class(object):
      @api.require(checker)
      def method(self, *args, **kwargs):
        return (self, args, kwargs)

    obj = Class()
    self.assertEqual((obj, ('value',), {'a': 2}), obj.method('value', a=2))
    self.assertEqual(1, len(calls))

  def test_require_decorator_on_static_method(self):
    calls = []
    def checker():
      calls.append(1)
      return True

    class Class(object):
      @staticmethod
      @api.require(checker)
      def static_method(*args, **kwargs):
        return (args, kwargs)

    self.assertEqual((('value',), {'a': 2}), Class.static_method('value', a=2))
    self.assertEqual(1, len(calls))

  def test_require_decorator_on_class_method(self):
    calls = []
    def checker():
      calls.append(1)
      return True

    class Class(object):
      @classmethod
      @api.require(checker)
      def class_method(cls, *args, **kwargs):
        return (cls, args, kwargs)

    self.assertEqual(
        (Class, ('value',), {'a': 2}), Class.class_method('value', a=2))
    self.assertEqual(1, len(calls))

  def test_require_decorator_ndb_nesting_require_first(self):
    calls = []
    def checker():
      calls.append(1)
      return True

    @api.require(checker)
    @ndb.non_transactional
    def func(*args, **kwargs):
      return (args, kwargs)
    self.assertEqual((('value',), {'a': 2}), func('value', a=2))
    self.assertEqual(1, len(calls))

  def test_require_decorator_ndb_nesting_require_last(self):
    calls = []
    def checker():
      calls.append(1)
      return True

    @ndb.non_transactional
    @api.require(checker)
    def func(*args, **kwargs):
      return (args, kwargs)
    self.assertEqual((('value',), {'a': 2}), func('value', a=2))
    self.assertEqual(1, len(calls))

  def test_public_then_require_fails(self):
    with self.assertRaises(TypeError):
      @api.public
      @api.require(lambda: True)
      def _func():
        pass

  def test_require_then_public_fails(self):
    with self.assertRaises(TypeError):
      @api.require(lambda: True)
      @api.public
      def _func():
        pass

  def test_is_decorated(self):
    self.assertTrue(api.is_decorated(api.public(lambda: None)))
    self.assertTrue(
        api.is_decorated(api.require(lambda: True)(lambda: None)))

  @mock.patch('logging.info')
  def test_require_log_identity(self, logfunc):
    ident = model.Identity.from_bytes('user:abc@example.com')
    api.get_request_cache().current_identity = ident

    @api.require(lambda: True, log_identity=True)
    def func():
      pass

    func()
    logfunc.assert_called_once_with('Accessed from user:abc@example.com')


class OAuthAccountsTest(test_case.TestCase):
  """Test for extract_oauth_caller_identity function."""

  def mock_all(self, user_email, client_id, allowed_client_ids=()):
    class FakeUser(object):
      email = lambda _: user_email
    class FakeAuthDB(object):
      is_allowed_oauth_client_id = lambda _, cid: cid in allowed_client_ids
    self.mock(api.oauth, 'get_current_user', lambda _: FakeUser())
    self.mock(api.oauth, 'get_client_id', lambda _: client_id)
    self.mock(api, 'get_request_auth_db', FakeAuthDB)

  @staticmethod
  def user(email):
    return model.Identity(model.IDENTITY_USER, email)

  def test_is_allowed_oauth_client_id_ok(self):
    self.mock_all('email@email.com', 'some-client-id', ['some-client-id'])
    self.assertEqual(
        (self.user('email@email.com'), api.new_auth_details()),
        api.extract_oauth_caller_identity())

  def test_is_allowed_oauth_client_id_not_ok(self):
    self.mock_all('email@email.com', 'some-client-id', ['another-client-id'])
    with self.assertRaises(api.AuthorizationError):
      api.extract_oauth_caller_identity()

  def test_is_allowed_oauth_client_id_not_ok_empty(self):
    self.mock_all('email@email.com', 'some-client-id')
    with self.assertRaises(api.AuthorizationError):
      api.extract_oauth_caller_identity()


class AuthWebUIConfigTest(test_case.TestCase):
  def test_works(self):
    utils.clear_cache(api.get_web_client_id)
    self.assertEqual('', api.get_web_client_id_uncached())
    api.set_web_client_id('zzz')
    self.assertEqual('zzz', api.get_web_client_id_uncached())
    self.assertEqual('zzz', api.get_web_client_id())


class AuthDBBuilder(object):
  def __init__(self):
    self.groups = []

  def group(self, name, members=None, globs=None, nested=None, owners=None):
    self.groups.append(model.AuthGroup(
        key=model.group_key(name),
        members=[model.Identity.from_bytes(m) for m in (members or [])],
        globs=[model.IdentityGlob.from_bytes(g) for g in (globs or [])],
        nested=nested or [],
        owners=owners or 'default-owners-group',
    ))
    return self

  def build(self):
    return new_auth_db(groups=self.groups)


class RelevantSubgraphTest(test_case.TestCase):
  def call(self, db, principal):
    if '*' in principal:
      principal = model.IdentityGlob.from_bytes(principal)
    elif '@' in principal:
      principal = model.Identity.from_bytes(principal)
    graph = db.get_relevant_subgraph(principal)
    # Use a dict with integer keys instead of a list to improve the readability
    # of assertions below.
    nodes = {}
    for i, (node, edges) in enumerate(graph.describe()):
      if isinstance(node, (model.Identity, model.IdentityGlob)):
        node = node.to_bytes()
      nodes[i] = (node, {l: sorted(s) for l, s in edges.items() if s})
    return nodes

  def test_empty(self):
    db = AuthDBBuilder().build()
    self.assertEqual(
        {0: ('user:a@example.com', {})}, self.call(db, 'user:a@example.com'))
    self.assertEqual(
        {0: ('user:*@example.com', {})}, self.call(db, 'user:*@example.com'))
    # In the case of a nonexistent group, a empty graph is returned.
    self.assertEqual({}, self.call(db, 'group'))

  def test_identity_discoverable_directly_and_through_glob(self):
    b = AuthDBBuilder()
    b.group('g1', ['user:a@example.com'])
    b.group('g2', ['user:b@example.com'])
    b.group('g3', [], ['user:*@example.com'])
    b.group('g4', ['user:a@example.com'], ['user:*'])
    self.assertEqual({
      0: ('user:a@example.com', {'IN': [1, 3, 4, 5]}),
      1: ('user:*@example.com', {'IN': [2]}),
      2: ('g3', {}),
      3: ('user:*', {'IN': [4]}),
      4: ('g4', {}),
      5: ('g1', {}),
    }, self.call(b.build(), 'user:a@example.com'))

  def test_glob_is_matched_directly(self):
    b = AuthDBBuilder()
    b.group('g1', [], ['user:*@example.com'])
    b.group('g2', [], ['user:*'])
    self.assertEqual({
      0: ('user:*@example.com', {'IN': [1]}),
      1: ('g1', {}),
    }, self.call(b.build(), 'user:*@example.com'))

  def test_simple_group_lookup(self):
    b = AuthDBBuilder()
    b.group('g1', nested=['g2', 'g3'])
    b.group('g2', nested=['g3'])
    b.group('g3')
    self.assertEqual({
      0: ('g3', {'IN': [1, 2]}),
      1: ('g1', {}),
      2: ('g2', {'IN': [1]}),
    }, self.call(b.build(), 'g3'))

  def test_ownership_relations(self):
    b = AuthDBBuilder()
    b.group('a-root', nested=['b-inner'])
    b.group('b-inner')
    b.group('c-owned-by-root', owners='a-root')
    b.group('d-includes-owned-by-root', nested=['c-owned-by-root'])
    b.group('e-owned-by-3', owners='d-includes-owned-by-root')
    self.assertEqual({
      0: ('b-inner', {'IN': [1]}),
      1: ('a-root', {'OWNS': [2]}),
      2: ('c-owned-by-root', {'IN': [3]}),
      3: ('d-includes-owned-by-root', {'OWNS': [4]}),
      4: ('e-owned-by-3', {}),
    }, self.call(b.build(), 'b-inner'))

  def test_diamond(self):
    b = AuthDBBuilder()
    b.group('top', nested=['middle1', 'middle2'])
    b.group('middle1', nested=['bottom'])
    b.group('middle2', nested=['bottom'])
    b.group('bottom')
    self.assertEqual({
      0: ('bottom', {'IN': [1, 3]}),
      1: ('middle1', {'IN': [2]}),
      2: ('top', {}),
      3: ('middle2', {'IN': [2]}),
    }, self.call(b.build(), 'bottom'))

  def test_cycle(self):
    # Note: cycles in groups are forbidden on API layer, but make sure we still
    # handle them without hanging in case something unexpected happens and they
    # appear.
    b = AuthDBBuilder()
    b.group('g1', nested=['g2'])
    b.group('g2', nested=['g1', 'g2'])
    self.assertEqual({
      0: ('g2', {'IN': [0, 1]}),
      1: ('g1', {'IN': [0]}),
    }, self.call(b.build(), 'g2'))

  def test_selfowners(self):
    b = AuthDBBuilder()
    b.group('g1', nested=['g2'], owners='g1')
    b.group('g2')
    self.assertEqual({0: ('g1', {'OWNS': [0]})}, self.call(b.build(), 'g1'))
    self.assertEqual({
      0: ('g2', {'IN': [1]}),
      1: ('g1', {'OWNS': [1]}),
    }, self.call(b.build(), 'g2'))

  def test_messy_graph(self):
    b = AuthDBBuilder()
    b.group('directly', ['user:a@example.com'])
    b.group('via-glob', [], ['user:*@example.com'])
    b.group('g1', nested=['via-glob'], owners='g2')
    b.group('g2', nested=['directly'])
    b.group('g3', nested=['g1'])
    self.assertEqual({
      0: ('user:a@example.com', {'IN': [1, 5]}),
      1: ('user:*@example.com', {'IN': [2]}),
      2: ('via-glob', {'IN': [3]}),
      3: ('g1', {'IN': [4]}),
      4: ('g3', {}),
      5: ('directly', {'IN': [6]}),
      6: ('g2', {'OWNS': [3]}),
    }, self.call(b.build(), 'user:a@example.com'))


class PermissionsTest(test_case.TestCase):
  def test_happy_path(self):
    p1 = api.Permission('service.subject.verb')
    p2 = api.Permission('service.subject.verb')
    p3 = api.Permission('service.subject.another')
    self.assertEqual(p1, p2)
    self.assertTrue(p1 is p2)
    self.assertNotEqual(p1, p3)
    self.assertEqual('service.subject.verb', str(p1))
    self.assertEqual("'service.subject.verb'", '%r' % (p1,))

  def test_validation_errors(self):
    with self.assertRaises(TypeError):
      api.Permission(123)
    with self.assertRaises(TypeError):
      api.Permission(u'no.unicode.here')
    with self.assertRaises(ValueError):
      api.Permission('too.few')
    with self.assertRaises(ValueError):
      api.Permission('too.too.too.much')
    with self.assertRaises(ValueError):
      api.Permission('has..empty')


class RealmStringsTest(test_case.TestCase):
  def test_happy_path(self):
    self.assertEqual(api.root_realm('proj'), 'proj:@root')
    self.assertEqual(api.root_realm(u'proj'), 'proj:@root')
    self.assertEqual(api.legacy_realm('proj'), 'proj:@legacy')
    self.assertEqual(api.legacy_realm(u'proj'), 'proj:@legacy')

  def test_validation_errors(self):
    with self.assertRaises(TypeError):
      api.root_realm(None)
    with self.assertRaises(TypeError):
      api.legacy_realm(None)
    with self.assertRaises(ValueError):
      api.root_realm('')
    with self.assertRaises(ValueError):
      api.legacy_realm('')

  def test_validate_realm_name(self):
    self.assertIsNone(api.validate_realm_name('proj:realm'))
    self.assertIsNone(api.validate_realm_name('proj:@root'))
    self.assertIsNone(api.validate_realm_name('proj:@legacy'))
    self.assertIsNone(api.validate_realm_name('@internal:realm'))
    self.assertIsNone(api.validate_realm_name('@internal:@root'))
    self.assertIsNone(api.validate_realm_name('@internal:@legacy'))

  def test_validate_realm_name_errors(self):
    with self.assertRaises(ValueError):
      self.assertFalse(api.validate_realm_name('realm'))
    with self.assertRaises(ValueError):
      self.assertFalse(api.validate_realm_name('proj:@invalid'))
    with self.assertRaises(ValueError):
      self.assertFalse(api.validate_realm_name('proj:re:alm'))
    with self.assertRaises(ValueError):
      self.assertFalse(api.validate_realm_name('@proj:realm'))


PERM0 = api.Permission('luci.dev.testing0')
PERM1 = api.Permission('luci.dev.testing1')
PERM2 = api.Permission('luci.dev.testing2')
ALL_PERMS = [PERM0, PERM1, PERM2]

ID1 = model.Identity.from_bytes('user:1@example.com')
ID2 = model.Identity.from_bytes('user:2@example.com')
ID3 = model.Identity.from_bytes('user:3@example.com')

ADMIN = model.Identity.from_bytes('user:admin@example.com')


class RealmsTest(test_case.TestCase):
  @staticmethod
  def auth_db(realms_map, groups=None, conditions=None, api_version=None):
    return api.AuthDB.from_proto(
        replication_state=model.AuthReplicationState(),
        auth_db=replication_pb2.AuthDB(
            groups=[
                {
                    'name': name,
                    'members': [m.to_bytes() for m in members],
                    'created_by': 'user:zzz@example.com',
                    'modified_by': 'user:zzz@example.com',
                } for name, members in (groups or {}).items()
            ],
            realms={
                'api_version': api_version or realms.API_VERSION,
                'conditions': conditions or [],
                'permissions': [
                    {'name': p.name} for p in ALL_PERMS
                ],
                'realms': [
                    {
                        'name': name,
                        'bindings': [
                            {
                                'conditions': conds,
                                'permissions': [
                                    ALL_PERMS.index(p)
                                    for p in perms
                                ],
                                'principals': [
                                    p if isinstance(p, str) else p.to_bytes()
                                    for p in principals
                                ],
                            } for conds, perms, principals in sorted(bindings)
                        ],
                        'data': {
                            'enforce_in_service': ['data for %s' % name],
                        },
                    } for name, bindings in sorted(realms_map.items())
                ],
            },
        ),
        additional_client_ids=[])

  def setUp(self):
    super(RealmsTest, self).setUp()
    self.all_perms = {p.name: p for p in ALL_PERMS}
    self.mock(api, '_all_perms', self.all_perms)
    self.logs = {}
    for lvl in ('info', 'warning', 'error', 'exception'):
      self.logs[lvl] = []
      def appender(lvl):  # need to capture lvl in a separate closure
        return lambda msg, *args: self.logs[lvl].append(msg % args)
      self.mock(api.logging, lvl, appender(lvl))

  def assert_logs_empty(self, lvl):
    self.assertEqual([], self.logs[lvl])

  def assert_logs(self, lvl, msg):
    self.assertTrue(
        any(msg in m for m in self.logs[lvl]),
        '%r not in %r' % (msg, self.logs[lvl]))

  # pylint: disable=redefined-outer-name
  def assert_check(self, db, perm, realms, ident, attrs, outcome):
    self.assertEqual(
        outcome, db.has_permission(perm, realms, ident, attributes=attrs),
        'has_permission(%r, %r, %r, %r) is %s, but should be %s' %
        (perm, realms, ident.to_bytes(), attrs, not outcome, outcome))

  def test_direct_inclusion_in_binding(self):
    db = self.auth_db({
        'proj:@root': [],
        'proj:realm': [
            ([], [PERM0, PERM1], [ID1]),
            ([], [PERM0, PERM2], [ID2]),
        ],
        'proj:another/realm': [
            ([], [PERM2], [ID1, ID3]),
        ],
    })
    self.assert_check(db, PERM0, ['proj:realm'], ID1, None, True)
    self.assert_check(db, PERM1, ['proj:realm'], ID1, None, True)
    self.assert_check(db, PERM2, ['proj:realm'], ID1, None, False)
    self.assert_check(db, PERM0, ['proj:realm'], ID2, None, True)
    self.assert_check(db, PERM1, ['proj:realm'], ID2, None, False)
    self.assert_check(db, PERM2, ['proj:realm'], ID2, None, True)
    self.assert_check(
        db, PERM2, ['proj:realm', 'proj:another/realm'], ID1, None, True)
    self.assert_check(
        db, PERM2, ['proj:realm', 'proj:another/realm'], ID3, None, True)

  def test_inclusion_through_group(self):
    db = self.auth_db({
        'proj:@root': [],
        'proj:realm': [
            ([], [PERM0, PERM1], ['group:empty', 'group:g1']),
            ([], [PERM0, PERM2], ['group:empty', 'group:g2']),
        ],
    }, groups={'empty': [], 'g1': [ID1], 'g2': [ID2]})
    self.assert_check(db, PERM0, ['proj:realm'], ID1, None, True)
    self.assert_check(db, PERM1, ['proj:realm'], ID1, None, True)
    self.assert_check(db, PERM2, ['proj:realm'], ID1, None, False)
    self.assert_check(db, PERM0, ['proj:realm'], ID2, None, True)
    self.assert_check(db, PERM1, ['proj:realm'], ID2, None, False)
    self.assert_check(db, PERM2, ['proj:realm'], ID2, None, True)

  def test_conditional_bindings(self):
    conditions = [
        {'restrict': {'attribute': 'a1', 'values': ['a', 'b']}}, # 0
        {'restrict': {'attribute': 'a2', 'values': ['c']}},      # 1
        {'restrict': {'attribute': 'a3', 'values': []}},         # 2
        {'restrict': {'attribute': 'a1', 'values': ['c']}},      # 3
    ]
    db = self.auth_db({
        'p:r': [
            ([0], [PERM0], [ID1]),
            ([0, 1], [PERM1], [ID1]),
            ([0, 2], [PERM2], [ID1]),

            ([0], [PERM0], [ID2]),
            ([3], [PERM0], [ID2]),
        ],
    }, conditions=conditions)

    # "Restrict" condition works.
    self.assert_check(db, PERM0, ['p:r'], ID1, {'a1': 'a'}, True)
    self.assert_check(db, PERM0, ['p:r'], ID1, {'a1': 'b'}, True)
    self.assert_check(db, PERM0, ['p:r'], ID1, {'a1': 'c'}, False)
    self.assert_check(db, PERM0, ['p:r'], ID1, {'xx': 'a'}, False)
    self.assert_check(db, PERM0, ['p:r'], ID1, None, False)

    # ANDing conditions works.
    self.assert_check(db, PERM1, ['p:r'], ID1, {'a1': 'a', 'a2': 'c'}, True)
    self.assert_check(db, PERM1, ['p:r'], ID1, {'a1': 'a'}, False)
    self.assert_check(db, PERM1, ['p:r'], ID1, {'a2': 'c'}, False)

    # Empty restriction is allowed and evaluates to False.
    self.assert_check(db, PERM2, ['p:r'], ID1, {'a1': 'a', 'a3': 'c'}, False)
    self.assert_check(db, PERM2, ['p:r'], ID1, {'a1': 'a'}, False)

    # ORing conditions via multiple bindings.
    self.assert_check(db, PERM0, ['p:r'], ID2, {'a1': 'a'}, True) # via 0
    self.assert_check(db, PERM0, ['p:r'], ID2, {'a1': 'b'}, True) # via 0
    self.assert_check(db, PERM0, ['p:r'], ID2, {'a1': 'c'}, True) # via 3
    self.assert_check(db, PERM0, ['p:r'], ID2, {'a1': 'x'}, False)
    self.assert_check(db, PERM0, ['p:r'], ID2, None, False)

  def test_fallback_to_root(self):
    db = self.auth_db({'proj:@root': [([], [PERM0], [ID1])]})
    self.assert_check(db, PERM0, ['proj:@root'], ID1, None, True)
    self.assert_check(db, PERM0, ['proj:@root'], ID2, None, False)

    self.assert_logs_empty('warning')
    self.assert_check(db, PERM0, ['proj:realm'], ID1, None, True)
    self.assert_logs('warning', 'falling back to the root')

    self.assert_check(db, PERM0, ['proj:realm'], ID2, None, False)
    self.assert_check(db, PERM0, ['proj:another/realm'], ID1, None, True)

  def test_missing_project(self):
    db = self.auth_db({})

    self.assert_check(db, PERM0, ['proj:@root'], ID1, None, False)
    self.assert_logs('warning', 'a non-existing root realm')
    self.logs['warning'] = []

    self.assert_check(db, PERM0, ['proj:@legacy'], ID1, None, False)
    self.assert_logs('warning', 'doesn\'t have a root realm')
    self.logs['warning'] = []

    self.assert_check(db, PERM0, ['proj:another/realm'], ID1, None, False)
    self.assert_logs('warning', 'doesn\'t have a root realm')
    self.logs['warning'] = []

  def test_unknown_permission(self):
    unknown = api.Permission('luci.dev.unknown')
    self.all_perms[unknown.name] = unknown

    db = self.auth_db({'proj:realm': [([], [PERM0], [ID1])]})
    self.assert_logs('warning', 'is not in the AuthDB')

    self.assert_check(db, unknown, ['proj:realm'], ID1, None, False)
    self.assert_logs('warning', 'not present in the AuthDB')

  def test_realms_unavailable(self):
    empty = new_auth_db()
    with self.assertRaises(api.RealmsError):
      empty.has_permission('luci.dev.p1', ['proj:realm'], ID1)

  def test_bad_api_version(self):
    with self.assertRaises(api.RealmsError):
      self.auth_db({}, api_version=666)

  def test_bad_permission_type(self):
    db = self.auth_db({})
    with self.assertRaises(TypeError):
      db.has_permission('luci.dev.p1', ['proj:realm'], ID1)

  def test_bad_realm_names(self):
    db = self.auth_db({})
    for r in ['z', ':z', 'p:', 'blah blah:z', 'p:BLAH', 'p:@z', 'p:p:z']:
      with self.assertRaises(ValueError):
        db.has_permission(PERM0, [r], ID1)

  def test_has_permission_dryrun(self):
    rc = api.RequestCache()
    rc._auth_db = self.auth_db(
        {'proj:@root': [([], [PERM0], [ID1])]}, groups={'admin': [ADMIN]})
    self.mock(api, 'get_request_cache', lambda: rc)

    # Match.
    self.logs['info'] = []
    api.has_permission_dryrun(
        PERM0, ['proj:@root'], True, ID1,
        admin_group='admin', tracking_bug='bug')
    self.assert_logs('info',
        "bug: has_permission_dryrun('luci.dev.testing0', ['proj:@root'], "
        "'user:1@example.com'), authdb=0: match - ALLOW")
    self.logs['info'] = []
    api.has_permission_dryrun(
        PERM1, ['proj:@root'], False, ID1,
        admin_group='admin', tracking_bug='bug')
    self.assert_logs('info',
        "bug: has_permission_dryrun('luci.dev.testing1', ['proj:@root'], "
        "'user:1@example.com'), authdb=0: match - DENY")

    # Mismatch.
    self.logs['warning'] = []
    api.has_permission_dryrun(
        PERM0, ['proj:@root'], False, ID1,
        admin_group='admin', tracking_bug='bug')
    self.assert_logs('warning',
        "bug: has_permission_dryrun('luci.dev.testing0', ['proj:@root'], "
        "'user:1@example.com'), authdb=0: mismatch - got ALLOW, want DENY")
    self.logs['warning'] = []
    api.has_permission_dryrun(
        PERM1, ['proj:@root'], True, ID1,
        admin_group='admin', tracking_bug='bug')
    self.assert_logs('warning',
        "bug: has_permission_dryrun('luci.dev.testing1', ['proj:@root'], "
        "'user:1@example.com'), authdb=0: mismatch - got DENY, want ALLOW")

    # Admin match.
    self.logs['info'] = []
    api.has_permission_dryrun(
        PERM0, ['proj:@root'], True, ADMIN,
        admin_group='admin', tracking_bug='bug')
    self.assert_logs('info',
        "bug: has_permission_dryrun('luci.dev.testing0', ['proj:@root'], "
        "'user:admin@example.com'), authdb=0: match - ADMIN_ALLOW")

    # Blow up.
    self.logs['exception'] = []
    api.has_permission_dryrun(
        PERM1, ['@root'], True, ID1,
        admin_group='admin', tracking_bug='bug')
    self.assert_logs('exception',
        "bug: has_permission_dryrun('luci.dev.testing1', ['@root'], "
        "'user:1@example.com'), authdb=0: exception ValueError, want ALLOW")

  def test_realm_data(self):
    db = self.auth_db({'proj:@root': [], 'proj:r': []})

    def realm_data(realm):
      r = db.get_realm_data(realm)
      return r.enforce_in_service[0] if r else None

    self.assertEqual('data for proj:r', realm_data('proj:r'))
    self.assertEqual('data for proj:@root', realm_data('proj:@root'))
    self.assertEqual('data for proj:@root', realm_data('proj:zzz'))
    self.assertEqual(None, realm_data('zzz:@root'))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
