# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: components/auth/proto/replication.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='components/auth/proto/replication.proto',
  package='components.auth',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\'components/auth/proto/replication.proto\x12\x0f\x63omponents.auth\"b\n\x11ServiceLinkTicket\x12\x12\n\nprimary_id\x18\x01 \x01(\t\x12\x13\n\x0bprimary_url\x18\x02 \x01(\t\x12\x14\n\x0cgenerated_by\x18\x03 \x01(\t\x12\x0e\n\x06ticket\x18\x04 \x01(\x0c\"O\n\x12ServiceLinkRequest\x12\x0e\n\x06ticket\x18\x01 \x01(\x0c\x12\x13\n\x0breplica_url\x18\x02 \x01(\t\x12\x14\n\x0cinitiated_by\x18\x03 \x01(\t\"\x9e\x01\n\x13ServiceLinkResponse\x12;\n\x06status\x18\x01 \x01(\x0e\x32+.components.auth.ServiceLinkResponse.Status\"J\n\x06Status\x12\x0b\n\x07SUCCESS\x10\x00\x12\x13\n\x0fTRANSPORT_ERROR\x10\x01\x12\x0e\n\nBAD_TICKET\x10\x02\x12\x0e\n\nAUTH_ERROR\x10\x03\"\xc0\x01\n\tAuthGroup\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07members\x18\x02 \x03(\t\x12\r\n\x05globs\x18\x03 \x03(\t\x12\x0e\n\x06nested\x18\x04 \x03(\t\x12\x13\n\x0b\x64\x65scription\x18\x05 \x01(\t\x12\x12\n\ncreated_ts\x18\x06 \x01(\x03\x12\x12\n\ncreated_by\x18\x07 \x01(\t\x12\x13\n\x0bmodified_ts\x18\x08 \x01(\x03\x12\x13\n\x0bmodified_by\x18\t \x01(\t\x12\x0e\n\x06owners\x18\n \x01(\t\"\x97\x01\n\x0f\x41uthIPWhitelist\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07subnets\x18\x02 \x03(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\x12\x12\n\ncreated_ts\x18\x04 \x01(\x03\x12\x12\n\ncreated_by\x18\x05 \x01(\t\x12\x13\n\x0bmodified_ts\x18\x06 \x01(\x03\x12\x13\n\x0bmodified_by\x18\x07 \x01(\t\"|\n\x19\x41uthIPWhitelistAssignment\x12\x10\n\x08identity\x18\x01 \x01(\t\x12\x14\n\x0cip_whitelist\x18\x02 \x01(\t\x12\x0f\n\x07\x63omment\x18\x03 \x01(\t\x12\x12\n\ncreated_ts\x18\x04 \x01(\x03\x12\x12\n\ncreated_by\x18\x05 \x01(\t\"\xb6\x02\n\x06\x41uthDB\x12\x17\n\x0foauth_client_id\x18\x01 \x01(\t\x12\x1b\n\x13oauth_client_secret\x18\x02 \x01(\t\x12#\n\x1boauth_additional_client_ids\x18\x03 \x03(\t\x12*\n\x06groups\x18\x04 \x03(\x0b\x32\x1a.components.auth.AuthGroup\x12\x37\n\rip_whitelists\x18\x06 \x03(\x0b\x32 .components.auth.AuthIPWhitelist\x12L\n\x18ip_whitelist_assignments\x18\x07 \x03(\x0b\x32*.components.auth.AuthIPWhitelistAssignment\x12\x18\n\x10token_server_url\x18\x08 \x01(\tJ\x04\x08\x05\x10\x06\"N\n\x0e\x41uthDBRevision\x12\x12\n\nprimary_id\x18\x01 \x01(\t\x12\x13\n\x0b\x61uth_db_rev\x18\x02 \x01(\x03\x12\x13\n\x0bmodified_ts\x18\x03 \x01(\x03\"G\n\x12\x43hangeNotification\x12\x31\n\x08revision\x18\x01 \x01(\x0b\x32\x1f.components.auth.AuthDBRevision\"\x90\x01\n\x16ReplicationPushRequest\x12\x31\n\x08revision\x18\x01 \x01(\x0b\x32\x1f.components.auth.AuthDBRevision\x12(\n\x07\x61uth_db\x18\x02 \x01(\x0b\x32\x17.components.auth.AuthDB\x12\x19\n\x11\x61uth_code_version\x18\x03 \x01(\t\"\xbf\x03\n\x17ReplicationPushResponse\x12?\n\x06status\x18\x01 \x01(\x0e\x32/.components.auth.ReplicationPushResponse.Status\x12\x39\n\x10\x63urrent_revision\x18\x02 \x01(\x0b\x32\x1f.components.auth.AuthDBRevision\x12\x46\n\nerror_code\x18\x03 \x01(\x0e\x32\x32.components.auth.ReplicationPushResponse.ErrorCode\x12\x19\n\x11\x61uth_code_version\x18\x04 \x01(\t\"H\n\x06Status\x12\x0b\n\x07\x41PPLIED\x10\x00\x12\x0b\n\x07SKIPPED\x10\x01\x12\x13\n\x0fTRANSIENT_ERROR\x10\x02\x12\x0f\n\x0b\x46\x41TAL_ERROR\x10\x03\"{\n\tErrorCode\x12\x11\n\rERROR_UNKNOWN\x10\x00\x12\x11\n\rNOT_A_REPLICA\x10\x01\x12\r\n\tFORBIDDEN\x10\x02\x12\x15\n\x11MISSING_SIGNATURE\x10\x03\x12\x11\n\rBAD_SIGNATURE\x10\x04\x12\x0f\n\x0b\x42\x41\x44_REQUEST\x10\x05\x62\x06proto3')
)



