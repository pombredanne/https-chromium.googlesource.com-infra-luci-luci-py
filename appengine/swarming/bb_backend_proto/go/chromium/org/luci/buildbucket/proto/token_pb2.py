# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/buildbucket/proto/token.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/buildbucket/proto/token.proto',
  package='buildbucket.v2',
  syntax='proto3',
  serialized_options=b'Z4go.chromium.org/luci/buildbucket/proto;buildbucketpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n2go.chromium.org/luci/buildbucket/proto/token.proto\x12\x0e\x62uildbucket.v2\"\x99\x01\n\tTokenBody\x12\x10\n\x08\x62uild_id\x18\x01 \x01(\x03\x12\x32\n\x07purpose\x18\x02 \x01(\x0e\x32!.buildbucket.v2.TokenBody.Purpose\x12\r\n\x05state\x18\x03 \x01(\x0c\"7\n\x07Purpose\x12\x17\n\x13PURPOSE_UNSPECIFIED\x10\x00\x12\t\n\x05\x42UILD\x10\x01\x12\x08\n\x04TASK\x10\x02\"\x9b\x01\n\rTokenEnvelope\x12\x36\n\x07version\x18\x01 \x01(\x0e\x32%.buildbucket.v2.TokenEnvelope.Version\x12\x0f\n\x07payload\x18\x02 \x01(\x0c\"A\n\x07Version\x12\x17\n\x13VERSION_UNSPECIFIED\x10\x00\x12\x1d\n\x19UNENCRYPTED_PASSWORD_LIKE\x10\x01\x42\x36Z4go.chromium.org/luci/buildbucket/proto;buildbucketpbb\x06proto3'
)



_TOKENBODY_PURPOSE = _descriptor.EnumDescriptor(
  name='Purpose',
  full_name='buildbucket.v2.TokenBody.Purpose',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PURPOSE_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='BUILD', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TASK', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=169,
  serialized_end=224,
)
_sym_db.RegisterEnumDescriptor(_TOKENBODY_PURPOSE)

_TOKENENVELOPE_VERSION = _descriptor.EnumDescriptor(
  name='Version',
  full_name='buildbucket.v2.TokenEnvelope.Version',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='VERSION_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='UNENCRYPTED_PASSWORD_LIKE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=317,
  serialized_end=382,
)
_sym_db.RegisterEnumDescriptor(_TOKENENVELOPE_VERSION)


_TOKENBODY = _descriptor.Descriptor(
  name='TokenBody',
  full_name='buildbucket.v2.TokenBody',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='build_id', full_name='buildbucket.v2.TokenBody.build_id', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='purpose', full_name='buildbucket.v2.TokenBody.purpose', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='state', full_name='buildbucket.v2.TokenBody.state', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _TOKENBODY_PURPOSE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=71,
  serialized_end=224,
)


_TOKENENVELOPE = _descriptor.Descriptor(
  name='TokenEnvelope',
  full_name='buildbucket.v2.TokenEnvelope',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='version', full_name='buildbucket.v2.TokenEnvelope.version', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='payload', full_name='buildbucket.v2.TokenEnvelope.payload', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _TOKENENVELOPE_VERSION,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=227,
  serialized_end=382,
)

_TOKENBODY.fields_by_name['purpose'].enum_type = _TOKENBODY_PURPOSE
_TOKENBODY_PURPOSE.containing_type = _TOKENBODY
_TOKENENVELOPE.fields_by_name['version'].enum_type = _TOKENENVELOPE_VERSION
_TOKENENVELOPE_VERSION.containing_type = _TOKENENVELOPE
DESCRIPTOR.message_types_by_name['TokenBody'] = _TOKENBODY
DESCRIPTOR.message_types_by_name['TokenEnvelope'] = _TOKENENVELOPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TokenBody = _reflection.GeneratedProtocolMessageType('TokenBody', (_message.Message,), {
  'DESCRIPTOR' : _TOKENBODY,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.token_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.TokenBody)
  })
_sym_db.RegisterMessage(TokenBody)

TokenEnvelope = _reflection.GeneratedProtocolMessageType('TokenEnvelope', (_message.Message,), {
  'DESCRIPTOR' : _TOKENENVELOPE,
  '__module__' : 'go.chromium.org.luci.buildbucket.proto.token_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.TokenEnvelope)
  })
_sym_db.RegisterMessage(TokenEnvelope)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
