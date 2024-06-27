# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Main entry point for Swarming backend handlers."""

import datetime
import json
import logging

import webapp2
from google.appengine.api import datastore_errors
from google.appengine.ext import ndb
from google.appengine import runtime

from google.protobuf import json_format

from proto.plugin import plugin_pb2

from components import decorators
from components import datastore_utils
from components import utils
from server import bot_groups_config
from server import bot_management
from server import config
from server import external_scheduler
from server import named_caches
from server import task_queues
from server import task_request
from server import task_result
from server import task_scheduler
import ts_mon_metrics


class WarmupHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.write('ok')


## Cron jobs.


class _CronHandlerBase(webapp2.RequestHandler):
  @decorators.require_cronjob
  def get(self):
    self.run_cron()

  def run_cron(self):
    raise NotImplementedError()


class CronBotDiedHandler(_CronHandlerBase):
  """Sets running tasks where the bot is not sending ping updates for several
  minutes as BOT_DIED.
  """

  def run_cron(self):
    task_scheduler.cron_handle_bot_died()


class CronAbortExpiredShardToRunHandler(_CronHandlerBase):
  """Set tasks that haven't started before their expiration_ts timestamp as
  EXPIRED.

  Most of the tasks will be expired 'inline' as bots churn through the queue,
  but tasks where the bots are not polling will be expired by this cron job.
  """

  def run_cron(self):
    task_scheduler.cron_abort_expired_task_to_run()


class CronTidyTaskDimensionSets(_CronHandlerBase):
  """Removes expired task dimension sets from the datastore."""

  def run_cron(self):
    f = task_queues.tidy_task_dimension_sets_async()
    if not f.get_result():
      self.response.set_status(429, 'Need to retry')


class CronUpdateBotInfoComposite(_CronHandlerBase):
  """Updates BotInfo.composite if needed, e.g. the bot became dead because it
  hasn't pinged for a while.
  """

  def run_cron(self):
    bot_management.cron_update_bot_info()


class CronDeleteOldBots(_CronHandlerBase):
  """Deletes old BotRoot entity groups."""

  def run_cron(self):
    bot_management.cron_delete_old_bot()


class CronDeleteOldBotEvents(_CronHandlerBase):
  """Deletes old BotEvent entities."""

  def run_cron(self):
    bot_management.cron_delete_old_bot_events()


class CronDeleteOldTasks(_CronHandlerBase):
  """Deletes old TaskRequest entities and all their decendants."""

  def run_cron(self):
    task_request.cron_delete_old_task_requests()


class CronNamedCachesUpdate(_CronHandlerBase):
  """Updates named caches hints."""

  def run_cron(self):
    named_caches.cron_update_named_caches()

class CronBotsDimensionAggregationHandler(_CronHandlerBase):
  """Aggregates all bots dimensions (except id) in the fleet."""

  def run_cron(self):
    bot_management.cron_aggregate_dimensions()


class CronBotGroupsConfigHandler(_CronHandlerBase):
  """Fetches bots.cfg with all includes, assembles the final config."""

  def run_cron(self):
    try:
      bot_groups_config.refetch_from_config_service()
    except bot_groups_config.BadConfigError:
      pass


class CronExternalSchedulerCancellationsHandler(_CronHandlerBase):
  """Fetches cancelled tasks from external schedulers, and cancels them."""

  def run_cron(self):
    task_scheduler.cron_handle_external_cancellations()


class CronExternalSchedulerGetCallbacksHandler(_CronHandlerBase):
  """Fetches callbacks requests from external schedulers, and notifies them."""

  def run_cron(self):
    task_scheduler.cron_handle_get_callbacks()


## Task queues.


