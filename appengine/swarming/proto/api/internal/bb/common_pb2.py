# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: common.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import duration_pb2 as google_dot_protobuf_dot_duration__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='common.proto',
  package='bb',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x0c\x63ommon.proto\x12\x02\x62\x62\x1a\x1egoogle/protobuf/duration.proto\"_\n\x12RequestedDimension\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12-\n\nexpiration\x18\x03 \x01(\x0b\x32\x19.google.protobuf.Duration\"\xab\x01\n\rStatusDetails\x12\x41\n\x13resource_exhaustion\x18\x03 \x01(\x0b\x32$.bb.StatusDetails.ResourceExhaustion\x12*\n\x07timeout\x18\x04 \x01(\x0b\x32\x19.bb.StatusDetails.Timeout\x1a\x14\n\x12ResourceExhaustion\x1a\t\n\x07TimeoutJ\x04\x08\x01\x10\x02J\x04\x08\x02\x10\x03*\x87\x01\n\x06Status\x12\x16\n\x12STATUS_UNSPECIFIED\x10\x00\x12\r\n\tSCHEDULED\x10\x01\x12\x0b\n\x07STARTED\x10\x02\x12\x0e\n\nENDED_MASK\x10\x04\x12\x0b\n\x07SUCCESS\x10\x0c\x12\x0b\n\x07\x46\x41ILURE\x10\x14\x12\x11\n\rINFRA_FAILURE\x10$\x12\x0c\n\x08\x43\x41NCELED\x10\x44\x62\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_duration__pb2.DESCRIPTOR,])

_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='bb.Status',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STATUS_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SCHEDULED', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='STARTED', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='ENDED_MASK', index=3, number=4,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=4, number=12,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FAILURE', index=5, number=20,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='INFRA_FAILURE', index=6, number=36,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='CANCELED', index=7, number=68,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=324,
  serialized_end=459,
)
_sym_db.RegisterEnumDescriptor(_STATUS)

Status = enum_type_wrapper.EnumTypeWrapper(_STATUS)
STATUS_UNSPECIFIED = 0
SCHEDULED = 1
STARTED = 2
ENDED_MASK = 4
SUCCESS = 12
FAILURE = 20
INFRA_FAILURE = 36
CANCELED = 68



_REQUESTEDDIMENSION = _descriptor.Descriptor(
  name='RequestedDimension',
  full_name='bb.RequestedDimension',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='bb.RequestedDimension.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='value', full_name='bb.RequestedDimension.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='expiration', full_name='bb.RequestedDimension.expiration', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
  serialized_start=52,
  serialized_end=147,
)


_STATUSDETAILS_RESOURCEEXHAUSTION = _descriptor.Descriptor(
  name='ResourceExhaustion',
  full_name='bb.StatusDetails.ResourceExhaustion',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
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
  serialized_start=278,
  serialized_end=298,
)

_STATUSDETAILS_TIMEOUT = _descriptor.Descriptor(
  name='Timeout',
  full_name='bb.StatusDetails.Timeout',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
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
  serialized_start=300,
  serialized_end=309,
)

_STATUSDETAILS = _descriptor.Descriptor(
  name='StatusDetails',
  full_name='bb.StatusDetails',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='resource_exhaustion', full_name='bb.StatusDetails.resource_exhaustion', index=0,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='timeout', full_name='bb.StatusDetails.timeout', index=1,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_STATUSDETAILS_RESOURCEEXHAUSTION, _STATUSDETAILS_TIMEOUT, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=150,
  serialized_end=321,
)

_REQUESTEDDIMENSION.fields_by_name['expiration'].message_type = google_dot_protobuf_dot_duration__pb2._DURATION
_STATUSDETAILS_RESOURCEEXHAUSTION.containing_type = _STATUSDETAILS
_STATUSDETAILS_TIMEOUT.containing_type = _STATUSDETAILS
_STATUSDETAILS.fields_by_name['resource_exhaustion'].message_type = _STATUSDETAILS_RESOURCEEXHAUSTION
_STATUSDETAILS.fields_by_name['timeout'].message_type = _STATUSDETAILS_TIMEOUT
DESCRIPTOR.message_types_by_name['RequestedDimension'] = _REQUESTEDDIMENSION
DESCRIPTOR.message_types_by_name['StatusDetails'] = _STATUSDETAILS
DESCRIPTOR.enum_types_by_name['Status'] = _STATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

RequestedDimension = _reflection.GeneratedProtocolMessageType('RequestedDimension', (_message.Message,), {
  'DESCRIPTOR' : _REQUESTEDDIMENSION,
  '__module__' : 'common_pb2'
  # @@protoc_insertion_point(class_scope:bb.RequestedDimension)
  })
_sym_db.RegisterMessage(RequestedDimension)

StatusDetails = _reflection.GeneratedProtocolMessageType('StatusDetails', (_message.Message,), {

  'ResourceExhaustion' : _reflection.GeneratedProtocolMessageType('ResourceExhaustion', (_message.Message,), {
    'DESCRIPTOR' : _STATUSDETAILS_RESOURCEEXHAUSTION,
    '__module__' : 'common_pb2'
    # @@protoc_insertion_point(class_scope:bb.StatusDetails.ResourceExhaustion)
    })
  ,

  'Timeout' : _reflection.GeneratedProtocolMessageType('Timeout', (_message.Message,), {
    'DESCRIPTOR' : _STATUSDETAILS_TIMEOUT,
    '__module__' : 'common_pb2'
    # @@protoc_insertion_point(class_scope:bb.StatusDetails.Timeout)
    })
  ,
  'DESCRIPTOR' : _STATUSDETAILS,
  '__module__' : 'common_pb2'
  # @@protoc_insertion_point(class_scope:bb.StatusDetails)
  })
_sym_db.RegisterMessage(StatusDetails)
_sym_db.RegisterMessage(StatusDetails.ResourceExhaustion)
_sym_db.RegisterMessage(StatusDetails.Timeout)


# @@protoc_insertion_point(module_scope)
