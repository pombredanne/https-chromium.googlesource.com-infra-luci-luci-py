#!/usr/bin/env vpython3
# Copyright 2013 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import copy
import datetime
import json
import logging
import os
import random
import sys
import tempfile
import textwrap
import threading
import time
import unittest
import uuid
import zipfile

import test_env_bot_code
test_env_bot_code.setup_test_env()

# Creates a server mock for functions in net.py.
import net_utils

from api import bot
from api import os_utilities
from api.platforms import gce
from bot_code import bot_main
from bot_code import clock
from bot_code import remote_client
from depot_tools import fix_encoding
from utils import file_path
from utils import logging_utils
from utils import net
from utils import subprocess42
from utils import tools
from utils import zip_package


# pylint: disable=no-self-argument


REQUEST_UUID = '7905e667-d415-48f1-9df7-f914541d6331'


class FakeThreadingEvent(object):
  def __init__(self):
    self.signaled = False
    self.slept = []
    self.now = 1234.0

  def is_set(self):
    return self.signaled

  def wait(self, timeout):
    self.slept.append(timeout)
    # Add extra time to emulate "real" sleeps and avoid floating point epsilon
    # issues when comparing how long we slept.
    self.now += max(0.0, timeout) + 0.0001
    return self.signaled

  def set(self):
    self.signaled = True

  def reset(self):
    self.signaled = False
    del self.slept[:]


class TestBotBase(net_utils.TestCase):
  maxDiff = None

  def setUp(self):
    super(TestBotBase, self).setUp()
    tools.clear_cache_all()
    # Throw away all swarming environ if running the test on Swarming. It may
    # interfere with the test.
    for k in os.environ:
      if k.startswith('SWARMING_'):
        os.environ.pop(k)
    self.root_dir = tempfile.mkdtemp(prefix='bot_main')
    self.old_cwd = os.getcwd()
    os.chdir(self.root_dir)
    self.url = 'https://localhost:1'
    self.attributes = {
        'dimensions': {
            'foo': ['bar'],
            'id': ['localhost'],
            'pool': ['default'],
            'server_version': ['version1'],
        },
        'state': {
            'bot_group_cfg_version': None,
            'cost_usd_hour': 3600.,
            'rbe_instance': None,
            'sleep_streak': 0,
        },
        'version': '123',
    }
    self.mock(uuid, 'uuid4', lambda: uuid.UUID(REQUEST_UUID))
    self.mock(os_utilities,
              'get_dimensions', lambda: self.attributes['dimensions'])
    self.mock(os_utilities, 'get_state', lambda *_: self.attributes['state'])
    self.mock(bot_main, 'get_config', lambda: {
        'server': self.url,
        'server_version': 'version1',
    })
    self.mock(bot_main, '_TRAP_ALL_EXCEPTIONS', False)
    self.quit_bit = None  # see make_bot
    self.bot = None  # see make_bot
    self.clock = None  # see make_bot
    self.loop_state = None  # see make_bot
    self.make_bot()

  def tearDown(self):
    os.chdir(self.old_cwd)
    file_path.rmtree(self.root_dir)
    super(TestBotBase, self).tearDown()

  def make_bot(self, auth_headers_cb=None):
    self.quit_bit = FakeThreadingEvent()
    self.bot = bot.Bot(
        remote_client.createRemoteClient(self.url, auth_headers_cb, 'localhost',
                                         self.root_dir), self.attributes,
        self.url,
        bot_main.get_config()['server_version'], self.root_dir, self.fail)
    bot_main._update_bot_attributes(self.bot, 0)
    self.clock = clock.Clock(self.quit_bit)
    self.clock._now_impl = lambda: self.quit_bit.now
    self.loop_state = bot_main._BotLoopState(self.bot, None, self.quit_bit,
                                             self.clock)

  def poll_once(self):
    self.quit_bit.reset()
    self.loop_state.run(test_hook=lambda: False)

  def prep_hybrid_mode(self, rbe_params, scheduler='swarming'):
    self.loop_state.rbe_enable(rbe_params)
    self.loop_state._next_scheduler = scheduler
    self.loop_state._swarming_poll_timer.reset(0.0)

  def expected_poll_request(self,
                            response,
                            rbe_idle=None,
                            sleep_streak=None,
                            force=False,
                            extra_headers=None):
    data = self.attributes

    def on_request(kwargs):
      self.assertEqual(kwargs['data']['request_uuid'], REQUEST_UUID)
      self.assertEqual(kwargs['data']['dimensions'], data['dimensions'])
      if rbe_idle is not None:
        self.assertEqual(kwargs['data']['state']['rbe_idle'], rbe_idle)
      if sleep_streak is not None:
        self.assertEqual(kwargs['data']['state']['sleep_streak'], sleep_streak)
      self.assertEqual(kwargs['data'].get('force', False), force)
      if extra_headers is not None:
        with_extra = dict(kwargs['headers'])
        with_extra.update(extra_headers)
        self.assertEqual(kwargs['headers'], with_extra)

    return 'https://localhost:1/swarming/api/v1/bot/poll', on_request, response

  def expected_claim_request(self, claim_id, task_id, task_to_run_shard,
                             task_to_run_id, response):
    data = self.attributes

    def on_request(kwargs):
      self.assertEqual(kwargs['data']['dimensions'], data['dimensions'])
      self.assertEqual(kwargs['data']['state'], data['state'])
      self.assertEqual(kwargs['data']['claim_id'], claim_id)
      self.assertEqual(kwargs['data']['task_id'], task_id)
      self.assertEqual(kwargs['data']['task_to_run_shard'], task_to_run_shard)
      self.assertEqual(kwargs['data']['task_to_run_id'], task_to_run_id)

    return 'https://localhost:1/swarming/api/v1/bot/claim', on_request, response

  def expected_task_update_request(self, task_id):
    def on_request(kwargs):
      self.assertEqual(kwargs['data']['task_id'], task_id)

    return (
        'https://localhost:1/swarming/api/v1/bot/task_update/' + task_id,
        on_request,
        {},
    )

  def expected_rbe_create_request(self, poll_token, session_token, fail=False):
    data = {
        'dimensions': self.attributes['dimensions'],
        'poll_token': poll_token,
    }

    def on_request(kwargs):
      self.assertEqual(kwargs['data'], data)

    return (
        'https://localhost:1/swarming/api/v1/bot/rbe/session/create',
        on_request,
        None if fail else {
            'session_token': session_token,
            'session_id': 'fake-rbe-session-id',
        },
    )

  def expected_rbe_update_request(self,
                                  poll_token,
                                  session_token,
                                  status_in='OK',
                                  status_out='OK',
                                  lease_in=None,
                                  lease_out=None,
                                  blocking=True):
    data = {
        'status': status_in,
        'dimensions': self.attributes['dimensions'],
        'session_token': session_token,
    }
    if lease_in:
      data['lease'] = lease_in
    if not blocking:
      data['nonblocking'] = True
    # Shutdown requests and pings skip poll tokens.
    if poll_token:
      data['poll_token'] = poll_token

    def on_request(kwargs):
      self.assertEqual(kwargs['data'], data)
      # Emulate RBE blocking waiting for a lease.
      self.clock.sleep(10.0)

    response = {
        'session_token': session_token,
        'status': status_out,
    }
    if lease_out:
      response['lease'] = lease_out

    return (
        'https://localhost:1/swarming/api/v1/bot/rbe/session/update',
        on_request,
        response,
    )


