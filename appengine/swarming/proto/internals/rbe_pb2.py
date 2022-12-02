# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/internals/rbe.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='proto/internals/rbe.proto',
  package='swarming.internals.rbe',
  syntax='proto3',
  serialized_options=b'Z9go.chromium.org/luci/swarming/proto/internals;internalspb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\x19proto/internals/rbe.proto\x12\x16swarming.internals.rbe\x1a\x1fgoogle/protobuf/timestamp.proto\"\xbb\x01\n\rTaggedMessage\x12G\n\x0cpayload_type\x18\x01 \x01(\x0e\x32\x31.swarming.internals.rbe.TaggedMessage.PayloadType\x12\x0f\n\x07payload\x18\x02 \x01(\x0c\x12\x13\n\x0bhmac_sha256\x18\x03 \x01(\x0c\";\n\x0bPayloadType\x12\x1c\n\x18PAYLOAD_TYPE_UNSPECIFIED\x10\x00\x12\x0e\n\nPOLL_STATE\x10\x01\"\x81\x07\n\tPollState\x12\n\n\x02id\x18\x01 \x01(\t\x12*\n\x06\x65xpiry\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x14\n\x0crbe_instance\x18\x03 \x01(\t\x12H\n\x13\x65nforced_dimensions\x18\x04 \x03(\x0b\x32+.swarming.internals.rbe.PollState.Dimension\x12?\n\ndebug_info\x18\x05 \x01(\x0b\x32+.swarming.internals.rbe.PollState.DebugInfo\x12\x14\n\x0cip_allowlist\x18\n \x01(\t\x12=\n\x08gce_auth\x18\x0b \x01(\x0b\x32).swarming.internals.rbe.PollState.GCEAuthH\x00\x12T\n\x14service_account_auth\x18\x0c \x01(\x0b\x32\x34.swarming.internals.rbe.PollState.ServiceAccountAuthH\x00\x12Y\n\x17luci_machine_token_auth\x18\r \x01(\x0b\x32\x36.swarming.internals.rbe.PollState.LUCIMachineTokenAuthH\x00\x12N\n\x11ip_allowlist_auth\x18\x0e \x01(\x0b\x32\x31.swarming.internals.rbe.PollState.IPAllowlistAuthH\x00\x1a(\n\tDimension\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x0e\n\x06values\x18\x02 \x03(\t\x1a\x66\n\tDebugInfo\x12+\n\x07\x63reated\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x18\n\x10swarming_version\x18\x02 \x01(\t\x12\x12\n\nrequest_id\x18\x03 \x01(\t\x1a\x34\n\x07GCEAuth\x12\x13\n\x0bgce_project\x18\x01 \x01(\t\x12\x14\n\x0cgce_instance\x18\x02 \x01(\t\x1a-\n\x12ServiceAccountAuth\x12\x17\n\x0fservice_account\x18\x01 \x01(\t\x1a,\n\x14LUCIMachineTokenAuth\x12\x14\n\x0cmachine_fqdn\x18\x01 \x01(\t\x1a\x11\n\x0fIPAllowlistAuthB\r\n\x0b\x61uth_methodB;Z9go.chromium.org/luci/swarming/proto/internals;internalspbb\x06proto3'
  ,
  dependencies=[google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,])



_TAGGEDMESSAGE_PAYLOADTYPE = _descriptor.EnumDescriptor(
  name='PayloadType',
  full_name='swarming.internals.rbe.TaggedMessage.PayloadType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PAYLOAD_TYPE_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='POLL_STATE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=215,
  serialized_end=274,
)
_sym_db.RegisterEnumDescriptor(_TAGGEDMESSAGE_PAYLOADTYPE)


_TAGGEDMESSAGE = _descriptor.Descriptor(
  name='TaggedMessage',
  full_name='swarming.internals.rbe.TaggedMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='payload_type', full_name='swarming.internals.rbe.TaggedMessage.payload_type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='payload', full_name='swarming.internals.rbe.TaggedMessage.payload', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=b"",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='hmac_sha256', full_name='swarming.internals.rbe.TaggedMessage.hmac_sha256', index=2,
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
    _TAGGEDMESSAGE_PAYLOADTYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=87,
  serialized_end=274,
)


_POLLSTATE_DIMENSION = _descriptor.Descriptor(
  name='Dimension',
  full_name='swarming.internals.rbe.PollState.Dimension',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='swarming.internals.rbe.PollState.Dimension.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='values', full_name='swarming.internals.rbe.PollState.Dimension.values', index=1,
      number=2, type=9, cpp_type=9, label=3,
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
  serialized_start=849,
  serialized_end=889,
)

_POLLSTATE_DEBUGINFO = _descriptor.Descriptor(
  name='DebugInfo',
  full_name='swarming.internals.rbe.PollState.DebugInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='created', full_name='swarming.internals.rbe.PollState.DebugInfo.created', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='swarming_version', full_name='swarming.internals.rbe.PollState.DebugInfo.swarming_version', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='request_id', full_name='swarming.internals.rbe.PollState.DebugInfo.request_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=891,
  serialized_end=993,
)

