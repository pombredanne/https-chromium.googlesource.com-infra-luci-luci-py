# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This module defines Swarming Server frontend pRPC handlers."""

from components import prpc
from components.prpc.codes import StatusCode

from components import datastore_utils
from proto import swarming_prpc_pb2  # pylint: disable=no-name-in-module
from proto import swarming_pb2  # pylint: disable=no-name-in-module
from server import bot_management


class BotAPIService(object):
  """Service implements the pRPC service in swarming.proto."""

  DESCRIPTION = swarming_prpc_pb2.BotAPIServiceDescription

  # TODO(maruel): Add implementation. https://crbug.com/913953

  def Events(self, request, context):
    try:
      if not request.bot_id:
        raise ValueError('specify bot_id')
      page_size = request.page_size or 200
      if not 1 <= page_size <= 1000:
        raise ValueError('page_size must be between 1 and 1000')
      start = request.start_time.ToDatetime()
      end = request.end_time.ToDatetime()
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
    except ValueError as e:
      context.set_code(StatusCode.INVALID_ARGUMENT)
      context.set_details(str(e))
      return None
    out = swarming_pb2.BotEventsResponse(next_page_token=cursor)
    for r in items:
      i = out.items.add()
      r.to_proto(i)
    return out


def get_routes():
  s = prpc.Server()
  s.add_service(BotAPIService())
  return s.get_routes()
