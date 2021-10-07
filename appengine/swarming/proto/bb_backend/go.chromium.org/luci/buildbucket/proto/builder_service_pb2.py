# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: builder_service.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import field_behavior_pb2 as google_dot_api_dot_field__behavior__pb2
from go.chromium.org.luci.buildbucket.proto import builder_pb2 as go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_builder__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='builder_service.proto',
  package='buildbucket.v2',
  syntax='proto3',
  serialized_options=b'Z4go.chromium.org/luci/buildbucket/proto;buildbucketpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x15\x62uilder_service.proto\x12\x0e\x62uildbucket.v2\x1a\x1fgoogle/api/field_behavior.proto\x1a\x34go.chromium.org/luci/buildbucket/proto/builder.proto\":\n\x11GetBuilderRequest\x12%\n\x02id\x18\x01 \x01(\x0b\x32\x19.buildbucket.v2.BuilderID\"b\n\x13ListBuildersRequest\x12\x14\n\x07project\x18\x01 \x01(\tB\x03\xe0\x41\x02\x12\x0e\n\x06\x62ucket\x18\x02 \x01(\t\x12\x11\n\tpage_size\x18\x03 \x01(\x05\x12\x12\n\npage_token\x18\x04 \x01(\t\"^\n\x14ListBuildersResponse\x12-\n\x08\x62uilders\x18\x01 \x03(\x0b\x32\x1b.buildbucket.v2.BuilderItem\x12\x17\n\x0fnext_page_token\x18\x02 \x01(\t2\xb7\x01\n\x08\x42uilders\x12N\n\nGetBuilder\x12!.buildbucket.v2.GetBuilderRequest\x1a\x1b.buildbucket.v2.BuilderItem\"\x00\x12[\n\x0cListBuilders\x12#.buildbucket.v2.ListBuildersRequest\x1a$.buildbucket.v2.ListBuildersResponse\"\x00\x42\x36Z4go.chromium.org/luci/buildbucket/proto;buildbucketpbb\x06proto3'
  ,
  dependencies=[google_dot_api_dot_field__behavior__pb2.DESCRIPTOR,go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_builder__pb2.DESCRIPTOR,])




_GETBUILDERREQUEST = _descriptor.Descriptor(
  name='GetBuilderRequest',
  full_name='buildbucket.v2.GetBuilderRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='buildbucket.v2.GetBuilderRequest.id', index=0,
      number=1, type=11, cpp_type=10, label=1,
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
  serialized_start=128,
  serialized_end=186,
)


_LISTBUILDERSREQUEST = _descriptor.Descriptor(
  name='ListBuildersRequest',
  full_name='buildbucket.v2.ListBuildersRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='project', full_name='buildbucket.v2.ListBuildersRequest.project', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='bucket', full_name='buildbucket.v2.ListBuildersRequest.bucket', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='page_size', full_name='buildbucket.v2.ListBuildersRequest.page_size', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='page_token', full_name='buildbucket.v2.ListBuildersRequest.page_token', index=3,
      number=4, type=9, cpp_type=9, label=1,
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
  serialized_start=188,
  serialized_end=286,
)


_LISTBUILDERSRESPONSE = _descriptor.Descriptor(
  name='ListBuildersResponse',
  full_name='buildbucket.v2.ListBuildersResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='builders', full_name='buildbucket.v2.ListBuildersResponse.builders', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='next_page_token', full_name='buildbucket.v2.ListBuildersResponse.next_page_token', index=1,
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
  serialized_start=288,
  serialized_end=382,
)

_GETBUILDERREQUEST.fields_by_name['id'].message_type = go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_builder__pb2._BUILDERID
_LISTBUILDERSRESPONSE.fields_by_name['builders'].message_type = go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_builder__pb2._BUILDERITEM
DESCRIPTOR.message_types_by_name['GetBuilderRequest'] = _GETBUILDERREQUEST
DESCRIPTOR.message_types_by_name['ListBuildersRequest'] = _LISTBUILDERSREQUEST
DESCRIPTOR.message_types_by_name['ListBuildersResponse'] = _LISTBUILDERSRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GetBuilderRequest = _reflection.GeneratedProtocolMessageType('GetBuilderRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETBUILDERREQUEST,
  '__module__' : 'builder_service_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.GetBuilderRequest)
  })
_sym_db.RegisterMessage(GetBuilderRequest)

ListBuildersRequest = _reflection.GeneratedProtocolMessageType('ListBuildersRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTBUILDERSREQUEST,
  '__module__' : 'builder_service_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.ListBuildersRequest)
  })
_sym_db.RegisterMessage(ListBuildersRequest)

ListBuildersResponse = _reflection.GeneratedProtocolMessageType('ListBuildersResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTBUILDERSRESPONSE,
  '__module__' : 'builder_service_pb2'
  # @@protoc_insertion_point(class_scope:buildbucket.v2.ListBuildersResponse)
  })
_sym_db.RegisterMessage(ListBuildersResponse)


DESCRIPTOR._options = None
_LISTBUILDERSREQUEST.fields_by_name['project']._options = None

_BUILDERS = _descriptor.ServiceDescriptor(
  name='Builders',
  full_name='buildbucket.v2.Builders',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=385,
  serialized_end=568,
  methods=[
  _descriptor.MethodDescriptor(
    name='GetBuilder',
    full_name='buildbucket.v2.Builders.GetBuilder',
    index=0,
    containing_service=None,
    input_type=_GETBUILDERREQUEST,
    output_type=go_dot_chromium_dot_org_dot_luci_dot_buildbucket_dot_proto_dot_builder__pb2._BUILDERITEM,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ListBuilders',
    full_name='buildbucket.v2.Builders.ListBuilders',
    index=1,
    containing_service=None,
    input_type=_LISTBUILDERSREQUEST,
    output_type=_LISTBUILDERSRESPONSE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_BUILDERS)

DESCRIPTOR.services_by_name['Builders'] = _BUILDERS

# @@protoc_insertion_point(module_scope)
