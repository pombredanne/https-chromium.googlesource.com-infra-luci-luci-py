#!/usr/bin/env vpython
# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import logging
import os
import random
import sys
import unittest

from parameterized import parameterized
import mock

# Setups environment.
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, APP_DIR)
import test_env_handlers

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb

import webtest

import handlers_backend

from components import auth
from components import auth_testing
from components import datastore_utils
from components import pubsub
from components import utils
from components.auth.proto import delegation_pb2

from server import bot_management
from server import config
from server import external_scheduler
from server import pools_config
from server import resultdb
from server import task_pack
from server import task_queues
from server import task_request
from server import task_result
from server import task_scheduler
from server import task_to_run
from server.task_result import State

from proto.api import plugin_pb2

# pylint: disable=W0212,W0612


def _gen_properties(**kwargs):
  """Creates a TaskProperties."""
  args = {
      'command': [u'command1'],
      'dimensions': {
          u'os': [u'Windows-3.1.1'],
          u'pool': [u'default']
      },
      'env': {},
      'execution_timeout_secs': 24 * 60 * 60,
      'io_timeout_secs': None,
  }
  args.update(kwargs)
  args['dimensions_data'] = args.pop('dimensions')
  return task_request.TaskProperties(**args)


def _gen_request_slices(**kwargs):
  """Returns an initialized task_request.TaskRequest."""
  now = utils.utcnow()
  args = {
      # Don't be confused, this is not part of the API. This code is
      # constructing a DB entity, not a swarming_rpcs.NewTaskRequest.
      u'created_ts': now,
      u'manual_tags': [u'tag:1'],
      u'name': u'yay',
      u'priority': 50,
      u'task_slices': [
          task_request.TaskSlice(
              expiration_secs=60,
              properties=_gen_properties(),
              wait_for_capacity=False),
      ],
      u'user': u'Jesus',
      u'bot_ping_tolerance_secs': 120,
  }
  args.update(kwargs)
  ret = task_request.TaskRequest(**args)
  task_request.init_new_request(ret, True, task_request.TEMPLATE_AUTO)
  return ret


def _get_results(request_key):
  """Fetches all task results for a specified TaskRequest ndb.Key.

  Returns:
    tuple(TaskResultSummary, list of TaskRunResult that exist).
  """
  result_summary_key = task_pack.request_key_to_result_summary_key(request_key)
  result_summary = result_summary_key.get()
  # There's two way to look at it, either use a DB query or fetch all the
  # entities that could exist, at most 255. In general, there will be <3
  # entities so just fetching them by key would be faster. This function is
  # exclusively used in unit tests so it's not performance critical.
  q = task_result.TaskRunResult.query(ancestor=result_summary_key)
  q = q.order(task_result.TaskRunResult.key)
  return result_summary, q.fetch()


def _run_result_to_to_run_key(run_result):
  """Returns a TaskToRun ndb.Key that was used to trigger the TaskRunResult."""
  return task_to_run.request_to_task_to_run_key(run_result.request_key.get(),
                                                run_result.try_number,
                                                run_result.current_task_slice)


def _bot_update_task(run_result_key, **kwargs):
  args = {
      'bot_id': 'localhost',
      'cas_output_root': None,
      'cipd_pins': None,
      'output': 'hi',
      'output_chunk_start': 0,
      'exit_code': None,
      'duration': None,
      'hard_timeout': False,
      'io_timeout': False,
      'cost_usd': 0.1,
      'outputs_ref': None,
      'performance_stats': None,
      'canceled': None,
  }
  args.update(kwargs)
  return task_scheduler.bot_update_task(run_result_key, **args)