_POLLSTATE_GCEAUTH = _descriptor.Descriptor(
  name='GCEAuth',
  full_name='swarming.internals.rbe.PollState.GCEAuth',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='gce_project', full_name='swarming.internals.rbe.PollState.GCEAuth.gce_project', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='gce_instance', full_name='swarming.internals.rbe.PollState.GCEAuth.gce_instance', index=1,
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
  serialized_start=995,
  serialized_end=1047,
)

_POLLSTATE_SERVICEACCOUNTAUTH = _descriptor.Descriptor(
  name='ServiceAccountAuth',
  full_name='swarming.internals.rbe.PollState.ServiceAccountAuth',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='service_account', full_name='swarming.internals.rbe.PollState.ServiceAccountAuth.service_account', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=1049,
  serialized_end=1094,
)

_POLLSTATE_LUCIMACHINETOKENAUTH = _descriptor.Descriptor(
  name='LUCIMachineTokenAuth',
  full_name='swarming.internals.rbe.PollState.LUCIMachineTokenAuth',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='machine_fqdn', full_name='swarming.internals.rbe.PollState.LUCIMachineTokenAuth.machine_fqdn', index=0,
      number=1, type=9, cpp_type=9, label=1,
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
  serialized_start=1096,
  serialized_end=1140,
)

_POLLSTATE_IPALLOWLISTAUTH = _descriptor.Descriptor(
  name='IPAllowlistAuth',
  full_name='swarming.internals.rbe.PollState.IPAllowlistAuth',
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
  serialized_start=1142,
  serialized_end=1159,
)

_POLLSTATE = _descriptor.Descriptor(
  name='PollState',
  full_name='swarming.internals.rbe.PollState',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='swarming.internals.rbe.PollState.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='expiry', full_name='swarming.internals.rbe.PollState.expiry', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='rbe_instance', full_name='swarming.internals.rbe.PollState.rbe_instance', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='enforced_dimensions', full_name='swarming.internals.rbe.PollState.enforced_dimensions', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='debug_info', full_name='swarming.internals.rbe.PollState.debug_info', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ip_allowlist', full_name='swarming.internals.rbe.PollState.ip_allowlist', index=5,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='gce_auth', full_name='swarming.internals.rbe.PollState.gce_auth', index=6,
      number=11, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='service_account_auth', full_name='swarming.internals.rbe.PollState.service_account_auth', index=7,
      number=12, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='luci_machine_token_auth', full_name='swarming.internals.rbe.PollState.luci_machine_token_auth', index=8,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='ip_allowlist_auth', full_name='swarming.internals.rbe.PollState.ip_allowlist_auth', index=9,
      number=14, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_POLLSTATE_DIMENSION, _POLLSTATE_DEBUGINFO, _POLLSTATE_GCEAUTH, _POLLSTATE_SERVICEACCOUNTAUTH, _POLLSTATE_LUCIMACHINETOKENAUTH, _POLLSTATE_IPALLOWLISTAUTH, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='auth_method', full_name='swarming.internals.rbe.PollState.auth_method',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=277,
  serialized_end=1174,
)