class TestBotMain(TestBotBase):
  def setUp(self):
    super(TestBotMain, self).setUp()
    # __main__ does it for us.
    os.mkdir('logs')
    self.mock(zip_package, 'generate_version', lambda: '123')
    self.mock(self.bot, 'post_error', self.fail)
    self.mock(os_utilities, 'host_reboot', self.fail)
    self.mock(subprocess42, 'call', self.fail)
    self.mock(time, 'time', lambda: 100.)
    self.mock(remote_client, 'make_appengine_id', lambda *a: 42)
    self.mock(random, 'uniform', lambda a, _b: a)
    self.mock(bot_main, '_bot_restart', self.fail)
    self.mock(bot_main, 'THIS_FILE',
              os.path.join(test_env_bot_code.BOT_DIR, 'swarming_bot.zip'))
    # Need to disable this otherwise it'd kill the current checkout.
    self.mock(bot_main, '_cleanup_bot_directory', lambda _: None)
    # Test results shouldn't depend on where they run. And they should not use
    # real GCE tokens.
    self.mock(gce, 'is_gce', lambda: False)
    self.mock(
        gce, 'oauth2_access_token_with_expiration',
        lambda *_args, **_kwargs: ('fake-access-token', 0))
    # Ensures the global state is reset after each test case.
    self.mock(bot_main, '_BOT_CONFIG', None)
    self.mock(bot_main, '_EXTRA_BOT_CONFIG', None)
    self.mock(bot_main, '_QUARANTINED', None)
    self.mock(bot_main, 'SINGLETON', None)

  def print_err_and_fail(self, _bot, msg, _task_id):
    print(msg)
    self.fail('post_error_task was called')

  def test_hook_restart(self):
    from config import bot_config
    def get_dimensions(botobj):
      self.assertEqual(self.bot, botobj)
      self.bot.bot_restart('Yo')
      return {'id': ['foo'], 'pool': ['bar']}
    self.mock(bot_config, 'get_dimensions', get_dimensions)
    restarts = []
    self.mock(bot_main, '_bot_restart', lambda *args: restarts.append(args))
    expected = {
        'id': ['foo'],
        'pool': ['bar'],
        'server_version': ['version1']
    }
    self.assertEqual(expected, bot_main._get_dimensions(self.bot))
    self.assertEqual('Yo', self.bot.bot_restart_msg())
    self.assertEqual([(self.bot, 'Yo')], restarts)

  def test_get_dimensions(self):
    from config import bot_config
    def get_dimensions(botobj):
      self.assertEqual(self.bot, botobj)
      return {'yo': ['dawh']}

    self.mock(bot_config, 'get_dimensions', get_dimensions)
    expected = {'server_version': ['version1'], 'yo': ['dawh']}
    self.assertEqual(expected, bot_main._get_dimensions(self.bot))

  def test_get_dimensions_extra(self):
    from config import bot_config
    def get_dimensions(botobj):
      self.assertEqual(self.bot, botobj)
      return {'yo': ['dawh']}
    self.mock(bot_config, 'get_dimensions', get_dimensions)

    # The extra version takes priority.
    class extra(object):
      def get_dimensions(self2, botobj): # pylint: disable=no-self-argument
        self.assertEqual(self.bot, botobj)
        return {'alternative': ['truth']}
    self.mock(bot_main, '_EXTRA_BOT_CONFIG', extra())
    expected = {'alternative': ['truth'], 'server_version': ['version1']}
    self.assertEqual(expected, bot_main._get_dimensions(self.bot))

  def test_generate_version(self):
    self.assertEqual('123', bot_main.generate_version())

  def test_get_state(self):
    from config import bot_config
    def get_state(botobj):
      self.assertEqual(self.bot, botobj)
      return {'yo': 'dawh'}
    self.mock(bot_config, 'get_state', get_state)
    expected = {'sleep_streak': 0.1, 'yo': 'dawh'}
    self.assertEqual(expected, bot_main._get_state(self.bot, 0.1))

  def test_get_state_quarantine(self):
    botobj = bot_main.get_bot(bot_main.get_config())
    root = 'c:\\' if sys.platform == 'win32' else '/'
    def get_state(_):
      return {
          'disks': {
              root: {
                  'free_mb': 0.1,
                  'size_mb': 1000,
              },
              botobj.base_dir: {
                  'free_mb': 0.1,
                  'size_mb': 1000,
              },
          },
      }

    # This uses the default get_settings() values. The threshold used is
    # dependent on these values. This affects the error message below.
    # 'size' == 4096Mb
    # 'max_percent' == 15% * 1000Mb = 150Mb
    # 'min_percent' == 5% of 1000Mb == 50Mb
    # 'max_percent' is chosen.
    from config import bot_config
    self.mock(bot_config, 'get_state', get_state)
    expected = {
        'disks': {
            'c:\\' if sys.platform == 'win32' else '/': {
                'free_mb': 0.1,
                'size_mb': 1000,
            },
            botobj.base_dir: {
                'free_mb': 0.1,
                'size_mb': 1000,
            },
        },
        'quarantined':
            ('Not enough free disk space on %s. 0.1mib < 100.0mib\n'
             'Not enough free disk space on %s. 0.1mib < 150.0mib') %
            (root, botobj.base_dir),
        'sleep_streak':
            1,
    }
    self.assertEqual(expected, bot_main._get_state(botobj, 1))

  def test_get_state_quarantine_sticky(self):
    # A crash in get_dimensions() causes sticky quarantine in get_state.
    from config import bot_config

    def get_dimensions(botobj):
      self.assertEqual(self.bot, botobj)
      return 'invalid'

    self.mock(bot_config, 'get_dimensions', get_dimensions)

    def get_dimensions_os():
      return {'os': ['safe']}

    self.mock(os_utilities, 'get_dimensions', get_dimensions_os)
    def get_state(botobj):
      self.assertEqual(self.bot, botobj)
      return {'yo': 'dawh'}
    self.mock(bot_config, 'get_state', get_state)

    expected = {
        'os': ['safe'],
        'quarantined': ['1'],
        'server_version': ['version1'],
    }
    self.assertEqual(expected, bot_main._get_dimensions(self.bot))
    expected = {
        'quarantined': "get_dimensions(): expected a dict, got 'invalid'",
        'sleep_streak': 0.1,
        'yo': 'dawh',
    }
    self.assertEqual(expected, bot_main._get_state(self.bot, 0.1))

  def test_get_disks_quarantine_empty(self):
    root = 'c:\\' if sys.platform == 'win32' else '/'
    disks = {
        self.bot.base_dir: {
            'free_mb': 0,
            'size_mb': 0,
        },
        root: {
            'free_mb': 0,
            'size_mb': 0,
        },
    }
    expected = ('Not enough free disk space on %s. 0.0mib < 1024.0mib\n'
                'Not enough free disk space on %s. 0.0mib < 4096.0mib') % (
                    root, self.bot.base_dir)
    self.assertEqual(expected, bot_main._get_disks_quarantine(self.bot, disks))

  def test_get_disks_quarantine(self):
    root = 'c:\\' if sys.platform == 'win32' else '/'
    disks = {
        self.bot.base_dir: {
            'free_mb': 4096,
            'size_mb': 4096,
        },
        root: {
            'free_mb': 4096,
            'size_mb': 4096,
        },
    }
    expected = None
    self.assertEqual(expected, bot_main._get_disks_quarantine(self.bot, disks))

  def test_default_settings(self):
    # If this trigger, you either forgot to update bot_main.py or bot_config.py.
    from config import bot_config
    self.assertEqual(bot_main.DEFAULT_SETTINGS, bot_config.get_settings(None))

  def test_min_free_disk(self):
    # size_mb, size, min_percent, max_percent, expected
    data = [
        (0, 0, 0, 0, 0),
        # 1GB*10% = 100Mb
        (1000, 1000, 10., 20., 104857600),
        # size is between min_percent (104857600) and max_percent (209715200)
        (1000, 150000000, 10., 20., 150000000),
        # 1GB*20% = 200Mb
        (1000, 300000000, 10., 20., 209715200),
        # No max_percent, so use size
        (1000, 300000000, 10., 0, 300000000),
    ]
    for size_mb, size, minp, maxp, expected in data:
      infos = {'size_mb': size_mb}
      settings = {'size': size, 'min_percent': minp, 'max_percent': maxp}
      actual = bot_main._min_free_disk(infos, settings)
      self.assertEqual(expected, actual)

  def test_dict_deep_merge(self):
    a = {
        'a': {
            'a': 1,
            'b': 2,
        },
    }
    b = {
        'a': {
            'b': 3,
            'c': 4,
        },
    }
    expected = {
      'a': {
        'a': 1,
        'b': 3,
        'c': 4,
      },
    }
    self.assertEqual(expected, bot_main._dict_deep_merge(a, b))
    self.assertEqual(a, bot_main._dict_deep_merge(a, None))
    self.assertEqual(a, bot_main._dict_deep_merge(None, a))

  def test_setup_bot(self):
    setup_bots = []

    def setup_bot(_bot):
      setup_bots.append(1)
      return False

    from config import bot_config
    self.mock(bot_config, 'setup_bot', setup_bot)
    self.mock(bot, '_make_stack', lambda: 'fake stack')
    restarts = []
    post_event = []
    self.mock(os_utilities, 'host_reboot',
              lambda *a, **kw: restarts.append((a, kw)))
    self.mock(bot.Bot, 'post_event',
              lambda *a, **kw: post_event.append((a, kw)))
    self.expected_requests([])
    bot_main.setup_bot(False)
    expected = [
      (('Starting new swarming bot: %s' % bot_main.THIS_FILE,),
        {'timeout': 900}),
    ]
    self.assertEqual(expected, restarts)
    # It is called twice, one as part of setup_bot(False), another as part of
    # on_shutdown_hook().
    self.assertEqual([1, 1], setup_bots)
    expected = [
        'Starting new swarming bot: %s' % bot_main.THIS_FILE,
        ('Host is stuck rebooting for: Starting new swarming bot: %s\n'
         'Calling stack:\nfake stack') % bot_main.THIS_FILE,
    ]
    self.assertEqual(expected, [i[0][2] for i in post_event])

  def test_post_error_task(self):
    self.mock(time, 'time', lambda: 126.0)
    self.mock(logging, 'error', lambda *_, **_kw: None)
    self.assertEqual('localhost', self.bot.id)
    self.expected_requests([
        (
            'https://localhost:1/swarming/api/v1/bot/task_error/23',
            {
                'data': {
                    'id': self.bot.id,
                    'message': 'error',
                    'client_error': {
                        'missing_cas': [],
                        'missing_cipd': [],
                    },
                    'task_id': 23,
                },
                'expected_error_codes': None,
                'follow_redirects': False,
                'headers': {
                    'Cookie': 'GOOGAPPUID=42',
                    'X-Luci-Swarming-Bot-ID': 'localhost',
                },
                'timeout': remote_client.NET_CONNECTION_TIMEOUT_SEC,
                'max_attempts': remote_client.NET_MAX_ATTEMPTS,
            },
            {
                'resp': 1
            },
        ),
    ])
    self.assertEqual(True, bot_main._post_error_task(self.bot, 'error', 23))

  def test_do_handshake(self):
    # Ensures the injected code was called. Ensures the injected name is
    # 'injected', that it can imports the base one.

    # Hack into bot_config.
    bot_config = bot_main._get_bot_config()
    bot_config.base_func = lambda: 'yo'
    try:
      def do_handshake(attributes):
        return {
          'bot_version': attributes['version'],
          'bot_group_cfg_version': None,
          'bot_group_cfg': None,
          'bot_config': textwrap.dedent("""
              from config import bot_config
              def get_dimensions(_):
                return {
                  'alternative': __name__,
                  'bot_config': bot_config.__file__,
                  'called': bot_config.base_func(),
                }
              """),
        }

      self.mock(self.bot.remote, 'do_handshake', do_handshake)
      bot_main._do_handshake(self.bot, self.quit_bit)
      self.assertEqual(None, self.bot.bot_restart_msg())
      expected = {
          'alternative': 'injected',
          'bot_config': bot_config.__file__,
          'called': 'yo',
      }
      self.assertEqual(expected,
                       bot_main._EXTRA_BOT_CONFIG.get_dimensions(self.bot))
    finally:
      del bot_config.base_func

  def test_call_hook_both(self):
    # Both hooks must be called.
    first = threading.Event()
    second = threading.Event()
    from config import bot_config
    def on_bot_shutdown_1(botobj):
      self.assertEqual(self.bot, botobj)
      first.set()
    self.mock(bot_config, 'on_bot_shutdown', on_bot_shutdown_1)

    class extra(object):
      def on_bot_shutdown(self2, botobj): # pylint: disable=no-self-argument
        self.assertEqual(self.bot, botobj)
        second.set()
    self.mock(bot_main, '_EXTRA_BOT_CONFIG', extra())
    bot_main._call_hook(True, self.bot, 'on_bot_shutdown')
    self.assertTrue(first.is_set())
    self.assertTrue(second.is_set())

  def test_run_bot(self):
    # Test the run_bot() loop. Does not use self.bot.
    fake_event = FakeThreadingEvent()
    fake_clock = clock.Clock(fake_event)
    fake_clock._now_impl = lambda: fake_event.now
    self.mock(threading, 'Event', lambda: fake_event)
    self.mock(clock, 'Clock', lambda _: fake_clock)
    self.mock(time, 'time', lambda: fake_event.now)

    # pylint: disable=unused-argument
    class Popen(object):
      def __init__(
          self2, cmd, detached, cwd, stdout, stderr, stdin, **kwargs):
        self2.returncode = None
        expected = [sys.executable, bot_main.THIS_FILE, 'run_isolated']
        self.assertEqual(expected, cmd[:len(expected)])
        self.assertEqual(True, detached)
        self.assertEqual(subprocess42.PIPE, stdout)
        self.assertEqual(subprocess42.STDOUT, stderr)
        self.assertEqual(subprocess42.PIPE, stdin)
        if sys.platform == 'win32':
          creationflags = kwargs['creationflags']
          self.assertEqual(subprocess42.CREATE_NEW_CONSOLE, creationflags)
        else:
          close_fds = kwargs['close_fds']
          self.assertTrue(close_fds)

      def communicate(self2, i):
        self.assertEqual(None, i)
        self2.returncode = 0
        return '', None
    self.mock(subprocess42, 'Popen', Popen)

    orig = bot_main.get_bot
    botobj = [None]

    def get_bot(config):
      botobj[0] = orig(config)
      return botobj[0]

    self.mock(bot_main, 'get_bot', get_bot)

    # Polling will happen with an extra dimensions returned in the handshake.
    def payload(sleep_streak, extra):
      attrs = copy.deepcopy(self.attributes)
      attrs['dimensions']['bot_side'] = ['A']
      attrs['state'] = {
          'bot_config': {
              'name': None,
              'revision': None
          },
          'bot_group_cfg_version': 'abc:def',
          'cost_usd_hour': 3600.0,
          'rbe_instance': None,
          'sleep_streak': sleep_streak,
          'original_bot_id': 'localhost',
      }
      attrs.update(extra)
      return attrs

    def expect_poll(sleep_streak, resp):
      return (
          'https://localhost:1/swarming/api/v1/bot/poll',
          {
              'data': payload(sleep_streak, {'request_uuid': REQUEST_UUID}),
              'expected_error_codes': None,
              'follow_redirects': False,
              'headers': {
                  'Cookie': 'GOOGAPPUID=42',
                  'X-Luci-Swarming-Bot-ID': 'localhost',
              },
              'timeout': remote_client.NET_CONNECTION_TIMEOUT_SEC,
              'max_attempts': 1,
          },
          resp,
      )

    self.expected_requests([
        (
            'https://localhost:1/swarming/api/v1/bot/server_ping',
            {},
            'foo',
            None,
        ),
        (
            'https://localhost:1/swarming/api/v1/bot/handshake',
            {
                'data': self.attributes,
                'expected_error_codes': None,
                'follow_redirects': False,
                'headers': {
                    'Cookie': 'GOOGAPPUID=42',
                    'X-Luci-Swarming-Bot-ID': 'localhost',
                },
                'timeout': remote_client.NET_CONNECTION_TIMEOUT_SEC,
                'max_attempts': remote_client.NET_MAX_ATTEMPTS,
            },
            None,  # fails, gets retried
        ),
        (
            'https://localhost:1/swarming/api/v1/bot/handshake',
            {
                'data': self.attributes,
                'expected_error_codes': None,
                'follow_redirects': False,
                'headers': {
                    'Cookie': 'GOOGAPPUID=42',
                    'X-Luci-Swarming-Bot-ID': 'localhost',
                },
                'timeout': remote_client.NET_CONNECTION_TIMEOUT_SEC,
                'max_attempts': remote_client.NET_MAX_ATTEMPTS,
            },
            {
                'bot_version': '123',
                'server': self.url,
                'server_version': 1,
                'bot_group_cfg_version': 'abc:def',
                'bot_group_cfg': {
                    'dimensions': {
                        'bot_side': ['A']
                    },
                },
            },
        ),
        expect_poll(0, {
            'cmd': 'sleep',
            'duration': 1.0
        }),
        expect_poll(1, {
            'cmd': 'sleep',
            'duration': 1.0
        }),
        expect_poll(2, None),  # fails, gets retried
        expect_poll(2, None),  # fails, gets retried
        expect_poll(2, {
            'cmd': 'sleep',
            'duration': 1.0
        }),
        expect_poll(3, {
            'cmd': 'terminate',
            'task_id': 'terminate-id'
        }),
        # Reports the termination task as finished.
        (
            'https://localhost:1/swarming/api/v1/bot/task_update/terminate-id',
            {
                'data': {
                    'id': 'localhost',
                    'task_id': 'terminate-id',
                    'duration': 0,
                    'exit_code': 0,
                },
                'expected_error_codes': None,
                'follow_redirects': False,
                'headers': {
                    'Cookie': 'GOOGAPPUID=42',
                    'X-Luci-Swarming-Bot-ID': 'localhost',
                },
                'timeout': remote_client.NET_CONNECTION_TIMEOUT_SEC,
                'max_attempts': remote_client.NET_MAX_ATTEMPTS,
            },
            {
                'ok': True,
            },
        ),
        # Reports that the bot is shutting down.
        (
            'https://localhost:1/swarming/api/v1/bot/event',
            {
                'data':
                payload(3, {
                    'event': 'bot_shutdown',
                    'message': 'Signal was received',
                }),
                'expected_error_codes':
                None,
                'follow_redirects':
                False,
                'headers': {
                    'Cookie': 'GOOGAPPUID=42',
                    'X-Luci-Swarming-Bot-ID': 'localhost',
                },
                'timeout':
                remote_client.NET_CONNECTION_TIMEOUT_SEC,
                'max_attempts':
                remote_client.NET_MAX_ATTEMPTS,
            },
            {
                'ok': True,
            },
        ),
    ])

    bot_main._run_bot(None)

    self.assertEqual(self.attributes['dimensions']['id'][0],
                     os.environ['SWARMING_BOT_ID'])

    self.assertEqual(
        {
            'bot_side': ['A'],
            'foo': ['bar'],
            'id': ['localhost'],
            'pool': ['default'],
            'server_version': ['version1'],
        }, botobj[0].dimensions)

  def test_poll_server_unexpected_exception(self):
    # Enable it back, we want to test it now.
    self.mock(bot_main, '_TRAP_ALL_EXCEPTIONS', True)

    self.mock(bot_main, '_run_manifest', self.fail)
    self.mock(bot_main, '_update_bot', self.fail)
    self.mock(self.bot, 'host_reboot', self.fail)

    def mocked_restart(*_args):
      raise Exception('Totally random exception')

    self.mock(bot_main, '_bot_restart', mocked_restart)

    errs = []
    self.mock(self.bot, 'post_error', errs.append)

    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'bot_restart',
            'message': 'Restart now',
        }),
    ])
    self.poll_once()

    # Reported the error.
    self.assertEqual(1, len(errs))
    self.assertTrue(errs[0].startswith(
        'Exception in cmd_bot_restart: Totally random exception\n'))
    del errs[:]

    # Do it again. The error should be dedupped.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'bot_restart',
            'message': 'Restart now',
        }),
    ])
    self.poll_once()
    self.assertEqual(0, len(errs))

    # >10 min later, the error is reported again.
    self.quit_bit.reset()
    self.clock.sleep(601)
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'bot_restart',
            'message': 'Restart now',
        }),
    ])
    self.poll_once()
    self.assertEqual(1, len(errs))

  def test_poll_server_sleep(self):
    self.mock(bot_main, '_run_manifest', self.fail)
    self.mock(bot_main, '_update_bot', self.fail)

    from config import bot_config
    called = []
    self.mock(bot_config, 'on_bot_idle', lambda _bot, _s: called.append(1))

    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'sleep',
            'duration': 123,
        }),
    ])

    self.poll_once()
    self.assertEqual([123], self.quit_bit.slept)
    self.assertEqual([1], called)

  def test_poll_server_sleep_with_auth(self):
    self.mock(bot_main, '_run_manifest', self.fail)
    self.mock(bot_main, '_update_bot', self.fail)

    self.make_bot(lambda: ({'A': 'a'}, time.time() + 3600))

    # Expect the additional header.
    req = {
        'cmd': 'sleep',
        'duration': 123,
    }
    self.expected_requests([
        self.expected_poll_request(req, extra_headers={'A': 'a'}),
    ])
    self.poll_once()
    self.assertEqual([123], self.quit_bit.slept)

  def test_poll_server_run(self):
    manifest = []
    clean = []

    self.mock(bot_main, '_run_manifest', lambda *args: manifest.append(args))
    self.mock(bot_main, '_clean_cache', lambda *args: clean.append(args))
    self.mock(bot_main, '_update_bot', self.fail)

    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'run',
            'manifest': {
                'foo': 'bar'
            },
        }),
    ])
    self.poll_once()

    expected = [(self.bot, {'foo': 'bar'}, None)]
    self.assertEqual(expected, manifest)
    expected = [(self.bot,)]
    self.assertEqual(expected, clean)
    self.assertEqual(None, self.bot.bot_restart_msg())

  def test_poll_server_update(self):
    update = []

    self.mock(bot_main, '_run_manifest', self.fail)
    self.mock(bot_main, '_update_bot', lambda *args: update.append(args))

    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'update',
            'version': '123',
        }),
    ])
    self.poll_once()

    self.assertEqual([(self.bot, '123')], update)
    self.assertEqual(None, self.bot.bot_restart_msg())

  def test_poll_server_restart(self):
    restarts = []

    self.mock(bot_main, '_run_manifest', self.fail)
    self.mock(bot_main, '_update_bot', self.fail)
    self.mock(self.bot, 'host_reboot', self.fail)
    self.mock(bot_main, '_bot_restart', lambda obj, x: restarts.append(x))

    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'bot_restart',
            'message': 'Please restart now',
        }),
    ])
    self.poll_once()

    self.assertEqual(['Please restart now'], restarts)
    self.assertEqual(None, self.bot.bot_restart_msg())

  def test_poll_server_reboot(self):
    reboots = []

    self.mock(bot_main, '_run_manifest', self.fail)
    self.mock(bot_main, '_update_bot', self.fail)
    self.mock(self.bot, 'host_reboot', lambda *args: reboots.append(args))

    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'host_reboot',
            'message': 'Please die now',
        }),
    ])
    self.poll_once()

    self.assertEqual([('Please die now',)], reboots)
    self.assertEqual(None, self.bot.bot_restart_msg())

  def test_rbe_mode_idle(self):
    # Switches into the RBE mode, creates and polls the session. Gets nothing.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt0',
                'instance': 'instance_0',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

    # Wants to report the idle status to Swarming right away. Also polls RBE
    # as always.
    self.assertTrue(self.loop_state._swarming_poll_timer.firing)
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': False,
                    'sleep': 0.0,
                },
            },
            rbe_idle=True,
            sleep_streak=1),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

    # Does a bunch of RBE polls until it is time to poll Swarming again. The
    # exact number depends on sleep timings (which are all mocked in the test).
    polls = 0
    while not self.loop_state._swarming_poll_timer.firing:
      self.assertTrue(self.loop_state._rbe_poll_timer.firing)
      polls += 1
      self.expected_requests([
          self.expected_rbe_update_request('pt0', 'st0'),
      ])
      self.poll_once()
    self.assertEqual(polls, 9)

    # Reports the idle state again, but gets the command to terminate.
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'terminate',
                'task_id': 'terminate-id',
            },
            rbe_idle=True,
            sleep_streak=11),
        self.expected_rbe_update_request('pt0', 'st0', 'BOT_TERMINATING'),
        self.expected_task_update_request('terminate-id'),
    ])
    self.poll_once()

    # When the bot shuts down, rbe_disable doesn't do anything, since the
    # session is already closed.
    self.loop_state.rbe_disable()

  def test_rbe_mode_idle_dimensions_change(self):
    # Switches into the RBE mode, creates and polls the session. Gets nothing.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt0',
                'instance': 'instance_0',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

    # Wants to report the idle status to Swarming right away. Also polls RBE
    # as always.
    self.assertTrue(self.loop_state._swarming_poll_timer.firing)
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': False,
                    'sleep': 0.0,
                },
            },
            rbe_idle=True,
            sleep_streak=1),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

    # Swarming is scheduled to be called at some later time.
    self.assertFalse(self.loop_state._swarming_poll_timer.firing)

    # Dimensions suddenly change.
    self.attributes['dimensions']['extra'] = ['1']

    # Swarming should be called right away (followed by an RBE poll).
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': False,
                    'sleep': 0.0,
                },
            },
            rbe_idle=True,
            sleep_streak=2),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

    # Swarming is again scheduled to be called at some later time.
    self.assertFalse(self.loop_state._swarming_poll_timer.firing)

  def test_rbe_mode_swarming_task(self):
    self.mock(bot_main, '_run_manifest', lambda *_args: True)
    self.mock(bot_main, '_clean_cache', lambda *_args: None)
    self.mock(bot_main, '_update_lkgbc', lambda *_args: None)

    # Switches into the RBE mode, creates and polls the session. Gets nothing.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt0',
                'instance': 'instance_0',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

    # Reports the idle status to Swarming right away but suddenly gets a task.
    # This forces the bot to shutdown the session.
    self.assertTrue(self.loop_state._swarming_poll_timer.firing)
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'run',
                'manifest': {
                    'task_id': 'task-id',
                },
            },
            rbe_idle=True,
            sleep_streak=1),
        self.expected_rbe_update_request(None, 'st0', 'BOT_TERMINATING'),
    ])
    self.poll_once()

    # On the next poll the bot is still in the Swarming mode.
    self.assertTrue(self.loop_state._swarming_poll_timer.firing)
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'sleep',
            'duration': 5.0,
        }),
    ])
    self.poll_once()

    # On the next poll opens a new RBE session.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt1',
                'instance': 'instance_1',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt1', 'st1'),
        self.expected_rbe_update_request('pt1', 'st1'),
    ])
    self.poll_once()

  def test_rbe_mode_unhealthy_session(self):
    self.mock(self.loop_state, 'report_exception', lambda *_args: None)

    # Switches into the RBE mode. Tries to open a session and fails.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt0',
                'instance': 'instance_0',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt0', 'st0', fail=True),
    ])
    self.poll_once()

    # This is recognized as an error.
    self.assertEqual(self.loop_state._rbe_consecutive_errors, 1)

    # On the next poll tries to open the session again. It succeeds, but then
    # the poll reports the session is gone.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt1',
                'instance': 'instance_0',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt1', 'st1'),  # resets cons. errors
        self.expected_rbe_update_request('pt1',
                                         'st1',
                                         status_out='BOT_TERMINATING'),
    ])
    self.poll_once()

    # This is also recognized as an error.
    self.assertEqual(self.loop_state._rbe_consecutive_errors, 1)

    # Termination doesn't do anything, there's no session.
    self.loop_state.rbe_disable()

  def test_rbe_mode_switching_instance(self):
    # Switches into the RBE mode, creates and polls the session. Gets nothing.
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt0',
                'instance': 'instance_0',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

    # Wants to report it as idle, but suddenly told to use another instance.
    # Closes the old session and opens the new one.
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt1',
                    'instance': 'instance_1',
                    'hybrid_mode': False,
                    'sleep': 0.0,
                },
            },
            rbe_idle=True,
            sleep_streak=1),
        self.expected_rbe_update_request(None, 'st0', 'BOT_TERMINATING'),
        self.expected_rbe_create_request('pt1', 'st1'),
        self.expected_rbe_update_request('pt1', 'st1'),
    ])
    self.poll_once()

  def test_rbe_mode_handling_noop_leases(self):
    finished = []
    self.mock(self.loop_state, 'on_task_completed', finished.append)

    # Switches into the RBE mode, creates and polls the session. Gets a lease
    # right away.
    cur_lease_id = 0
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': 'pt0',
                'instance': 'instance_0',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0',
                                         'st0',
                                         lease_out={
                                             'id': 'lease-%d' % cur_lease_id,
                                             'payload': {
                                                 'noop': True
                                             },
                                             'state': 'PENDING',
                                         }),
    ])
    self.poll_once()

    # Did something.
    self.assertEqual(len(finished), 1)
    self.assertFalse(self.loop_state.idle)

    # Keeps spinning finishing leases back to back until it is time to call
    # Swarming to see what to do next.
    while not self.loop_state._swarming_poll_timer.firing:
      self.assertTrue(self.loop_state._rbe_poll_timer.firing)
      self.assertEqual(len(finished), cur_lease_id + 1)
      self.assertFalse(self.loop_state.idle)
      self.expected_requests([
          self.expected_rbe_update_request(
              'pt0',
              'st0',
              lease_in={
                  'id': 'lease-%d' % cur_lease_id,
                  'result': {},
                  'state': 'COMPLETED',
              },
              lease_out={
                  'id': 'lease-%d' % (cur_lease_id + 1),
                  'payload': {
                      'noop': True
                  },
                  'state': 'PENDING',
              },
          ),
      ])
      self.poll_once()
      cur_lease_id += 1

    # This number depends on mocked sleep timings.
    self.assertEqual(cur_lease_id, 9)

    # Tells Swarming the bot is busy doing RBE leases. Also reports the result
    # of the last lease and gets the next one.
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': False,
                    'sleep': 0.0,
                },
            },
            rbe_idle=False,
            sleep_streak=0),
        self.expected_rbe_update_request(
            'pt0',
            'st0',
            lease_in={
                'id': 'lease-%d' % cur_lease_id,
                'result': {},
                'state': 'COMPLETED',
            },
            lease_out={
                'id': 'lease-%d' % (cur_lease_id + 1),
                'payload': {
                    'noop': True
                },
                'state': 'PENDING',
            },
        ),
    ])
    self.poll_once()
    cur_lease_id += 1

    # Finally RBE tells there are no more leases.
    self.expected_requests([
        self.expected_rbe_update_request(
            'pt0',
            'st0',
            lease_in={
                'id': 'lease-%d' % cur_lease_id,
                'result': {},
                'state': 'COMPLETED',
            },
        ),
    ])
    self.poll_once()

    # The bot is idle now and want to report this to Swarming ASAP.
    self.assertTrue(self.loop_state.idle)
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': False,
                    'sleep': 0.0,
                },
            },
            rbe_idle=True,
            sleep_streak=1),
        self.expected_rbe_update_request('pt0', 'st0'),
    ])
    self.poll_once()

  def expected_rbe_poll_and_claim(self, poll_token, session_token, lease_id,
                                  claim_resp):
    return [
        self.expected_poll_request({
            'cmd': 'rbe',
            'rbe': {
                'poll_token': poll_token,
                'instance': 'instance',
                'hybrid_mode': False,
                'sleep': 0.0,
            },
        }),
        self.expected_rbe_create_request(poll_token, session_token),
        self.expected_rbe_update_request(poll_token,
                                         session_token,
                                         lease_out={
                                             'id': lease_id,
                                             'payload': {
                                                 'task_id': 'some-task-id',
                                                 'task_to_run_shard': 5,
                                                 'task_to_run_id': 6,
                                             },
                                             'state': 'PENDING',
                                         }),
        self.expected_claim_request(lease_id, 'some-task-id', 5, 6, claim_resp),
    ]

  def test_rbe_mode_claim_skip(self):
    finished = []
    self.mock(self.loop_state, 'on_task_completed', finished.append)

    # Switches into the RBE mode, creates and polls the session. Gets a lease
    # right away, proceeds to claiming it, discovers it should be skipped.
    self.expected_requests(
        self.expected_rbe_poll_and_claim('pt', 'st', 'lease-id', {
            'cmd': 'skip',
            'reason': 'Just skip',
        }))
    self.poll_once()

    # On the next cycle reports the lease was skipped.
    self.expected_requests([
        self.expected_rbe_update_request(
            'pt',
            'st',
            lease_in={
                'id': 'lease-id',
                'result': {
                    'skip_reason': 'Just skip'
                },
                'state': 'COMPLETED',
            },
        ),
    ])
    self.poll_once()

    # This doesn't count as a completed task.
    self.assertFalse(finished)

  def test_rbe_mode_claim_terminate(self):
    # Switches into the RBE mode, creates and polls the session. Gets a lease
    # right away, proceeds to claiming it, discovers it is termination, executes
    # it.
    self.expected_requests(
        self.expected_rbe_poll_and_claim('pt', 'st', 'lease-id', {
            'cmd': 'terminate',
            'task_id': 'terminate-id',
        }) + [self.expected_task_update_request('terminate-id')])
    self.poll_once()

    # Stopped now.
    self.assertTrue(self.quit_bit.is_set())

    # On shutdown reports the reservation as completed.
    self.expected_requests([
        self.expected_rbe_update_request(
            None,
            'st',
            status_in='BOT_TERMINATING',
            lease_in={
                'id': 'lease-id',
                'result': {},
                'state': 'COMPLETED',
            },
        ),
    ])
    self.loop_state.rbe_disable()

  def test_rbe_mode_claim_run(self):
    ran = []

    def run_manifest(_bot, manifest, rbe_session):
      rbe_session.finish_active_lease({})
      ran.append(manifest)
      return True

    self.mock(bot_main, '_run_manifest', run_manifest)

    finished = []
    self.mock(self.loop_state, 'on_task_completed', finished.append)

    # Switches into the RBE mode, creates and polls the session. Gets a lease
    # right away, proceeds to claiming it, discovers it is a real task, executes
    # it.
    self.expected_requests(
        self.expected_rbe_poll_and_claim('pt', 'st', 'lease-id', {
            'cmd': 'run',
            'manifest': {
                'fake': 'manifest'
            },
        }))
    self.poll_once()

    # Ran the task.
    self.assertEqual(ran, [{'fake': 'manifest'}])
    self.assertEqual(finished, [True])

    # Reports the lease is finished on completion.
    self.expected_requests([
        self.expected_rbe_update_request(
            'pt',
            'st',
            lease_in={
                'id': 'lease-id',
                'result': {},
                'state': 'COMPLETED',
            },
        ),
    ])
    self.poll_once()

  def test_hybrid_mode_idle(self):
    # Starting in hybrid mode, polling Swarming next.
    self.prep_hybrid_mode({
        'poll_token': 'pt0',
        'instance': 'instance_0',
        'hybrid_mode': True,
        'sleep': 1.0,
    })

    # Makes a forced Swarming poll, gets nothing. Opens an RBE session and makes
    # maintenance poll.
    self.assertEqual(self.loop_state._next_scheduler, 'swarming')
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': True,
                    'sleep': 5.0,
                },
            },
            force=True),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0',
                                         'st0',
                                         status_in='UNHEALTHY',
                                         blocking=False),
    ])
    self.poll_once()
    self.assertEqual(self.loop_state._consecutive_idle_cycles, 1)

    # The next poll is from RBE scheduler. Makes a non-forced Swarming poll,
    # gets nothing. Makes a full RBE poll.
    self.assertEqual(self.loop_state._next_scheduler, 'rbe')
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': True,
                    'sleep': 10.0,
                },
            },
            rbe_idle=True,
            sleep_streak=1,
            force=False),
        self.expected_rbe_update_request('pt0', 'st0', blocking=False),
    ])
    self.poll_once()
    self.assertEqual(self.loop_state._consecutive_idle_cycles, 2)

    # Swarming's turn again.
    self.assertEqual(self.loop_state._next_scheduler, 'swarming')
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': True,
                    'sleep': 5.0,
                },
            },
            rbe_idle=True,
            sleep_streak=2,
            force=True),
        self.expected_rbe_update_request('pt0',
                                         'st0',
                                         status_in='UNHEALTHY',
                                         blocking=False),
    ])
    self.poll_once()
    self.assertEqual(self.loop_state._consecutive_idle_cycles, 3)

  def test_hybrid_mode_swarming_scheduler_task(self):
    self.mock(bot_main, '_run_manifest', lambda *args: True)

    finished = []
    self.mock(self.loop_state, 'on_task_completed', finished.append)

    # Starting in hybrid mode, polling Swarming next.
    self.prep_hybrid_mode({
        'poll_token': 'pt0',
        'instance': 'instance_0',
        'hybrid_mode': True,
        'sleep': 1.0,
    })

    # Makes a forced Swarming poll, gets a task. Nevertheless opens an RBE
    # session and makes a maintenance poll.
    self.assertEqual(self.loop_state._next_scheduler, 'swarming')
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'run',
                'manifest': {
                    'task_id': 'some-task-id',
                },
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': True,
                    'sleep': 5.0,
                },
            },
            force=True),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0',
                                         'st0',
                                         status_in='UNHEALTHY',
                                         blocking=False),
    ])
    self.poll_once()
    self.assertEqual(self.loop_state._consecutive_idle_cycles, 0)

    # Ran the task.
    self.assertEqual(len(finished), 1)

    # The next poll is from RBE scheduler. Makes a non-forced Swarming poll,
    # gets nothing. Makes a full RBE poll.
    self.assertEqual(self.loop_state._next_scheduler, 'rbe')
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': True,
                    'sleep': 10.0,
                },
            },
            rbe_idle=False,
            sleep_streak=0,
            force=False),
        self.expected_rbe_update_request('pt0', 'st0', blocking=False),
    ])
    self.poll_once()
    self.assertEqual(self.loop_state._consecutive_idle_cycles, 1)

  def test_hybrid_mode_rbe_scheduler_task(self):
    def run_manifest(_bot, _manifest, rbe_session):
      rbe_session.finish_active_lease({})
      return True

    self.mock(bot_main, '_run_manifest', run_manifest)

    finished = []
    self.mock(self.loop_state, 'on_task_completed', finished.append)

    # Starting in hybrid mode, polling RBE next.
    self.prep_hybrid_mode(
        {
            'poll_token': 'pt0',
            'instance': 'instance_0',
            'hybrid_mode': True,
            'sleep': 1.0,
        }, 'rbe')

    # Makes a maintenance Swarming poll, gets nothing. Opens an RBE session and
    # makes a full poll getting a lease.
    self.assertEqual(self.loop_state._next_scheduler, 'rbe')
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': True,
                    'sleep': 5.0,
                },
            },
            force=False),
        self.expected_rbe_create_request('pt0', 'st0'),
        self.expected_rbe_update_request('pt0',
                                         'st0',
                                         lease_out={
                                             'id': 'lease-id',
                                             'payload': {
                                                 'task_id': 'some-task-id',
                                                 'task_to_run_shard': 5,
                                                 'task_to_run_id': 6,
                                             },
                                             'state': 'PENDING',
                                         },
                                         blocking=False),
        self.expected_claim_request('lease-id', 'some-task-id', 5, 6, {
            'cmd': 'run',
            'manifest': {
                'fake': 'manifest'
            },
        }),
    ])
    self.poll_once()
    self.assertEqual(self.loop_state._consecutive_idle_cycles, 0)

    # Ran the task.
    self.assertEqual(len(finished), 1)

    # The next poll is from Swarming scheduler. Still making a maintenance poll
    # of RBE, reporting the result of the previously executed lease.
    self.assertEqual(self.loop_state._next_scheduler, 'swarming')
    self.expected_requests([
        self.expected_poll_request(
            {
                'cmd': 'rbe',
                'rbe': {
                    'poll_token': 'pt0',
                    'instance': 'instance_0',
                    'hybrid_mode': True,
                    'sleep': 10.0,
                },
            },
            rbe_idle=False,
            sleep_streak=0,
            force=True),
        self.expected_rbe_update_request('pt0',
                                         'st0',
                                         status_in='UNHEALTHY',
                                         lease_in={
                                             'id': 'lease-id',
                                             'result': {},
                                             'state': 'COMPLETED',
                                         },
                                         blocking=False),
    ])
    self.poll_once()
    self.assertEqual(self.loop_state._consecutive_idle_cycles, 1)

  def test_hybrid_mode_update(self):
    update = []
    self.mock(bot_main, '_update_bot', lambda *args: update.append(args))

    # Starting in hybrid mode, polling RBE next.
    self.prep_hybrid_mode(
        {
            'poll_token': 'pt0',
            'instance': 'instance_0',
            'hybrid_mode': True,
            'sleep': 1.0,
        }, 'rbe')

    # Immediately gets `update` command. Does NOT open an RBE session.
    self.assertEqual(self.loop_state._next_scheduler, 'rbe')
    self.expected_requests([
        self.expected_poll_request({
            'cmd': 'update',
            'version': '123',
        },
                                   force=False),
    ])
    self.poll_once()

    # Updated.
    self.assertEqual(len(update), 1)

  def _mock_popen(self,
                  returncode=0,
                  exit_code=0,
                  url='https://localhost:1',
                  expected_auth_params_json=None,
                  expected_rbe_session_json=None,
                  internal_error=None,
                  internal_error_reported=False):
    result = {
        'exit_code': exit_code,
        'internal_error': internal_error,
        'internal_error_reported': internal_error_reported,
        'version': 3,
    }
    # Method should have "self" as first argument - pylint: disable=E0213
    class Popen(object):

      def __init__(self2, cmd, detached, cwd, env, stdout, stderr, stdin,
                   **kwargs):
        self2.returncode = None
        self2._out_file = os.path.join(self.root_dir, 'w',
                                       'task_runner_out.json')
        cmd = cmd[:]
        expected = [
            sys.executable,
            bot_main.THIS_FILE,
            'task_runner',
            '--swarming-server',
            url,
            '--default-swarming-server',
            'https://localhost:1',
            '--in-file',
            os.path.join(self.root_dir, 'w', 'task_runner_in.json'),
            '--out-file',
            self2._out_file,
            '--cost-usd-hour',
            '3600.0',
            '--start',
            '100.0',
        ]

        self.assertEqual(cmd[:len(expected)], expected)
        del cmd[:len(expected)]

        # After than there may be --bot-file and --auth-params-file. Then --
        # will be used to mark the separation of flags meant to be sent to
        # run_isolated.
        while cmd and cmd[0] != '--':
          flag = cmd.pop(0)
          self.assertIn(
              flag, ('--bot-file', '--auth-params-file', '--rbe-session-state'))
          with open(cmd[0], 'rb') as f:
            body = f.read()
          cmd.pop(0)
          if flag == '--bot-file':
            self.assertEqual(b'', body)
          if flag == '--auth-params-file' and expected_auth_params_json:
            self.assertEqual(expected_auth_params_json, json.loads(body))
          if flag == '--rbe-session-state' and expected_rbe_session_json:
            self.assertEqual(expected_rbe_session_json, json.loads(body))

        self.assertEqual(True, detached)
        self.assertEqual(self.bot.base_dir, cwd)
        self.assertEqual('24', env['SWARMING_TASK_ID'])
        self.assertTrue(stdout)
        self.assertEqual(subprocess42.STDOUT, stderr)
        self.assertEqual(subprocess42.PIPE, stdin)
        if sys.platform == 'win32':
          creationflags = kwargs['creationflags']
          self.assertEqual(subprocess42.CREATE_NEW_CONSOLE, creationflags)
        else:
          close_fds = kwargs['close_fds']
          self.assertTrue(close_fds)

      def wait(self2, timeout=None): # pylint: disable=unused-argument
        self2.returncode = returncode
        with open(self2._out_file, 'w') as f:
          json.dump(result, f)
        return 0

    self.mock(subprocess42, 'Popen', Popen)
    return result

  def test_run_manifest(self):
    self.mock(bot_main, '_post_error_task', self.print_err_and_fail)

    def call_hook(_chained, botobj, name, *args):
      if name == 'on_after_task':
        failure, internal_failure, dimensions, summary = args
        self.assertEqual(self.attributes['dimensions'], botobj.dimensions)
        self.assertEqual(False, failure)
        self.assertEqual(False, internal_failure)
        self.assertEqual({'os': 'Amiga', 'pool': 'default'}, dimensions)
        self.assertEqual(result, summary)
    self.mock(bot_main, '_call_hook', call_hook)
    result = self._mock_popen(url='https://localhost:3')

    manifest = {
        'command': ['echo', 'hi'],
        'dimensions': {
            'os': 'Amiga',
            'pool': 'default'
        },
        'grace_period': 30,
        'hard_timeout': 60,
        'io_timeout': None,
        'host': 'https://localhost:3',
        'task_id': '24',
    }
    self.assertEqual(self.root_dir, self.bot.base_dir)
    bot_main._run_manifest(self.bot, manifest, None)

  def test_run_manifest_with_auth_headers(self):
    self.make_bot(auth_headers_cb=lambda: ({'A': 'a'}, time.time() + 3600))

    self.mock(bot_main, '_post_error_task', self.print_err_and_fail)

    def call_hook(_chained, botobj, name, *args):
      if name == 'on_after_task':
        failure, internal_failure, dimensions, summary = args
        self.assertEqual(self.attributes['dimensions'], botobj.dimensions)
        self.assertEqual(False, failure)
        self.assertEqual(False, internal_failure)
        self.assertEqual({'os': 'Amiga', 'pool': 'default'}, dimensions)
        self.assertEqual(result, summary)
    self.mock(bot_main, '_call_hook', call_hook)
    result = self._mock_popen(
        url='https://localhost:3',
        expected_auth_params_json={
            'bot_id': 'localhost',
            'task_id': '24',
            'swarming_http_headers': {
                'A': 'a'
            },
            'swarming_http_headers_exp': int(time.time() + 3600),
            'bot_service_account': 'none',
            'system_service_account':
                'robot@example.com',  # as in task manifest
            'task_service_account': 'bot',
        })

    manifest = {
        'command': ['echo', 'hi'],
        'dimensions': {
            'os': 'Amiga',
            'pool': 'default'
        },
        'grace_period': 30,
        'hard_timeout': 60,
        'io_timeout': None,
        'host': 'https://localhost:3',
        'service_accounts': {
            'system': {
                'service_account': 'robot@example.com'
            },
            'task': {
                'service_account': 'bot'
            },
        },
        'task_id': '24',
    }
    self.assertEqual(self.root_dir, self.bot.base_dir)
    bot_main._run_manifest(self.bot, manifest, None)

  def test_run_manifest_with_rbe(self):
    self.mock(bot_main, '_post_error_task', self.print_err_and_fail)

    rbe_session = remote_client.RBESession(self.bot.remote, 'rbe-instance',
                                           self.bot.dimensions, 'poll-token',
                                           'session-token', 'session-id')
    rbe_session._active_lease = remote_client.RBELease(
        'id', remote_client.RBELeaseState.ACTIVE)
    rbe_results = []
    self.mock(rbe_session, 'finish_active_lease', rbe_results.append)

    self._mock_popen(
        url='https://localhost:3',
        expected_rbe_session_json=rbe_session.to_dict(),
    )

    manifest = {
        'command': ['echo', 'hi'],
        'dimensions': {
            'os': 'Amiga',
            'pool': 'default'
        },
        'grace_period': 30,
        'hard_timeout': 60,
        'io_timeout': None,
        'host': 'https://localhost:3',
        'task_id': '24',
    }
    self.assertEqual(self.root_dir, self.bot.base_dir)
    bot_main._run_manifest(self.bot, manifest, rbe_session)

    self.assertTrue(rbe_results)

  def test_run_manifest_task_failure(self):
    self.mock(bot_main, '_post_error_task', self.print_err_and_fail)

    def call_hook(_chained, _botobj, name, *args):
      if name == 'on_after_task':
        failure, internal_failure, dimensions, summary = args
        self.assertEqual(True, failure)
        self.assertEqual(False, internal_failure)
        self.assertEqual({'pool': 'default'}, dimensions)
        self.assertEqual(result, summary)

    self.mock(bot_main, '_call_hook', call_hook)
    result = self._mock_popen(exit_code=1)

    manifest = {
        'command': ['echo', 'hi'],
        'dimensions': {
            'pool': 'default'
        },
        'grace_period': 30,
        'hard_timeout': 60,
        'io_timeout': 60,
        'task_id': '24',
    }
    bot_main._run_manifest(self.bot, manifest, None)

  def test_run_manifest_internal_failure(self):
    posted = []
    self.mock(bot_main, '_post_error_task', lambda *args: posted.append(args))

    def call_hook(_chained, _botobj, name, *args):
      if name == 'on_after_task':
        failure, internal_failure, dimensions, summary = args
        self.assertEqual(False, failure)
        self.assertEqual(True, internal_failure)
        self.assertEqual({'pool': 'default'}, dimensions)
        self.assertEqual(result, summary)

    self.mock(bot_main, '_call_hook', call_hook)
    result = self._mock_popen(returncode=1)

    manifest = {
        'command': ['echo', 'hi'],
        'dimensions': {
            'pool': 'default'
        },
        'grace_period': 30,
        'hard_timeout': 60,
        'io_timeout': 60,
        'task_id': '24',
    }
    bot_main._run_manifest(self.bot, manifest, None)
    expected = [(self.bot, 'Execution failed: internal error (1).', '24')]
    self.assertEqual(expected, posted)

  def test_run_manifest_internal_error_reported(self):
    posted = []
    self.mock(bot_main, '_post_error_task', lambda *args: posted.append(args))

    def call_hook(_chained, _botobj, name, *args):
      if name == 'on_after_task':
        failure, internal_failure, dimensions, summary = args
        self.assertEqual(False, failure)
        self.assertEqual(True, internal_failure)
        self.assertEqual({'pool': 'default'}, dimensions)
        self.assertEqual(result, summary)

    self.mock(bot_main, '_call_hook', call_hook)
    result = self._mock_popen(returncode=0,
                              internal_error='there is an error',
                              internal_error_reported=True)

    manifest = {
        'command': ['echo', 'hi'],
        'dimensions': {
            'pool': 'default'
        },
        'grace_period': 30,
        'hard_timeout': 60,
        'io_timeout': 60,
        'task_id': '24',
    }
    bot_main._run_manifest(self.bot, manifest, None)

  def test_run_manifest_exception(self):
    posted = []

    def post_error_task(botobj, msg, task_id):
      posted.append((botobj, msg.splitlines()[0], task_id))

    self.mock(bot_main, '_post_error_task', post_error_task)

    def call_hook(_chained, _botobj, name, *args):
      if name == 'on_after_task':
        failure, internal_failure, dimensions, summary = args
        self.assertEqual(False, failure)
        self.assertEqual(True, internal_failure)
        self.assertEqual({'pool': 'default'}, dimensions)
        self.assertEqual({}, summary)

    self.mock(bot_main, '_call_hook', call_hook)

    def raiseOSError(*_a, **_k):
      raise OSError('Dang')

    self.mock(subprocess42, 'Popen', raiseOSError)

    manifest = {
        'command': ['echo', 'hi'],
        'dimensions': {
            'pool': 'default'
        },
        'grace_period': 30,
        'hard_timeout': 60,
        'io_timeout': None,
        'task_id': '24',
    }
    bot_main._run_manifest(self.bot, manifest, None)
    expected = [(self.bot, 'Internal exception occurred: Dang', '24')]
    self.assertEqual(expected, posted)

  def test_update_bot(self):
    restarts = []
    def bot_restart(_botobj, message, filepath):
      self.assertEqual('Updating to 123', message)
      self.assertEqual(new_zip, filepath)
      restarts.append(1)
    self.mock(bot_main, '_bot_restart', bot_restart)
    # Mock the file to download in the temporary directory.
    self.mock(bot_main, 'THIS_FILE',
              os.path.join(self.root_dir, 'swarming_bot.1.zip'))
    new_zip = os.path.join(self.root_dir, 'swarming_bot.2.zip')
    # This is necessary otherwise zipfile will crash.
    self.mock(time, 'time', lambda: 1400000000)

    def url_retrieve(f, url, headers=None, timeout=None):
      self.assertEqual(
          'https://localhost:1/swarming/api/v1/bot/bot_code'
          '/123', url)
      self.assertEqual(new_zip, f)
      self.assertEqual({
          'Cookie': 'GOOGAPPUID=42',
          'X-Luci-Swarming-Bot-ID': 'localhost',
      }, headers)
      self.assertEqual(remote_client.NET_CONNECTION_TIMEOUT_SEC, timeout)
      # Create a valid zip that runs properly.
      with zipfile.ZipFile(f, 'w') as z:
        z.writestr('__main__.py', 'print("hi")')
      return True
    self.mock(net, 'url_retrieve', url_retrieve)
    self.bot.remote.bot_id = self.bot.id
    bot_main._update_bot(self.bot, '123')
    self.assertEqual([1], restarts)

  def test_main(self):

    def check(x):
      self.assertEqual(logging.WARNING, x)
    self.mock(logging_utils, 'set_console_level', check)

    def run_bot(error):
      self.assertEqual(None, error)
      return 0

    self.mock(bot_main, '_run_bot', run_bot)

    class Singleton(object):
      # pylint: disable=no-self-argument
      def acquire(self2):
        return True
      def release(self2):
        self.fail()
    self.mock(bot_main, 'SINGLETON', Singleton())

    self.assertEqual(0, bot_main.main([]))

  def test_update_lkgbc(self):
    # Create LKGBC with a timestamp from 1h ago.
    lkgbc = os.path.join(self.bot.base_dir, 'swarming_bot.zip')
    with open(lkgbc, 'wb') as f:
      f.write(b'a')
    past = time.time() - 60 * 60
    os.utime(lkgbc, (past, past))

    cur = os.path.join(self.bot.base_dir, 'swarming_bot.1.zip')
    with open(cur, 'wb') as f:
      f.write(b'ab')
    self.mock(bot_main, 'THIS_FILE', cur)

    self.assertEqual(True, bot_main._update_lkgbc(self.bot))
    with open(lkgbc, 'rb') as f:
      self.assertEqual(b'ab', f.read())

  def test_maybe_update_lkgbc(self):
    # Create LKGBC with a timestamp from 1h ago.
    lkgbc = os.path.join(self.bot.base_dir, 'swarming_bot.zip')
    with open(lkgbc, 'wb') as f:
      f.write(b'a')
    past = time.time() - 60 * 60
    os.utime(lkgbc, (past, past))

    cur = os.path.join(self.bot.base_dir, 'swarming_bot.1.zip')
    with open(cur, 'wb') as f:
      f.write(b'ab')
    self.mock(bot_main, 'THIS_FILE', cur)

    # No update even if they mismatch, LKGBC is not old enough.
    self.assertEqual(False, bot_main._maybe_update_lkgbc(self.bot))
    with open(lkgbc, 'rb') as f:
      self.assertEqual(b'a', f.read())

    # Fast forward a little more than 7 days.
    now = time.time()
    self.mock(time, 'time', lambda: now + 7 * 24 * 60 * 60 + 10)
    self.assertEqual(True, bot_main._maybe_update_lkgbc(self.bot))
    with open(lkgbc, 'rb') as f:
      self.assertEqual(b'ab', f.read())


