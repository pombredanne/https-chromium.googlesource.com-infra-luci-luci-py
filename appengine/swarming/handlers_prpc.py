# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This module defines Swarming Server frontend pRPC handlers."""

import logging

from google.appengine.api import datastore_errors
from google.appengine.datastore import datastore_query
from google.appengine.ext import ndb
from google.protobuf import empty_pb2

from components import prpc
from components.prpc.codes import StatusCode
from components import auth
from components import datastore_utils

from proto.api.internal.bb import backend_prpc_pb2
from proto.api.internal.bb import backend_pb2
from proto.api import swarming_api_prpc_pb2  # pylint: disable=no-name-in-module
from proto.api import swarming_api_pb2  # pylint: disable=no-name-in-module

from server import bot_management

from server import acl

import api_common
import message_conversion
import message_conversion_prpc
import handlers_exceptions
import prpc_helpers


class BotService(prpc_helpers.SwarmingPRPCService):
  DESCRIPTION = swarming_api_prpc_pb2.BotServiceServiceDescription

  @prpc_helpers.prpc_method
  @auth.require(acl.can_access, log_identity=True)
  def GetBot(self, request, context):
    bot_id = request.bot_id

    bot, deleted = api_common.get_bot(bot_id)
    if not bot:
      raise handlers_exceptions.NotFoundException("bot not found")

    return message_conversion_prpc.bot_info_to_proto(bot, deleted)

  @prpc_helpers.prpc_method
  @auth.require(acl.can_access, log_identity=True)
  def DeleteBot(self, request, context):
    bot_id = request.bot_id
    api_common.delete_bot(bot_id)
    return swarming_api_pb2.DeletedResponse(deleted=True)

  @prpc_helpers.prpc_method
  @auth.require(acl.can_access, log_identity=True)
  def ListBotEvents(self, request, context):
    try:
      start = request.start.ToDatetime()
      end = request.end.ToDatetime()
      limit = request.limit
      cursor = request.cursor
      bot_id = request.bot_id
      items, cursor = api_common.get_bot_events(bot_id, start, end, limit,
                                                cursor)
    except ValueError as e:
      raise handlers_exceptions.BadRequestException(
          'Inappropriate filter for bot.events: %s' % e)
    return message_conversion_prpc.bot_events_response(items, cursor)

  @prpc_helpers.prpc_method
  @auth.require(acl.can_access, log_identity=True)
  def TerminateBot(self, request, context):
    bot_id = request.bot_id
    task_id = api_common.terminate_bot(bot_id)
    return swarming_api_pb2.TerminateResponse(task_id=task_id)

  @prpc_helpers.prpc_method
  def ListBotTasks(self, request, context):
    pass


class TaskService:
  DESCRIPTION = swarming_api_prpc_pb2.TaskServiceServiceDescription


class TasksService:
  DESCRIPTION = swarming_api_prpc_pb2.TasksServiceServiceDescription


class ServerService:
  DESCRIPTION = swarming_api_prpc_pb2.ServerServiceServiceDescription


def get_routes():
  s = prpc.Server()
  s.add_service(BotService())
  # s.add_interceptor(auth.prpc_interceptor)
  return s.get_routes()
