#!/usr/bin/env python
# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import sys
import unittest

import test_env
test_env.setup_test_env()

from components import auth
from components import config
from components import utils
from components.config import validation
from test_support import test_case

from proto import pools_pb2
from server import pools_config as pc

from google.protobuf import text_format


TEST_CONFIG = pools_pb2.PoolsCfg(pool=[
  pools_pb2.Pool(
    name=['pool_name', 'another_name'],
    schedulers=pools_pb2.Schedulers(
      user=['user:a@example.com', 'b@example.com'],
      group=['group1', 'group2'],
      trusted_delegation=[
        pools_pb2.TrustedDelegation(
          peer_id='delegatee@example.com',
          require_any_of=pools_pb2.TrustedDelegation.TagList(
            tag=['k:tag1', 'k:tag2'],
          ),
        ),
      ],
    ),
    allowed_service_account=[
      'a1@example.com',
      'a2@example.com',
    ],
    allowed_service_account_group=[
      'accounts_group1',
      'accounts_group2',
    ],
  ),
], forbid_unknown_pools=True)


class PoolsConfigTest(test_case.TestCase):
  def validator_test(self, cfg, messages):
    ctx = validation.Context()
    pc._validate_pools_cfg(cfg, ctx)
    self.assertEquals(ctx.result().messages, [
      validation.Message(severity=logging.ERROR, text=m)
      for m in messages
    ])

  def mock_config(self, cfg):
    def get_self_config_mock(path, cls=None, **kwargs):
      self.assertEqual({'store_last_good': True}, kwargs)
      self.assertEqual('pools.cfg', path)
      self.assertEqual(cls, pools_pb2.PoolsCfg)
      return 'rev', cfg
    self.mock(config, 'get_self_config', get_self_config_mock)
    utils.clear_cache(pc._fetch_pools_config)

  def test_get_pool_config(self):
    self.mock_config(TEST_CONFIG)
    self.assertTrue(pc.forbid_unknown_pools())
    self.assertEqual(None, pc.get_pool_config('unknown'))

    expected1 = pc.PoolConfig(
        name=u'pool_name',
        rev='rev',
        scheduling_users=frozenset([
          auth.Identity('user', 'b@example.com'),
          auth.Identity('user', 'a@example.com'),
        ]),
        scheduling_groups=frozenset([u'group2', u'group1']),
        trusted_delegatees={
          auth.Identity('user', 'delegatee@example.com'):
            pc.TrustedDelegatee(
              peer_id=auth.Identity('user', 'delegatee@example.com'),
              required_delegation_tags=frozenset([u'k:tag1', u'k:tag2']),
            ),
        },
        service_accounts=frozenset([u'a2@example.com', u'a1@example.com']),
        service_accounts_groups=(u'accounts_group1', u'accounts_group2'),
        task_template_deployment=None)
    expected2 = expected1._replace(name='another_name')

    self.assertEqual(expected1, pc.get_pool_config('pool_name'))
    self.assertEqual(expected2, pc.get_pool_config('another_name'))

  def test_empty_config_is_valid(self):
    self.validator_test(pools_pb2.PoolsCfg(), [])

  def test_good_config_is_valid(self):
    self.validator_test(TEST_CONFIG, [])

  def test_missing_pool_name(self):
    cfg = pools_pb2.PoolsCfg(pool=[pools_pb2.Pool()])
    self.validator_test(cfg, [
      'pool #0 (unnamed): at least one pool name must be given',
    ])

  def test_bad_pool_name(self):
    n = 'x'*300
    cfg = pools_pb2.PoolsCfg(pool=[pools_pb2.Pool(name=[n])])
    self.validator_test(cfg, [
      'pool #0 (%s): bad pool name "%s", not a valid dimension value' % (n, n),
    ])

  def test_duplicate_pool_name(self):
    cfg = pools_pb2.PoolsCfg(pool=[
      pools_pb2.Pool(name=['abc']),
      pools_pb2.Pool(name=['abc']),
    ])
    self.validator_test(cfg, [
      'pool #1 (abc): pool "abc" was already declared',
    ])

  def test_bad_scheduling_user(self):
    cfg = pools_pb2.PoolsCfg(pool=[
      pools_pb2.Pool(name=['abc'], schedulers=pools_pb2.Schedulers(
        user=['not valid email'],
      )),
    ])
    self.validator_test(cfg, [
      'pool #0 (abc): bad user value "not valid email" - '
      'Identity has invalid format: not valid email',
    ])

  def test_bad_scheduling_group(self):
    cfg = pools_pb2.PoolsCfg(pool=[
      pools_pb2.Pool(name=['abc'], schedulers=pools_pb2.Schedulers(
        group=['!!!'],
      )),
    ])
    self.validator_test(cfg, [
      'pool #0 (abc): bad group name "!!!"',
    ])

  def test_no_delegatee_peer_id(self):
    cfg = pools_pb2.PoolsCfg(pool=[
      pools_pb2.Pool(name=['abc'], schedulers=pools_pb2.Schedulers(
        trusted_delegation=[pools_pb2.TrustedDelegation()],
      )),
    ])
    self.validator_test(cfg, [
      'pool #0 (abc): trusted_delegation #0 (): "peer_id" is required',
    ])

  def test_bad_delegatee_peer_id(self):
    cfg = pools_pb2.PoolsCfg(pool=[
      pools_pb2.Pool(name=['abc'], schedulers=pools_pb2.Schedulers(
        trusted_delegation=[pools_pb2.TrustedDelegation(
          peer_id='not valid email',
        )],
      )),
    ])
    self.validator_test(cfg, [
      'pool #0 (abc): trusted_delegation #0 (not valid email): bad peer_id '
      'value "not valid email" - Identity has invalid format: not valid email',
    ])

  def test_duplicate_delegatee_peer_id(self):
    cfg = pools_pb2.PoolsCfg(pool=[
      pools_pb2.Pool(name=['abc'], schedulers=pools_pb2.Schedulers(
        trusted_delegation=[
          pools_pb2.TrustedDelegation(peer_id='a@example.com'),
          pools_pb2.TrustedDelegation(peer_id='a@example.com'),
        ],
      )),
    ])
    self.validator_test(cfg, [
      'pool #0 (abc): trusted_delegation #0 (a@example.com): peer '
      '"a@example.com" was specified twice',
    ])

  def test_bad_delegation_tag(self):
    cfg = pools_pb2.PoolsCfg(pool=[
      pools_pb2.Pool(name=['abc'], schedulers=pools_pb2.Schedulers(
        trusted_delegation=[pools_pb2.TrustedDelegation(
          peer_id='a@example.com',
          require_any_of=pools_pb2.TrustedDelegation.TagList(
            tag=['not kv'],
          ),
        )],
      )),
    ])
    self.validator_test(cfg, [
      'pool #0 (abc): trusted_delegation #0 (a@example.com): bad tag #0 '
      '"not kv" - must be <key>:<value>',
    ])

  def test_bad_service_account(self):
    cfg = pools_pb2.PoolsCfg(pool=[pools_pb2.Pool(
      name=['abc'],
      allowed_service_account=['not an email'],
    )])
    self.validator_test(cfg, [
      'pool #0 (abc): bad allowed_service_account #0 "not an email"',
    ])

  def test_bad_service_account_group(self):
    cfg = pools_pb2.PoolsCfg(pool=[pools_pb2.Pool(
      name=['abc'],
      allowed_service_account_group=['!!!'],
    )])
    self.validator_test(cfg, [
      'pool #0 (abc): bad allowed_service_account_group #0 "!!!"',
    ])


