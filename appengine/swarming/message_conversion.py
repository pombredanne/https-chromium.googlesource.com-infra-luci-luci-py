# Copyright 2015 The Swarming Authors. All rights reserved.
# Use of this source code is governed by the Apache v2.0 license that can be
# found in the LICENSE file.

"""This module facilitates conversion from dictionaries to ProtoRPC messages.

Given a dictionary whose keys' names and values' types comport with the
fields defined for a protorpc.messages.Message subclass, this module tries to
generate a Message instance that corresponds to the provided dictionary. The
"normal" use case is for ndb.Models which need to be represented as a
ProtoRPC.
"""

import datetime
import functools
import logging
import re

import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

import swarming_rpcs

from components import utils
from server import task_request
from server import task_result


def _string_pairs_from_dict(dictionary):
  return [
    swarming_rpcs.StringPair(key=k, value=v)
    for k, v in sorted(dictionary.iteritems())
  ]


def _string_list_pairs_from_dict(dictionary):
  return [
    swarming_rpcs.StringListPair(key=k, value=v)
    for k, v in sorted(dictionary.iteritems())
  ]


def _ndb_to_rpc(cls, entity, **overrides):
  members = (f.name for f in cls.all_fields())
  kwargs = {m: getattr(entity, m) for m in members if not m in overrides}
  kwargs.update(overrides)
  return cls(**{k: v for k, v in kwargs.iteritems() if v is not None})


def _rpc_to_ndb(cls, entity, **overrides):
  kwargs = {
    m: getattr(entity, m) for m in cls._properties if not m in overrides
  }
  kwargs.update(overrides)
  return cls(**{k: v for k, v in kwargs.iteritems() if v is not None})


def bot_info_to_rpc(entity, now):
  """"Returns a swarming_rpcs.BotInfo from a bot.BotInfo."""
  return _ndb_to_rpc(
      swarming_rpcs.BotInfo,
      entity,
      dimensions=_string_list_pairs_from_dict(entity.dimensions),
      is_dead=entity.is_dead(now),
      bot_id=entity.id)


def task_request_to_rpc(entity):
  """"Returns a swarming_rpcs.TaskRequest from a task_request.TaskRequest."""
  assert entity.__class__ is task_request.TaskRequest
  inputs_ref = None
  if entity.properties.inputs_ref:
    inputs_ref = _ndb_to_rpc(
        swarming_rpcs.FilesRef, entity.properties.inputs_ref)
  props = entity.properties
  # Work around bugs in the entities.
  # TODO(maruel): Run a map reduce to remove these entities.
  extra_args = props.extra_args or []
  if extra_args == [None]:
    extra_args = []
  properties = _ndb_to_rpc(
      swarming_rpcs.TaskProperties,
      props,
      command=(props.commands or [[]])[0],
      dimensions=_string_pairs_from_dict(props.dimensions),
      extra_args=extra_args,
      env=_string_pairs_from_dict(props.env),
      inputs_ref=inputs_ref)

  return _ndb_to_rpc(
      swarming_rpcs.TaskRequest,
      entity,
      authenticated=entity.authenticated.to_bytes(),
      properties=properties)


def new_task_request_from_rpc(msg, now):
  """"Returns a task_request.TaskRequest from a swarming_rpcs.NewTaskRequest."""
  assert msg.__class__ is swarming_rpcs.NewTaskRequest
  if not msg.properties:
    raise ValueError('properties is required')
  inputs_ref = None
  if msg.properties.inputs_ref:
    inputs_ref = _rpc_to_ndb(task_request.FilesRef, msg.properties.inputs_ref)
  props = msg.properties
  if not props:
    raise ValueError('properties is required')
  properties = _rpc_to_ndb(
      task_request.TaskProperties,
      props,
      commands=[props.command] if props.command else [],
      data=[],
      dimensions={i.key: i.value for i in props.dimensions},
      env={i.key: i.value for i in props.env},
      inputs_ref=inputs_ref)

  return _rpc_to_ndb(
      task_request.TaskRequest,
      msg,
      created_ts=now,
      expiration_ts=now+datetime.timedelta(seconds=msg.expiration_secs),
      # It is set in task_request.make_request().
      authenticated=None,
      properties=properties)


def task_result_to_rpc(entity):
  """"Returns a swarming_rpcs.TaskResult from a task_result.TaskResultSummary or
  task_result.TaskRunResult.
  """
  kwargs = {
    'bot_dimensions': _string_list_pairs_from_dict(entity.bot_dimensions or {}),
    'duration': (entity.durations or [None])[0],
    'exit_code': (entity.exit_codes or [None])[0],
    'state': swarming_rpcs.StateField(entity.state),
  }
  if entity.__class__ is task_result.TaskRunResult:
    kwargs['costs_usd'] = []
    if entity.cost_usd is not None:
      kwargs['costs_usd'].append(entity.cost_usd)
    kwargs['properties_hash'] = None
    kwargs['tags'] = []
    kwargs['user'] = None
  else:
    assert entity.__class__ is task_result.TaskResultSummary, entity
    kwargs['properties_hash'] = (
        entity.properties_hash.encode('hex')
        if entity.properties_hash else None)
  return _ndb_to_rpc(swarming_rpcs.TaskResult, entity, **kwargs)
