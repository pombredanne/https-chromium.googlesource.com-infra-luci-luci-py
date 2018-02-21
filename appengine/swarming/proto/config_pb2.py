# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: config.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='config.proto',
  package='',
  syntax='proto2',
  serialized_pb=_b('\n\x0c\x63onfig.proto\"\xd4\x03\n\x0bSettingsCfg\x12\x18\n\x10google_analytics\x18\x01 \x01(\t\x12\x1e\n\x16reusable_task_age_secs\x18\x02 \x01(\x05\x12\x1e\n\x16\x62ot_death_timeout_secs\x18\x03 \x01(\x05\x12\x1c\n\x14\x65nable_ts_monitoring\x18\x04 \x01(\x08\x12!\n\x07isolate\x18\x05 \x01(\x0b\x32\x10.IsolateSettings\x12\x1b\n\x04\x63ipd\x18\x06 \x01(\x0b\x32\r.CipdSettings\x12$\n\x02mp\x18\x07 \x01(\x0b\x32\x18.MachineProviderSettings\x12,\n$force_bots_to_sleep_and_not_run_task\x18\x08 \x01(\x08\x12\x14\n\x0cui_client_id\x18\t \x01(\t\x12#\n\x1b\x64isplay_server_url_template\x18\x0b \x01(\t\x12\x1a\n\x12max_bot_sleep_time\x18\x0c \x01(\x05\x12\x1b\n\x04\x61uth\x18\r \x01(\x0b\x32\r.AuthSettings\x12\x1e\n\x16\x62ot_isolate_grpc_proxy\x18\x0e \x01(\t\x12\x1f\n\x17\x62ot_swarming_grpc_proxy\x18\x0f \x01(\tJ\x04\x08\n\x10\x0b\"D\n\x0fIsolateSettings\x12\x16\n\x0e\x64\x65\x66\x61ult_server\x18\x01 \x01(\t\x12\x19\n\x11\x64\x65\x66\x61ult_namespace\x18\x02 \x01(\t\"4\n\x0b\x43ipdPackage\x12\x14\n\x0cpackage_name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\"T\n\x0c\x43ipdSettings\x12\x16\n\x0e\x64\x65\x66\x61ult_server\x18\x01 \x01(\t\x12,\n\x16\x64\x65\x66\x61ult_client_package\x18\x02 \x01(\x0b\x32\x0c.CipdPackage\":\n\x17MachineProviderSettings\x12\x0f\n\x07\x65nabled\x18\x01 \x01(\x08\x12\x0e\n\x06server\x18\x02 \x01(\t\"\xb1\x01\n\x0c\x41uthSettings\x12\x14\n\x0c\x61\x64mins_group\x18\x01 \x01(\t\x12\x1b\n\x13\x62ot_bootstrap_group\x18\x02 \x01(\t\x12\x1e\n\x16privileged_users_group\x18\x03 \x01(\t\x12\x13\n\x0busers_group\x18\x04 \x01(\t\x12\x1b\n\x13view_all_bots_group\x18\x05 \x01(\t\x12\x1c\n\x14view_all_tasks_group\x18\x06 \x01(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




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
      options=None),
    _descriptor.FieldDescriptor(
      name='reusable_task_age_secs', full_name='SettingsCfg.reusable_task_age_secs', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_death_timeout_secs', full_name='SettingsCfg.bot_death_timeout_secs', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='enable_ts_monitoring', full_name='SettingsCfg.enable_ts_monitoring', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='isolate', full_name='SettingsCfg.isolate', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cipd', full_name='SettingsCfg.cipd', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mp', full_name='SettingsCfg.mp', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='force_bots_to_sleep_and_not_run_task', full_name='SettingsCfg.force_bots_to_sleep_and_not_run_task', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ui_client_id', full_name='SettingsCfg.ui_client_id', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='display_server_url_template', full_name='SettingsCfg.display_server_url_template', index=9,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_bot_sleep_time', full_name='SettingsCfg.max_bot_sleep_time', index=10,
      number=12, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='auth', full_name='SettingsCfg.auth', index=11,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_isolate_grpc_proxy', full_name='SettingsCfg.bot_isolate_grpc_proxy', index=12,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_swarming_grpc_proxy', full_name='SettingsCfg.bot_swarming_grpc_proxy', index=13,
      number=15, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=17,
  serialized_end=485,
)


