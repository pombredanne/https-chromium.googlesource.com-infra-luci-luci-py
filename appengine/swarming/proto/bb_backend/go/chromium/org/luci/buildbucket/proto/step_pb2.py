# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/buildbucket/proto/step.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from go.chromium.org.luci.buildbucket.proto import common_pb2 as go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/buildbucket/proto/step.proto',
  package='buildbucket.v2',
  syntax='proto3',
  serialized_options=b'Z4go.chromium.org/luci/buildbucket/proto;buildbucketpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n1go.chromium.org/luci/buildbucket/proto/step.proto\x12\x0e\x62uildbucket.v2\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x33go.chromium.org/luci/buildbucket/proto/common.proto\"\xd7\x01\n\x04Step\x12\x0c\n\x04name\x18\x01 \x01(\t\x12.\n\nstart_time\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12,\n\x08\x65nd_time\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12&\n\x06status\x18\x04 \x01(\x0e\x32\x16.buildbucket.v2.Status\x12!\n\x04logs\x18\x05 \x03(\x0b\x32\x13.buildbucket.v2.Log\x12\x18\n\x10summary_markdown\x18\x07 \x01(\tB6Z4go.chromium.org/luci/buildbucket/proto;buildbucketpbb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2.DESCRIPTOR,])




_STEP = _descriptor.Descriptor(
  name='Step',
  full_name='buildbucket.v2.Step',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='buildbucket.v2.Step.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='start_time', full_name='buildbucket.v2.Step.start_time', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='end_time', full_name='buildbucket.v2.Step.end_time', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='status', full_name='buildbucket.v2.Step.status', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='logs', full_name='buildbucket.v2.Step.logs', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='summary_markdown', full_name='buildbucket.v2.Step.summary_markdown', index=5,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
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
  serialized_start=156,
  serialized_end=371,
)

_STEP.fields_by_name['start_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_STEP.fields_by_name['end_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_STEP.fields_by_name['status'].enum_type = go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2._STATUS
_STEP.fields_by_name['logs'].message_type = go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_common__pb2._LOG
DESCRIPTOR.message_types_by_name['Step'] = _STEP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Step = _reflection.GeneratedProtocolMessageType('Step', (_message.Message,), {
  'DESCRIPTOR' : _STEP,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.step_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.Step)
  })
_sym_db.RegisterMessage(Step)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