class TaskTemplateBaseTest(unittest.TestCase):
  def setUp(self):
    self.ctx = validation.Context()

  @staticmethod
  def tt(cache=None, cipd_package=None, env=None, inclusions=None):
    return pc.TaskTemplate(
      cache=tuple(cache or ()),
      cipd_package=tuple(cipd_package or ()),
      env=tuple(env or ()),
      inclusions=frozenset(inclusions or ()),
    )


class TestTaskTemplates(TaskTemplateBaseTest):
  @staticmethod
  def parse(textpb):
    return text_format.Merge(textpb, pools_pb2.TaskTemplate())

  def test_task_template_update_cache(self):
    tti = pc.TaskTemplate._Intermediate()
    tti.update(self.ctx, self.tt(cache=[pc.CacheEntry('hi', 'there')]))

    self.assertEqual(
      self.tt(cache=[pc.CacheEntry('hi', 'there')]),
      tti.finalize(self.ctx))

    # override existing
    tti.update(self.ctx, self.tt(cache=[pc.CacheEntry('hi', 'nerd')]))

    self.assertEqual(
      self.tt(cache=[pc.CacheEntry('hi', 'nerd')]),
      tti.finalize(self.ctx))

    # add new
    tti.update(self.ctx, self.tt(cache=[
      pc.CacheEntry('other', 'yep'),
    ]))

    self.assertEqual(
      self.tt(cache=[
        pc.CacheEntry('hi', 'nerd'),
        pc.CacheEntry('other', 'yep'),
      ]),
      tti.finalize(self.ctx))

  def test_task_template_update_cipd_package(self):
    tti = pc.TaskTemplate._Intermediate()
    tti.update(self.ctx, self.tt(cipd_package=[
      pc.CipdPackage('path', 'some/pkg', 'latest')]))

    self.assertEqual(
      self.tt(cipd_package=[pc.CipdPackage('path', 'some/pkg', 'latest')]),
      tti.finalize(self.ctx),
    )

    # override existing
    tti.update(self.ctx, self.tt(cipd_package=[
      pc.CipdPackage('path', 'some/pkg', 'oldest')]))

    self.assertEqual(
      self.tt(cipd_package=[pc.CipdPackage('path', 'some/pkg', 'oldest')]),
      tti.finalize(self.ctx),
    )

    # add new
    tti.update(self.ctx, self.tt(cipd_package=[
      pc.CipdPackage('other_path', 'some/pkg', '1'),
    ]))

    self.assertEqual(
      self.tt(cipd_package=[
        pc.CipdPackage('other_path', 'some/pkg', '1'),
        pc.CipdPackage('path', 'some/pkg', 'oldest'),
      ]),
      tti.finalize(self.ctx),
    )

  def test_task_template_update_env(self):
    tti = pc.TaskTemplate._Intermediate()
    tti.update(self.ctx, self.tt(env=[pc.Env('VAR', '1', (), True)]))

    self.assertEqual(
      self.tt(env=[pc.Env('VAR', '1', (), True)]),
      tti.finalize(self.ctx),
    )

    # override existing
    tti.update(self.ctx, self.tt(env=[pc.Env('VAR', '2', (), False)]))

    self.assertEqual(
      self.tt(env=[pc.Env('VAR', '2', (), False)]),
      tti.finalize(self.ctx),
    )

    # add new
    tti.update(self.ctx, self.tt(env=[
      pc.Env('OTHER', 'thing', (), False),
    ]))

    self.assertEqual(
      self.tt(env=[
        pc.Env('OTHER', 'thing', (), False),
        pc.Env('VAR', '2', (), False),
      ]),
      tti.finalize(self.ctx),
    )

  def test_task_template_update_env_prefix(self):
    tti = pc.TaskTemplate._Intermediate()
    tti.update(self.ctx, self.tt(env=[pc.Env('PATH', '', ('1',), True)]))

    self.assertEqual(
      self.tt(env=[pc.Env('PATH', '', ('1',), True)]),
      tti.finalize(self.ctx),
    )

    # append existing
    tti.update(self.ctx, self.tt(env=[pc.Env('PATH', '', ('2',), False)]))

    self.assertEqual(
      self.tt(env=[pc.Env('PATH', '', ('1', '2'), False)]),
      tti.finalize(self.ctx),
    )

    # existing, add new
    tti.update(self.ctx, self.tt(env=[
      pc.Env('OTHER', '', ('thing',), False),
    ]))

    self.assertEqual(
      self.tt(env=[
        pc.Env('OTHER', '', ('thing',), False),
        pc.Env('PATH', '', ('1', '2',), False),
      ]),
      tti.finalize(self.ctx),
    )

  def test_finalize_overlapping_paths(self):
    tti = pc.TaskTemplate._Intermediate()
    tti.update(self.ctx, self.tt(
      cache=[
        pc.CacheEntry('other_name', 'cache_cipd/path'),

        # Cannot overlap caches
        pc.CacheEntry('some_name', 'good/path'),
        pc.CacheEntry('whatnow', 'good/path/b'),
      ],
      cipd_package=[
        pc.CipdPackage('good/other', 'some/pkg', 'latest'),
        pc.CipdPackage('cache_cipd', 'other/pkg', 'latest'),

        # multiple cipd in same dir is OK
        pc.CipdPackage('cache_cipd', 'other/pkg2', 'latest'),
      ]
    ))

    with self.assertRaises(pc.InvalidTaskTemplateError):
      tti.finalize(self.ctx)
    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      [
        "'cipd other/pkg2 latest' overlaps 'cache other_name'",
        "'cache some_name' overlaps 'cache whatnow'",
      ])

  def test_finalize_empty_values(self):
    tti = pc.TaskTemplate._Intermediate()
    tti.update(self.ctx, self.tt(
      cache=[
        pc.CacheEntry('', 'path'),
        pc.CacheEntry('cool_name', ''),
      ],
      cipd_package=[
        pc.CipdPackage('good/other', 'some/pkg', ''),
        pc.CipdPackage('', 'some/pkg', 'latest'),
        pc.CipdPackage('good/other', '', 'latest'),
      ],
      env=[
        pc.Env('', '1', ('path',), True),
        pc.Env('VAR', '1', ('',), True),
        pc.Env('VARR', '', (), True),
      ],
    ))

    with self.assertRaises(pc.InvalidTaskTemplateError):
      tti.finalize(self.ctx)
    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      [
        'cache[#0]: empty name',
        "cache['cool_name']: empty path",
        "cipd_package[('good/other', 'some/pkg')]: empty version",
        'cipd_package[#2]: empty pkg',
        'env[#0]: empty var',
        'env[\'VARR\']: empty value AND prefix',
        "'cache cool_name' overlaps 'cipd some/pkg latest'",
      ])

  def test_simple_pb(self):
    tt = self.parse("""
    cache: { name: "hi"  path: "cache/hi" }
    cache: { name: "there"  path: "cache/there" }
    cipd_package: { path: "bin" pkg: "foo/bar" version: "latest" }
    env: {var: "VAR" value: "1"}
    env: {var: "PATH" prefix: "1" prefix: "2" soft: true}
    """)

    self.assertEqual(
      pc.TaskTemplate.from_pb(self.ctx, tt, {}),
      pc.TaskTemplate(
        cache=(
          pc.CacheEntry(name='hi', path='cache/hi'),
          pc.CacheEntry(name='there', path='cache/there'),
        ),
        cipd_package=(
          pc.CipdPackage(path='bin', pkg='foo/bar', version='latest'),
        ),
        env=(
          pc.Env('PATH', '', ('1', '2'), True),
          pc.Env('VAR', '1', (), False),
        ),
        inclusions=frozenset(),
      ))

  def test_simple_include(self):
    base = pc.TaskTemplate.from_pb(self.ctx, self.parse("""
    cache: { name: "hi"  path: "cache/hi" }
    cipd_package: { path: "bin" pkg: "foo/bar" version: "latest" }
    env: {var: "VAR" value: "1"}
    env: {var: "PATH" prefix: "1" prefix: "2" soft: true}
    """), {})

    tt = self.parse("""
    include: "base"
    cache: { name: "there"  path: "cache/there" }
    cipd_package: { path: "bin" pkg: "foo/nerps" version: "yes" }
    env: {var: "VAR" value: "2"}
    env: {var: "PATH" prefix: "3" soft: true}
    """)

    self.assertEqual(
      pc.TaskTemplate.from_pb(self.ctx, tt, {'base': base}),
      pc.TaskTemplate(
        cache=(
          pc.CacheEntry(name='hi', path='cache/hi'),
          pc.CacheEntry(name='there', path='cache/there'),
        ),
        cipd_package=(
          pc.CipdPackage(path='bin', pkg='foo/bar', version='latest'),
          pc.CipdPackage(path='bin', pkg='foo/nerps', version='yes'),
        ),
        env=(
          pc.Env('PATH', '', ('1', '2', '3'), True),
          pc.Env('VAR', '2', (), False),
        ),
        inclusions=frozenset({'base'}),
      ))


