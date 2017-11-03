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
  package='gce_backend',
  syntax='proto2',
  serialized_pb=_b('\n\x0c\x63onfig.proto\x12\x0bgce_backend\"\xd0\x07\n\x16InstanceTemplateConfig\x12G\n\ttemplates\x18\x01 \x03(\x0b\x32\x34.gce_backend.InstanceTemplateConfig.InstanceTemplate\x1a\xec\x06\n\x10InstanceTemplate\x12\x11\n\tbase_name\x18\x01 \x01(\t\x12\x0f\n\x07project\x18\x02 \x01(\t\x12\x12\n\ndimensions\x18\x03 \x03(\t\x12\x12\n\nimage_name\x18\x04 \x01(\t\x12\x15\n\rimage_project\x18\n \x01(\t\x12\x14\n\x0c\x64isk_size_gb\x18\x05 \x01(\x05\x12]\n\x10service_accounts\x18\x06 \x03(\x0b\x32\x43.gce_backend.InstanceTemplateConfig.InstanceTemplate.ServiceAccount\x12\x0c\n\x04tags\x18\x07 \x03(\t\x12\x10\n\x08metadata\x18\x08 \x03(\t\x12\x14\n\x0cmachine_type\x18\t \x01(\t\x12\x13\n\x0bnetwork_url\x18\x0b \x01(\t\x12\x1f\n\x17\x61uto_assign_external_ip\x18\x0c \x01(\x08\x12\x18\n\x10min_cpu_platform\x18\r \x01(\t\x12\x61\n\x12guest_accelerators\x18\x0e \x03(\x0b\x32\x45.gce_backend.InstanceTemplateConfig.InstanceTemplate.GuestAccelerator\x12S\n\nscheduling\x18\x0f \x01(\x0b\x32?.gce_backend.InstanceTemplateConfig.InstanceTemplate.Scheduling\x1a.\n\x0eServiceAccount\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0e\n\x06scopes\x18\x02 \x03(\t\x1aG\n\x10GuestAccelerator\x12\x18\n\x10\x61\x63\x63\x65lerator_type\x18\x01 \x01(\t\x12\x19\n\x11\x61\x63\x63\x65lerator_count\x18\x02 \x01(\x05\x1a\xc8\x01\n\nScheduling\x12n\n\x13on_host_maintenance\x18\x01 \x01(\x0e\x32Q.gce_backend.InstanceTemplateConfig.InstanceTemplate.Scheduling.OnHostMaintenance\x12\x19\n\x11\x61utomatic_restart\x18\x02 \x01(\x08\"/\n\x11OnHostMaintenance\x12\x0b\n\x07MIGRATE\x10\x00\x12\r\n\tTERMINATE\x10\x01\"\xda\x01\n\x1aInstanceGroupManagerConfig\x12N\n\x08managers\x18\x01 \x03(\x0b\x32<.gce_backend.InstanceGroupManagerConfig.InstanceGroupManager\x1al\n\x14InstanceGroupManager\x12\x1a\n\x12template_base_name\x18\x01 \x01(\t\x12\x14\n\x0cminimum_size\x18\x02 \x01(\x05\x12\x14\n\x0cmaximum_size\x18\x03 \x01(\x05\x12\x0c\n\x04zone\x18\x04 \x01(\t\">\n\x0bSettingsCfg\x12\x1c\n\x14\x65nable_ts_monitoring\x18\x01 \x01(\x08\x12\x11\n\tmp_server\x18\x02 \x01(\t')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING_ONHOSTMAINTENANCE = _descriptor.EnumDescriptor(
  name='OnHostMaintenance',
  full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.Scheduling.OnHostMaintenance',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='MIGRATE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TERMINATE', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=959,
  serialized_end=1006,
)
_sym_db.RegisterEnumDescriptor(_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING_ONHOSTMAINTENANCE)


_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SERVICEACCOUNT = _descriptor.Descriptor(
  name='ServiceAccount',
  full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.ServiceAccount',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.ServiceAccount.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='scopes', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.ServiceAccount.scopes', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=684,
  serialized_end=730,
)

_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_GUESTACCELERATOR = _descriptor.Descriptor(
  name='GuestAccelerator',
  full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.GuestAccelerator',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='accelerator_type', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.GuestAccelerator.accelerator_type', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='accelerator_count', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.GuestAccelerator.accelerator_count', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=732,
  serialized_end=803,
)

