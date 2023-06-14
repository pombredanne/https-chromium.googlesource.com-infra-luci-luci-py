# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/buildbucket/proto/field_option.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2
from google.api import field_behavior_pb2 as google_dot_api_dot_field__behavior__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/buildbucket/proto/field_option.proto',
  package='buildbucket.v2',
  syntax='proto3',
  serialized_options=b'Z4go.chromium.org/luci/buildbucket/proto;buildbucketpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n9go.chromium.org/luci/buildbucket/proto/field_option.proto\x12\x0e\x62uildbucket.v2\x1a google/protobuf/descriptor.proto\x1a\x1fgoogle/api/field_behavior.proto\"K\n\x16\x43reateBuildFieldOption\x12\x31\n\x0e\x66ield_behavior\x18\x01 \x01(\x0e\x32\x19.google.api.FieldBehavior\"Q\n\x1cRegisterBuildTaskFieldOption\x12\x31\n\x0e\x66ield_behavior\x18\x01 \x01(\x0e\x32\x19.google.api.FieldBehavior:j\n\x19\x63reate_build_field_option\x12\x1d.google.protobuf.FieldOptions\x18\xb1\xa8\x03 \x01(\x0b\x32&.buildbucket.v2.CreateBuildFieldOption:w\n register_build_task_field_option\x12\x1d.google.protobuf.FieldOptions\x18\xb2\xa8\x03 \x01(\x0b\x32,.buildbucket.v2.RegisterBuildTaskFieldOption:8\n\x0frequired_by_rpc\x12\x1d.google.protobuf.FieldOptions\x18\xb3\xa8\x03 \x03(\tB6Z4go.chromium.org/luci/buildbucket/proto;buildbucketpbb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_descriptor__pb2.DESCRIPTOR,google_dot_api_dot_field__behavior__pb2.DESCRIPTOR,])


CREATE_BUILD_FIELD_OPTION_FIELD_NUMBER = 54321
create_build_field_option = _descriptor.FieldDescriptor(
  name='create_build_field_option', full_name='buildbucket.v2.create_build_field_option', index=0,
  number=54321, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key)
REGISTER_BUILD_TASK_FIELD_OPTION_FIELD_NUMBER = 54322
register_build_task_field_option = _descriptor.FieldDescriptor(
  name='register_build_task_field_option', full_name='buildbucket.v2.register_build_task_field_option', index=1,
  number=54322, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key)
REQUIRED_BY_RPC_FIELD_NUMBER = 54323
required_by_rpc = _descriptor.FieldDescriptor(
  name='required_by_rpc', full_name='buildbucket.v2.required_by_rpc', index=2,
  number=54323, type=9, cpp_type=9, label=3,
  has_default_value=False, default_value=[],
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key)


_CREATEBUILDFIELDOPTION = _descriptor.Descriptor(
  name='CreateBuildFieldOption',
  full_name='buildbucket.v2.CreateBuildFieldOption',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='field_behavior', full_name='buildbucket.v2.CreateBuildFieldOption.field_behavior', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=144,
  serialized_end=219,
)


_REGISTERBUILDTASKFIELDOPTION = _descriptor.Descriptor(
  name='RegisterBuildTaskFieldOption',
  full_name='buildbucket.v2.RegisterBuildTaskFieldOption',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='field_behavior', full_name='buildbucket.v2.RegisterBuildTaskFieldOption.field_behavior', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=221,
  serialized_end=302,
)

_CREATEBUILDFIELDOPTION.fields_by_name['field_behavior'].enum_type = google_dot_api_dot_field__behavior__pb2._FIELDBEHAVIOR
_REGISTERBUILDTASKFIELDOPTION.fields_by_name['field_behavior'].enum_type = google_dot_api_dot_field__behavior__pb2._FIELDBEHAVIOR
DESCRIPTOR.message_types_by_name['CreateBuildFieldOption'] = _CREATEBUILDFIELDOPTION
DESCRIPTOR.message_types_by_name['RegisterBuildTaskFieldOption'] = _REGISTERBUILDTASKFIELDOPTION
DESCRIPTOR.extensions_by_name['create_build_field_option'] = create_build_field_option
DESCRIPTOR.extensions_by_name['register_build_task_field_option'] = register_build_task_field_option
DESCRIPTOR.extensions_by_name['required_by_rpc'] = required_by_rpc
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CreateBuildFieldOption = _reflection.GeneratedProtocolMessageType('CreateBuildFieldOption', (_message.Message,), {
  'DESCRIPTOR' : _CREATEBUILDFIELDOPTION,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.field_option_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.CreateBuildFieldOption)
  })
_sym_db.RegisterMessage(CreateBuildFieldOption)

RegisterBuildTaskFieldOption = _reflection.GeneratedProtocolMessageType('RegisterBuildTaskFieldOption', (_message.Message,), {
  'DESCRIPTOR' : _REGISTERBUILDTASKFIELDOPTION,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.field_option_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.RegisterBuildTaskFieldOption)
  })
_sym_db.RegisterMessage(RegisterBuildTaskFieldOption)

create_build_field_option.message_type = _CREATEBUILDFIELDOPTION
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(create_build_field_option)
register_build_task_field_option.message_type = _REGISTERBUILDTASKFIELDOPTION
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(register_build_task_field_option)
google_dot_protobuf_dot_descriptor__pb2.FieldOptions.RegisterExtension(required_by_rpc)

DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