class TestPoolCfgTaskTemplate(TaskTemplateBaseTest):
  @staticmethod
  def parse(textpb):
    return text_format.Merge(textpb, pools_pb2.PoolsCfg())

  def test_resolve_tree_inclusion(self):
    poolcfg = self.parse("""
      task_template: {
        name: "a"
        env: {var: "VAR" value: "1"}
      }
      task_template: {
        name: "b"
        env: {var: "VAR" prefix: "pfx"}
      }
      task_template: {
        name: "c"
        include: "a"
        include: "b"
      }
      task_template: {
        name: "d"
        include: "c"
      }
    """)

    template_map = pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template)

    self.assertSetEqual(set('abcd'), set(template_map.keys()))

    self.assertEqual(template_map['d'], self.tt(
      env=(
        pc.Env('VAR', '1', ("pfx",), False),
      ),
      inclusions='abc',
    ))

  def test_resolve_repeated_inclusion(self):
    poolcfg = self.parse("""
      task_template: {name: "a"}
      task_template: {
        name: "b"
        include: "a"
        include: "a"
      }
    """)

    pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template)

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ["template['b']: template 'a' included multiple times"])

  def test_resolve_diamond_inclusion(self):
    poolcfg = self.parse("""
      task_template: {name: "a"}
      task_template: {
        name: "b"
        include: "a"
      }
      task_template: {
        name: "c"
        include: "a"
      }
      task_template: {
        name: "d"
        include: "b" include: "c"
      }
    """)

    pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template)

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ["template['d']: template 'a' included (transitively) multiple times"])

  def test_inclusion_cycle(self):
    poolcfg = self.parse("""
      task_template: {name: "a" include: "b"}
      task_template: {name: "b" include: "a"}
    """)

    self.assertIsNone(pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ['include cycle detected'])

  def test_no_name(self):
    poolcfg = self.parse("""
      task_template: {}
    """)

    self.assertIsNone(pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ['one or more templates has a blank name'])

  def test_dup_name(self):
    poolcfg = self.parse("""
      task_template: {name: "a"}
      task_template: {name: "a"}
    """)

    self.assertIsNone(pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ['one or more templates has a duplicate name'])

  def test_bad_include(self):
    poolcfg = self.parse("""
      task_template: {name: "a" include: "nope"}
    """)

    self.assertIsNone(pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ["template['a']: unknown include: 'nope'"])

  def test_bad_result(self):
    poolcfg = self.parse("""
      task_template: {
        name: "a"
        env: {var: "VAR" }
      }
    """)

    self.assertIsNone(pc._resolve_task_template_inclusions(
      self.ctx, poolcfg.task_template))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ["template['a']: env['VAR']: empty value AND prefix"])