_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING = _descriptor.Descriptor(
  name='Scheduling',
  full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.Scheduling',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='on_host_maintenance', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.Scheduling.on_host_maintenance', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='automatic_restart', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.Scheduling.automatic_restart', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING_ONHOSTMAINTENANCE,
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=806,
  serialized_end=1006,
)

_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE = _descriptor.Descriptor(
  name='InstanceTemplate',
  full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='base_name', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.base_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='project', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.project', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dimensions', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.dimensions', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='image_name', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.image_name', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='image_project', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.image_project', index=4,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='disk_size_gb', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.disk_size_gb', index=5,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='service_accounts', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.service_accounts', index=6,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tags', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.tags', index=7,
      number=7, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='metadata', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.metadata', index=8,
      number=8, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='machine_type', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.machine_type', index=9,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='network_url', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.network_url', index=10,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='auto_assign_external_ip', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.auto_assign_external_ip', index=11,
      number=12, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='min_cpu_platform', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.min_cpu_platform', index=12,
      number=13, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='guest_accelerators', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.guest_accelerators', index=13,
      number=14, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='scheduling', full_name='gce_backend.InstanceTemplateConfig.InstanceTemplate.scheduling', index=14,
      number=15, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SERVICEACCOUNT, _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_GUESTACCELERATOR, _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=130,
  serialized_end=1006,
)

_INSTANCETEMPLATECONFIG = _descriptor.Descriptor(
  name='InstanceTemplateConfig',
  full_name='gce_backend.InstanceTemplateConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='templates', full_name='gce_backend.InstanceTemplateConfig.templates', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=30,
  serialized_end=1006,
)


_INSTANCEGROUPMANAGERCONFIG_INSTANCEGROUPMANAGER = _descriptor.Descriptor(
  name='InstanceGroupManager',
  full_name='gce_backend.InstanceGroupManagerConfig.InstanceGroupManager',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='template_base_name', full_name='gce_backend.InstanceGroupManagerConfig.InstanceGroupManager.template_base_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='minimum_size', full_name='gce_backend.InstanceGroupManagerConfig.InstanceGroupManager.minimum_size', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='maximum_size', full_name='gce_backend.InstanceGroupManagerConfig.InstanceGroupManager.maximum_size', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='zone', full_name='gce_backend.InstanceGroupManagerConfig.InstanceGroupManager.zone', index=3,
      number=4, type=9, cpp_type=9, label=1,
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
  serialized_start=1119,
  serialized_end=1227,
)

_INSTANCEGROUPMANAGERCONFIG = _descriptor.Descriptor(
  name='InstanceGroupManagerConfig',
  full_name='gce_backend.InstanceGroupManagerConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='managers', full_name='gce_backend.InstanceGroupManagerConfig.managers', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_INSTANCEGROUPMANAGERCONFIG_INSTANCEGROUPMANAGER, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1009,
  serialized_end=1227,
)


_SETTINGSCFG = _descriptor.Descriptor(
  name='SettingsCfg',
  full_name='gce_backend.SettingsCfg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='enable_ts_monitoring', full_name='gce_backend.SettingsCfg.enable_ts_monitoring', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='mp_server', full_name='gce_backend.SettingsCfg.mp_server', index=1,
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
  serialized_start=1229,
  serialized_end=1291,
)

_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SERVICEACCOUNT.containing_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_GUESTACCELERATOR.containing_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING.fields_by_name['on_host_maintenance'].enum_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING_ONHOSTMAINTENANCE
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING.containing_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING_ONHOSTMAINTENANCE.containing_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE.fields_by_name['service_accounts'].message_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SERVICEACCOUNT
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE.fields_by_name['guest_accelerators'].message_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_GUESTACCELERATOR
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE.fields_by_name['scheduling'].message_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING
_INSTANCETEMPLATECONFIG_INSTANCETEMPLATE.containing_type = _INSTANCETEMPLATECONFIG
_INSTANCETEMPLATECONFIG.fields_by_name['templates'].message_type = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE
_INSTANCEGROUPMANAGERCONFIG_INSTANCEGROUPMANAGER.containing_type = _INSTANCEGROUPMANAGERCONFIG
_INSTANCEGROUPMANAGERCONFIG.fields_by_name['managers'].message_type = _INSTANCEGROUPMANAGERCONFIG_INSTANCEGROUPMANAGER
DESCRIPTOR.message_types_by_name['InstanceTemplateConfig'] = _INSTANCETEMPLATECONFIG
DESCRIPTOR.message_types_by_name['InstanceGroupManagerConfig'] = _INSTANCEGROUPMANAGERCONFIG
DESCRIPTOR.message_types_by_name['SettingsCfg'] = _SETTINGSCFG

