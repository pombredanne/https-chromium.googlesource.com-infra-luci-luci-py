# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This module defines Swarming Server frontend pRPC handlers."""

import logging

from google.appengine.api import datastore_errors
from google.appengine.ext import ndb
from google.protobuf import empty_pb2

from components import auth
from components import cipd
from components import datastore_utils
from components import prpc
from components.prpc.codes import StatusCode

import api_helpers
import backend_conversions
import handlers_exceptions
import prpc_helpers

from proto.api.internal.bb import backend_prpc_pb2
from proto.api.internal.bb import backend_pb2
from proto.api import swarming_prpc_pb2  # pylint: disable=no-name-in-module
from proto.api import swarming_pb2  # pylint: disable=no-name-in-module
from server import acl
from server import bot_management
from server import task_pack
from server import task_request
from server import task_result
from server import task_scheduler
from server import task_result


class TaskBackendAPIService(prpc_helpers.SwarmingPRPCService):
  """Service implements the pRPC service in backend.proto."""

  DESCRIPTION = backend_prpc_pb2.TaskBackendServiceDescription

  @prpc_helpers.PRPCMethod
  @auth.require(
      acl.can_create_task, 'User cannot create tasks.', log_identity=True)
  def RunTask(self, request, _context):
    # type: (backend_pb2.RunTaskRequest, context.ServicerContext)
    #     -> empty_pb2.Empty

    tr, secret_bytes, build_token = backend_conversions.compute_task_request(
        request)

    api_helpers.process_task_request(tr, task_request.TEMPLATE_AUTO)

    def _schedule_request():
      try:
        return task_scheduler.schedule_request(
            tr, secret_bytes=secret_bytes, build_token=build_token)
      except (TypeError, ValueError) as e:
        raise handlers_exceptions.BadRequestException(e.message)

    result, is_deduped = api_helpers.cache_request('backend_run_task',
                                                   request.request_id,
                                                   _schedule_request)
    if is_deduped:
      logging.info('Reusing task %s with uuid %s', result.task_id,
                   request.request_id)

    return empty_pb2.Empty()

  @prpc_helpers.PRPCMethod
  @auth.require(acl.can_access, log_identity=True)
  def CancelTasks(self, request, _context):
    # type: (backend_pb2.CancelTasksRequest, context.ServicerContext)
    #     -> backend_pb2.CancelTasksResponse

    # TODO(crbug/1236848): Check cancel permissions for pools:
    # `realms.check_tasks_cancel_acl(pools)`
    task_ids = [task_id.id for task_id in request.task_ids]
    task_result_keys = [task_pack.get_request_and_result_keys(task_id)[1]
                        for task_id in task_ids]

    # TODO(crbug/1236848): Fetch limits and/or return cursor from the request.
    filter_node = task_result.TaskResultSummary.key.IN(task_result_keys)
    task_scheduler.cancel_tasks(
        100, condition=filter_node, kill_running=True)

    # CancelTasksResponse should return ALL tasks in `request.task_ids`
    # not just the tasks that are actually getting cancelled.
    task_results = task_result.fetch_task_results(task_ids)

    return backend_pb2.CancelTasksResponse(
        tasks=backend_conversions.convert_results_to_tasks(
            task_results, task_ids))


  @prpc_helpers.PRPCMethod
  def FetchTasks(self, request, _context):
    # type: (backend_pb2.FetchTasksRequest, context.ServicerContext)
    #     -> backend_pb2.FetchTaskResponse

    # TODO(crbug/1236848): Check user can view each task.

    requested_task_ids = [task_id.id for task_id in request.task_ids]
    task_results = task_result.fetch_task_results(requested_task_ids)

    return backend_pb2.FetchTasksResponse(
        tasks=backend_conversions.convert_results_to_tasks(
            task_results, requested_task_ids))

  @prpc_helpers.PRPCMethod
  def ValidateConfigs(self, request, _context):
    # type: (backend_pb2.ValidateConfigsRequest, context.ServicerContext)
    #     -> backend_pb2.ValidateConfigsResponse

    configs = [backend_conversions.ingest_backend_config(config.config_json) for
               config in request.configs]
    errors = []  # type: Tuple[int, str]
    for i, config in enumerate(configs):
      if (config.priority < 1 or
          task_request.MAXIMUM_PRIORITY < config.priority):
        errors.append((i, '`priority` must be between 1 and %s' % (
            task_request.MAXIMUM_PRIORITY)))

      if (config.bot_ping_tolerance < task_request.MIN_BOT_PING_TOLERANCE_SECS
          or
          task_request.MAX_BOT_PING_TOLERANCE_SECS < config.bot_ping_tolerance):
        errors.append((i, '`bot_ping_tolerance` must be between %s and %s' % (
            task_request.MIN_BOT_PING_TOLERANCE_SECS,
            task_request.MAX_BOT_PING_TOLERANCE_SECS)))

      if config.service_account and (
          config.service_account not in ('bot', 'none') or not
          service_accounts_utils.is_service_account(config.service_account)):
        errors.append(
            (i, '`service_account` must be an email, "bot" or "none" string'))

      if config.parent_run_id:
        try:
          task_pack.unpack_run_result_key(config.parent_run_id)
        except ValueError as e:
          errors.append((i, e.message))

      if (not config.agent_binary_cipd_pkg or
          not cipd.is_valid_package_name_template(
              config.agent_binary_cipd_pkg)):
        errors.append((i, 'invalid `agent_binary_cipd_pkg`'))
      if (not config.agent_binary_cipd_vers or
          not cipd.is_valid_version(config.agent_binary_cipd_vers)):
        errors.append((i, 'invalid `agent_binary_cipd_vers`'))
      if not config.agent_binary_cipd_filename:
        errors.append((i, 'missing `agent_binary_cipd_filename`'))


    return backend_pb2.ValidateConfigsResponse(
        config_errors=[
            backend_pb2.ValidateConfigsResponse.ErrorDetail(
                index=i, error=error)
            for (i, error) in errors])


