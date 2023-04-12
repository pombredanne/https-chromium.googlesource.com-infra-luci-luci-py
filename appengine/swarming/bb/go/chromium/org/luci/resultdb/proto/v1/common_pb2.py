# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/resultdb/proto/v1/common.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/resultdb/proto/v1/common.proto',
  package='luci.resultdb.v1',
  syntax='proto3',
  serialized_options=b'Z/go.chromium.org/luci/resultdb/proto/v1;resultpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n3go.chromium.org/luci/resultdb/proto/v1/common.proto\x12\x10luci.resultdb.v1\x1a\x1fgoogle/protobuf/timestamp.proto\"f\n\x07Variant\x12/\n\x03\x64\x65\x66\x18\x01 \x03(\x0b\x32\".luci.resultdb.v1.Variant.DefEntry\x1a*\n\x08\x44\x65\x66\x45ntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"(\n\nStringPair\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"b\n\rGitilesCommit\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0f\n\x07project\x18\x02 \x01(\t\x12\x0b\n\x03ref\x18\x03 \x01(\t\x12\x13\n\x0b\x63ommit_hash\x18\x04 \x01(\t\x12\x10\n\x08position\x18\x05 \x01(\x04\"O\n\x0cGerritChange\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0f\n\x07project\x18\x02 \x01(\t\x12\x0e\n\x06\x63hange\x18\x03 \x01(\x03\x12\x10\n\x08patchset\x18\x04 \x01(\x03\"N\n\x0e\x43ommitPosition\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0f\n\x07project\x18\x02 \x01(\t\x12\x0b\n\x03ref\x18\x03 \x01(\t\x12\x10\n\x08position\x18\x04 \x01(\x03\"{\n\x13\x43ommitPositionRange\x12\x32\n\x08\x65\x61rliest\x18\x01 \x01(\x0b\x32 .luci.resultdb.v1.CommitPosition\x12\x30\n\x06latest\x18\x02 \x01(\x0b\x32 .luci.resultdb.v1.CommitPosition\"e\n\tTimeRange\x12,\n\x08\x65\x61rliest\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12*\n\x06latest\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampB1Z/go.chromium.org/luci/resultdb/proto/v1;resultpbb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])




_VARIANT_DEFENTRY = _descriptor.Descriptor(
  name='DefEntry',
  full_name='luci.resultdb.v1.Variant.DefEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='luci.resultdb.v1.Variant.DefEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='luci.resultdb.v1.Variant.DefEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_options=b'8\001',
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=166,
  serialized_end=208,
)

_VARIANT = _descriptor.Descriptor(
  name='Variant',
  full_name='luci.resultdb.v1.Variant',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='def', full_name='luci.resultdb.v1.Variant.def', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
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
  serialized_start=106,
  serialized_end=208,
)


_STRINGPAIR = _descriptor.Descriptor(
  name='StringPair',
  full_name='luci.resultdb.v1.StringPair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='luci.resultdb.v1.StringPair.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='luci.resultdb.v1.StringPair.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=210,
  serialized_end=250,
)


_GITILESCOMMIT = _descriptor.Descriptor(
  name='GitilesCommit',
  full_name='luci.resultdb.v1.GitilesCommit',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='host', full_name='luci.resultdb.v1.GitilesCommit.host', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='project', full_name='luci.resultdb.v1.GitilesCommit.project', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ref', full_name='luci.resultdb.v1.GitilesCommit.ref', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='commit_hash', full_name='luci.resultdb.v1.GitilesCommit.commit_hash', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='position', full_name='luci.resultdb.v1.GitilesCommit.position', index=4,
      number=5, type=4, cpp_type=4, label=1,
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
  serialized_start=252,
  serialized_end=350,
)


_GERRITCHANGE = _descriptor.Descriptor(
  name='GerritChange',
  full_name='luci.resultdb.v1.GerritChange',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='host', full_name='luci.resultdb.v1.GerritChange.host', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='project', full_name='luci.resultdb.v1.GerritChange.project', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='change', full_name='luci.resultdb.v1.GerritChange.change', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='patchset', full_name='luci.resultdb.v1.GerritChange.patchset', index=3,
      number=4, type=3, cpp_type=2, label=1,
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
  serialized_start=352,
  serialized_end=431,
)


