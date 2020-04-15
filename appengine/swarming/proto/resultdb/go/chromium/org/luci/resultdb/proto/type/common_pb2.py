# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/resultdb/proto/type/common.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/resultdb/proto/type/common.proto',
  package='luci.resultdb.type',
  syntax='proto3',
  serialized_options=_b('Z/go.chromium.org/luci/resultdb/proto/type;typepb'),
  serialized_pb=_b('\n5go.chromium.org/luci/resultdb/proto/type/common.proto\x12\x12luci.resultdb.type\"h\n\x07Variant\x12\x31\n\x03\x64\x65\x66\x18\x01 \x03(\x0b\x32$.luci.resultdb.type.Variant.DefEntry\x1a*\n\x08\x44\x65\x66\x45ntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"(\n\nStringPair\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\tB1Z/go.chromium.org/luci/resultdb/proto/type;typepbb\x06proto3')
)




_VARIANT_DEFENTRY = _descriptor.Descriptor(
  name='DefEntry',
  full_name='luci.resultdb.type.Variant.DefEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='luci.resultdb.type.Variant.DefEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='luci.resultdb.type.Variant.DefEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=139,
  serialized_end=181,
)

_VARIANT = _descriptor.Descriptor(
  name='Variant',
  full_name='luci.resultdb.type.Variant',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='def', full_name='luci.resultdb.type.Variant.def', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_VARIANT_DEFENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=77,
  serialized_end=181,
)


_STRINGPAIR = _descriptor.Descriptor(
  name='StringPair',
  full_name='luci.resultdb.type.StringPair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='luci.resultdb.type.StringPair.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='luci.resultdb.type.StringPair.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
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
  serialized_start=183,
  serialized_end=223,
)

_VARIANT_DEFENTRY.containing_type = _VARIANT
_VARIANT.fields_by_name['def'].message_type = _VARIANT_DEFENTRY
DESCRIPTOR.message_types_by_name['Variant'] = _VARIANT
DESCRIPTOR.message_types_by_name['StringPair'] = _STRINGPAIR
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Variant = _reflection.GeneratedProtocolMessageType('Variant', (_message.Message,), dict(

  DefEntry = _reflection.GeneratedProtocolMessageType('DefEntry', (_message.Message,), dict(
    DESCRIPTOR = _VARIANT_DEFENTRY,
    __module__ = 'go.chromium.org.luci.resultdb.proto.type.common_pb2'
    # @@protoc_insertion_point(class_scope:luci.resultdb.type.Variant.DefEntry)
    ))
  ,
  DESCRIPTOR = _VARIANT,
  __module__ = 'go.chromium.org.luci.resultdb.proto.type.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.type.Variant)
  ))
_sym_db.RegisterMessage(Variant)
_sym_db.RegisterMessage(Variant.DefEntry)

StringPair = _reflection.GeneratedProtocolMessageType('StringPair', (_message.Message,), dict(
  DESCRIPTOR = _STRINGPAIR,
  __module__ = 'go.chromium.org.luci.resultdb.proto.type.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.type.StringPair)
  ))
_sym_db.RegisterMessage(StringPair)


DESCRIPTOR._options = None
_VARIANT_DEFENTRY._options = None
# @@protoc_insertion_point(module_scope)