class BotAPIService(object):
  """Service implements the pRPC service in swarming.proto."""

  DESCRIPTION = swarming_prpc_pb2.BotAPIServiceDescription

  # TODO(maruel): Add implementation. https://crbug.com/913953

  def Events(self, request, context):
    logging.debug('%s', request)
    try:
      if not request.bot_id:
        # TODO(maruel): Allows not specifying one. Or specifying a pool.
        raise ValueError('specify bot_id')

      # Transparently limit to 1000, default to 200.
      page_size = request.page_size or 200
      if page_size > 1000:
        page_size = 1000
      if page_size < 0:
        raise ValueError('page_size must be positive')

      start = None
      end = None
      if request.HasField('start_time'):
        start = request.start_time.ToDatetime()
      if request.HasField('end_time'):
        end = request.end_time.ToDatetime()
      if (start and end) and start >= end:
        raise ValueError('start_time must be before end_time')

      # The BotEvent key is already in the right chronological order, but
      # querying per BotEvent.ts *requires* ordering per BotEvent.ts.
      order = not (start or end)
      q = bot_management.get_events_query(request.bot_id, order)
      if not order:
        q = q.order(-bot_management.BotEvent.ts, bot_management.BotEvent.key)
      if start:
        q = q.filter(bot_management.BotEvent.ts >= start)
      if end:
        q = q.filter(bot_management.BotEvent.ts < end)

      items, cursor = datastore_utils.fetch_page(
          q, page_size, request.page_token)
      if not items:
        # Check if the bot exists, if not, return a 404. We check BotRoot, not
        # BotInfo, so that even deleted bots can be queried. See bot_management
        # for more information.
        if not bot_management.get_root_key(request.bot_id).get():
          context.set_code(StatusCode.NOT_FOUND)
          context.set_details('Bot does not exist')
          return None
    except ValueError as e:
      context.set_code(StatusCode.INVALID_ARGUMENT)
      context.set_details(str(e))
      return None
    logging.info('Returning %d events', len(items))
    out = swarming_pb2.BotEventsResponse(next_page_token=cursor)
    for r in items:
      i = out.events.add()
      r.to_proto(i)
    return out


def get_routes():
  s = prpc.Server()
  s.add_service(BotAPIService())
  # TODO(crbug/1236848): add
  # s.add_service(TaskBackendAPIService())
  # s.add_interceptor(auth.prpc_interceptor)
  return s.get_routes()
