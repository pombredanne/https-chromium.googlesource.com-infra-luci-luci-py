# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/buildbucket/proto/task.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import struct_pb2 as google_dot_protobuf_dot_struct__pb2
from bb.go.chromium.org.luci.buildbucket.proto import common_pb2 as go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2
from bb.go.chromium.org.luci.buildbucket.proto import field_option_pb2 as go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_field__option__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/buildbucket/proto/task.proto',
  package='buildbucket.v2',
  syntax='proto3',
  serialized_options=b'Z4go.chromium.org/luci/buildbucket/proto;buildbucketpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n1go.chromium.org/luci/buildbucket/proto/task.proto\x12\x0e\x62uildbucket.v2\x1a\x1cgoogle/protobuf/struct.proto\x1a\x33go.chromium.org/luci/buildbucket/proto/common.proto\x1a\x39go.chromium.org/luci/buildbucket/proto/field_option.proto\"\x82\x02\n\x04Task\x12*\n\x02id\x18\x01 \x01(\x0b\x32\x16.buildbucket.v2.TaskIDB\x06\x92\xc3\x1a\x02\x08\x02\x12\x0c\n\x04link\x18\x02 \x01(\t\x12.\n\x06status\x18\x03 \x01(\x0e\x32\x16.buildbucket.v2.StatusB\x06\x92\xc3\x1a\x02\x08\x02\x12\x35\n\x0estatus_details\x18\x04 \x01(\x0b\x32\x1d.buildbucket.v2.StatusDetails\x12\x14\n\x0csummary_html\x18\x05 \x01(\t\x12(\n\x07\x64\x65tails\x18\x06 \x01(\x0b\x32\x17.google.protobuf.Struct\x12\x19\n\tupdate_id\x18\x07 \x01(\x03\x42\x06\x92\xc3\x1a\x02\x08\x02\":\n\x06TaskID\x12\x1c\n\x06target\x18\x01 \x01(\tB\x0c\x8a\xc3\x1a\x02\x08\x02\x92\xc3\x1a\x02\x08\x02\x12\x12\n\x02id\x18\x02 \x01(\tB\x06\x92\xc3\x1a\x02\x08\x02\"G\n\x0f\x42uildTaskUpdate\x12\x10\n\x08\x62uild_id\x18\x01 \x01(\t\x12\"\n\x04task\x18\x02 \x01(\x0b\x32\x14.buildbucket.v2.TaskB6Z4go.chromium.org/luci/buildbucket/proto;buildbucketpbb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_struct__pb2.DESCRIPTOR,go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2.DESCRIPTOR,go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_field__option__pb2.DESCRIPTOR,])




_TASK = _descriptor.Descriptor(
  name='Task',
  full_name='buildbucket.v2.Task',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='buildbucket.v2.Task.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\222\303\032\002\010\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='link', full_name='buildbucket.v2.Task.link', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='buildbucket.v2.Task.status', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\222\303\032\002\010\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status_details', full_name='buildbucket.v2.Task.status_details', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='summary_html', full_name='buildbucket.v2.Task.summary_html', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='details', full_name='buildbucket.v2.Task.details', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='update_id', full_name='buildbucket.v2.Task.update_id', index=6,
      number=7, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\222\303\032\002\010\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=212,
  serialized_end=470,
)


_TASKID = _descriptor.Descriptor(
  name='TaskID',
  full_name='buildbucket.v2.TaskID',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='target', full_name='buildbucket.v2.TaskID.target', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\212\303\032\002\010\002\222\303\032\002\010\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='id', full_name='buildbucket.v2.TaskID.id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\222\303\032\002\010\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=472,
  serialized_end=530,
)


_BUILDTASKUPDATE = _descriptor.Descriptor(
  name='BuildTaskUpdate',
  full_name='buildbucket.v2.BuildTaskUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='build_id', full_name='buildbucket.v2.BuildTaskUpdate.build_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='task', full_name='buildbucket.v2.BuildTaskUpdate.task', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=532,
  serialized_end=603,
)

_TASK.fields_by_name['id'].message_type = _TASKID
_TASK.fields_by_name['status'].enum_type = go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2._STATUS
_TASK.fields_by_name['status_details'].message_type = go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2._STATUSDETAILS
_TASK.fields_by_name['details'].message_type = google_dot_protobuf_dot_struct__pb2._STRUCT
_BUILDTASKUPDATE.fields_by_name['task'].message_type = _TASK
DESCRIPTOR.message_types_by_name['Task'] = _TASK
DESCRIPTOR.message_types_by_name['TaskID'] = _TASKID
DESCRIPTOR.message_types_by_name['BuildTaskUpdate'] = _BUILDTASKUPDATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Task = _reflection.GeneratedProtocolMessageType('Task', (_message.Message,), {
  'DESCRIPTOR' : _TASK,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.task_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.Task)
  })
_sym_db.RegisterMessage(Task)

TaskID = _reflection.GeneratedProtocolMessageType('TaskID', (_message.Message,), {
  'DESCRIPTOR' : _TASKID,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.task_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.TaskID)
  })
_sym_db.RegisterMessage(TaskID)

BuildTaskUpdate = _reflection.GeneratedProtocolMessageType('BuildTaskUpdate', (_message.Message,), {
  'DESCRIPTOR' : _BUILDTASKUPDATE,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.task_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.BuildTaskUpdate)
  })
_sym_db.RegisterMessage(BuildTaskUpdate)


DESCRIPTOR._options = None
_TASK.fields_by_name['id']._options = None
_TASK.fields_by_name['status']._options = None
_TASK.fields_by_name['update_id']._options = None
_TASKID.fields_by_name['target']._options = None
_TASKID.fields_by_name['id']._options = None
# @@protoc_insertion_point(module_scope)
