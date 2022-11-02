# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import json

from proto.api import swarming_api_pb2


def _string_pairs_from_dict(dictionary):
  # For key: value items like env.
  return [
      swarming_api_pb2.StringPair(key=k, value=v)
      for k, v in sorted((dictionary or {}).items())
  ]


def _duplicate_string_pairs_from_dict(dictionary):
  # For compatibility due to legacy swarming_rpcs.TaskProperties.dimensions.
  out = []
  for k, values in (dictionary or {}).items():
    assert isinstance(values, (list, tuple)), dictionary
    for v in values:
      out.append(swarming_api_pb2.StringPair(key=k, value=v))
  return out


def _string_list_pairs_from_dict(dictionary, string_list_pairs):
  # For key: values items like bot dimensions.
  string_list_pairs.extend([
      swarming_api_pb2.StringListPair(key=k, value=v)
      for k, v in sorted((dictionary or {}).items())
  ])
  for k, v in sorted((dictionary or {}).items()):
    pass


def bot_info_to_proto(bot_info, deleted=False):
  """Converts a ndb BotInfo object into a BotInfoResponse for pRPC api
  """
  out = swarming_api_pb2.BotInfoResponse()
  out.bot_id = bot_info.id
  _string_list_pairs_from_dict(bot_info.dimensions, out.dimensions)
  out.external_ip = bot_info.external_ip or ''
  out.authenticated_as = bot_info.authenticated_as or ''
  if bot_info.first_seen_ts:
    out.first_seen_ts.FromDatetime(bot_info.first_seen_ts)
  out.is_dead = bot_info.is_dead
  if bot_info.last_seen_ts:
    out.last_seen_ts.FromDatetime(bot_info.last_seen_ts)
  out.quarantined = bot_info.quarantined
  out.maintenance_msg = bot_info.maintenance_msg or ''
  out.task_id = bot_info.task_id or ''
  out.task_name = bot_info.task_name or ''
  out.version = bot_info.version or ''
  out.state = json.dumps(bot_info.state or {},
                         sort_keys=True,
                         separators=(',', ':'))
  out.deleted = deleted
  return out


def _bot_event_response(event):
  """Converts a ndb BotEvent entity to a BotEvent response of pRPC"""
  out = swarming_api_pb2.BotEventResponse()
  # must have a value because ts is indexed on
  assert event.ts
  out.ts.FromDatetime(event.ts)
  out.event_type = event.event_type
  out.message = event.message or ''
  out.state = json.dumps(event.state or {},
                         sort_keys=True,
                         separators=(',', ':'))
  out.external_ip = event.external_ip or ''
  out.authenticated_as = event.authenticated_as or ''
  out.version = event.version or ''
  out.quarantined = event.quarantined
  out.maintenance_msg = event.maintenance_msg or ''
  out.task_id = event.task_id or ''
  _string_list_pairs_from_dict(event.dimensions or {}, out.dimensions)
  return out


def bot_events_response(items, cursor):
  out = swarming_api_pb2.BotEventsResponse()
  out.items.extend([_bot_event_response(event) for event in items])
  out.cursor = cursor or ''
  out.now.GetCurrentTime()
  return out