_TAGGEDMESSAGE.fields_by_name['payload_type'].enum_type = _TAGGEDMESSAGE_PAYLOADTYPE
_TAGGEDMESSAGE_PAYLOADTYPE.containing_type = _TAGGEDMESSAGE
_POLLSTATE_DIMENSION.containing_type = _POLLSTATE
_POLLSTATE_DEBUGINFO.fields_by_name['created'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_POLLSTATE_DEBUGINFO.containing_type = _POLLSTATE
_POLLSTATE_GCEAUTH.containing_type = _POLLSTATE
_POLLSTATE_SERVICEACCOUNTAUTH.containing_type = _POLLSTATE
_POLLSTATE_LUCIMACHINETOKENAUTH.containing_type = _POLLSTATE
_POLLSTATE_IPALLOWLISTAUTH.containing_type = _POLLSTATE
_POLLSTATE.fields_by_name['expiry'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_POLLSTATE.fields_by_name['enforced_dimensions'].message_type = _POLLSTATE_DIMENSION
_POLLSTATE.fields_by_name['debug_info'].message_type = _POLLSTATE_DEBUGINFO
_POLLSTATE.fields_by_name['gce_auth'].message_type = _POLLSTATE_GCEAUTH
_POLLSTATE.fields_by_name['service_account_auth'].message_type = _POLLSTATE_SERVICEACCOUNTAUTH
_POLLSTATE.fields_by_name['luci_machine_token_auth'].message_type = _POLLSTATE_LUCIMACHINETOKENAUTH
_POLLSTATE.fields_by_name['ip_allowlist_auth'].message_type = _POLLSTATE_IPALLOWLISTAUTH
_POLLSTATE.oneofs_by_name['auth_method'].fields.append(
  _POLLSTATE.fields_by_name['gce_auth'])
_POLLSTATE.fields_by_name['gce_auth'].containing_oneof = _POLLSTATE.oneofs_by_name['auth_method']
_POLLSTATE.oneofs_by_name['auth_method'].fields.append(
  _POLLSTATE.fields_by_name['service_account_auth'])
_POLLSTATE.fields_by_name['service_account_auth'].containing_oneof = _POLLSTATE.oneofs_by_name['auth_method']
_POLLSTATE.oneofs_by_name['auth_method'].fields.append(
  _POLLSTATE.fields_by_name['luci_machine_token_auth'])
_POLLSTATE.fields_by_name['luci_machine_token_auth'].containing_oneof = _POLLSTATE.oneofs_by_name['auth_method']
_POLLSTATE.oneofs_by_name['auth_method'].fields.append(
  _POLLSTATE.fields_by_name['ip_allowlist_auth'])
_POLLSTATE.fields_by_name['ip_allowlist_auth'].containing_oneof = _POLLSTATE.oneofs_by_name['auth_method']
DESCRIPTOR.message_types_by_name['TaggedMessage'] = _TAGGEDMESSAGE
DESCRIPTOR.message_types_by_name['PollState'] = _POLLSTATE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TaggedMessage = _reflection.GeneratedProtocolMessageType('TaggedMessage', (_message.Message,), {
  'DESCRIPTOR' : _TAGGEDMESSAGE,
  '__module__' : 'proto.internals.rbe_pb2'
  # @@protoc_insertion_point(class_scope:swarming.internals.rbe.TaggedMessage)
  })
_sym_db.RegisterMessage(TaggedMessage)

PollState = _reflection.GeneratedProtocolMessageType('PollState', (_message.Message,), {

  'Dimension' : _reflection.GeneratedProtocolMessageType('Dimension', (_message.Message,), {
    'DESCRIPTOR' : _POLLSTATE_DIMENSION,
    '__module__' : 'proto.internals.rbe_pb2'
    # @@protoc_insertion_point(class_scope:swarming.internals.rbe.PollState.Dimension)
    })
  ,

  'DebugInfo' : _reflection.GeneratedProtocolMessageType('DebugInfo', (_message.Message,), {
    'DESCRIPTOR' : _POLLSTATE_DEBUGINFO,
    '__module__' : 'proto.internals.rbe_pb2'
    # @@protoc_insertion_point(class_scope:swarming.internals.rbe.PollState.DebugInfo)
    })
  ,

  'GCEAuth' : _reflection.GeneratedProtocolMessageType('GCEAuth', (_message.Message,), {
    'DESCRIPTOR' : _POLLSTATE_GCEAUTH,
    '__module__' : 'proto.internals.rbe_pb2'
    # @@protoc_insertion_point(class_scope:swarming.internals.rbe.PollState.GCEAuth)
    })
  ,

  'ServiceAccountAuth' : _reflection.GeneratedProtocolMessageType('ServiceAccountAuth', (_message.Message,), {
    'DESCRIPTOR' : _POLLSTATE_SERVICEACCOUNTAUTH,
    '__module__' : 'proto.internals.rbe_pb2'
    # @@protoc_insertion_point(class_scope:swarming.internals.rbe.PollState.ServiceAccountAuth)
    })
  ,

  'LUCIMachineTokenAuth' : _reflection.GeneratedProtocolMessageType('LUCIMachineTokenAuth', (_message.Message,), {
    'DESCRIPTOR' : _POLLSTATE_LUCIMACHINETOKENAUTH,
    '__module__' : 'proto.internals.rbe_pb2'
    # @@protoc_insertion_point(class_scope:swarming.internals.rbe.PollState.LUCIMachineTokenAuth)
    })
  ,

  'IPAllowlistAuth' : _reflection.GeneratedProtocolMessageType('IPAllowlistAuth', (_message.Message,), {
    'DESCRIPTOR' : _POLLSTATE_IPALLOWLISTAUTH,
    '__module__' : 'proto.internals.rbe_pb2'
    # @@protoc_insertion_point(class_scope:swarming.internals.rbe.PollState.IPAllowlistAuth)
    })
  ,
  'DESCRIPTOR' : _POLLSTATE,
  '__module__' : 'proto.internals.rbe_pb2'
  # @@protoc_insertion_point(class_scope:swarming.internals.rbe.PollState)
  })
_sym_db.RegisterMessage(PollState)
_sym_db.RegisterMessage(PollState.Dimension)
_sym_db.RegisterMessage(PollState.DebugInfo)
_sym_db.RegisterMessage(PollState.GCEAuth)
_sym_db.RegisterMessage(PollState.ServiceAccountAuth)
_sym_db.RegisterMessage(PollState.LUCIMachineTokenAuth)
_sym_db.RegisterMessage(PollState.IPAllowlistAuth)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
