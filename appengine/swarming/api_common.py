# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Contains code which is common between bot the prpc API and the protorpc api.
"""
from google.appengine.api import datastore_errors

import endpoints
from google.appengine.ext import ndb

from components import datastore_utils
from server import task_queues
from server import bot_management
from server import realms
from server import task_scheduler
from server import task_request
from server import task_pack
from server import task_result


def _get_or_raise(key):
  """Returns an entity or raises an endpoints exception if it does not exist."""
  result = key.get()
  if not result:
    raise endpoints.NotFoundException('%s not found.' % key.id())
  return result


def get_bot(bot_id):
  """Retrieves a bot for a given bot_id

  Returns:
    (bot_info, deleted)

  bot_info is a `bot_management.BotInfo` ndb entity.

  If a `BotInfo` entity is not found, events associated with the bot_id are
  queried.
  If an event is associated with a `bot_id`, `bot_info` is created from that
  event and returned. `deleted` will be set to True only in this circumstance.
  Otherwise it will be set to False.

  Expects that caller will perform realm check.
  """
  bot = bot_management.get_info_key(bot_id).get()
  deleted = False

  if not bot:
    # If there is not BotInfo, look if there are BotEvent child of this
    # entity. If this is the case, it means the bot was deleted but it's
    # useful to show information about it to the user even if the bot was
    # deleted.
    events = bot_management.get_events_query(bot_id).fetch(1)
    if events:
      bot = bot_management.BotInfo(
          key=bot_management.get_info_key(bot_id),
          dimensions_flat=task_queues.bot_dimensions_to_flat(
              events[0].dimensions),
          state=events[0].state,
          external_ip=events[0].external_ip,
          authenticated_as=events[0].authenticated_as,
          version=events[0].version,
          quarantined=events[0].quarantined,
          maintenance_msg=events[0].maintenance_msg,
          task_id=events[0].task_id,
          last_seen_ts=events[0].ts)
      # message_conversion.bot_info_to_rpc calls `is_dead` and this property
      # require `composite` to be calculated. The calculation is done in
      # _pre_put_hook usually. But the BotInfo shouldn't be stored in this case,
      # as it's already deleted.
      bot.composite = bot._calc_composite()
      deleted = True

  return (bot, deleted)


def delete_bot(bot_id):
  """Deletes the bot corresponding to a provided bot_id.

  At that point, the bot will not appears in the list of bots but it is still
  possible to get information about the bot with its bot id is known, as
  historical data is not deleted.

  It is meant to remove from the DB the presence of a bot that was retired,
  e.g. the VM was shut down already. Use 'terminate' instead of the bot is
  still alive.

  Expects that caller will perform realm check.
  """

  bot_info_key = bot_management.get_info_key(bot_id)
  _get_or_raise(bot_info_key)  # raises 404 if there is no such bot
  # It is important to note that the bot is not there anymore, so it is not
  # a member of any task queue.
  task_queues.cleanup_after_bot(bot_id)
  bot_info_key.delete()


def get_bot_events(bot_id, start, end, limit, cursor):
  """Retrieves a list of `bot_management.BotEvent` within a specific time range.

  Returns:
  (items, cursor) where items is a list of BotEvent entities and a cursor to
  next group of results.

  Expects that caller will perform realm check.
  """
  q = bot_management.get_events_query(bot_id)
  if start:
    q = q.filter(bot_management.BotEvent.ts >= start)
  if end:
    q = q.filter(bot_management.BotEvent.ts < end)
  items, cursor = datastore_utils.fetch_page(q, limit, cursor)
  return items, cursor


def terminate_bot(bot_id):
  """Terminates a bot with a given bot_id. Will raise a `BadRequestException`
  if something goes wrong when creating the termination task.

  Returns:
  `task_id` of the task to terminate the bot.

  Expects that caller will perform realm check.
  """
  bot_key = bot_management.get_info_key(bot_id)
  _get_or_raise(bot_key)  # raises 404 if there is no such bot
  try:
    # Craft a special priority 0 task to tell the bot to shutdown.
    request = task_request.create_termination_task(bot_id,
                                                   wait_for_capacity=True)
  except (datastore_errors.BadValueError, TypeError, ValueError) as e:
    raise handlers_exceptions.BadRequestException(e.message)

  result_summary = task_scheduler.schedule_request(request,
                                                   enable_resultdb=False)
  return task_pack.pack_result_summary_key(result_summary.key)


def list_bot_tasks(bot_id, start, end, sort, state, cursor, limit):
  sort = sort.lower()
  state = state.lower()
  q = task_result.get_run_results_query(start, end, sort, state, bot_id)
  items, cursor = datastore_utils.fetch_page(q, limit, cursor)
  return items, cursor


def to_keys(task_id):
  """Returns request and result keys, handling failure."""
  try:
    return task_pack.get_request_and_result_keys(task_id)
  except ValueError:
    raise endpoints.BadRequestException('%s is an invalid key.' % task_id)


# Used by _get_task_request_async(), clearer than using True/False and important
# as this is part of the security boundary.
CANCEL = object()
VIEW = object()


@ndb.tasklet
def get_task_request_async(task_id, request_key, viewing):
  """Returns the TaskRequest corresponding to a task ID.

  Enforces the ACL for users. Allows bots all access for the moment.

  Returns:
    TaskRequest instance.
  """
  request = yield request_key.get_async()
  if not request:
    raise endpoints.NotFoundException('%s not found.' % task_id)
  if viewing == VIEW:
    realms.check_task_get_acl(request)
  elif viewing == CANCEL:
    realms.check_task_cancel_acl(request)
  else:
    raise endpoints.InternalServerErrorException('_get_task_request_async()')
  raise ndb.Return(request)


def get_request_and_result(task_id, viewing, trust_memcache):
  """Returns the TaskRequest and task result corresponding to a task ID.

  For the task result, first do an explict lookup of the caches, and then decide
  if it is necessary to fetch from the DB.

  Arguments:
    task_id: task ID as provided by the user.
    viewing: one of _CANCEL or _VIEW
    trust_memcache: bool to state if memcache should be trusted for running
        task. If False, when a task is still pending/running, do a DB fetch.

  Returns:
    tuple(TaskRequest, result): result can be either for a TaskRunResult or a
                                TaskResultSummay.
  """
  request_key, result_key = to_keys(task_id)
  # The task result has a very high odd of taking much more time to fetch than
  # the TaskRequest, albeit it is the TaskRequest that enforces ACL. Do the task
  # result fetch first, the worst that will happen is unnecessarily fetching the
  # task result.
  result_future = result_key.get_async(use_cache=True,
                                       use_memcache=True,
                                       use_datastore=False)

  # The TaskRequest has P(99.9%) chance of being fetched from memcache since it
  # is immutable.
  request_future = get_task_request_async(task_id, request_key, viewing)

  result = result_future.get_result()
  if (not result or (result.state in task_result.State.STATES_RUNNING
                     and not trust_memcache)):
    # Either the entity is not in cache, or we don't trust memcache for a
    # running task result. Do the DB fetch, which is slow.
    result = result_key.get(use_cache=False,
                            use_memcache=False,
                            use_datastore=True)

  request = request_future.get_result()

  if not result:
    raise endpoints.NotFoundException('%s not found.' % task_id)
  return request, result


def cancel_task(task_id, kill_running):
  request_key, result_key = to_keys(task_id)
  request_obj = get_task_request_async(task_id, request_key,
                                       CANCEL).get_result()
  return task_scheduler.cancel_task(request_obj, result_key, kill_running
                                    or False, None)


def get_output(task_id, offset, length):
  """Returns the output of the task corresponding to a task ID."""
  _, result = get_request_and_result(task_id, VIEW, True)
  output = result.get_output(offset or 0, length)
  if output:
    # That was an error, don't do that in pRPC:
    output = output.decode('utf-8', 'replace')
  return output, result.state