_SERVICELINKRESPONSE_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='components.auth.ServiceLinkResponse.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TRANSPORT_ERROR', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_TICKET', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='AUTH_ERROR', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=326,
  serialized_end=400,
)
_sym_db.RegisterEnumDescriptor(_SERVICELINKRESPONSE_STATUS)

_REPLICATIONPUSHRESPONSE_STATUS = _descriptor.EnumDescriptor(
  name='Status',
  full_name='components.auth.ReplicationPushResponse.Status',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='APPLIED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SKIPPED', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TRANSIENT_ERROR', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FATAL_ERROR', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1741,
  serialized_end=1813,
)
_sym_db.RegisterEnumDescriptor(_REPLICATIONPUSHRESPONSE_STATUS)

_REPLICATIONPUSHRESPONSE_ERRORCODE = _descriptor.EnumDescriptor(
  name='ErrorCode',
  full_name='components.auth.ReplicationPushResponse.ErrorCode',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ERROR_UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NOT_A_REPLICA', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FORBIDDEN', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='MISSING_SIGNATURE', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_SIGNATURE', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='BAD_REQUEST', index=5, number=5,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1815,
  serialized_end=1938,
)
_sym_db.RegisterEnumDescriptor(_REPLICATIONPUSHRESPONSE_ERRORCODE)


_SERVICELINKTICKET = _descriptor.Descriptor(
  name='ServiceLinkTicket',
  full_name='components.auth.ServiceLinkTicket',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='primary_id', full_name='components.auth.ServiceLinkTicket.primary_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='primary_url', full_name='components.auth.ServiceLinkTicket.primary_url', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='generated_by', full_name='components.auth.ServiceLinkTicket.generated_by', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ticket', full_name='components.auth.ServiceLinkTicket.ticket', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
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
  serialized_start=60,
  serialized_end=158,
)


_SERVICELINKREQUEST = _descriptor.Descriptor(
  name='ServiceLinkRequest',
  full_name='components.auth.ServiceLinkRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ticket', full_name='components.auth.ServiceLinkRequest.ticket', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='replica_url', full_name='components.auth.ServiceLinkRequest.replica_url', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='initiated_by', full_name='components.auth.ServiceLinkRequest.initiated_by', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=160,
  serialized_end=239,
)


