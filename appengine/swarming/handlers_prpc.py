# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This module defines Swarming Server frontend pRPC handlers."""
import datetime

from components import prpc
from components import auth
import proto.api_v2.swarming_prpc_pb2 as swarming_prpc_pb2
import proto.api_v2.swarming_pb2 as swarming_pb2
from server import realms
from server import acl
import api_common
import message_conversion_prpc
import prpc_helpers
import handlers_exceptions


def _is_empty_date(dt):
  """prpc does not support setting optional fields for python.
  We check whether the datetime value is the default date (therefore unset)."""
  return dt == datetime.datetime(1970, 1, 1, 0, 0)


def _format_query(query):
  """pRPC api uses QUERY_<SOMEQUERY> for TaskQuery and TaskState values.
  The protorpc api expects them to be <somequery>.
  For example:
  prpc=QUERY_ALL while protorpc=all
  """
  return query[6:].lower()


class BotsService(object):
  DESCRIPTION = swarming_prpc_pb2.BotsServiceDescription

  @prpc_helpers.method
  @auth.require(acl.can_access, log_identity=True)
  def GetBot(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_get_acl(bot_id)
    bot, deleted = api_common.get_bot(bot_id)
    return message_conversion_prpc.bot_info_to_proto(bot, deleted)

  @prpc_helpers.method
  @auth.require(acl.can_access, log_identity=True)
  def DeleteBot(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_delete_acl(bot_id)
    api_common.delete_bot(bot_id)
    return swarming_pb2.DeleteResponse(deleted=True)

  @prpc_helpers.method
  @auth.require(acl.can_access, log_identity=True)
  def ListBotEvents(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_get_acl(bot_id)
    try:
      start = request.start.ToDatetime()
      end = request.end.ToDatetime()
      limit = request.limit
      cursor = request.cursor
      items, cursor = api_common.get_bot_events(bot_id, start, end, limit,
                                                cursor)
    except ValueError as e:
      raise handlers_exceptions.BadRequestException(
          'Inappropriate filter for bot.events: %s' % e)
    return message_conversion_prpc.bot_events_response(items, cursor)

  @prpc_helpers.method
  @auth.require(acl.can_access, log_identity=True)
  def TerminateBot(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_terminate_acl(bot_id)
    task_id = api_common.terminate_bot(bot_id)
    return swarming_pb2.TerminateResponse(task_id=task_id)

  @prpc_helpers.method
  @auth.require(acl.can_access, log_identity=True)
  def ListBotTasks(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_terminate_acl(bot_id)
    start = request.start.ToDatetime()
    if _is_empty_date(start):
      start = None
    end = request.end.ToDatetime()
    if _is_empty_date(end):
      end = None
    sort = _format_query(swarming_pb2.SortQuery.Name(request.sort))
    state = _format_query(swarming_pb2.StateQuery.Name(request.state))
    limit = request.limit
    cursor = request.cursor
    try:
      items, cursor = api_common.list_bot_tasks(bot_id, start, end, sort, state,
                                                cursor, limit)
    except ValueError as e:
      raise handlers_exceptions.BadRequestException(
          "Inappropriate filter bot tasks %s" % e)
    return message_conversion_prpc.bot_tasks_response(items, cursor)


class TasksService:
  DESCRIPTION = swarming_prpc_pb2.TasksServiceDescription


class SwarmingService:
  DESCRIPTION = swarming_prpc_pb2.SwarmingServiceDescription


def get_routes():
  s = prpc.Server()
  s.add_service(BotsService())
  s.add_interceptor(auth.prpc_interceptor)
  return s.get_routes()