_ISOLATESETTINGS = _descriptor.Descriptor(
  name='IsolateSettings',
  full_name='IsolateSettings',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='default_server', full_name='IsolateSettings.default_server', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='default_namespace', full_name='IsolateSettings.default_namespace', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=487,
  serialized_end=555,
)


_CIPDPACKAGE = _descriptor.Descriptor(
  name='CipdPackage',
  full_name='CipdPackage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='package_name', full_name='CipdPackage.package_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='version', full_name='CipdPackage.version', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=557,
  serialized_end=609,
)


_CIPDSETTINGS = _descriptor.Descriptor(
  name='CipdSettings',
  full_name='CipdSettings',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='default_server', full_name='CipdSettings.default_server', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='default_client_package', full_name='CipdSettings.default_client_package', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=611,
  serialized_end=695,
)


_MACHINEPROVIDERSETTINGS = _descriptor.Descriptor(
  name='MachineProviderSettings',
  full_name='MachineProviderSettings',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='enabled', full_name='MachineProviderSettings.enabled', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='server', full_name='MachineProviderSettings.server', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=697,
  serialized_end=755,
)


_AUTHSETTINGS = _descriptor.Descriptor(
  name='AuthSettings',
  full_name='AuthSettings',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='admins_group', full_name='AuthSettings.admins_group', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_bootstrap_group', full_name='AuthSettings.bot_bootstrap_group', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='privileged_users_group', full_name='AuthSettings.privileged_users_group', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='users_group', full_name='AuthSettings.users_group', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='view_all_bots_group', full_name='AuthSettings.view_all_bots_group', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='view_all_tasks_group', full_name='AuthSettings.view_all_tasks_group', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=758,
  serialized_end=935,
)

_SETTINGSCFG.fields_by_name['isolate'].message_type = _ISOLATESETTINGS
_SETTINGSCFG.fields_by_name['cipd'].message_type = _CIPDSETTINGS
_SETTINGSCFG.fields_by_name['mp'].message_type = _MACHINEPROVIDERSETTINGS
_SETTINGSCFG.fields_by_name['auth'].message_type = _AUTHSETTINGS
_CIPDSETTINGS.fields_by_name['default_client_package'].message_type = _CIPDPACKAGE
DESCRIPTOR.message_types_by_name['SettingsCfg'] = _SETTINGSCFG
DESCRIPTOR.message_types_by_name['IsolateSettings'] = _ISOLATESETTINGS
DESCRIPTOR.message_types_by_name['CipdPackage'] = _CIPDPACKAGE
DESCRIPTOR.message_types_by_name['CipdSettings'] = _CIPDSETTINGS
DESCRIPTOR.message_types_by_name['MachineProviderSettings'] = _MACHINEPROVIDERSETTINGS
DESCRIPTOR.message_types_by_name['AuthSettings'] = _AUTHSETTINGS

SettingsCfg = _reflection.GeneratedProtocolMessageType('SettingsCfg', (_message.Message,), dict(
  DESCRIPTOR = _SETTINGSCFG,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:SettingsCfg)
  ))
_sym_db.RegisterMessage(SettingsCfg)

IsolateSettings = _reflection.GeneratedProtocolMessageType('IsolateSettings', (_message.Message,), dict(
  DESCRIPTOR = _ISOLATESETTINGS,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:IsolateSettings)
  ))
_sym_db.RegisterMessage(IsolateSettings)

CipdPackage = _reflection.GeneratedProtocolMessageType('CipdPackage', (_message.Message,), dict(
  DESCRIPTOR = _CIPDPACKAGE,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:CipdPackage)
  ))
_sym_db.RegisterMessage(CipdPackage)

CipdSettings = _reflection.GeneratedProtocolMessageType('CipdSettings', (_message.Message,), dict(
  DESCRIPTOR = _CIPDSETTINGS,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:CipdSettings)
  ))
_sym_db.RegisterMessage(CipdSettings)

MachineProviderSettings = _reflection.GeneratedProtocolMessageType('MachineProviderSettings', (_message.Message,), dict(
  DESCRIPTOR = _MACHINEPROVIDERSETTINGS,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:MachineProviderSettings)
  ))
_sym_db.RegisterMessage(MachineProviderSettings)

AuthSettings = _reflection.GeneratedProtocolMessageType('AuthSettings', (_message.Message,), dict(
  DESCRIPTOR = _AUTHSETTINGS,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:AuthSettings)
  ))
_sym_db.RegisterMessage(AuthSettings)


# @@protoc_insertion_point(module_scope)