_SERVICELINKRESPONSE = _descriptor.Descriptor(
  name='ServiceLinkResponse',
  full_name='components.auth.ServiceLinkResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='components.auth.ServiceLinkResponse.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SERVICELINKRESPONSE_STATUS,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=242,
  serialized_end=400,
)


_AUTHGROUP = _descriptor.Descriptor(
  name='AuthGroup',
  full_name='components.auth.AuthGroup',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='components.auth.AuthGroup.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='members', full_name='components.auth.AuthGroup.members', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='globs', full_name='components.auth.AuthGroup.globs', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nested', full_name='components.auth.AuthGroup.nested', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='components.auth.AuthGroup.description', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_ts', full_name='components.auth.AuthGroup.created_ts', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_by', full_name='components.auth.AuthGroup.created_by', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='modified_ts', full_name='components.auth.AuthGroup.modified_ts', index=7,
      number=8, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='modified_by', full_name='components.auth.AuthGroup.modified_by', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='owners', full_name='components.auth.AuthGroup.owners', index=9,
      number=10, type=9, cpp_type=9, label=1,
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
  serialized_start=403,
  serialized_end=595,
)


_AUTHIPWHITELIST = _descriptor.Descriptor(
  name='AuthIPWhitelist',
  full_name='components.auth.AuthIPWhitelist',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='components.auth.AuthIPWhitelist.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='subnets', full_name='components.auth.AuthIPWhitelist.subnets', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='description', full_name='components.auth.AuthIPWhitelist.description', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_ts', full_name='components.auth.AuthIPWhitelist.created_ts', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_by', full_name='components.auth.AuthIPWhitelist.created_by', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='modified_ts', full_name='components.auth.AuthIPWhitelist.modified_ts', index=5,
      number=6, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='modified_by', full_name='components.auth.AuthIPWhitelist.modified_by', index=6,
      number=7, type=9, cpp_type=9, label=1,
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
  serialized_start=598,
  serialized_end=749,
)


_AUTHIPWHITELISTASSIGNMENT = _descriptor.Descriptor(
  name='AuthIPWhitelistAssignment',
  full_name='components.auth.AuthIPWhitelistAssignment',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='identity', full_name='components.auth.AuthIPWhitelistAssignment.identity', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ip_whitelist', full_name='components.auth.AuthIPWhitelistAssignment.ip_whitelist', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='comment', full_name='components.auth.AuthIPWhitelistAssignment.comment', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_ts', full_name='components.auth.AuthIPWhitelistAssignment.created_ts', index=3,
      number=4, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='created_by', full_name='components.auth.AuthIPWhitelistAssignment.created_by', index=4,
      number=5, type=9, cpp_type=9, label=1,
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
  serialized_start=751,
  serialized_end=875,
)


_AUTHDB = _descriptor.Descriptor(
  name='AuthDB',
  full_name='components.auth.AuthDB',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='oauth_client_id', full_name='components.auth.AuthDB.oauth_client_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='oauth_client_secret', full_name='components.auth.AuthDB.oauth_client_secret', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='oauth_additional_client_ids', full_name='components.auth.AuthDB.oauth_additional_client_ids', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='groups', full_name='components.auth.AuthDB.groups', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ip_whitelists', full_name='components.auth.AuthDB.ip_whitelists', index=4,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ip_whitelist_assignments', full_name='components.auth.AuthDB.ip_whitelist_assignments', index=5,
      number=7, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='token_server_url', full_name='components.auth.AuthDB.token_server_url', index=6,
      number=8, type=9, cpp_type=9, label=1,
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
  serialized_start=878,
  serialized_end=1188,
)