class TaskCancelTasksHandler(webapp2.RequestHandler):
  """Cancels tasks given a list of their ids."""

  @decorators.silence(datastore_utils.CommitError)
  @decorators.require_taskqueue('cancel-tasks')
  def post(self):
    payload = json.loads(self.request.body)
    logging.info('Cancelling tasks with ids: %s', payload['tasks'])
    kill_running = payload['kill_running']
    # TODO(maruel): Parallelize.
    for task_id in payload['tasks']:
      ok, was_running = task_scheduler.cancel_task_with_id(
          task_id, kill_running, None)
      logging.info('task %s canceled: %s was running: %s',
                   task_id, ok, was_running)


class TaskCancelTaskOnBotHandler(webapp2.RequestHandler):
  """Cancels a given task if it is running on the given bot.

  If bot is not specified, cancel task unconditionally.
  If bot is specified, and task is not running on bot, then do nothing.
  """

  @decorators.require_taskqueue('cancel-task-on-bot')
  def post(self):
    payload = json.loads(self.request.body)
    task_id = payload.get('task_id')
    if not task_id:
      logging.error('Missing task_id.')
      return
    bot_id = payload.get('bot_id')
    try:
      ok, was_running = task_scheduler.cancel_task_with_id(
          task_id, True, bot_id)
      logging.info('task %s canceled: %s was running: %s',
                   task_id, ok, was_running)
    except ValueError:
      # Ignore errors that may be due to missing or invalid tasks.
      logging.warning('Ignoring a task cancellation due to exception.',
          exc_info=True)


class TaskCancelChildrenTasksHandler(webapp2.RequestHandler):
  """Cancels children tasks with pending state of the given task."""

  @decorators.silence(runtime.DeadlineExceededError)
  @decorators.require_taskqueue('cancel-children-tasks')
  def post(self):
    payload = json.loads(self.request.body)
    task = payload['task']
    logging.info('Cancelling children tasks of task %s', task)

    task_scheduler.task_cancel_running_children_tasks(task)


class TaskExpireTasksHandler(webapp2.RequestHandler):
  """Expires a list of tasks, given a list of their ids."""

  @decorators.require_taskqueue('task-expire')
  def post(self):
    payload = json.loads(self.request.body)
    task_scheduler.task_expire_tasks(payload['entities'])


class TaskDeleteTasksHandler(webapp2.RequestHandler):
  """Deletes a list of tasks, given a list of their ids."""

  @decorators.require_taskqueue('delete-tasks')
  def post(self):
    payload = json.loads(self.request.body)
    task_request.task_delete_tasks(payload['task_ids'])


class TaskUpdateBotMatchesHandler(webapp2.RequestHandler):
  """Assigns new task queues to existing bots."""

  @decorators.require_taskqueue('update-bot-matches')
  def post(self):
    f = task_queues.update_bot_matches_async(self.request.body)
    if not f.get_result():
      self.response.set_status(429, 'Need to retry')


class TaskRescanMatchingTaskSetsHandler(webapp2.RequestHandler):
  """A task queue task that finds all matching TaskDimensionsSets for a bot."""

  @decorators.require_taskqueue('rescan-matching-task-sets')
  def post(self):
    f = task_queues.rescan_matching_task_sets_async(self.request.body)
    if not f.get_result():
      self.response.set_status(429, 'Need to retry')


class TaskSendPubSubMessage(webapp2.RequestHandler):
  """Sends PubSub notification about task completion."""

  # Add task_id to the URL for better visibility in request logs.
  @decorators.require_taskqueue('pubsub')
  def post(self, task_id):  # pylint: disable=unused-argument
    task_scheduler.task_handle_pubsub_task(json.loads(self.request.body))


class TaskNotifyBuildbucketHandler(webapp2.RequestHandler):
  """Sends updates to Buildbucket about task status."""

  @decorators.require_taskqueue('buildbucket-notify')
  def post(self, task_id):  # pylint: disable=unused-argument
    task_scheduler.task_buildbucket_update(json.loads(self.request.body))


