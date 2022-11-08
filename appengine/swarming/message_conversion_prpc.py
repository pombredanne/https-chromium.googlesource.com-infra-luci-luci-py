# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import json

from proto.api import swarming_api_pb2
from server import task_result
from server import task_request
from server import task_pack


class ProtoFactory(object):
  def __init__(self, proto):
    self._proto = proto

  def _get_proto(self, field_name):
    return getattr(self._proto, field_name)

  def collection(self, proto_field, items, conversion_fn=None):
    field = self._get_proto(proto_field)
    if conversion_fn:
      field.extend([conversion_fn(item) for item in items])
    else:
      field.extend(item for item in items)
    return self

  def to_proto(self):
    return self._proto


class ObjectDerivedProtoFactory(ProtoFactory):
  def __init__(self, obj, proto):
    super(ObjectDerivedProtoFactory, self).__init__(proto)
    self._obj = obj

  def _get(self, field_name, required=False):
    if hasattr(self._obj, field_name):
      value = getattr(self._obj, field_name)
      if value is None and required:
        raise ValueError("Required field %s is null")
      return value
    if required:
      raise ValueError("Required field %s not present in object" % field_name)

  def field(self,
            field_name,
            proto_field=None,
            conversion_fn=None,
            required=False):
    proto_field = proto_field or field_name
    value = self._get(field_name, required)
    if value:
      if conversion_fn:
        value = conversion_fn(value)
      setattr(self._proto, proto_field, value)
    return self

  def fields(self, *field_names):
    for field_name in field_names:
      self.field(field_name)
    return self

  def date(self, field_name, proto_field=None, required=False):
    proto_field = proto_field or field_name
    field = self._get_proto(proto_field)
    date = self._get(field_name, required)
    if date:
      field.FromDatetime(date)
    return self

  def dates(self, *dates):
    for date_field in dates:
      self.date(date_field)
    return self

  def string_list_pairs(self, field_name, proto_field=None, required=False):
    proto_field = self._get_proto(proto_field or field_name)
    obj_field = self._get(field_name, required)
    _string_list_pairs_from_dict(obj_field or {}, proto_field)
    return self

  def message_field(self, field_name, factory_fn, required=False):
    obj_field = self._get(field_name, required)
    proto_field = self._get_proto(field_name)
    if obj_field is not None:
      factory = ObjectDerivedProtoFactory(obj_field, proto_field)
      factory_fn(factory)
    return self

  def repeated_field(self, field_name, factory_fn=None, required=False):
    self.collection(field_name,
                    self._get(field_name, required) or [], factory_fn)
    return self

  def repeated_message_field(self, field_name, factory_fn, required=False):
    proto_field = self._get_proto(field_name)
    obj_field = self._get(field_name, required)
    if obj_field is not None:
      for item in obj_field:
        proto_entry = proto_field.Add()
        factory = ObjectDerivedProtoFactory(item, proto_entry)
        factory_fn(factory)
    return self


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


def bot_info_to_proto(bot_info, deleted=False):
  """Converts a ndb BotInfo object into a BotInfoResponse for pRPC api
  """
  factory = ObjectDerivedProtoFactory(
      bot_info, swarming_api_pb2.BotInfoResponse()).fields(
          'external_ip', 'authenticated_as', 'is_dead', 'quarantined',
          'maintenance_msg', 'task_id', 'task_name', 'version')
  factory.dates('first_seen_ts', 'last_seen_ts')
  factory.field('state',
                conversion_fn=lambda state: json.dumps(
                    state or {}, sort_keys=True, separators=(',', ':')))
  factory.field('id', proto_field='bot_id')
  factory.string_list_pairs('dimensions')
  out = factory.to_proto()
  out.deleted = deleted
  return out


def _bot_event_response(event):
  """Converts a ndb BotEvent entity to a BotEvent response of pRPC"""
  # must have a value because ts is indexed on
  assert event.ts
  out = ObjectDerivedProtoFactory(event, swarming_api_pb2.BotEventResponse())
  out.date('ts')
  out.fields('event_type', 'message', 'external_ip', 'authenticated_as',
             'version', 'quarantined', 'maintenance_msg', 'task_id')
  out.string_list_pairs('dimensions')
  out.field('state',
            conversion_fn=lambda state: json.dumps(
                state or {}, sort_keys=True, separators=(',', ':')))
  return out.to_proto()


def bot_events_response(items, cursor):
  out = swarming_api_pb2.BotEventsResponse()
  out.items.extend([_bot_event_response(event) for event in items])
  out.cursor = cursor or ''
  out.now.GetCurrentTime()
  return out


def _perf_stats(out):
  out.field('bot_overhead')

  def _cas_op_stats(out):
    out.fields('duration', 'initial_number_items', 'initial_size', 'items_cold',
               'items_hot', 'num_items_cold', 'num_items_hot',
               'total_bytes_items_hot', 'total_bytes_items_cold')

  def _op_stats(out):
    out.field('duration')

  out.message_field('isolated_download', _cas_op_stats, required=False)
  out.message_field('isolated_upload', _cas_op_stats, required=False)
  out.message_field('package_installation', _op_stats, required=False)
  out.message_field('cache_trim', _op_stats, required=False)
  out.message_field('named_caches_uninstall', _op_stats, required=False)
  out.message_field('named_caches_install', _op_stats, required=False)
  out.message_field('cleanup', _op_stats, required=False)


def _cas_reference(out):
  out.field('cas_instance')
  out.message_field(
      'digest', lambda digest: digest.fields('hash', 'size_bytes'))


def _cipd_package(out):
  out.fields('package_name', 'version', 'path')


def _cipd_pins(out):
  out.message_field('client_package', _cipd_package)


def _result_db_info(out):
  out.fields('hostname', 'invocation')


def task_result_response(result):
  factory = ObjectDerivedProtoFactory(result,
                                      swarming_api_pb2.TaskResultResponse())
  factory.fields('bot_id', 'bot_version', 'bot_logs_cloud_project',
                 'deduped_from', 'duration', 'exit_code', 'failure',
                 'internal_failure', 'state', 'task_id', 'name',
                 'current_task_slice', 'user', 'run_id', 'costs_saved_usd')
  factory.dates('completed_ts', 'bot_idle_since_ts', 'abandoned_ts',
                'modified_ts', 'started_ts', 'created_ts')
  factory.string_list_pairs('bot_dimensions')
  factory.repeated_field('children_task_ids')
  factory.repeated_field('server_versions')
  factory.repeated_field('tags')
  factory.message_field('performance_stats', _perf_stats)
  factory.message_field('cas_output_root', _cas_reference)
  factory.repeated_message_field('missing_cas', _cas_reference)
  factory.repeated_message_field('missing_cipd', _cipd_package)

  out = factory.to_proto()
  if result.__class__ is task_result.TaskRunResult:
    if result.cost_usd is not None:
      out.costs_usd.extend([result.cost_usd])
    if result.task_id:
      out.run_id = result.task_id
  else:
    assert result.__class__ is task_result.TaskResultSummary, result
    k = result.run_result_key
    run_id = task_pack.pack_run_result_key(k) if k else None
    if run_id:
      out.run_id = run_id
  return out

def bot_tasks_response(items, cursor):
  out = swarming_api_pb2.TaskListResponse()
  out.cursor = cursor or ''
  out.items.extend([task_result_response(item) for item in items])
  out.now.GetCurrentTime()
  return out