_AUTHDBREVISION = _descriptor.Descriptor(
  name='AuthDBRevision',
  full_name='components.auth.AuthDBRevision',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='primary_id', full_name='components.auth.AuthDBRevision.primary_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='auth_db_rev', full_name='components.auth.AuthDBRevision.auth_db_rev', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='modified_ts', full_name='components.auth.AuthDBRevision.modified_ts', index=2,
      number=3, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=1190,
  serialized_end=1268,
)


_CHANGENOTIFICATION = _descriptor.Descriptor(
  name='ChangeNotification',
  full_name='components.auth.ChangeNotification',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='revision', full_name='components.auth.ChangeNotification.revision', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=1270,
  serialized_end=1341,
)


_REPLICATIONPUSHREQUEST = _descriptor.Descriptor(
  name='ReplicationPushRequest',
  full_name='components.auth.ReplicationPushRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='revision', full_name='components.auth.ReplicationPushRequest.revision', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='auth_db', full_name='components.auth.ReplicationPushRequest.auth_db', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='auth_code_version', full_name='components.auth.ReplicationPushRequest.auth_code_version', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  serialized_start=1344,
  serialized_end=1488,
)


_REPLICATIONPUSHRESPONSE = _descriptor.Descriptor(
  name='ReplicationPushResponse',
  full_name='components.auth.ReplicationPushResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='components.auth.ReplicationPushResponse.status', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='current_revision', full_name='components.auth.ReplicationPushResponse.current_revision', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='error_code', full_name='components.auth.ReplicationPushResponse.error_code', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='auth_code_version', full_name='components.auth.ReplicationPushResponse.auth_code_version', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _REPLICATIONPUSHRESPONSE_STATUS,
    _REPLICATIONPUSHRESPONSE_ERRORCODE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1491,
  serialized_end=1938,
)

_SERVICELINKRESPONSE.fields_by_name['status'].enum_type = _SERVICELINKRESPONSE_STATUS
_SERVICELINKRESPONSE_STATUS.containing_type = _SERVICELINKRESPONSE
_AUTHDB.fields_by_name['groups'].message_type = _AUTHGROUP
_AUTHDB.fields_by_name['ip_whitelists'].message_type = _AUTHIPWHITELIST
_AUTHDB.fields_by_name['ip_whitelist_assignments'].message_type = _AUTHIPWHITELISTASSIGNMENT
_CHANGENOTIFICATION.fields_by_name['revision'].message_type = _AUTHDBREVISION
_REPLICATIONPUSHREQUEST.fields_by_name['revision'].message_type = _AUTHDBREVISION
_REPLICATIONPUSHREQUEST.fields_by_name['auth_db'].message_type = _AUTHDB
_REPLICATIONPUSHRESPONSE.fields_by_name['status'].enum_type = _REPLICATIONPUSHRESPONSE_STATUS
_REPLICATIONPUSHRESPONSE.fields_by_name['current_revision'].message_type = _AUTHDBREVISION
_REPLICATIONPUSHRESPONSE.fields_by_name['error_code'].enum_type = _REPLICATIONPUSHRESPONSE_ERRORCODE
_REPLICATIONPUSHRESPONSE_STATUS.containing_type = _REPLICATIONPUSHRESPONSE
_REPLICATIONPUSHRESPONSE_ERRORCODE.containing_type = _REPLICATIONPUSHRESPONSE
DESCRIPTOR.message_types_by_name['ServiceLinkTicket'] = _SERVICELINKTICKET
DESCRIPTOR.message_types_by_name['ServiceLinkRequest'] = _SERVICELINKREQUEST
DESCRIPTOR.message_types_by_name['ServiceLinkResponse'] = _SERVICELINKRESPONSE
DESCRIPTOR.message_types_by_name['AuthGroup'] = _AUTHGROUP
DESCRIPTOR.message_types_by_name['AuthIPWhitelist'] = _AUTHIPWHITELIST
DESCRIPTOR.message_types_by_name['AuthIPWhitelistAssignment'] = _AUTHIPWHITELISTASSIGNMENT
DESCRIPTOR.message_types_by_name['AuthDB'] = _AUTHDB
DESCRIPTOR.message_types_by_name['AuthDBRevision'] = _AUTHDBREVISION
DESCRIPTOR.message_types_by_name['ChangeNotification'] = _CHANGENOTIFICATION
DESCRIPTOR.message_types_by_name['ReplicationPushRequest'] = _REPLICATIONPUSHREQUEST
DESCRIPTOR.message_types_by_name['ReplicationPushResponse'] = _REPLICATIONPUSHRESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