class TestPoolCfgTaskTemplateDeployments(TaskTemplateBaseTest):
  @staticmethod
  def parse(textpb):
    return text_format.Merge(textpb, pools_pb2.PoolsCfg())

  def test_resolve_deployments(self):
    poolcfg = self.parse("""
      task_template: {name: "prod" env: {var: "VAR" value: "prod"}}
      task_template: {name: "canary" env: {var: "VAR" value: "canary"}}

      task_template_deployment: {
        name: "standard"
        prod: {include: "prod"}
        canary: {include: "canary"}
        canary_chance: 5000
      }

      task_template_deployment: {
        name: "fun"
        prod: {include: "canary"}
        canary: {include: "canary"}
        canary_chance: 0
      }
    """)

    tmap = pc._resolve_task_template_inclusions(self.ctx, poolcfg.task_template)
    dmap = pc._resolve_task_template_deployments(
      self.ctx, tmap, poolcfg.task_template_deployment)

    self.assertSetEqual({'standard', 'fun'}, set(dmap.keys()))

    self.assertEqual(dmap['standard'], pc.TaskTemplateDeployment(
      prod=self.tt(env=(pc.Env('VAR', 'prod', (), False),),
                   inclusions={'prod'}),
      canary=self.tt(env=(pc.Env('VAR', 'canary', (), False),),
                     inclusions={'canary'}),
      canary_chance=5000,
    ))

    self.assertEqual(dmap['fun'], pc.TaskTemplateDeployment(
      prod=self.tt(env=(pc.Env('VAR', 'canary', (), False),),
                   inclusions={'canary'}),
      canary=None,
      canary_chance=None,
    ))

  def test_resolve_noname_deployment(self):
    poolcfg = self.parse("""
      task_template_deployment: {}
    """)

    self.assertIsNone(pc._resolve_task_template_deployments(
      self.ctx, {}, poolcfg.task_template_deployment))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ["deployment[0]: has no name"])

  def test_resolve_bad_canary(self):
    poolcfg = self.parse("""
      task_template_deployment: {name: "a" canary_chance: 10000}
    """)

    self.assertIsNone(pc._resolve_task_template_deployments(
      self.ctx, {}, poolcfg.task_template_deployment))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ["deployment['a']: "+
       "canary_chance out of range `[0,9999]`: 10000 -> %100.00"])

  def test_resolve_bad_canary_2(self):
    poolcfg = self.parse("""
      task_template_deployment: {name: "a" canary_chance: -1}
    """)

    self.assertIsNone(pc._resolve_task_template_deployments(
      self.ctx, {}, poolcfg.task_template_deployment))

    self.assertEqual(
      [x.text for x in self.ctx.result().messages],
      ["deployment['a']: canary_chance out of range `[0,9999]`: -1 -> %-0.01"])

  def test_resolve_single_deployment(self):
    poolcfg = self.parse("""
      task_template: {name: "a" env: {var: "VAR" value: "1"} }
      task_template_deployment: {
        name: "std"
        prod: {include: "a"}
        canary_chance: 0
      }
      pool {
        task_template_deployment: "std"
      }
      pool {
        task_template_deployment_inline: {
          prod: {include: "a"}
          canary: {
            include: "a"
            env: {var: "WAT" value: "yes"}
          }
          canary_chance: 5000
        }
      }
    """)

    tmap = pc._resolve_task_template_inclusions(self.ctx, poolcfg.task_template)
    dmap = pc._resolve_task_template_deployments(
      self.ctx, tmap, poolcfg.task_template_deployment)

    self.assertEqual(pc.TaskTemplateDeployment(
      prod=self.tt(env=(pc.Env("VAR", "1", (), False),), inclusions={'a'}),
      canary=None, canary_chance=None
    ), pc._resolve_deployment(self.ctx, poolcfg.pool[0], tmap, dmap))

    self.assertEqual(pc.TaskTemplateDeployment(
      prod=self.tt(env=(pc.Env("VAR", "1", (), False),), inclusions={'a'}),
      canary=self.tt(
        env=(
          pc.Env("VAR", "1", (), False),
          pc.Env("WAT", "yes", (), False)),
        inclusions={'a'}),
      canary_chance=5000,
    ), pc._resolve_deployment(self.ctx, poolcfg.pool[1], tmap, dmap))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