class TaskSchedulerApiTest(test_env_handlers.AppTestBase):

  def setUp(self):
    super(TaskSchedulerApiTest, self).setUp()
    self.now = datetime.datetime(2014, 1, 2, 3, 4, 5, 6)
    self.mock_now(self.now)
    auth_testing.mock_get_current_identity(self)
    # Setup the backend to handle task queues.
    self.app = webtest.TestApp(
        handlers_backend.create_application(True),
        extra_environ={
            'REMOTE_ADDR': self.source_ip,
            'SERVER_SOFTWARE': os.environ['SERVER_SOFTWARE'],
        })
    self._enqueue_orig = self.mock(utils, 'enqueue_task', self._enqueue)
    self._enqueue_async_orig = self.mock(utils, 'enqueue_task_async',
                                         self._enqueue_async)
    # See mock_pub_sub()
    self._pub_sub_mocked = False
    self.publish_successful = True
    self._random = 0x88
    self.mock(random, 'getrandbits', self._getrandbits)
    self.bot_dimensions = {
        u'foo': [u'bar'],
        u'id': [u'localhost'],
        u'os': [u'Windows', u'Windows-3.1.1'],
        u'pool': [u'default'],
    }
    self._known_pools = None

  def _enqueue(self, *args, **kwargs):
    # Only then add use_dedicated_module as default False.
    kwargs = kwargs.copy()
    kwargs.setdefault('use_dedicated_module', False)
    return self._enqueue_orig(*args, **kwargs)

  def _enqueue_async(self, *args, **kwargs):
    # Only then add use_dedicated_module as default False.
    kwargs = kwargs.copy()
    kwargs.setdefault('use_dedicated_module', False)
    return self._enqueue_async_orig(*args, **kwargs)

  def _getrandbits(self, bits):
    self.assertEqual(16, bits)
    self._random += 1
    return self._random

  def mock_pub_sub(self):
    self.assertFalse(self._pub_sub_mocked)
    self._pub_sub_mocked = True
    calls = []

    def pubsub_publish(**kwargs):
      if not self.publish_successful:
        raise pubsub.TransientError('Fail')
      calls.append(('directly', kwargs))

    self.mock(pubsub, 'publish', pubsub_publish)
    return calls

  def _gen_result_summary_pending(self, **kwargs):
    """Returns the dict for a TaskResultSummary for a pending task."""
    expected = {
        'abandoned_ts': None,
        'bot_dimensions': None,
        'bot_id': None,
        'bot_version': None,
        'cipd_pins': None,
        'children_task_ids': [],
        'completed_ts': None,
        'costs_usd': [],
        'cost_saved_usd': None,
        'created_ts': self.now,
        'current_task_slice': 0,
        'deduped_from': None,
        'duration': None,
        'exit_code': None,
        'expiration_delay': None,
        'failure': False,
        'internal_failure': False,
        'modified_ts': self.now,
        'name': u'yay',
        'outputs_ref': None,
        'priority': 50,
        'cas_output_root': None,
        'resultdb_info': None,
        'server_versions': [u'v1a'],
        'started_ts': None,
        'state': State.PENDING,
        'tags': [
            u'os:Windows-3.1.1',
            u'pool:default',
            u'priority:50',
            u'realm:none',
            u'service_account:none',
            u'swarming.pool.template:no_config',
            u'tag:1',
            u'user:Jesus',
        ],
        'try_number': None,
        'user': u'Jesus',
    }
    expected.update(kwargs)
    return expected

  def _gen_result_summary_reaped(self, **kwargs):
    """Returns the dict for a TaskResultSummary for a pending task."""
    kwargs.setdefault(u'bot_dimensions', self.bot_dimensions.copy())
    kwargs.setdefault(u'bot_id', u'localhost')
    kwargs.setdefault(u'bot_version', u'abc')
    kwargs.setdefault(u'state', State.RUNNING)
    kwargs.setdefault(u'try_number', 1)
    return self._gen_result_summary_pending(**kwargs)

  def _gen_run_result(self, **kwargs):
    expected = {
        'abandoned_ts': None,
        'bot_dimensions': self.bot_dimensions,
        'bot_id': u'localhost',
        'bot_version': u'abc',
        'cipd_pins': None,
        'children_task_ids': [],
        'completed_ts': None,
        'cost_usd': 0.,
        'current_task_slice': 0,
        'dead_after_ts': None,
        'duration': None,
        'exit_code': None,
        'failure': False,
        'internal_failure': False,
        'killing': None,
        'modified_ts': self.now,
        'outputs_ref': None,
        'cas_output_root': None,
        'resultdb_info': None,
        'server_versions': [u'v1a'],
        'started_ts': self.now,
        'state': State.RUNNING,
        'try_number': 1,
    }
    expected.update(**kwargs)
    return expected

  def _quick_schedule(self, num_task, **kwargs):
    """Schedules a task.

    Arguments:
      num_task: number of AppEngine task queues enqueued (and run
                synchronously). It is either 0 or 1, if the task queue
                rebuild-task-cache was enqueued and run. Do not confuse with
                Swarming task queues, completely unrelated.
      kwargs: passed to _gen_request_slices().
    """
    self.assertEqual(0, self.execute_tasks())
    request = _gen_request_slices(**kwargs)
    result_summary = task_scheduler.schedule_request(request, None, False)
    # State will be either PENDING or COMPLETED (for deduped task)
    self.assertEqual(num_task, self.execute_tasks())
    self.assertEqual(0, self.execute_tasks())
    return result_summary

  def _register_bot(self, num_btd_updated, bot_dimensions):
    """Registers the bot so the task queues knows there's a worker than can run
    the task.

    Arguments:
      num_btd_updated: number of 'BotTaskDimensions' entities (from
                       task_queues.py) updated, normally 0, 1 or None if it was
                       cached.
      bot_dimensions: bot dimensions to assert.
    """
    self.assertEqual(0, self.execute_tasks())
    bot_id = bot_dimensions[u'id'][0]
    bot_management.bot_event(
        'request_sleep',
        bot_id,
        '1.2.3.4',
        'joe@localhost',
        bot_dimensions, {'state': 'real'},
        '1234',
        False,
        None,
        None,
        None,
        register_dimensions=True)
    bot_root_key = bot_management.get_root_key(bot_id)
    self.assertEqual(
        num_btd_updated,
        task_queues.assert_bot_async(bot_root_key, bot_dimensions).get_result())
    self.assertEqual(0, self.execute_tasks())

  def _quick_reap(self, num_task, num_btd_updated, **kwargs):
    """Makes sure the bot is registered and have it reap a task."""
    self._register_bot(num_btd_updated, self.bot_dimensions)
    self._quick_schedule(num_task, **kwargs)

    reaped_request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')

    # Reaping causes an additional task if pubsub is specified.
    self.assertEqual(int('pubsub_topic' in kwargs), self.execute_tasks())
    return run_result

  def _cancel_running_task(self, run_result):
    """Cancels running task"""
    canceled, was_running = task_scheduler.cancel_task(run_result.request,
                                                       run_result.key, True,
                                                       run_result.bot_id)
    self.assertTrue(canceled)
    self.assertTrue(was_running)
    self.execute_tasks()
    run_result = run_result.key.get()
    self.assertTrue(run_result.killing)

  def test_all_apis_are_tested(self):
    # Ensures there's a test for each public API.
    # TODO(maruel): Remove this once coverage is asserted.
    module = task_scheduler
    expected = set(
        i for i in dir(module)
        if i[0] != '_' and hasattr(getattr(module, i), 'func_name'))
    missing = expected - set(i[5:] for i in dir(self) if i.startswith('test_'))
    self.assertFalse(missing)

  def test_bot_reap_task(self):
    # Essentially check _quick_reap() works.
    run_result = self._quick_reap(1, 0)
    self.assertEqual('localhost', run_result.bot_id)
    self.assertEqual(1, run_result.try_number)
    to_run_key = task_to_run.request_to_task_to_run_key(
        run_result.request_key.get(), 1, 0)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertIsNone(to_run_key.get().expiration_ts)

  @parameterized.expand([
      ({
          u'pool': [u'default'],
          u'os': [u'Windows-3.1.1|Windows-3.2.1'],
      },),
      ({
          u'pool': [u'default'],
          u'os': [u'Windows-3.1.1|Windows-3.2.1'],
          u'foo': [u'bar|A|B|C'],
      },),
  ])
  def test_bot_reap_task_or_dimensions(self, or_dimensions):
    run_result = self._quick_reap(
        1,
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(dimensions=or_dimensions),
                wait_for_capacity=False,
            )
        ])

    self.assertEqual('localhost', run_result.bot_id)
    self.assertEqual(1, run_result.try_number)
    to_run_key = task_to_run.request_to_task_to_run_key(
        run_result.request_key.get(), 1, 0)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertIsNone(to_run_key.get().expiration_ts)

  def test_bot_reap_tasks_using_or_dimensions(self):
    # The fist part of this case checks for bot -> task
    # Register a bot first
    bot1_dimensions = self.bot_dimensions.copy()
    bot1_dimensions[u'id'] = [u'bot1']
    bot1_dimensions[u'os'] = [u'v1', u'v2']
    bot1_dimensions[u'gpu'] = [u'nv', u'sega']
    self._register_bot(0, bot1_dimensions)
    # Then send a request
    task_slices = [
        task_request.TaskSlice(
            expiration_secs=60,
            properties=_gen_properties(
                dimensions={
                    u'pool': [u'default'],
                    u'os': [u'v1|v2'],
                    u'gpu': [u'sega', u'amd|nv'],
                }),
            wait_for_capacity=False),
    ]
    self._quick_schedule(1, task_slices=task_slices)
    _, _, run_result = task_scheduler.bot_reap_task(bot1_dimensions, 'abc')
    self.assertEqual(u'bot1', run_result.bot_id)
    to_run_key = _run_result_to_to_run_key(run_result)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(
            run_result.key, bot_id=u'bot1', exit_code=0, duration=0.1))
    self.assertEqual(1, self.execute_tasks())

    # The second part checks for task -> bot
    # Send an identical request
    self._quick_schedule(1, task_slices=task_slices)
    # Then register another bot
    bot2_dimensions = self.bot_dimensions.copy()
    bot2_dimensions[u'id'] = [u'bot2']
    bot2_dimensions[u'os'] = [u'v2']
    bot2_dimensions[u'gpu'] = [u'amd', u'sega']
    self._register_bot(1, bot2_dimensions)

    _, _, run_result = task_scheduler.bot_reap_task(bot2_dimensions, 'def')
    self.assertEqual(u'bot2', run_result.bot_id)
    to_run_key = _run_result_to_to_run_key(run_result)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(
            run_result.key, bot_id=u'bot2', exit_code=0, duration=0.1))
    self.assertEqual(1, self.execute_tasks())

  @parameterized.expand([(0,), (1,)])
  def test_either_bot_reap_tasks_using_or_dimensions(self, bi):
    bots_ids = [u'bot1', u'bot2']
    bot1_dimensions = self.bot_dimensions.copy()
    bot1_dimensions[u'id'] = [bots_ids[0]]
    bot1_dimensions[u'os'] = [u'v1', u'v2']
    bot1_dimensions[u'gpu'] = [u'nv', u'sega']
    self._register_bot(0, bot1_dimensions)

    bot2_dimensions = self.bot_dimensions.copy()
    bot2_dimensions[u'id'] = [bots_ids[1]]
    bot2_dimensions[u'os'] = [u'v2']
    bot2_dimensions[u'gpu'] = [u'amd', u'sega']
    self._register_bot(0, bot2_dimensions)
    bots_dimensions = [bot1_dimensions, bot2_dimensions]

    task_slices = [
        task_request.TaskSlice(
            expiration_secs=60,
            properties=_gen_properties(
                dimensions={
                    u'pool': [u'default'],
                    u'os': [u'v1|v2'],
                    u'gpu': [u'sega', u'amd|nv'],
                }),
            wait_for_capacity=False),
    ]
    self._quick_schedule(1, task_slices=task_slices)

    test_bot_id = bots_ids[bi]
    _, _, run_result = task_scheduler.bot_reap_task(bots_dimensions[bi], 'abc')
    self.assertEqual(test_bot_id, run_result.bot_id)
    to_run_key = _run_result_to_to_run_key(run_result)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(
            run_result.key, bot_id=test_bot_id, exit_code=0, duration=0.1))
    self.assertEqual(1, self.execute_tasks())

  def test_schedule_request(self):
    # It is tested indirectly in the other functions.
    # Essentially check _quick_schedule() and _register_bot() works.
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(1)
    to_run_key = task_to_run.request_to_task_to_run_key(
        result_summary.request_key.get(), 1, 0)
    self.assertTrue(to_run_key.get().queue_number)
    self.assertEqual(State.PENDING, result_summary.state)

  def test_schedule_request_new_key(self):
    # Ensure that _gen_new_keys work by generating deterministic key.
    self.mock(random, 'getrandbits', lambda _bits: 42)
    old_gen_new_keys = self.mock(task_scheduler, '_gen_new_keys', self.fail)
    self._register_bot(0, self.bot_dimensions)
    result_summary_1 = self._quick_schedule(1)
    self.assertEqual('1d69b9f088002a10', result_summary_1.task_id)

    def _gen_new_keys(result_summary, to_run, secret_bytes):
      self.assertTrue(result_summary)
      self.assertTrue(to_run)
      self.assertIsNone(secret_bytes)
      # Change the random bits to give a chance to get a new key ID.
      self.mock(random, 'getrandbits', lambda _bits: 43)
      return old_gen_new_keys(result_summary, to_run, secret_bytes)

    old_gen_new_keys = self.mock(task_scheduler, '_gen_new_keys', _gen_new_keys)
    # In this case, _gen_new_keys is called because:
    # - Time is exactly the same, as utils.utcnow() is mocked.
    # - random.getrandbits() always return the same value.
    # This leads into a constant TaskRequest key id, leading to conflict in
    # datastore_utils.insert(), which causes a call to _gen_new_keys().
    result_summary_2 = self._quick_schedule(0)
    self.assertEqual('1d69b9f088002b10', result_summary_2.task_id)

  def test_schedule_request_new_key_idempotent(self):
    # Ensure that _gen_new_keys work by generating deterministic key, but in the
    # case of task deduplication.
    pub_sub_calls = self.mock_pub_sub()
    self.mock(random, 'getrandbits', lambda _bits: 42)
    task_id_1 = self._task_ran_successfully(1, 0)
    self.assertEqual('1d69b9f088002a11', task_id_1)

    def _gen_new_keys(result_summary, to_run, secret_bytes):
      self.assertTrue(result_summary)
      self.assertIsNone(to_run)
      self.assertIsNone(secret_bytes)
      # Change the random bits to give a chance to get a new key ID.
      self.mock(random, 'getrandbits', lambda _bits: 43)
      return old_gen_new_keys(result_summary, to_run, secret_bytes)

    old_gen_new_keys = self.mock(task_scheduler, '_gen_new_keys', _gen_new_keys)
    # In this case, _gen_new_keys is called because:
    # - Time is exactly the same, as utils.utcnow() is mocked.
    # - random.getrandbits() always return the same value.
    # This leads into a constant TaskRequest key id, leading to conflict in
    # datastore_utils.insert(), which causes a call to _gen_new_keys().
    result_summary_2 = self._quick_schedule(
        1,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ],
        pubsub_topic='projects/abc/topics/def')
    self.assertEqual('1d69b9f088002b10', result_summary_2.task_id)
    self.assertEqual(State.COMPLETED, result_summary_2.state)
    self.assertEqual(task_id_1, result_summary_2.deduped_from)
    expected = [
        (
            'directly',
            {
                'attributes': None,
                'message': '{"task_id":"1d69b9f088002b10"}',
                'topic': u'projects/abc/topics/def',
            },
        ),
    ]
    self.assertEqual(expected, pub_sub_calls)

  def test_schedule_request_no_capacity(self):
    # No capacity, denied. That's the default.
    pub_sub_calls = self.mock_pub_sub()
    request = _gen_request_slices(pubsub_topic='projects/abc/topics/def')
    result_summary = task_scheduler.schedule_request(request, None, False)
    self.assertEqual(State.NO_RESOURCE, result_summary.state)
    self.assertEqual(2, self.execute_tasks())
    expected = [
        (
            'directly',
            {
                'attributes': None,
                'message': '{"task_id":"1d69b9f088008910"}',
                'topic': u'projects/abc/topics/def',
            },
        ),
    ]
    self.assertEqual(expected, pub_sub_calls)

  def test_schedule_request_no_check_capacity(self):
    # No capacity, but check disabled, allowed.
    request = _gen_request_slices(task_slices=[
        task_request.TaskSlice(
            expiration_secs=60,
            properties=_gen_properties(),
            wait_for_capacity=True),
    ])
    result_summary = task_scheduler.schedule_request(request, None, False)
    self.assertEqual(State.PENDING, result_summary.state)
    self.assertEqual(1, self.execute_tasks())

  @ndb.tasklet
  def _mock_create_invocation_async(self, _task_run_id, _realm):
    raise ndb.Return('resultdb-update-token')

  def test_schedule_request_resultdb(self):
    self._register_bot(0, self.bot_dimensions)

    with mock.patch(
        'server.resultdb.create_invocation_async',
        mock.Mock(side_effect=self._mock_create_invocation_async)) as mock_call:
      request = _gen_request_slices(realm='infra:try')
      result_summary = task_scheduler.schedule_request(request, None, True)
      mock_call.assert_called_once_with('1d69b9f088008911', 'infra:try')

    self.assertEqual(
        result_summary.resultdb_info,
        task_result.ResultDBInfo(
            hostname='test-resultdb-server.com',
            invocation=(
                'invocations/task-test-swarming.appspot.com-1d69b9f088008911')))
    self.assertEqual(result_summary.request_key.get().resultdb_update_token,
                     'resultdb-update-token')

    self.assertEqual(1, self.execute_tasks())

  def test_bot_reap_task_expired(self):
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(1)
    # Forwards clock to get past expiration.
    self.mock_now(result_summary.request_key.get().expiration_ts, 1)

    actual_request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')
    # The task is not returned because it's expired.
    self.assertIsNone(actual_request)
    self.assertIsNone(run_result)
    # It's effectively expired.
    to_run_key = task_to_run.request_to_task_to_run_key(
        result_summary.request_key.get(), 1, 0)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertIsNone(to_run_key.get().expiration_ts)
    self.assertEqual(State.EXPIRED, result_summary.key.get().state)

  def test_bot_reap_task_6_expired_fifo(self):
    cfg = config.settings()
    cfg.use_lifo = False
    self.mock(config, 'settings', lambda: cfg)

    # A lot of tasks are expired, eventually stop expiring them.
    self._register_bot(0, self.bot_dimensions)
    result_summaries = []
    for i in range(6):
      self.mock_now(self.now, i)
      result_summaries.append(self._quick_schedule(int(not bool(i))))
    # Forwards clock to get past expiration.
    self.mock_now(result_summaries[-1].request_key.get().expiration_ts, 1)

    # Fail to reap a task.
    actual_request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')
    self.assertIsNone(actual_request)
    self.assertIsNone(run_result)
    # They all got expired ...
    for result_summary in result_summaries[:-1]:
      result_summary = result_summary.key.get()
      self.assertEqual(State.EXPIRED, result_summary.state)
    # ... except for the very last one because of the limit of 5 task expired
    # per poll.
    result_summary = result_summaries[-1]
    result_summary = result_summary.key.get()
    self.assertEqual(State.PENDING, result_summary.state)

  def test_bot_reap_task_6_expired_lifo(self):
    cfg = config.settings()
    cfg.use_lifo = True
    self.mock(config, 'settings', lambda: cfg)

    # A lot of tasks are expired, eventually stop expiring them.
    self._register_bot(0, self.bot_dimensions)
    result_summaries = []
    for i in range(6):
      self.mock_now(self.now, i)
      result_summaries.append(self._quick_schedule(int(not bool(i))))
    # Forwards clock to get past expiration.
    self.mock_now(result_summaries[-1].request_key.get().expiration_ts, 1)

    # Fail to reap a task.
    actual_request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')
    self.assertIsNone(actual_request)
    self.assertIsNone(run_result)
    # They all got expired ...
    for result_summary in result_summaries[1:]:
      result_summary = result_summary.key.get()
      self.assertEqual(State.EXPIRED, result_summary.state)
    # ... except for the most recent one because of the limit of 5 task expired
    # per poll.
    result_summary = result_summaries[0]
    result_summary = result_summary.key.get()
    self.assertEqual(State.PENDING, result_summary.state)

  @ndb.tasklet
  def nop_async(self, *_args, **_kwargs):
    pass

  def test_resultdb_task_expired(self):
    self._register_bot(0, self.bot_dimensions)

    with mock.patch(
        'server.resultdb.create_invocation_async',
        mock.Mock(side_effect=self._mock_create_invocation_async)) as mock_call:
      request = _gen_request_slices(realm='infra:try')
      result_summary = task_scheduler.schedule_request(request, None, True)
      mock_call.assert_called_once_with('1d69b9f088008911', 'infra:try')

    with mock.patch('server.resultdb.finalize_invocation_async',
                    mock.Mock(side_effect=self.nop_async)) as mock_call:
      to_run_key = task_to_run.request_to_task_to_run_key(request, 1, 0)
      task_scheduler._expire_task(to_run_key, request, True)
      mock_call.assert_called_once_with('1d69b9f088008911',
                                        u'resultdb-update-token')

    self.assertEqual(1, self.execute_tasks())

  def _setup_es(self, allow_es_fallback):
    """Set up mock es_config."""
    es_address = 'externalscheduler_address'
    es_id = 'es_id'
    external_schedulers = [
        pools_config.ExternalSchedulerConfig(
            address=es_address,
            id=es_id,
            dimensions=set([u'foo:bar', u'label-pool:CTS']),
            all_dimensions=None,
            any_dimensions=None,
            enabled=False,
            allow_es_fallback=allow_es_fallback),
        pools_config.ExternalSchedulerConfig(
            address=es_address,
            id=es_id,
            dimensions=set([u'foo:bar']),
            all_dimensions=None,
            any_dimensions=None,
            enabled=True,
            allow_es_fallback=allow_es_fallback),
    ]
    self.mock_pool_config('default', external_schedulers=external_schedulers)

  def _mock_reap_calls(self):
    """Mock out external scheduler and native scheduler reap calls.

    Returns: (list of es calls, list of native reap calls)
    """
    er_calls = []

    def ext_reap(*args):
      er_calls.append(args)
      return None, None, None

    result_summary = self._quick_schedule(
        1,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(),
                # The tests that use this mock rely on tasks that wait
                # for capacity.
                wait_for_capacity=True),
        ])
    to_run_key = task_to_run.request_to_task_to_run_key(result_summary.request,
                                                        1, 0)

    r_calls = []

    def reap(*args):
      r_calls.append(args)
      return [(result_summary.request, to_run_key.get())]

    self.mock(task_scheduler, '_bot_reap_task_external_scheduler', ext_reap)
    self.mock(task_to_run, 'yield_next_available_task_to_dispatch', reap)

    return er_calls, r_calls

  def _mock_es_assign(self, task_id, slice_number):
    """Mock out the return behavior from external_scheduler.assign_task"""

    # pylint: disable=unused-argument
    def mock_assign(*args):
      return task_id, slice_number

    self.mock(external_scheduler, "assign_task", mock_assign)

  def _mock_es_notify(self):
    """Mock out external_scheduler.notify_requests

    Returns a list that will receive any calls that were made to notify.
    """
    calls = []

    # pylint: disable=unused-argument
    def mock_notify(es_cfg, requests, use_tq, is_callback):
      assert isinstance(es_cfg, pools_config.ExternalSchedulerConfig)
      for request, result in requests:
        assert isinstance(request, task_request.TaskRequest)
        assert isinstance(result, task_result._TaskResultCommon)
      calls.append([es_cfg, requests, use_tq, is_callback])
      return

    self.mock(external_scheduler, "notify_requests", mock_notify)

    return calls

  def test_bot_reap_task_es_with_fallback(self):
    self._setup_es(True)
    notify_calls = self._mock_es_notify()
    er_calls, r_calls = self._mock_reap_calls()

    # Ignore es notifications that were side-effects of the setup code, they
    # are incidental to this test.
    del notify_calls[:]

    task_scheduler.bot_reap_task(self.bot_dimensions, 'abc')

    self.assertEqual(len(er_calls), 1, 'external scheduler was not called')
    self.assertEqual(len(r_calls), 1, 'native scheduler was not called')

  def test_bot_reap_task_es_no_task(self):
    self._setup_es(False)
    self._mock_es_assign(None, 0)

    task_scheduler.bot_reap_task(self.bot_dimensions, 'abc')

  def test_bot_reap_task_es_with_nonpending_task(self):
    self._setup_es(False)
    notify_calls = self._mock_es_notify()
    result_summary = self._quick_schedule(1)
    self._mock_es_assign(result_summary.task_id, 0)

    # Ignore es notifications that were side-effects of the setup code, they
    # are incidental to this test.
    del notify_calls[:]

    # It should notify to external scheduler. But an exception won't be raised
    # because the task is already running or has finished including failures.
    task_scheduler.bot_reap_task(self.bot_dimensions, 'abc')
    self.assertEqual(len(notify_calls), 1)

  def test_bot_reap_task_es_with_pending_task(self):
    self._setup_es(False)
    self._mock_es_notify()
    result_summary = self._quick_schedule(
        1,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(),
                wait_for_capacity=True)
        ])

    self._mock_es_assign(result_summary.task_id, 0)

    # Able to successfully reap given PENDING task from external scheduler.
    request, _, _ = task_scheduler.bot_reap_task(self.bot_dimensions, 'abc')
    self.assertEqual(request.task_id, result_summary.task_id)

  def test_bot_reap_task_for_nonexternal_pool(self):
    self._setup_es(False)
    notify_calls = self._mock_es_notify()
    dimensions = {u'os': [u'Windows-3.1.1'], u'pool': [u'label-pool:CTS']}
    slices = [
        task_request.TaskSlice(
            expiration_secs=60,
            properties=_gen_properties(dimensions=dimensions),
            wait_for_capacity=False),
    ]
    result_summary = self._quick_schedule(1, task_slices=slices)
    self._mock_es_assign(result_summary.task_id, 0)

    del notify_calls[:]
    bot_dimensions = {
        u'foo': [u'bar'],
        u'id': [u'localhost'],
        u'label-pool': [u'CTS'],
    }
    # CTS pool has disabled external scheduler, so notify_calls should have
    # nothing recorded.
    task_scheduler.bot_reap_task(bot_dimensions, 'abc')
    self.assertEqual(len(notify_calls), 0)

  def test_schedule_request_slice_fallback_to_second_immediate(self):
    # First TaskSlice couldn't run so it was immediately skipped, the second ran
    # instead.
    self._register_bot(0, self.bot_dimensions)
    self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(dimensions={
                    u'nonexistent': [u'really'],
                    u'pool': [u'default'],
                }),
                wait_for_capacity=False),
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(),
                wait_for_capacity=False),
        ])
    request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')
    self.assertEqual(1, run_result.current_task_slice)

  def test_schedule_request_slice_use_first_after_expiration(self):
    # First TaskSlice runs so it is reaped before expiring cron job.
    self._register_bot(0, self.bot_dimensions)
    self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(io_timeout_secs=61)),
            task_request.TaskSlice(
                expiration_secs=180, properties=_gen_properties()),
        ])
    self.mock_now(self.now, 181)
    # The first slice is returned from bot_reap_task if it is called earlier
    # than cron_abort_expired_task_to_run.
    request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')
    self.assertEqual(0, run_result.current_task_slice)

  def test_schedule_request_slice_fallback_to_different_property(self):
    # The first TaskSlice couldn't run so it was eventually expired and the
    # second couldn't be run by the bot that was polling.
    self._register_bot(0, self.bot_dimensions)
    second_bot = self.bot_dimensions.copy()
    second_bot[u'id'] = [u'second']
    second_bot[u'os'] = [u'Atari']
    self._register_bot(0, second_bot)
    self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(io_timeout_secs=61)),
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'os': [u'Atari']
                })),
        ])
    # The second bot can't reap the task.
    _, _, run_result = task_scheduler.bot_reap_task(second_bot, 'second')
    self.assertIsNone(run_result)

    self.mock_now(self.now, 181)

    # Expire first task here.
    task_scheduler.cron_abort_expired_task_to_run()
    tasks = self._taskqueue_stub.GetTasks('task-expire')
    self.assertEqual(1, len(tasks))
    self.assertEqual(1, self.execute_tasks())

    # The first is explicitly expired, and the second TaskSlice cannot be
    # reaped by this bot.
    _, _, run_result = task_scheduler.bot_reap_task(self.bot_dimensions, 'abc')
    self.assertIsNone(run_result)
    # The second bot is able to reap it immediately. This is because when the
    # first bot tried to reap the task, it expired the first TaskToRun and
    # created a new one, which the second bot *can* reap.
    _, _, run_result = task_scheduler.bot_reap_task(second_bot, 'second')
    self.assertEqual(1, run_result.current_task_slice)

  def test_schedule_request_slice_no_capacity(self):
    result_summary = self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(dimensions={
                    u'nonexistent': [u'really'],
                    u'pool': [u'default'],
                }),
                wait_for_capacity=False),
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(),
                wait_for_capacity=False),
        ])
    # The task is immediately denied, without waiting.
    self.assertEqual(State.NO_RESOURCE, result_summary.state)
    self.assertEqual(self.now, result_summary.abandoned_ts)
    self.assertEqual(self.now, result_summary.completed_ts)
    self.assertIsNone(result_summary.try_number)
    self.assertEqual(0, result_summary.current_task_slice)

  def test_schedule_request_slice_wait_for_capacity(self):
    result_summary = self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(dimensions={
                    u'nonexistent': [u'really'],
                    u'pool': [u'default'],
                }),
                wait_for_capacity=False),
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(),
                wait_for_capacity=True),
        ])
    # Pending on the second slice, even if there's no capacity.
    self.assertEqual(State.PENDING, result_summary.state)
    self.assertEqual(1, result_summary.current_task_slice)

  def test_schedule_request_slice_no_capacity_fallback_second(self):
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(dimensions={
                    u'nonexistent': [u'really'],
                    u'pool': [u'default'],
                }),
                wait_for_capacity=False),
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(),
                wait_for_capacity=False),
        ])
    # The task fell back to the second slice, still pending.
    self.assertEqual(State.PENDING, result_summary.state)
    self.assertIsNone(result_summary.abandoned_ts)
    self.assertIsNone(result_summary.completed_ts)
    self.assertIsNone(result_summary.try_number)
    self.assertEqual(1, result_summary.current_task_slice)

  def test_exponential_backoff(self):
    self.mock(task_scheduler.random,
              'random', lambda: task_scheduler._PROBABILITY_OF_QUICK_COMEBACK)
    self.mock(utils, 'is_dev', lambda: False)
    data = [
        (0, 2),
        (1, 2),
        (2, 3),
        (3, 5),
        (4, 8),
        (5, 11),
        (6, 17),
        (7, 26),
        (8, 38),
        (9, 58),
        (10, 60),
        (11, 60),
    ]
    for value, expected in data:
      actual = int(round(task_scheduler.exponential_backoff(value)))
      self.assertEqual(expected, actual, (value, expected, actual))

  def test_exponential_backoff_quick(self):
    self.mock(
        task_scheduler.random,
        'random', lambda: task_scheduler._PROBABILITY_OF_QUICK_COMEBACK - 0.01)
    self.assertEqual(1.0, task_scheduler.exponential_backoff(235))

  def test_task_handle_pubsub_task(self):
    calls = []

    def publish_mock(**kwargs):
      calls.append(kwargs)

    self.mock(task_scheduler.pubsub, 'publish', publish_mock)
    task_scheduler.task_handle_pubsub_task({
        'topic': 'projects/abc/topics/def',
        'task_id': 'abcdef123',
        'auth_token': 'token',
        'userdata': 'userdata',
    })
    self.assertEqual([{
        'attributes': {
            'auth_token': 'token'
        },
        'message': '{"task_id":"abcdef123","userdata":"userdata"}',
        'topic': 'projects/abc/topics/def',
    }], calls)

  def _task_ran_successfully(self, num_task, num_btd_updated):
    """Runs an idempotent task successfully and returns the task_id.

    Arguments:
      num_task: number of AppEngine task queues enqueued (and run
                synchronously). Do not confused with Swarming task queues,
                completely unrelated.
      num_btd_updated: number of 'BotTaskDimensions' entities (from
                       task_queues.py) updated, normally 0, 1 or None if it was
                       cached.
    """
    run_result = self._quick_reap(
        num_task,
        num_btd_updated,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    self.assertEqual('localhost', run_result.bot_id)
    to_run_key = _run_result_to_to_run_key(run_result)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertIsNone(to_run_key.get().expiration_ts)
    # It's important to complete the task with success.
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(run_result.key, exit_code=0, duration=0.1))
    # An idempotent task has properties_hash set after it succeeded.
    self.assertTrue(run_result.result_summary_key.get().properties_hash)
    self.assertEqual(1, self.execute_tasks())
    return unicode(run_result.task_id)

  def _task_deduped(self,
                    num_task,
                    new_ts,
                    deduped_from,
                    task_id,
                    now=None,
                    bot_dimensions_cached=False):
    """Runs a task that was deduped."""
    # TODO(maruel): Test with SecretBytes.
    if bot_dimensions_cached:
      self._register_bot(None, self.bot_dimensions)
    else:
      self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        num_task,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    request = result_summary.request_key.get()
    to_run_key = task_to_run.request_to_task_to_run_key(request, 1, 0)
    # TaskToRun was not stored.
    self.assertIsNone(to_run_key.get())
    # Bot can't reap.
    reaped_request, _, _ = task_scheduler.bot_reap_task(self.bot_dimensions,
                                                        'abc')
    self.assertIsNone(reaped_request)

    result_summary_duped, run_results_duped = _get_results(request.key)
    # A deduped task cannot be deduped again so properties_hash is None.
    expected = self._gen_result_summary_reaped(
        completed_ts=now or self.now,
        cost_saved_usd=0.1,
        created_ts=new_ts,
        deduped_from=deduped_from,
        duration=0.1,
        exit_code=0,
        id=task_id,
        # Only this value is updated to 'now', the rest uses the previous run
        # timestamps.
        modified_ts=new_ts,
        started_ts=now or self.now,
        state=State.COMPLETED,
        try_number=0)
    self.assertEqual(expected, result_summary_duped.to_dict())
    self.assertEqual([], run_results_duped)

  def test_task_idempotent(self):
    # First task is idempotent.
    task_id = self._task_ran_successfully(1, 0)

    # Second task is deduped against first task.
    new_ts = self.mock_now(self.now,
                           config.settings().reusable_task_age_secs - 1)
    self._task_deduped(1, new_ts, task_id, '1d8dc670a0008a10')

  def test_task_idempotent_old(self):
    # First task is idempotent.
    self._task_ran_successfully(1, 0)

    # Second task is scheduled, first task is too old to be reused.
    new_ts = self.mock_now(self.now, config.settings().reusable_task_age_secs)
    result_summary = self._quick_schedule(
        1,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    # The task was enqueued for execution.
    to_run_key = task_to_run.request_to_task_to_run_key(
        result_summary.request_key.get(), 1, 0)
    self.assertTrue(to_run_key.get().queue_number)

  def test_task_idempotent_three(self):
    # First task is idempotent.
    task_id = self._task_ran_successfully(1, 0)

    # Second task is deduped against first task.
    new_ts = self.mock_now(self.now,
                           config.settings().reusable_task_age_secs - 1)
    self._task_deduped(1, new_ts, task_id, '1d8dc670a0008a10')

    # Third task is scheduled, second task is not dedupable, first task is too
    # old.
    new_ts = self.mock_now(self.now, config.settings().reusable_task_age_secs)
    result_summary = self._quick_schedule(
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    # The task was enqueued for execution.
    to_run_key = task_to_run.request_to_task_to_run_key(
        result_summary.request_key.get(), 1, 0)
    self.assertTrue(to_run_key.get().queue_number)

  def test_task_idempotent_variable(self):
    # Test the edge case where config.settings().reusable_task_age_secs is being
    # modified. This ensure TaskResultSummary.order(TRS.key) works.
    cfg = config.settings()
    cfg.reusable_task_age_secs = 10
    self.mock(config, 'settings', lambda: cfg)

    # First task is idempotent.
    self._task_ran_successfully(1, 0)

    # Second task is scheduled, first task is too old to be reused.
    second_ts = self.mock_now(self.now, 10)
    task_id = self._task_ran_successfully(0, None)

    # Now any of the 2 tasks could be reused. Assert the right one (the most
    # recent) is reused.
    cfg.reusable_task_age_secs = 100

    # Third task is deduped against second task. That ensures ordering works
    # correctly.
    third_ts = self.mock_now(self.now, 20)
    self._task_deduped(
        0,
        third_ts,
        task_id,
        '1d69ba3ea8008b10',
        now=second_ts,
        bot_dimensions_cached=True)

  def test_task_idempotent_second_slice(self):
    # A task will dedupe against a second slice, and skip the first slice.
    # First task is idempotent.
    task_id = self._task_ran_successfully(1, 0)

    # Second task's second task slice is deduped against first task.
    new_ts = self.mock_now(self.now,
                           config.settings().reusable_task_age_secs - 1)
    result_summary = self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(dimensions={
                    u'inexistant': [u'really'],
                    u'pool': [u'default'],
                }),
                wait_for_capacity=False),
            task_request.TaskSlice(
                expiration_secs=180,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    to_run_key = task_to_run.request_to_task_to_run_key(
        result_summary.request_key.get(), 1, 0)
    self.assertIsNone(to_run_key.get())
    to_run_key = task_to_run.request_to_task_to_run_key(
        result_summary.request_key.get(), 1, 1)
    self.assertIsNone(to_run_key.get())
    self.assertEqual(State.COMPLETED, result_summary.state)
    self.assertEqual(task_id, result_summary.deduped_from)
    self.assertEqual(1, result_summary.current_task_slice)
    self.assertEqual(0, result_summary.try_number)

  def test_task_invalid_parent(self):
    parent_id = self._task_ran_successfully(1, 0)
    self.assertTrue(parent_id.endswith('1'))
    invalid_parent_id = parent_id[:-1] + '2'
    # Try to create a children task with invalid parent_task_id.
    # task should be scheduled without error
    result_summary = self._quick_schedule(0, parent_task_id=invalid_parent_id)

  def test_task_parent_isolated(self):
    run_result = self._quick_reap(
        1,
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(
                    command=['python'],
                    inputs_ref=task_request.FilesRef(
                        isolated='1' * 40,
                        isolatedserver='http://localhost:1',
                        namespace='default-gzip')),
                wait_for_capacity=False),
        ])
    self.assertEqual('localhost', run_result.bot_id)
    to_run_key = _run_result_to_to_run_key(run_result)
    self.assertIsNone(to_run_key.get().queue_number)
    self.assertIsNone(to_run_key.get().expiration_ts)
    # It's important to terminate the task with success.
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(run_result.key, exit_code=0, duration=0.1))
    self.assertEqual(1, self.execute_tasks())

    parent_id = run_result.task_id
    result_summary = self._quick_schedule(0, parent_task_id=parent_id)
    self.assertEqual([], result_summary.children_task_ids)
    self.assertEqual(parent_id, result_summary.request_key.get().parent_task_id)

  def test_task_timeout(self):
    # Create a task, but the bot tries to timeout but fails to report exit code
    # and duration.
    run_result = self._quick_reap(1, 0)
    to_run_key = _run_result_to_to_run_key(run_result)
    self.mock_now(self.now, 10.5)
    self.assertEqual(State.TIMED_OUT,
                     _bot_update_task(run_result.key, hard_timeout=True))
    self.assertEqual(1, self.execute_tasks())
    run_result = run_result.key.get()
    self.assertEqual(-1, run_result.exit_code)
    self.assertEqual(10.5, run_result.duration)

  def test_get_results(self):
    # TODO(maruel): Split in more focused tests.
    created_ts = self.now
    self.mock_now(created_ts)
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(1)

    # The TaskRequest was enqueued, the TaskResultSummary was created but no
    # TaskRunResult exist yet since the task was not scheduled on any bot.
    result_summary, run_results = _get_results(result_summary.request_key)
    expected = self._gen_result_summary_pending(
        created_ts=created_ts, id='1d69b9f088008910', modified_ts=created_ts)
    self.assertEqual(expected, result_summary.to_dict())
    self.assertEqual([], run_results)

    # A bot reaps the TaskToRun.
    reaped_ts = self.now + datetime.timedelta(seconds=60)
    self.mock_now(reaped_ts)
    reaped_request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')
    self.assertEqual(result_summary.request_key.get(), reaped_request)
    self.assertTrue(run_result)
    result_summary, run_results = _get_results(result_summary.request_key)
    expected = self._gen_result_summary_reaped(
        created_ts=created_ts,
        costs_usd=[0.0],
        id='1d69b9f088008910',
        modified_ts=reaped_ts,
        started_ts=reaped_ts)
    self.assertEqual(expected, result_summary.to_dict())
    expected = [
        self._gen_run_result(
            id='1d69b9f088008911',
            modified_ts=reaped_ts,
            started_ts=reaped_ts,
            dead_after_ts=reaped_ts +
            datetime.timedelta(seconds=reaped_request.bot_ping_tolerance_secs)),
    ]
    self.assertEqual(expected, [i.to_dict() for i in run_results])

    # The bot completes the task.
    done_ts = self.now + datetime.timedelta(seconds=120)
    self.mock_now(done_ts)
    outputs_ref = task_request.FilesRef(
        isolated='a' * 40, isolatedserver='http://localhost', namespace='c')
    performance_stats = task_result.PerformanceStats(
        bot_overhead=0.1,
        isolated_download=task_result.CASOperationStats(
            duration=0.1,
            initial_number_items=10,
            initial_size=1000,
            items_cold='aa',
            items_hot='bb'),
        isolated_upload=task_result.CASOperationStats(
            duration=0.1, items_cold='aa', items_hot='bb'))
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(
            run_result.key,
            exit_code=0,
            duration=3.,
            outputs_ref=outputs_ref,
            performance_stats=performance_stats))
    # Simulate an unexpected retry, e.g. the response of the previous RPC never
    # got the client even if it succeedded.
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(
            run_result.key,
            exit_code=0,
            duration=3.,
            outputs_ref=outputs_ref,
            performance_stats=performance_stats))
    result_summary, run_results = _get_results(result_summary.request_key)
    expected = self._gen_result_summary_reaped(
        completed_ts=done_ts,
        costs_usd=[0.1],
        created_ts=created_ts,
        duration=3.0,
        exit_code=0,
        id='1d69b9f088008910',
        modified_ts=done_ts,
        outputs_ref={
            'isolated': u'a' * 40,
            'isolatedserver': u'http://localhost',
            'namespace': u'c',
        },
        started_ts=reaped_ts,
        state=State.COMPLETED,
        try_number=1)
    self.assertEqual(expected, result_summary.to_dict())
    expected = [
        self._gen_run_result(
            completed_ts=done_ts,
            cost_usd=0.1,
            duration=3.0,
            exit_code=0,
            id='1d69b9f088008911',
            modified_ts=done_ts,
            outputs_ref={
                'isolated': u'a' * 40,
                'isolatedserver': u'http://localhost',
                'namespace': u'c',
            },
            started_ts=reaped_ts,
            state=State.COMPLETED),
    ]
    self.assertEqual(expected, [t.to_dict() for t in run_results])
    self.assertEqual(2, self.execute_tasks())

  def test_exit_code_failure(self):
    run_result = self._quick_reap(1, 0)
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(run_result.key, exit_code=1, duration=0.1))
    result_summary, run_results = _get_results(run_result.request_key)

    expected = self._gen_result_summary_reaped(
        completed_ts=self.now,
        costs_usd=[0.1],
        duration=0.1,
        exit_code=1,
        failure=True,
        id='1d69b9f088008910',
        started_ts=self.now,
        state=State.COMPLETED,
        try_number=1)
    self.assertEqual(expected, result_summary.to_dict())

    expected = [
        self._gen_run_result(
            completed_ts=self.now,
            cost_usd=0.1,
            duration=0.1,
            exit_code=1,
            failure=True,
            id='1d69b9f088008911',
            started_ts=self.now,
            state=State.COMPLETED),
    ]
    self.assertEqual(expected, [t.to_dict() for t in run_results])
    self.assertEqual(1, self.execute_tasks())

  def test_schedule_request_id_without_pool(self):
    auth_testing.mock_is_admin(self)
    self._register_bot(0, self.bot_dimensions)
    with self.assertRaises(datastore_errors.BadValueError):
      self._quick_schedule(
          0,
          task_slices=[
              task_request.TaskSlice(
                  expiration_secs=60,
                  properties=_gen_properties(dimensions={u'id': [u'abc']}),
                  wait_for_capacity=False),
          ])

  def test_bot_update_task(self):
    self.mock(task_result.TaskOutput, 'CHUNK_SIZE', 2)
    run_result = self._quick_reap(1, 0)
    self.assertEqual(
        State.RUNNING,
        _bot_update_task(run_result.key, output='hi', output_chunk_start=0))
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(
            run_result.key,
            output='hey',
            output_chunk_start=2,
            exit_code=0,
            duration=0.1))
    self.assertEqual('hihey', run_result.key.get().get_output(0, 0))
    self.assertEqual(1, self.execute_tasks())

  def test_bot_update_task_new_overwrite(self):
    self.mock(task_result.TaskOutput, 'CHUNK_SIZE', 2)
    run_result = self._quick_reap(1, 0)
    self.assertEqual(
        State.RUNNING,
        _bot_update_task(
            run_result_key=run_result.key, output='hi', output_chunk_start=0))
    self.assertEqual(
        State.RUNNING,
        _bot_update_task(
            run_result_key=run_result.key, output='hey', output_chunk_start=1))
    self.assertEqual('hhey', run_result.key.get().get_output(0, 0))

  def test_bot_update_exception(self):
    run_result = self._quick_reap(1, 0)

    def r(*_):
      raise datastore_utils.CommitError('Sorry!')

    self.mock(ndb, 'put_multi', r)
    self.assertEqual(
        None, _bot_update_task(run_result.key, exit_code=0, duration=0.1))

  def test_bot_update_pubsub_error(self):
    pub_sub_calls = self.mock_pub_sub()
    run_result = self._quick_reap(1, 0, pubsub_topic='projects/abc/topics/def')

    # Attempt to terminate the task with success, but make PubSub call fail.
    self.publish_successful = False
    self.assertEqual(
        None, _bot_update_task(run_result.key, exit_code=0, duration=0.1))

    # Bot retries bot_update, now PubSub works and notification is sent.
    self.publish_successful = True
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(run_result.key, exit_code=0, duration=0.1))
    self.assertEqual(2, len(pub_sub_calls))  # notification is sent
    self.assertEqual(1, self.execute_tasks())

  def _bot_update_timeouts(self, hard, io):
    run_result = self._quick_reap(1, 0)
    self.assertEqual(
        State.TIMED_OUT,
        _bot_update_task(
            run_result.key,
            exit_code=0,
            duration=0.1,
            hard_timeout=hard,
            io_timeout=io))
    expected = self._gen_result_summary_reaped(
        completed_ts=self.now,
        costs_usd=[0.1],
        duration=0.1,
        exit_code=0,
        failure=True,
        id='1d69b9f088008910',
        started_ts=self.now,
        state=State.TIMED_OUT,
        try_number=1)
    self.assertEqual(expected, run_result.result_summary_key.get().to_dict())

    expected = self._gen_run_result(
        completed_ts=self.now,
        cost_usd=0.1,
        duration=0.1,
        exit_code=0,
        failure=True,
        id='1d69b9f088008911',
        started_ts=self.now,
        state=State.TIMED_OUT,
        try_number=1)
    self.assertEqual(expected, run_result.key.get().to_dict())
    self.assertEqual(1, self.execute_tasks())

  def test_bot_update_hard_timeout(self):
    self._bot_update_timeouts(True, False)

  def test_bot_update_io_timeout(self):
    self._bot_update_timeouts(False, True)

  def test_bot_update_child_with_cancelled_parent(self):
    self._register_bot(0, self.bot_dimensions)

    # Run parent task.
    parent_request = _gen_request_slices()
    parent_result_summary = task_scheduler.schedule_request(
        parent_request, None, False)
    self.assertEqual(1, self.execute_tasks())

    _, _, parent_run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')

    # Run a child task.
    child_request = _gen_request_slices(
        parent_task_id=parent_run_result.task_id)
    child_result_summary = task_scheduler.schedule_request(
        child_request, None, False)
    self.assertEqual(0, self.execute_tasks())

    bot2_dimensions = self.bot_dimensions.copy()
    bot2_dimensions['id'] = [bot2_dimensions['id'][0] + '2']
    self._register_bot(1, bot2_dimensions)
    _, _, child_run_result = task_scheduler.bot_reap_task(
        bot2_dimensions, 'abc')
    self.assertEqual(0, self.execute_tasks())

    # Run a child task 2.
    child_request2 = _gen_request_slices(
        parent_task_id=parent_run_result.task_id)
    child_result2_summary = task_scheduler.schedule_request(
        child_request2, None, False)
    self.assertEqual(0, self.execute_tasks())

    bot3_dimensions = self.bot_dimensions.copy()
    bot3_dimensions['id'] = [bot3_dimensions['id'][0] + '3']
    self._register_bot(1, bot3_dimensions)
    _, _, child_run_result2 = task_scheduler.bot_reap_task(
        bot3_dimensions, 'abc')
    self.assertEqual(0, self.execute_tasks())

    # Run a child task 3. This will be cancelled before running.
    child_request3 = _gen_request_slices(
        parent_task_id=parent_run_result.task_id)
    child_result3_summary = task_scheduler.schedule_request(
        child_request3, None, False)

    # Cancel parent task.
    ok, was_running = task_scheduler.cancel_task(
        parent_run_result.request_key.get(),
        parent_run_result.result_summary_key, True, None)
    self.assertEqual(True, ok)
    self.assertEqual(True, was_running)

    # parent_task should push task to cancel-children-tasks.
    self.execute_task(
        '/internal/taskqueue/important/tasks/cancel-children-tasks',
        'cancel-children-tasks',
        utils.encode_to_json({
            'task': parent_result_summary.task_id,
        }))
    # and child tasks should be cancelled via task queue.
    appended_child_task_ids = [
        child_result3_summary.task_id,
        child_result2_summary.task_id,
        child_result_summary.task_id,
    ]
    self.execute_task(
        '/internal/taskqueue/important/tasks/cancel', 'cancel-tasks',
        utils.encode_to_json({
            'kill_running': True,
            'tasks': appended_child_task_ids,
        }))

    self.assertEqual(
        State.KILLED,
        _bot_update_task(parent_run_result.key, exit_code=0, duration=0.1))

    # Child task is KILLED when parent task is cancelled.
    self.assertEqual(
        State.KILLED,
        _bot_update_task(
            child_run_result.key,
            bot_id='localhost2',
            exit_code=0,
            duration=0.1))

    self.assertEqual('hi', child_run_result.key.get().get_output(0, 0))

    # Child task is KILLED when parent task is cancelled and not being
    # completed.
    self.assertEqual(
        State.KILLED,
        _bot_update_task(child_run_result2.key, bot_id='localhost3'))
    self.assertEqual('hi', child_run_result2.key.get().get_output(0, 0))

    # flush tasks
    self.execute_tasks()

  def test_task_priority(self):
    # Create N tasks of various priority not in order.
    priorities = [200, 100, 20, 30, 50, 40, 199]
    # Call the expected ordered list out for clarity.
    expected = [20, 30, 40, 50, 100, 199, 200]
    self.assertEqual(expected, sorted(priorities))

    self._register_bot(0, self.bot_dimensions)
    # Triggers many tasks of different priorities.
    for i, p in enumerate(priorities):
      self._quick_schedule(num_task=int(not i), priority=p)
    self.assertEqual(0, self.execute_tasks())

    # Make sure they are scheduled in priority order. Bot polling should hand
    # out tasks in the expected order. In practice the order is not 100%
    # deterministic when running on GAE but it should be deterministic in the
    # unit test.
    for i, e in enumerate(expected):
      request, _, _ = task_scheduler.bot_reap_task(self.bot_dimensions, 'abc')
      self.assertEqual(request.priority, e)

  def test_bot_terminate_task(self):
    pub_sub_calls = self.mock_pub_sub()
    run_result = self._quick_reap(1, 0, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(1, len(pub_sub_calls))  # PENDING -> RUNNING

    self.assertEqual(
        None, task_scheduler.bot_terminate_task(run_result.key, 'localhost'))
    expected = self._gen_result_summary_reaped(
        abandoned_ts=self.now,
        completed_ts=self.now,
        costs_usd=[0.],
        id='1d69b9f088008910',
        internal_failure=True,
        started_ts=self.now,
        state=State.BOT_DIED)
    self.assertEqual(expected, run_result.result_summary_key.get().to_dict())
    expected = self._gen_run_result(
        abandoned_ts=self.now,
        completed_ts=self.now,
        id='1d69b9f088008911',
        internal_failure=True,
        state=State.BOT_DIED)
    self.assertEqual(expected, run_result.key.get().to_dict())
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(2, len(pub_sub_calls))  # RUNNING -> BOT_DIED

  def test_bot_terminate_canceled_task(self):
    pub_sub_calls = self.mock_pub_sub()
    run_result = self._quick_reap(1, 0, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(1, len(pub_sub_calls))  # PENDING -> RUNNING

    # cancel task
    self._cancel_running_task(run_result)
    self.assertEqual(2, len(pub_sub_calls))  # RUNNING -> killing

    # execute termination task
    err = task_scheduler.bot_terminate_task(run_result.key, 'localhost')
    self.assertEqual(None, err)

    # check result summary
    expected = self._gen_result_summary_reaped(
        abandoned_ts=self.now,
        completed_ts=self.now,
        costs_usd=[0.],
        id='1d69b9f088008910',
        internal_failure=True,
        started_ts=self.now,
        state=State.KILLED,
        duration=0.0,
        exit_code=-1,
        failure=True,
    )
    self.assertEqual(expected, run_result.result_summary_key.get().to_dict())

    # check run result
    expected = self._gen_run_result(
        abandoned_ts=self.now,
        completed_ts=self.now,
        id='1d69b9f088008911',
        internal_failure=True,
        state=State.KILLED,
        killing=False,
        duration=0.0,
        exit_code=-1,
        failure=True,
    )
    self.assertEqual(expected, run_result.key.get().to_dict())

    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(3, len(pub_sub_calls))  # killing -> KILLED

  def test_bot_terminate_task_wrong_bot(self):
    run_result = self._quick_reap(1, 0)
    expected = (
        'Bot bot1 sent task kill for task 1d69b9f088008911 owned by bot '
        'localhost')
    err = task_scheduler.bot_terminate_task(run_result.key, 'bot1')
    self.assertEqual(expected, err)

  def test_cancel_task(self):
    # Cancel a pending task.
    pub_sub_calls = self.mock_pub_sub()
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        1, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(0, len(pub_sub_calls))  # Nothing yet.

    ok, was_running = task_scheduler.cancel_task(
        result_summary.request_key.get(), result_summary.key, False, None)
    self.assertEqual(True, ok)
    self.assertEqual(False, was_running)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(1, len(pub_sub_calls))  # CANCELED

    result_summary = result_summary.key.get()
    self.assertEqual(State.CANCELED, result_summary.state)
    self.assertEqual(1, len(pub_sub_calls))  # No other message.

    # Make sure the TaskToRun is added to the negative cache.
    request = result_summary.request_key.get()
    to_run_key = task_to_run.request_to_task_to_run_key(request, 1, 0)
    actual = task_to_run._lookup_cache_is_taken_async(to_run_key).get_result()
    self.assertEqual(True, actual)

  def test_cancel_task_with_id(self):
    # Cancel a pending task.
    pub_sub_calls = self.mock_pub_sub()
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        1, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(0, len(pub_sub_calls))  # Nothing yet.

    ok, was_running = task_scheduler.cancel_task_with_id(
        result_summary.task_id, False, None)
    self.assertEqual(True, ok)
    self.assertEqual(False, was_running)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(1, len(pub_sub_calls))  # CANCELED

    result_summary = result_summary.key.get()
    self.assertEqual(State.CANCELED, result_summary.state)
    self.assertEqual(1, len(pub_sub_calls))  # No other message.

    # Make sure the TaskToRun is added to the negative cache.
    request = result_summary.request_key.get()
    to_run_key = task_to_run.request_to_task_to_run_key(request, 1, 0)
    actual = task_to_run._lookup_cache_is_taken_async(to_run_key).get_result()
    self.assertEqual(True, actual)

  def test_cancel_task_running(self):
    # Cancel a running task.
    pub_sub_calls = self.mock_pub_sub()
    run_result = self._quick_reap(1, 0, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(1, len(pub_sub_calls))  # RUNNING

    # Denied if kill_running == False.
    ok, was_running = task_scheduler.cancel_task(run_result.request_key.get(),
                                                 run_result.result_summary_key,
                                                 False, None)
    self.assertEqual(False, ok)
    self.assertEqual(True, was_running)
    self.assertEqual(0, self.execute_tasks())
    self.assertEqual(1, len(pub_sub_calls))  # No message.

    # Works if kill_running == True.
    ok, was_running = task_scheduler.cancel_task(run_result.request_key.get(),
                                                 run_result.result_summary_key,
                                                 True, None)
    self.assertEqual(True, ok)
    self.assertEqual(True, was_running)
    self.assertEqual(2, self.execute_tasks())
    self.assertEqual(2, len(pub_sub_calls))  # CANCELED

    # At this point, the task is still running and the bot is unaware.
    run_result = run_result.key.get()
    self.assertEqual(State.RUNNING, run_result.state)
    self.assertEqual(True, run_result.killing)

    # Repeatedly canceling works.
    ok, was_running = task_scheduler.cancel_task(run_result.request_key.get(),
                                                 run_result.result_summary_key,
                                                 True, None)
    self.assertEqual(True, ok)
    self.assertEqual(True, was_running)
    self.assertEqual(2, self.execute_tasks())
    self.assertEqual(3, len(pub_sub_calls))  # CANCELED (again)

    # Bot pulls once, gets the signal about killing, which starts the graceful
    # termination dance.
    self.assertEqual(State.KILLED, _bot_update_task(run_result.key))

    # At this point, it is still running, until the bot completes the task.
    run_result = run_result.key.get()
    self.assertEqual(State.RUNNING, run_result.state)
    self.assertEqual(True, run_result.killing)

    # Close the task.
    self.assertEqual(
        State.KILLED,
        _bot_update_task(
            run_result.key, output_chunk_start=3, exit_code=0, duration=0.1))

    run_result = run_result.key.get()
    self.assertEqual(False, run_result.killing)
    self.assertEqual(State.KILLED, run_result.state)
    self.assertEqual(4, len(pub_sub_calls))  # KILLED
    self.assertEqual(1, self.execute_tasks())

  def test_cancel_task_bot_id(self):
    # Cancel a running task.
    pub_sub_calls = self.mock_pub_sub()
    run_result = self._quick_reap(1, 0, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(1, len(pub_sub_calls))  # RUNNING

    # Denied if bot_id ('foo') doesn't match.
    ok, was_running = task_scheduler.cancel_task(run_result.request_key.get(),
                                                 run_result.result_summary_key,
                                                 True, 'foo')
    self.assertEqual(False, ok)
    self.assertEqual(True, was_running)
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(1, len(pub_sub_calls))  # No message.

    # Works if bot_id matches.
    ok, was_running = task_scheduler.cancel_task(run_result.request_key.get(),
                                                 run_result.result_summary_key,
                                                 True, 'localhost')
    self.assertEqual(True, ok)
    self.assertEqual(True, was_running)
    self.assertEqual(2, self.execute_tasks())
    self.assertEqual(2, len(pub_sub_calls))  # CANCELED

  def test_cancel_task_completed(self):
    # Cancel a completed task.
    pub_sub_calls = self.mock_pub_sub()
    run_result = self._quick_reap(1, 0, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(1, len(pub_sub_calls))  # RUNNING

    # The task completes successfully.
    self.assertEqual(
        State.COMPLETED,
        _bot_update_task(run_result.key, exit_code=0, duration=0.1))
    self.assertEqual(2, len(pub_sub_calls))  # COMPLETED

    # Cancel request is denied.
    ok, was_running = task_scheduler.cancel_task(run_result.request_key.get(),
                                                 run_result.result_summary_key,
                                                 False, None)
    self.assertEqual(False, ok)
    self.assertEqual(False, was_running)

    run_result = run_result.key.get()
    self.assertIsNone(run_result.killing)
    self.assertEqual(State.COMPLETED, run_result.state)
    self.assertEqual(2, len(pub_sub_calls))  # No other message.
    self.assertEqual(1, self.execute_tasks())

  def test_cancel_task_running_setup(self):
    # Cancel a assigned task before running
    pub_sub_calls = self.mock_pub_sub()
    run_result = self._quick_reap(1, 0, pubsub_topic='projects/abc/topics/def')
    self.assertEqual(1, len(pub_sub_calls))  # RUNNING

    # Request cancel
    ok, was_running = task_scheduler.cancel_task(run_result.request_key.get(),
                                                 run_result.result_summary_key,
                                                 True, None)
    self.assertEqual(True, ok)
    self.assertEqual(True, was_running)
    self.assertEqual(2, self.execute_tasks())
    self.assertEqual(2, len(pub_sub_calls))  # CANCELED

    # At this point, the task status is still running and the bot is unaware.
    run_result = run_result.key.get()
    self.assertEqual(State.RUNNING, run_result.state)
    self.assertEqual(True, run_result.killing)

    # Bot pulls once, gets the signal about killing, which starts the graceful
    # termination dance.
    self.assertEqual(State.KILLED, _bot_update_task(run_result.key))

    # At this point, the status is still running, until the bot cancels
    # the task.
    run_result = run_result.key.get()
    self.assertEqual(State.RUNNING, run_result.state)
    self.assertEqual(True, run_result.killing)

    # Close the task.
    self.assertEqual(
        State.CANCELED,
        _bot_update_task(
            run_result.key, exit_code=0, duration=0.1, canceled=True))

    run_result = run_result.key.get()
    self.assertEqual(False, run_result.killing)
    self.assertEqual(State.CANCELED, run_result.state)
    self.assertEqual(3, len(pub_sub_calls))  # CANCELED
    self.assertEqual(1, self.execute_tasks())

  def test_cron_abort_expired_task_to_run(self):
    pub_sub_calls = self.mock_pub_sub()
    self._register_bot(0, self.bot_dimensions)
    expiration_ts = self.now + datetime.timedelta(1)
    result_summary = self._quick_schedule(
        1, pubsub_topic='projects/abc/topics/def')
    expiration_ts = result_summary.request_key.get().expiration_ts
    abandoned_ts = self.mock_now(expiration_ts, 1)
    task_scheduler.cron_abort_expired_task_to_run()
    tasks = self._taskqueue_stub.GetTasks('task-expire')
    self.assertEqual(1, len(tasks))
    self.assertEqual(2, self.execute_tasks())  # +1 for a notify task execution
    self.assertEqual([], task_result.TaskRunResult.query().fetch())
    expected = self._gen_result_summary_pending(
        abandoned_ts=abandoned_ts,
        completed_ts=abandoned_ts,
        expiration_delay=1,
        id='1d69b9f088008910',
        modified_ts=abandoned_ts,
        state=State.EXPIRED)
    self.assertEqual(expected, result_summary.key.get().to_dict())
    self.assertEqual(1, len(pub_sub_calls))  # pubsub completion notification

  def test_cron_abort_expired_fallback(self):
    # 1 and 4 have capacity.
    self.bot_dimensions[u'item'] = [u'1', u'4']
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        4,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'item': [u'1']
                })),
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'item': [u'2']
                })),
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'item': [u'3']
                })),
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'item': [u'4']
                })),
        ])
    self.assertEqual(State.PENDING, result_summary.state)
    self.assertEqual(0, result_summary.current_task_slice)

    # Expire the first slice.
    self.mock_now(self.now, 601)

    # cron job 'expires' the task slices but not the whole task.
    task_scheduler.cron_abort_expired_task_to_run()
    tasks = self._taskqueue_stub.GetTasks('task-expire')
    self.assertEqual(1, len(tasks))
    self.assertEqual(1, self.execute_tasks())
    result_summary = result_summary.key.get()
    self.assertEqual(State.PENDING, result_summary.state)
    # Skipped the second and third TaskSlice.
    self.assertEqual(3, result_summary.current_task_slice)

    # The first task slice should be expired.
    request = result_summary.request_key.get()
    to_run_1 = task_to_run.request_to_task_to_run_key(request, 1, 0).get()
    self.assertEqual(to_run_1.expiration_delay, 601 - 600)

  def test_cron_abort_expired_fallback_wait_for_capacity(self):
    # 1 has capacity.
    self.bot_dimensions[u'item'] = [u'1']
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'item': [u'1']
                }),
                wait_for_capacity=False),
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'item': [u'2']
                }),
                wait_for_capacity=True),
        ])
    self.assertEqual(State.PENDING, result_summary.state)
    self.assertEqual(0, result_summary.current_task_slice)

    # Expire the first slice.
    self.mock_now(self.now, 601)
    task_scheduler.cron_abort_expired_task_to_run()
    tasks = self._taskqueue_stub.GetTasks('task-expire')
    self.assertEqual(1, len(tasks))
    self.assertEqual(1, self.execute_tasks())
    result_summary = result_summary.key.get()
    self.assertEqual(State.PENDING, result_summary.state)
    # Wait for the second TaskSlice even if there is no capacity.
    self.assertEqual(1, result_summary.current_task_slice)

  def test_cron_abort_expired_no_queue_number(self):
    pub_sub_calls = self.mock_pub_sub()
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        1, pubsub_topic='projects/abc/topics/def')
    request = result_summary.request
    abandoned_ts = self.mock_now(self.now, request.expiration_secs + 1)

    # set queue_number to None
    to_run_key = task_to_run.request_to_task_to_run_key(request, 1, 0)
    to_run = to_run_key.get()
    to_run.queue_number = None
    to_run.put()

    task_scheduler.cron_abort_expired_task_to_run()
    tasks = self._taskqueue_stub.GetTasks('task-expire')
    self.assertEqual(1, len(tasks))
    self.execute_tasks()
    self.assertEqual([], task_result.TaskRunResult.query().fetch())
    expected = self._gen_result_summary_pending(
        abandoned_ts=abandoned_ts,
        completed_ts=abandoned_ts,
        expiration_delay=1,
        id='1d69b9f088008910',
        modified_ts=abandoned_ts,
        state=State.EXPIRED)
    self.assertEqual(expected, result_summary.key.get().to_dict())
    self.assertEqual(1, len(pub_sub_calls))  # pubsub completion notification

  def test_cron_handle_bot_died(self):
    pub_sub_calls = self.mock_pub_sub()

    # This task will be marked as bot died.
    run_result = self._quick_reap(
        1,
        0,
        pubsub_topic='projects/abc/topics/def',
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=1200,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    self.assertEqual(1, len(pub_sub_calls))  # PENDING -> RUNNING
    request = run_result.request_key.get()

    def is_in_negative_cache(t):
      to_run_key = task_to_run.request_to_task_to_run_key(request, t, 0)
      return task_to_run._lookup_cache_is_taken_async(to_run_key).get_result()

    self.assertEqual(True, is_in_negative_cache(1))  # Was just reaped.
    self.assertEqual(False, is_in_negative_cache(2))

    now_0 = self.now
    now_1 = self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        1)
    self.assertEqual(([run_result.task_id], 0),
                     task_scheduler.cron_handle_bot_died())
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(2, len(pub_sub_calls))  # RUNNING -> COMPLETED
    self.assertEqual(False, is_in_negative_cache(1))
    self.assertEqual(False, is_in_negative_cache(2))

    # Refresh and compare:
    expected = self._gen_result_summary_reaped(
        abandoned_ts=now_1,
        completed_ts=now_1,
        costs_usd=[0.],
        id='1d69b9f088008910',
        internal_failure=True,
        modified_ts=now_1,
        started_ts=now_0,
        state=State.BOT_DIED,
        try_number=1)
    self.assertEqual(expected, run_result.result_summary_key.get().to_dict())
    expected = self._gen_run_result(
        abandoned_ts=now_1,
        completed_ts=now_1,
        id='1d69b9f088008911',
        internal_failure=True,
        modified_ts=now_1,
        state=State.BOT_DIED)
    self.assertEqual(expected, run_result.key.get().to_dict())

    self.assertEqual(0, self.execute_tasks())

  def test_cron_handle_bot_died_no_update_not_idempotent(self):
    # A bot reaped a task but the handler returned HTTP 500, leaving the task in
    # a lingering state.
    pub_sub_calls = self.mock_pub_sub()

    # This task will be marked as bot died.
    run_result = self._quick_reap(
        1,
        0,
        pubsub_topic='projects/abc/topics/def',
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=1200,
                properties=_gen_properties(),
                wait_for_capacity=False),
        ])
    request = run_result.request_key.get()
    self.assertEqual(1, len(pub_sub_calls))  # PENDING -> RUNNING

    now_0 = self.now

    # Bot becomes MIA.
    now_1 = self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        1)
    self.assertEqual(([run_result.task_id], 0),
                     task_scheduler.cron_handle_bot_died())
    self.assertEqual(1, self.execute_tasks())
    self.assertEqual(2, len(pub_sub_calls))  # RUNNING -> COMPLETED

    # Refresh and compare:
    expected = self._gen_result_summary_reaped(
        abandoned_ts=now_1,
        completed_ts=now_1,
        costs_usd=[0.],
        id='1d69b9f088008910',
        internal_failure=True,
        modified_ts=now_1,
        started_ts=now_0,
        state=State.BOT_DIED,
        try_number=1)
    self.assertEqual(expected, run_result.result_summary_key.get().to_dict())
    expected = self._gen_run_result(
        abandoned_ts=now_1,
        completed_ts=now_1,
        id='1d69b9f088008911',
        internal_failure=True,
        modified_ts=now_1,
        state=task_result.State.BOT_DIED)
    self.assertEqual(expected, run_result.key.get().to_dict())

    self.assertEqual(0, self.execute_tasks())

  def test_cron_handle_bot_died_broken_task(self):
    # Not sure why, but this was observed on the fleet: the TaskRequest is
    # missing from the DB. This test ensures the cron job doesn't throw in this
    # situation.
    run_result = self._quick_reap(
        1,
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(),
                wait_for_capacity=False),
        ])
    request = run_result.request_key.get()
    to_run_key = task_to_run.request_to_task_to_run_key(
        run_result.request_key.get(), 1, 0)
    now_1 = self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        1)

    # Very unusual, the TaskRequest disappeared:
    run_result.request_key.delete()

    self.assertEqual(([], 1), task_scheduler.cron_handle_bot_died())

  def test_bot_poll_http_500_but_bot_reapears_after_BOT_PING_TOLERANCE(self):
    # A bot reaped a task, sleeps for over BOT_PING_TOLERANCE (2 minutes), then
    # sends a ping.
    # In the meantime the cron job ran, saw the job idle with 0 update for more
    # than BOT_PING_TOLERANCE, make the task BOT_DIED.
    run_result = self._quick_reap(
        1,
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=6 * 60,
                properties=_gen_properties(),
                wait_for_capacity=False),
        ])
    request = run_result.request_key.get()
    to_run_key_1 = task_to_run.request_to_task_to_run_key(
        run_result.request_key.get(), 1, 0)
    self.assertIsNone(to_run_key_1.get().queue_number)
    self.assertIsNone(to_run_key_1.get().expiration_ts)

    # See _handle_dead_bot() with special case about non-idempotent task that
    # were never updated.
    self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        1)
    self.assertEqual(([to_run_key_1.get().task_id], 0),
                     task_scheduler.cron_handle_bot_died())

    # Now the task is available. Bot magically wakes up (let's say a laptop that
    # went to sleep). The update is denied.
    self.assertEqual(
        None,
        _bot_update_task(
            run_result.key,
            bot_id='localhost-second',
            exit_code=0,
            duration=0.1))
    # Confirm it is denied.
    run_result = run_result.key.get()
    self.assertEqual(State.BOT_DIED, run_result.state)
    result_summary = run_result.result_summary_key.get()
    self.assertEqual(State.BOT_DIED, result_summary.state)
    # The old TaskToRun is not reused.
    self.assertIsNone(to_run_key_1.get().queue_number)
    self.assertIsNone(to_run_key_1.get().expiration_ts)

  def test_cron_handle_bot_died_same_bot_denied(self):
    # This task will be marked as bot died.
    run_result = self._quick_reap(
        1,
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=1200,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    request = run_result.request_key.get()
    self.assertEqual(1, run_result.try_number)
    self.assertEqual(State.RUNNING, run_result.state)
    now_0 = self.now
    now_1 = self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        1)
    self.assertEqual(([run_result.task_id], 0),
                     task_scheduler.cron_handle_bot_died())

    # Refresh and compare:
    # The interesting point here is that even though the task is PENDING, it has
    # worker information from the initial BOT_DIED task.
    expected = self._gen_run_result(
        abandoned_ts=now_1,
        completed_ts=now_1,
        id='1d69b9f088008911',
        internal_failure=True,
        modified_ts=now_1,
        state=State.BOT_DIED)
    self.assertEqual(expected, run_result.key.get().to_dict())
    expected = self._gen_result_summary_pending(
        abandoned_ts=now_1,
        bot_dimensions=self.bot_dimensions.copy(),
        bot_version=u'abc',
        bot_id=u'localhost',
        completed_ts=now_1,
        costs_usd=[0.],
        id='1d69b9f088008910',
        internal_failure=True,
        modified_ts=now_1,
        started_ts=now_0,
        state=State.BOT_DIED,
        try_number=1)
    self.assertEqual(expected, run_result.result_summary_key.get().to_dict())

    # Task was retried but the same bot polls again, it's denied the task.
    now_2 = self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        2)
    request, _, run_result = task_scheduler.bot_reap_task(
        self.bot_dimensions, 'abc')
    self.assertIsNone(request)
    self.assertIsNone(run_result)

  def test_cron_handle_bot_died_ignored_expired(self):
    run_result = self._quick_reap(
        1,
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(),
                wait_for_capacity=False),
        ])
    request = run_result.request_key.get()
    self.assertEqual(1, run_result.try_number)
    self.assertEqual(State.RUNNING, run_result.state)
    self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        601)
    self.assertEqual((['1d69b9f088008911'], 0),
                     task_scheduler.cron_handle_bot_died())

  def test_cron_handle_bot_died_killing(self):
    # Test first retry, then success.
    run_result = self._quick_reap(
        1,
        0,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(idempotent=True),
                wait_for_capacity=False),
        ])
    result_summary = run_result.result_summary_key.get()
    request = run_result.request_key.get()

    # cancel running task
    self._cancel_running_task(run_result)

    # execute the cron
    self.mock_now(
        self.now + datetime.timedelta(seconds=request.bot_ping_tolerance_secs),
        601)
    self.assertEqual(([run_result.task_id], 0),
                     task_scheduler.cron_handle_bot_died())

    # state should be KILLED
    run_result = run_result.key.get()
    self.assertEqual(
        task_result.State.to_string(task_result.State.KILLED),
        task_result.State.to_string(run_result.state))

  def test_cron_handle_external_cancellations(self):
    es_address = 'externalscheduler_address'
    es_id = 'es_id'
    external_schedulers = [
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, True, True),
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, True, True),
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, False, True),
    ]
    self.mock_pool_config('es-pool', external_schedulers=external_schedulers)
    known_pools = pools_config.known()
    self.assertEqual(len(known_pools), 1)
    calls = []

    def mock_get_cancellations(es_cfg):
      calls.append(es_cfg)
      c = plugin_pb2.GetCancellationsResponse.Cancellation()
      # Note: This task key is invalid, but that helps to exercise
      # the exception handling in the handler.
      # Also, in the wild we would not be making duplicate calls with the same
      # task and bot; this is simply convenient for testing.
      c.task_id = 'task1'
      c.bot_id = 'bot1'
      return [c]

    self.mock(external_scheduler, 'get_cancellations', mock_get_cancellations)

    task_scheduler.cron_handle_external_cancellations()

    self.assertEqual(len(calls), 2)
    self.assertEqual(2, self.execute_tasks())

  def test_cron_handle_external_cancellations_none(self):
    es_address = 'externalscheduler_address'
    es_id = 'es_id'
    external_schedulers = [
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, True, True),
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, True, True),
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, False, True),
    ]
    self.mock_pool_config('es-pool', external_schedulers=external_schedulers)
    known_pools = pools_config.known()
    self.assertEqual(len(known_pools), 1)
    calls = []

    def mock_get_cancellations(es_cfg):
      calls.append(es_cfg)
      return None

    self.mock(external_scheduler, 'get_cancellations', mock_get_cancellations)

    task_scheduler.cron_handle_external_cancellations()

    self.assertEqual(len(calls), 2)
    self.assertEqual(0, self.execute_tasks())

  def test_cron_handle_get_callbacks(self):
    """Test that cron_handle_get_callbacks behaves as expected."""
    es_address = 'externalscheduler_address'
    es_id = 'es_id'
    external_schedulers = [
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, True, True),
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, True, True),
        pools_config.ExternalSchedulerConfig(es_address, es_id, None, None,
                                             None, False, True),
    ]
    self.mock_pool_config('es-pool', external_schedulers=external_schedulers)
    known_pools = pools_config.known()
    self.assertEqual(len(known_pools), 1)
    id1 = self._quick_schedule(1).task_id
    id2 = self._quick_schedule(0).task_id
    calls = []

    def mock_get_callbacks(es_cfg):
      calls.append(es_cfg)
      return [id1, id2]

    self.mock(external_scheduler, 'get_callbacks', mock_get_callbacks)

    notify_calls = self._mock_es_notify()

    task_scheduler.cron_handle_get_callbacks()

    self.assertEqual(len(calls), 2)
    self.assertEqual(len(notify_calls), 2)
    for notify_call in notify_calls:
      requests = notify_call[1]
      self.assertEqual(len(requests), 2)
      req1, _ = requests[0]
      req2, _ = requests[1]
      self.assertEqual(req1.task_id, id1)
      self.assertEqual(req2.task_id, id2)

  def mock_pool_config(self,
                       name,
                       scheduling_users=None,
                       scheduling_groups=None,
                       trusted_delegatees=None,
                       service_accounts=None,
                       service_accounts_groups=None,
                       external_schedulers=None):
    self._known_pools = self._known_pools or set()
    self._known_pools.add(name)

    def mocked_get_pool_config(pool):
      if pool == name:
        return pools_config.init_pool_config(
            name=name,
            rev='rev',
            scheduling_users=frozenset(scheduling_users or []),
            scheduling_groups=frozenset(scheduling_groups or []),
            trusted_delegatees={
                peer: pools_config.TrustedDelegatee(peer, frozenset(tags))
                for peer, tags in (trusted_delegatees or {}).items()
            },
            service_accounts=frozenset(service_accounts or []),
            service_accounts_groups=tuple(service_accounts_groups or []),
            external_schedulers=external_schedulers,
        )
      return None

    def mocked_known_pools():
      return list(self._known_pools)

    self.mock(pools_config, 'get_pool_config', mocked_get_pool_config)
    self.mock(pools_config, 'known', mocked_known_pools)

  def mock_delegation(self, peer_id, tags):
    self.mock(auth, 'get_peer_identity', lambda: peer_id)
    self.mock(
        auth,
        'get_delegation_token', lambda: delegation_pb2.Subtoken(tags=tags))

  def check_schedule_request_acl(self, properties, **kwargs):
    task_scheduler.check_schedule_request_acl(
        _gen_request_slices(
            task_slices=[
                task_request.TaskSlice(
                    expiration_secs=60,
                    properties=properties,
                    wait_for_capacity=False),
            ],
            **kwargs))

  def test_check_schedule_request_acl(self):

    # There's no "default ACL" anymore if there's no pool config.
    with self.assertRaises(auth.AuthorizationError) as ctx:
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))
    self.assertIn(
        'Can\'t submit tasks to pool "some-pool", not defined in pools.cfg',
        str(ctx.exception))

    # Service accounts are not allowed if not configured.
    with self.assertRaises(auth.AuthorizationError) as ctx:
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}),
          service_account='robot@example.com')
    self.assertIn(
        'Can\'t submit tasks to pool "some-pool", not defined in pools.cfg',
        str(ctx.exception))

  def test_check_schedule_request_acl_unknown_forbidden(self):
    self.mock_pool_config('some-other-pool')
    with self.assertRaises(auth.AuthorizationError) as ctx:
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))
    self.assertIn('not defined in pools.cfg', str(ctx.exception))

  def test_check_schedule_request_acl_forbidden(self):
    self.mock_pool_config('some-pool')
    with self.assertRaises(auth.AuthorizationError) as ctx:
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))
    self.assertIn('not allowed to schedule tasks', str(ctx.exception))

  def test_check_schedule_request_acl_allowed_explicitly(self):
    self.mock_pool_config(
        'some-pool', scheduling_users=[auth_testing.DEFAULT_MOCKED_IDENTITY])
    self.check_schedule_request_acl(
        properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))

  def test_check_schedule_request_acl_allowed_through_the_group(self):
    self.mock_pool_config('some-pool', scheduling_groups=['mocked'])

    def mocked_is_group_member(group, ident):
      return group == 'mocked' and ident == auth_testing.DEFAULT_MOCKED_IDENTITY

    self.mock(auth, 'is_group_member', mocked_is_group_member)
    self.check_schedule_request_acl(
        properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))

  def test_check_schedule_request_acl_unknown_delegation(self):
    delegatee1 = auth.Identity.from_bytes('user:d1@example.com')
    delegatee2 = auth.Identity.from_bytes('user:d2@example.com')
    self.mock_pool_config('some-pool', trusted_delegatees={delegatee1: ['t1']})
    self.mock_delegation(delegatee2, ['t1'])
    with self.assertRaises(auth.AuthorizationError):
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))

  def test_check_schedule_request_acl_delegation_ok(self):
    delegatee = auth.Identity.from_bytes('user:d1@example.com')
    self.mock_pool_config(
        'some-pool', trusted_delegatees={delegatee: ['t1', 'other']})
    self.mock_delegation(delegatee, ['t1', 'extra'])
    self.check_schedule_request_acl(
        properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))

  def test_check_schedule_request_acl_delegation_missing_tag(self):
    delegatee = auth.Identity.from_bytes('user:d1@example.com')
    self.mock_pool_config('some-pool', trusted_delegatees={delegatee: ['t1']})
    self.mock_delegation(delegatee, ['another'])
    with self.assertRaises(auth.AuthorizationError):
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))

  def test_check_schedule_request_acl_good_service_acc(self):
    self.mock_pool_config(
        'some-pool',
        scheduling_users=[auth_testing.DEFAULT_MOCKED_IDENTITY],
        service_accounts=['good@example.com'])
    self.check_schedule_request_acl(
        properties=_gen_properties(dimensions={u'pool': [u'some-pool']}),
        service_account='good@example.com')

  def test_check_schedule_request_acl_good_service_acc_through_group(self):

    def mocked_is_group_member(group, ident):
      return group == 'accounts' and ident.to_bytes() == 'user:good@example.com'

    self.mock(auth, 'is_group_member', mocked_is_group_member)

    self.mock_pool_config(
        'some-pool',
        scheduling_users=[auth_testing.DEFAULT_MOCKED_IDENTITY],
        service_accounts_groups=['accounts'])
    self.check_schedule_request_acl(
        properties=_gen_properties(dimensions={u'pool': [u'some-pool']}),
        service_account='good@example.com')

  def test_check_schedule_request_acl_bad_service_acc(self):
    self.mock_pool_config(
        'some-pool',
        scheduling_users=[auth_testing.DEFAULT_MOCKED_IDENTITY],
        service_accounts=['good@example.com'],
        service_accounts_groups=['accounts'])
    with self.assertRaises(auth.AuthorizationError) as ctx:
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}),
          service_account='bad@example.com')
    self.assertIn(
        'Is allowed_service_account or allowed_service_account_group specified '
        'in pools.cfg?', str(ctx.exception))

  def test_check_schedule_request_acl_caller(self):
    # the functionality is already  tested by
    # test_check_schedule_request_acl_*.
    pass

  def test_check_schedule_request_acl_service_account(self):
    # the functionality is already  tested by
    # test_check_schedule_request_acl_*.
    pass

  def test_check_schedule_request_wildcard_acl_delegation_ok(self):
    delegatee = auth.Identity.from_bytes('user:d1@example.com')
    self.mock_pool_config(
        'some-pool', trusted_delegatees={delegatee: ['t1/*', 'other']})
    self.mock_delegation(delegatee, ['t1/foo', 'extra'])
    self.check_schedule_request_acl(
        properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))

  def test_check_schedule_request_wildcard_acl_delegation_missing_tag(self):
    delegatee = auth.Identity.from_bytes('user:d1@example.com')
    self.mock_pool_config(
        'some-pool', trusted_delegatees={delegatee: ['t1', 'other/*']})
    self.mock_delegation(delegatee, ['t1/foo', 'extra'])
    with self.assertRaises(auth.AuthorizationError):
      self.check_schedule_request_acl(
          properties=_gen_properties(dimensions={u'pool': [u'some-pool']}))

  def test_cron_task_bot_distribution(self):
    # TODO(maruel): https://crbug.com/912154
    self.assertEqual(0, task_scheduler.cron_task_bot_distribution())

  def test_ensure_active_slice_nonpending(self):
    # Non-PENDING task cannot have active slice set.
    r = self._quick_schedule(1)
    self.assertEqual(
        task_scheduler._ensure_active_slice(r.request, 1), (None, False))

  def test_ensure_active_slice_pending(self):
    # Pending task can be forced between different active slices via
    # _ensure_active_slice.
    r = self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'foo': [u'bar']
                }),
                wait_for_capacity=True),
            task_request.TaskSlice(
                expiration_secs=60,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'foo': [u'qux']
                }),
                wait_for_capacity=True),
        ],
    )

    to_run, _ = task_scheduler._ensure_active_slice(r.request, 0)
    self.assertEqual(to_run.task_slice_index, 0)
    to_run, _ = task_scheduler._ensure_active_slice(r.request, 1)
    self.assertEqual(to_run.task_slice_index, 1)
    to_run, _ = task_scheduler._ensure_active_slice(r.request, 0)
    self.assertEqual(to_run.task_slice_index, 0)
    # This works even if there is no to_run entity.
    to_run.key.delete()
    to_run, _ = task_scheduler._ensure_active_slice(r.request, 1)
    self.assertEqual(to_run.task_slice_index, 1)

  def test_task_expire_tasks(self):
    # Tested indirectly via test_cron_abort_expired_*
    pass

  def test_task_expire_with_invalid_slice_index(self):
    self._register_bot(0, self.bot_dimensions)
    result_summary = self._quick_schedule(
        2,
        task_slices=[
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={u'pool': [u'default']})),
            task_request.TaskSlice(
                expiration_secs=600,
                properties=_gen_properties(dimensions={
                    u'pool': [u'default'],
                    u'foo': [u'bar']
                })),
        ])
    # activate a non-current slice forcebly.
    invalid_slice_index = 1
    task_scheduler._ensure_active_slice(result_summary.request,
                                        invalid_slice_index)
    self.assertEqual(State.PENDING, result_summary.state)
    self.assertEqual(0, result_summary.current_task_slice)

    # task_expire_tasks should expire the task.
    try_number = 1
    to_runs = [(result_summary.task_id, try_number, invalid_slice_index)]
    task_scheduler.task_expire_tasks(to_runs)
    self.assertEqual(State.EXPIRED, result_summary.key.get().state)

  def test_task_cancel_running_children_tasks(self):
    # Tested indirectly via test_bot_update_child_with_cancelled_parent.
    pass

  def test_task_append_child(self):
    # Tested indirectly via test_task_parent_*, test_task_invalid_parent
    pass


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