ServiceLinkTicket = _reflection.GeneratedProtocolMessageType('ServiceLinkTicket', (_message.Message,), dict(
  DESCRIPTOR = _SERVICELINKTICKET,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.ServiceLinkTicket)
  ))
_sym_db.RegisterMessage(ServiceLinkTicket)

ServiceLinkRequest = _reflection.GeneratedProtocolMessageType('ServiceLinkRequest', (_message.Message,), dict(
  DESCRIPTOR = _SERVICELINKREQUEST,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.ServiceLinkRequest)
  ))
_sym_db.RegisterMessage(ServiceLinkRequest)

ServiceLinkResponse = _reflection.GeneratedProtocolMessageType('ServiceLinkResponse', (_message.Message,), dict(
  DESCRIPTOR = _SERVICELINKRESPONSE,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.ServiceLinkResponse)
  ))
_sym_db.RegisterMessage(ServiceLinkResponse)

AuthGroup = _reflection.GeneratedProtocolMessageType('AuthGroup', (_message.Message,), dict(
  DESCRIPTOR = _AUTHGROUP,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.AuthGroup)
  ))
_sym_db.RegisterMessage(AuthGroup)

AuthIPWhitelist = _reflection.GeneratedProtocolMessageType('AuthIPWhitelist', (_message.Message,), dict(
  DESCRIPTOR = _AUTHIPWHITELIST,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.AuthIPWhitelist)
  ))
_sym_db.RegisterMessage(AuthIPWhitelist)

AuthIPWhitelistAssignment = _reflection.GeneratedProtocolMessageType('AuthIPWhitelistAssignment', (_message.Message,), dict(
  DESCRIPTOR = _AUTHIPWHITELISTASSIGNMENT,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.AuthIPWhitelistAssignment)
  ))
_sym_db.RegisterMessage(AuthIPWhitelistAssignment)

AuthDB = _reflection.GeneratedProtocolMessageType('AuthDB', (_message.Message,), dict(
  DESCRIPTOR = _AUTHDB,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.AuthDB)
  ))
_sym_db.RegisterMessage(AuthDB)

AuthDBRevision = _reflection.GeneratedProtocolMessageType('AuthDBRevision', (_message.Message,), dict(
  DESCRIPTOR = _AUTHDBREVISION,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.AuthDBRevision)
  ))
_sym_db.RegisterMessage(AuthDBRevision)

ChangeNotification = _reflection.GeneratedProtocolMessageType('ChangeNotification', (_message.Message,), dict(
  DESCRIPTOR = _CHANGENOTIFICATION,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.ChangeNotification)
  ))
_sym_db.RegisterMessage(ChangeNotification)

ReplicationPushRequest = _reflection.GeneratedProtocolMessageType('ReplicationPushRequest', (_message.Message,), dict(
  DESCRIPTOR = _REPLICATIONPUSHREQUEST,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.ReplicationPushRequest)
  ))
_sym_db.RegisterMessage(ReplicationPushRequest)

ReplicationPushResponse = _reflection.GeneratedProtocolMessageType('ReplicationPushResponse', (_message.Message,), dict(
  DESCRIPTOR = _REPLICATIONPUSHRESPONSE,
  __module__ = 'components.auth.proto.replication_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.ReplicationPushResponse)
  ))
_sym_db.RegisterMessage(ReplicationPushResponse)


# @@protoc_insertion_point(module_scope)
