# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: components/auth/proto/security_config.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='components/auth/proto/security_config.proto',
  package='components.auth',
  syntax='proto3',
  serialized_options=b'Z:go.chromium.org/luci/server/auth/service/protocol;protocol',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n+components/auth/proto/security_config.proto\x12\x0f\x63omponents.auth\"1\n\x0eSecurityConfig\x12\x1f\n\x17internal_service_regexp\x18\x01 \x03(\tB<Z:go.chromium.org/luci/server/auth/service/protocol;protocolb\x06proto3'
)




_SECURITYCONFIG = _descriptor.Descriptor(
  name='SecurityConfig',
  full_name='components.auth.SecurityConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='internal_service_regexp', full_name='components.auth.SecurityConfig.internal_service_regexp', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=64,
  serialized_end=113,
)

DESCRIPTOR.message_types_by_name['SecurityConfig'] = _SECURITYCONFIG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SecurityConfig = _reflection.GeneratedProtocolMessageType('SecurityConfig', (_message.Message,), {
  'DESCRIPTOR' : _SECURITYCONFIG,
  '__module__' : 'components.auth.proto.security_config_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.SecurityConfig)
  })
_sym_db.RegisterMessage(SecurityConfig)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