InstanceTemplateConfig = _reflection.GeneratedProtocolMessageType('InstanceTemplateConfig', (_message.Message,), dict(

  InstanceTemplate = _reflection.GeneratedProtocolMessageType('InstanceTemplate', (_message.Message,), dict(

    ServiceAccount = _reflection.GeneratedProtocolMessageType('ServiceAccount', (_message.Message,), dict(
      DESCRIPTOR = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SERVICEACCOUNT,
      __module__ = 'config_pb2'
      # @@protoc_insertion_point(class_scope:gce_backend.InstanceTemplateConfig.InstanceTemplate.ServiceAccount)
      ))
    ,

    GuestAccelerator = _reflection.GeneratedProtocolMessageType('GuestAccelerator', (_message.Message,), dict(
      DESCRIPTOR = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_GUESTACCELERATOR,
      __module__ = 'config_pb2'
      # @@protoc_insertion_point(class_scope:gce_backend.InstanceTemplateConfig.InstanceTemplate.GuestAccelerator)
      ))
    ,

    Scheduling = _reflection.GeneratedProtocolMessageType('Scheduling', (_message.Message,), dict(
      DESCRIPTOR = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE_SCHEDULING,
      __module__ = 'config_pb2'
      # @@protoc_insertion_point(class_scope:gce_backend.InstanceTemplateConfig.InstanceTemplate.Scheduling)
      ))
    ,
    DESCRIPTOR = _INSTANCETEMPLATECONFIG_INSTANCETEMPLATE,
    __module__ = 'config_pb2'
    # @@protoc_insertion_point(class_scope:gce_backend.InstanceTemplateConfig.InstanceTemplate)
    ))
  ,
  DESCRIPTOR = _INSTANCETEMPLATECONFIG,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:gce_backend.InstanceTemplateConfig)
  ))
_sym_db.RegisterMessage(InstanceTemplateConfig)
_sym_db.RegisterMessage(InstanceTemplateConfig.InstanceTemplate)
_sym_db.RegisterMessage(InstanceTemplateConfig.InstanceTemplate.ServiceAccount)
_sym_db.RegisterMessage(InstanceTemplateConfig.InstanceTemplate.GuestAccelerator)
_sym_db.RegisterMessage(InstanceTemplateConfig.InstanceTemplate.Scheduling)

InstanceGroupManagerConfig = _reflection.GeneratedProtocolMessageType('InstanceGroupManagerConfig', (_message.Message,), dict(

  InstanceGroupManager = _reflection.GeneratedProtocolMessageType('InstanceGroupManager', (_message.Message,), dict(
    DESCRIPTOR = _INSTANCEGROUPMANAGERCONFIG_INSTANCEGROUPMANAGER,
    __module__ = 'config_pb2'
    # @@protoc_insertion_point(class_scope:gce_backend.InstanceGroupManagerConfig.InstanceGroupManager)
    ))
  ,
  DESCRIPTOR = _INSTANCEGROUPMANAGERCONFIG,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:gce_backend.InstanceGroupManagerConfig)
  ))
_sym_db.RegisterMessage(InstanceGroupManagerConfig)
_sym_db.RegisterMessage(InstanceGroupManagerConfig.InstanceGroupManager)

SettingsCfg = _reflection.GeneratedProtocolMessageType('SettingsCfg', (_message.Message,), dict(
  DESCRIPTOR = _SETTINGSCFG,
  __module__ = 'config_pb2'
  # @@protoc_insertion_point(class_scope:gce_backend.SettingsCfg)
  ))
_sym_db.RegisterMessage(SettingsCfg)


# @@protoc_insertion_point(module_scope)