_COMMITPOSITION = _descriptor.Descriptor(
  name='CommitPosition',
  full_name='luci.resultdb.v1.CommitPosition',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='host', full_name='luci.resultdb.v1.CommitPosition.host', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='project', full_name='luci.resultdb.v1.CommitPosition.project', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ref', full_name='luci.resultdb.v1.CommitPosition.ref', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='position', full_name='luci.resultdb.v1.CommitPosition.position', index=3,
      number=4, type=3, cpp_type=2, label=1,
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
  serialized_start=433,
  serialized_end=511,
)


_COMMITPOSITIONRANGE = _descriptor.Descriptor(
  name='CommitPositionRange',
  full_name='luci.resultdb.v1.CommitPositionRange',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='earliest', full_name='luci.resultdb.v1.CommitPositionRange.earliest', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='latest', full_name='luci.resultdb.v1.CommitPositionRange.latest', index=1,
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
  serialized_start=513,
  serialized_end=636,
)


_TIMERANGE = _descriptor.Descriptor(
  name='TimeRange',
  full_name='luci.resultdb.v1.TimeRange',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='earliest', full_name='luci.resultdb.v1.TimeRange.earliest', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='latest', full_name='luci.resultdb.v1.TimeRange.latest', index=1,
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
  serialized_start=638,
  serialized_end=739,
)

_VARIANT_DEFENTRY.containing_type = _VARIANT
_VARIANT.fields_by_name['def'].message_type = _VARIANT_DEFENTRY
_COMMITPOSITIONRANGE.fields_by_name['earliest'].message_type = _COMMITPOSITION
_COMMITPOSITIONRANGE.fields_by_name['latest'].message_type = _COMMITPOSITION
_TIMERANGE.fields_by_name['earliest'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_TIMERANGE.fields_by_name['latest'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
DESCRIPTOR.message_types_by_name['Variant'] = _VARIANT
DESCRIPTOR.message_types_by_name['StringPair'] = _STRINGPAIR
DESCRIPTOR.message_types_by_name['GitilesCommit'] = _GITILESCOMMIT
DESCRIPTOR.message_types_by_name['GerritChange'] = _GERRITCHANGE
DESCRIPTOR.message_types_by_name['CommitPosition'] = _COMMITPOSITION
DESCRIPTOR.message_types_by_name['CommitPositionRange'] = _COMMITPOSITIONRANGE
DESCRIPTOR.message_types_by_name['TimeRange'] = _TIMERANGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Variant = _reflection.GeneratedProtocolMessageType('Variant', (_message.Message,), {

  'DefEntry' : _reflection.GeneratedProtocolMessageType('DefEntry', (_message.Message,), {
    'DESCRIPTOR' : _VARIANT_DEFENTRY,
    '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
    # @@protoc_insertion_point(class_scope:luci.resultdb.v1.Variant.DefEntry)
    })
  ,
  'DESCRIPTOR' : _VARIANT,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.Variant)
  })
_sym_db.RegisterMessage(Variant)
_sym_db.RegisterMessage(Variant.DefEntry)

StringPair = _reflection.GeneratedProtocolMessageType('StringPair', (_message.Message,), {
  'DESCRIPTOR' : _STRINGPAIR,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.StringPair)
  })
_sym_db.RegisterMessage(StringPair)

GitilesCommit = _reflection.GeneratedProtocolMessageType('GitilesCommit', (_message.Message,), {
  'DESCRIPTOR' : _GITILESCOMMIT,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.GitilesCommit)
  })
_sym_db.RegisterMessage(GitilesCommit)

GerritChange = _reflection.GeneratedProtocolMessageType('GerritChange', (_message.Message,), {
  'DESCRIPTOR' : _GERRITCHANGE,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.GerritChange)
  })
_sym_db.RegisterMessage(GerritChange)

CommitPosition = _reflection.GeneratedProtocolMessageType('CommitPosition', (_message.Message,), {
  'DESCRIPTOR' : _COMMITPOSITION,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.CommitPosition)
  })
_sym_db.RegisterMessage(CommitPosition)

CommitPositionRange = _reflection.GeneratedProtocolMessageType('CommitPositionRange', (_message.Message,), {
  'DESCRIPTOR' : _COMMITPOSITIONRANGE,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.CommitPositionRange)
  })
_sym_db.RegisterMessage(CommitPositionRange)

TimeRange = _reflection.GeneratedProtocolMessageType('TimeRange', (_message.Message,), {
  'DESCRIPTOR' : _TIMERANGE,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.common_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.TimeRange)
  })
_sym_db.RegisterMessage(TimeRange)


DESCRIPTOR._options = None
_VARIANT_DEFENTRY._options = None
# @@protoc_insertion_point(module_scope)