class TestBotNotMocked(TestBotBase):

  def test_bot_restart(self):
    calls = []

    def exec_python(args):
      calls.append(args)
      return 23
    self.mock(bot_main.common, 'exec_python', exec_python)

    # pylint: disable=unused-argument
    class Popen(object):
      def __init__(self2, cmd, cwd, stdin, stdout, stderr, detached, **kwargs):
        self2.returncode = None
        expected = [sys.executable, bot_main.THIS_FILE, 'is_fine']
        self.assertEqual(expected, cmd)
        self.assertEqual(self.root_dir, cwd)
        self.assertEqual(subprocess42.PIPE, stdin)
        self.assertEqual(subprocess42.PIPE, stdout)
        self.assertEqual(subprocess42.STDOUT, stderr)
        self.assertEqual(True, detached)
        if sys.platform == 'win32':
          creationflags = kwargs['creationflags']
          self.assertEqual(subprocess42.CREATE_NEW_CONSOLE, creationflags)
        else:
          close_fds = kwargs['close_fds']
          self.assertTrue(close_fds)

      def communicate(self2):
        self2.returncode = 0
        return '', None
    self.mock(subprocess42, 'Popen', Popen)

    self.mock(time, 'sleep', lambda _: None)
    self.mock(self.bot, 'post_event', lambda *_args: None)

    with self.assertRaises(SystemExit) as e:
      bot_main._bot_restart(self.bot, 'Yo', bot_main.THIS_FILE)
    self.assertEqual(23, e.exception.code)

    self.assertEqual([[bot_main.THIS_FILE, 'start_slave', '--survive']], calls)


if __name__ == '__main__':
  fix_encoding.fix_encoding()
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
