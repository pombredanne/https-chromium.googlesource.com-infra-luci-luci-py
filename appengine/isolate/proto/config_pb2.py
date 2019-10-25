# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: config.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='config.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x0c\x63onfig.proto\"\x98\x02\n\x0bSettingsCfg\x12\x18\n\x10google_analytics\x18\x01 \x01(\t\x12\x1a\n\x12\x64\x65\x66\x61ult_expiration\x18\x02 \x01(\x05\x12\x18\n\x10sharding_letters\x18\x03 \x01(\x05\x12\x11\n\tgs_bucket\x18\x04 \x01(\t\x12\x1a\n\x12gs_client_id_email\x18\x05 \x01(\t\x12\x1c\n\x14\x65nable_ts_monitoring\x18\x06 \x01(\x08\x12\x1b\n\x04\x61uth\x18\x07 \x01(\x0b\x32\r.AuthSettings\x12\x14\n\x0cui_client_id\x18\x08 \x01(\t\x12\x39\n\x18\x63lient_monitoring_config\x18\t \x03(\x0b\x32\x17.ClientMonitoringConfig\"H\n\x0c\x41uthSettings\x12\x19\n\x11\x66ull_access_group\x18\x01 \x01(\t\x12\x1d\n\x15readonly_access_group\x18\x02 \x01(\t\"=\n\x16\x43lientMonitoringConfig\x12\x14\n\x0cip_whitelist\x18\x01 \x01(\t\x12\r\n\x05label\x18\x02 \x01(\t')
)




_SETTINGSCFG = _descriptor.Descriptor(
  name='SettingsCfg',
  full_name='SettingsCfg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='google_analytics', full_name='SettingsCfg.google_analytics', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='default_expiration', full_name='SettingsCfg.default_expiration', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sharding_letters', full_name='SettingsCfg.sharding_letters', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gs_bucket', full_name='SettingsCfg.gs_bucket', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='gs_client_id_email', full_name='SettingsCfg.gs_client_id_email', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='enable_ts_monitoring', full_name='SettingsCfg.enable_ts_monitoring', index=5,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='auth', full_name='SettingsCfg.auth', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='ui_client_id', full_name='SettingsCfg.ui_client_id', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='client_monitoring_config', full_name='SettingsCfg.client_monitoring_config', index=8,
      number=9, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=17,
  serialized_end=297,
)


_AUTHSETTINGS = _descriptor.Descriptor(
  name='AuthSettings',
  full_name='AuthSettings',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='full_access_group', full_name='AuthSettings.full_access_group', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='readonly_access_group', full_name='AuthSettings.readonly_access_group', index=1,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=299,
  serialized_end=371,
)


_CLIENTMONITORINGCONFIG = _descriptor.Descriptor(
  name='ClientMonitoringConfig',
  full_name='ClientMonitoringConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ip_whitelist', full_name='ClientMonitoringConfig.ip_whitelist', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='label', full_name='ClientMonitoringConfig.label', index=1,
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
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=373,
  serialized_end=434,
)

_SETTINGSCFG.fields_by_name['auth'].message_type = _AUTHSETTINGS
_SETTINGSCFG.fields_by_name['client_monitoring_config'].message_type = _CLIENTMONITORINGCONFIG
DESCRIPTOR.message_types_by_name['SettingsCfg'] = _SETTINGSCFG
DESCRIPTOR.message_types_by_name['AuthSettings'] = _AUTHSETTINGS
DESCRIPTOR.message_types_by_name['ClientMonitoringConfig'] = _CLIENTMONITORINGCONFIG
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SettingsCfg = _reflection.GeneratedProtocolMessageType('SettingsCfg', (_message.Message,), dict(
  DESCRIPTOR = _SETTINGSCFG,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:SettingsCfg)
  ))
_sym_db.RegisterMessage(SettingsCfg)

AuthSettings = _reflection.GeneratedProtocolMessageType('AuthSettings', (_message.Message,), dict(
  DESCRIPTOR = _AUTHSETTINGS,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:AuthSettings)
  ))
_sym_db.RegisterMessage(AuthSettings)

ClientMonitoringConfig = _reflection.GeneratedProtocolMessageType('ClientMonitoringConfig', (_message.Message,), dict(
  DESCRIPTOR = _CLIENTMONITORINGCONFIG,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:ClientMonitoringConfig)
  ))
_sym_db.RegisterMessage(ClientMonitoringConfig)


# @@protoc_insertion_point(module_scope)
