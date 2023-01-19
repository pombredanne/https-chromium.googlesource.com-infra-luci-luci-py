# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This module defines Swarming Server frontend pRPC handlers."""

from components import prpc
from components import auth

# pylint: disable=no-name-in-module
import proto.api_v2.swarming_prpc_pb2 as swarming_prpc
# pylint: disable=no-name-in-module
import proto.api_v2.swarming_pb2 as swarming

from server import realms

from server import acl

import api_common
import message_conversion_prpc
import prpc_helpers
import handlers_exceptions


class BotsService(prpc_helpers.SwarmingPRPCService):
  DESCRIPTION = swarming_prpc.BotsServiceDescription

  @prpc_helpers.prpc_method
  @auth.require(acl.can_access, log_identity=True)
  def GetBot(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_get_acl(bot_id)
    bot, deleted = api_common.get_bot(bot_id)
    if not bot:
      raise handlers_exceptions.NotFoundException("bot not found")

    return message_conversion_prpc.bot_info_to_proto(bot, deleted)

  @prpc_helpers.prpc_method
  @auth.require(acl.can_access, log_identity=True)
  def DeleteBot(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_delete_acl(bot_id)
    api_common.delete_bot(bot_id)
    return swarming.DeleteResponse(deleted=True)

  @prpc_helpers.prpc_method
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

  @prpc_helpers.prpc_method
  @auth.require(acl.can_access, log_identity=True)
  def TerminateBot(self, request, _context):
    bot_id = request.bot_id
    realms.check_bot_terminate_acl(bot_id)
    task_id = api_common.terminate_bot(bot_id)
    return swarming.TerminateResponse(task_id=task_id)

  @prpc_helpers.prpc_method
  def ListBotTasks(self, request, _context):
    pass


class TasksService:
  DESCRIPTION = swarming_prpc.TasksServiceDescription


class SwarmingService:
  DESCRIPTION = swarming_prpc.SwarmingServiceDescription


def get_routes():
  s = prpc.Server()
  s.add_service(BotsService())
  return s.get_routes()
