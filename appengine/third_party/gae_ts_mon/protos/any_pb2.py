# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: infra_libs/ts_mon/protos/any.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='infra_libs/ts_mon/protos/any.proto',
  package='ts_mon.proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=b'\n\"infra_libs/ts_mon/protos/any.proto\x12\x0cts_mon.proto\".\n\x03\x41ny\x12\x14\n\x08type_url\x18\x01 \x01(\tB\x02\x08\x02\x12\x11\n\x05value\x18\x02 \x01(\x0c\x42\x02\x08\x01'
)




_ANY = _descriptor.Descriptor(
  name='Any',
  full_name='ts_mon.proto.Any',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type_url', full_name='ts_mon.proto.Any.type_url', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\010\002', file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='ts_mon.proto.Any.value', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\010\001', file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=52,
  serialized_end=98,
)

DESCRIPTOR.message_types_by_name['Any'] = _ANY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Any = _reflection.GeneratedProtocolMessageType('Any', (_message.Message,), {
  'DESCRIPTOR' : _ANY,
  '__module__' : 'infra_libs.ts_mon.protos.any_pb2'
  # @@protoc_insertion_point(class_scope:ts_mon.proto.Any)
  })
_sym_db.RegisterMessage(Any)


_ANY.fields_by_name['type_url']._options = None
_ANY.fields_by_name['value']._options = None
# @@protoc_insertion_point(module_scope)