class TaskESNotifyTasksHandler(webapp2.RequestHandler):
  """Sends task notifications to external scheduler."""

  @decorators.require_taskqueue('es-notify-tasks')
  def post(self):
    es_host = self.request.get('es_host')
    request_json = self.request.get('request_json')
    request = plugin_pb2.NotifyTasksRequest()
    json_format.Parse(request_json, request)
    external_scheduler.notify_request_now(es_host, request)


class TaskESNotifyKickHandler(webapp2.RequestHandler):
  """Kicks off the pull queue worker to batch the es-notifications."""

  @decorators.require_taskqueue('es-notify-kick')
  def post(self):
    external_scheduler.task_batch_handle_notifications()


class TaskNamedCachesPool(webapp2.RequestHandler):
  """Update named caches cache for a pool."""

  @decorators.silence(datastore_errors.Timeout)
  @decorators.require_taskqueue('named-cache-task')
  def post(self):
    params = json.loads(self.request.body)
    logging.info('Handling pool: %s', params['pool'])
    named_caches.task_update_pool(params['pool'])


###


def get_routes():
  """Returns internal urls that should only be accessible via the backend."""
  routes = [
      ('/_ah/warmup', WarmupHandler),

      # Cron jobs.
      ('/internal/cron/important/scheduler/abort_bot_missing',
       CronBotDiedHandler),
      ('/internal/cron/important/scheduler/abort_expired',
       CronAbortExpiredShardToRunHandler),
      ('/internal/cron/cleanup/task_dimension_sets', CronTidyTaskDimensionSets),
      ('/internal/cron/monitoring/bots/update_bot_info',
       CronUpdateBotInfoComposite),
      ('/internal/cron/cleanup/bots/delete_old', CronDeleteOldBots),
      ('/internal/cron/cleanup/bots/delete_old_bot_events',
       CronDeleteOldBotEvents),
      ('/internal/cron/cleanup/tasks/delete_old', CronDeleteOldTasks),
      ('/internal/cron/monitoring/bots/aggregate_dimensions',
       CronBotsDimensionAggregationHandler),
      ('/internal/cron/important/bot_groups_config',
       CronBotGroupsConfigHandler),
      ('/internal/cron/important/external_scheduler/cancellations',
       CronExternalSchedulerCancellationsHandler),
      ('/internal/cron/important/external_scheduler/get_callbacks',
       CronExternalSchedulerGetCallbacksHandler),
      ('/internal/cron/important/named_caches/update', CronNamedCachesUpdate),

      # Task queues.
      ('/internal/taskqueue/important/tasks/cancel', TaskCancelTasksHandler),
      ('/internal/taskqueue/important/tasks/cancel-task-on-bot',
       TaskCancelTaskOnBotHandler),
      ('/internal/taskqueue/important/tasks/cancel-children-tasks',
       TaskCancelChildrenTasksHandler),
      ('/internal/taskqueue/important/tasks/expire', TaskExpireTasksHandler),
      ('/internal/taskqueue/cleanup/tasks/delete', TaskDeleteTasksHandler),
      ('/internal/taskqueue/important/task_queues/update-bot-matches',
       TaskUpdateBotMatchesHandler),
      ('/internal/taskqueue/important/task_queues/rescan-matching-task-sets',
       TaskRescanMatchingTaskSetsHandler),
      (r'/internal/taskqueue/important/pubsub/notify-task/<task_id:[0-9a-f]+>',
       TaskSendPubSubMessage),
      (r'/internal/taskqueue/important/buildbucket/notify-task/'
       r'<task_id:[0-9a-f]+>', TaskNotifyBuildbucketHandler),
      ('/internal/taskqueue/important/external_scheduler/notify-tasks',
       TaskESNotifyTasksHandler),
      ('/internal/taskqueue/important/external_scheduler/notify-kick',
       TaskESNotifyKickHandler),
      (r'/internal/taskqueue/important/named_cache/update-pool',
       TaskNamedCachesPool),
  ]
  return [webapp2.Route(*a) for a in routes]


def create_application(debug):
  return webapp2.WSGIApplication(get_routes(), debug=debug)
