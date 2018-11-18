# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pools.proto

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
  name='pools.proto',
  package='swarming',
  syntax='proto3',
  serialized_pb=_b('\n\x0bpools.proto\x12\x08swarming\"\xa9\x02\n\x08PoolsCfg\x12\x1c\n\x04pool\x18\x01 \x03(\x0b\x32\x0e.swarming.Pool\x12\x1c\n\x14\x66orbid_unknown_pools\x18\x02 \x01(\x08\x12=\n\x19\x64\x65\x66\x61ult_external_services\x18\x06 \x01(\x0b\x32\x1a.swarming.ExternalServices\x12-\n\rtask_template\x18\x03 \x03(\x0b\x32\x16.swarming.TaskTemplate\x12\x42\n\x18task_template_deployment\x18\x04 \x03(\x0b\x32 .swarming.TaskTemplateDeployment\x12/\n\x0e\x62ot_monitoring\x18\x05 \x03(\x0b\x32\x17.swarming.BotMonitoring\"\xf9\x02\n\x04Pool\x12\x0c\n\x04name\x18\x01 \x03(\t\x12\x0e\n\x06owners\x18\x02 \x03(\t\x12(\n\nschedulers\x18\x03 \x01(\x0b\x32\x14.swarming.Schedulers\x12\x1f\n\x17\x61llowed_service_account\x18\x04 \x03(\t\x12%\n\x1d\x61llowed_service_account_group\x18\x05 \x03(\t\x12\"\n\x18task_template_deployment\x18\x06 \x01(\tH\x00\x12K\n\x1ftask_template_deployment_inline\x18\x07 \x01(\x0b\x32 .swarming.TaskTemplateDeploymentH\x00\x12\x16\n\x0e\x62ot_monitoring\x18\x08 \x01(\t\x12>\n\x13\x65xternal_schedulers\x18\t \x03(\x0b\x32!.swarming.ExternalSchedulerConfigB\x18\n\x16task_deployment_scheme\"b\n\nSchedulers\x12\x0c\n\x04user\x18\x01 \x03(\t\x12\r\n\x05group\x18\x02 \x03(\t\x12\x37\n\x12trusted_delegation\x18\x03 \x03(\x0b\x32\x1b.swarming.TrustedDelegation\"y\n\x11TrustedDelegation\x12\x0f\n\x07peer_id\x18\x01 \x01(\t\x12;\n\x0erequire_any_of\x18\x02 \x01(\x0b\x32#.swarming.TrustedDelegation.TagList\x1a\x16\n\x07TagList\x12\x0b\n\x03tag\x18\x01 \x03(\t\"\xe8\x02\n\x0cTaskTemplate\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07include\x18\x02 \x03(\t\x12\x30\n\x05\x63\x61\x63he\x18\x03 \x03(\x0b\x32!.swarming.TaskTemplate.CacheEntry\x12\x38\n\x0c\x63ipd_package\x18\x04 \x03(\x0b\x32\".swarming.TaskTemplate.CipdPackage\x12\'\n\x03\x65nv\x18\x05 \x03(\x0b\x32\x1a.swarming.TaskTemplate.Env\x1a(\n\nCacheEntry\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x1a\x39\n\x0b\x43ipdPackage\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0b\n\x03pkg\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\x1a?\n\x03\x45nv\x12\x0b\n\x03var\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x0e\n\x06prefix\x18\x03 \x03(\t\x12\x0c\n\x04soft\x18\x04 \x01(\x08\"\x8b\x01\n\x16TaskTemplateDeployment\x12\x0c\n\x04name\x18\x01 \x01(\t\x12$\n\x04prod\x18\x02 \x01(\x0b\x32\x16.swarming.TaskTemplate\x12&\n\x06\x63\x61nary\x18\x03 \x01(\x0b\x32\x16.swarming.TaskTemplate\x12\x15\n\rcanary_chance\x18\x04 \x01(\x05\"4\n\rBotMonitoring\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rdimension_key\x18\x02 \x03(\t\"[\n\x17\x45xternalSchedulerConfig\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\t\x12\x12\n\ndimensions\x18\x03 \x03(\t\x12\x0f\n\x07\x65nabled\x18\x04 \x01(\x08\"\xd4\x01\n\x10\x45xternalServices\x12\x33\n\x07isolate\x18\x01 \x01(\x0b\x32\".swarming.ExternalServices.Isolate\x12-\n\x04\x63ipd\x18\x02 \x01(\x0b\x32\x1f.swarming.ExternalServices.CIPD\x1a,\n\x07Isolate\x12\x0e\n\x06server\x18\x01 \x01(\t\x12\x11\n\tnamespace\x18\x02 \x01(\t\x1a.\n\x04\x43IPD\x12\x0e\n\x06server\x18\x01 \x01(\t\x12\x16\n\x0e\x63lient_version\x18\x02 \x01(\tb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_POOLSCFG = _descriptor.Descriptor(
  name='PoolsCfg',
  full_name='swarming.PoolsCfg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pool', full_name='swarming.PoolsCfg.pool', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='forbid_unknown_pools', full_name='swarming.PoolsCfg.forbid_unknown_pools', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='default_external_services', full_name='swarming.PoolsCfg.default_external_services', index=2,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template', full_name='swarming.PoolsCfg.task_template', index=3,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template_deployment', full_name='swarming.PoolsCfg.task_template_deployment', index=4,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_monitoring', full_name='swarming.PoolsCfg.bot_monitoring', index=5,
      number=5, type=11, cpp_type=10, label=3,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=26,
  serialized_end=323,
)


_POOL = _descriptor.Descriptor(
  name='Pool',
  full_name='swarming.Pool',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='swarming.Pool.name', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='owners', full_name='swarming.Pool.owners', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='schedulers', full_name='swarming.Pool.schedulers', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='allowed_service_account', full_name='swarming.Pool.allowed_service_account', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='allowed_service_account_group', full_name='swarming.Pool.allowed_service_account_group', index=4,
      number=5, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template_deployment', full_name='swarming.Pool.task_template_deployment', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template_deployment_inline', full_name='swarming.Pool.task_template_deployment_inline', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_monitoring', full_name='swarming.Pool.bot_monitoring', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='external_schedulers', full_name='swarming.Pool.external_schedulers', index=8,
      number=9, type=11, cpp_type=10, label=3,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='task_deployment_scheme', full_name='swarming.Pool.task_deployment_scheme',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=326,
  serialized_end=703,
)


_SCHEDULERS = _descriptor.Descriptor(
  name='Schedulers',
  full_name='swarming.Schedulers',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user', full_name='swarming.Schedulers.user', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='group', full_name='swarming.Schedulers.group', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='trusted_delegation', full_name='swarming.Schedulers.trusted_delegation', index=2,
      number=3, type=11, cpp_type=10, label=3,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=705,
  serialized_end=803,
)


_TRUSTEDDELEGATION_TAGLIST = _descriptor.Descriptor(
  name='TagList',
  full_name='swarming.TrustedDelegation.TagList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tag', full_name='swarming.TrustedDelegation.TagList.tag', index=0,
      number=1, type=9, cpp_type=9, label=3,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=904,
  serialized_end=926,
)

_TRUSTEDDELEGATION = _descriptor.Descriptor(
  name='TrustedDelegation',
  full_name='swarming.TrustedDelegation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='peer_id', full_name='swarming.TrustedDelegation.peer_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='require_any_of', full_name='swarming.TrustedDelegation.require_any_of', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TRUSTEDDELEGATION_TAGLIST, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=805,
  serialized_end=926,
)


_TASKTEMPLATE_CACHEENTRY = _descriptor.Descriptor(
  name='CacheEntry',
  full_name='swarming.TaskTemplate.CacheEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='swarming.TaskTemplate.CacheEntry.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='path', full_name='swarming.TaskTemplate.CacheEntry.path', index=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1125,
  serialized_end=1165,
)

_TASKTEMPLATE_CIPDPACKAGE = _descriptor.Descriptor(
  name='CipdPackage',
  full_name='swarming.TaskTemplate.CipdPackage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='swarming.TaskTemplate.CipdPackage.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pkg', full_name='swarming.TaskTemplate.CipdPackage.pkg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='version', full_name='swarming.TaskTemplate.CipdPackage.version', index=2,
      number=3, type=9, cpp_type=9, label=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1167,
  serialized_end=1224,
)

_TASKTEMPLATE_ENV = _descriptor.Descriptor(
  name='Env',
  full_name='swarming.TaskTemplate.Env',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='var', full_name='swarming.TaskTemplate.Env.var', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='swarming.TaskTemplate.Env.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='prefix', full_name='swarming.TaskTemplate.Env.prefix', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='soft', full_name='swarming.TaskTemplate.Env.soft', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1226,
  serialized_end=1289,
)

_TASKTEMPLATE = _descriptor.Descriptor(
  name='TaskTemplate',
  full_name='swarming.TaskTemplate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='swarming.TaskTemplate.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='include', full_name='swarming.TaskTemplate.include', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cache', full_name='swarming.TaskTemplate.cache', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cipd_package', full_name='swarming.TaskTemplate.cipd_package', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='env', full_name='swarming.TaskTemplate.env', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TASKTEMPLATE_CACHEENTRY, _TASKTEMPLATE_CIPDPACKAGE, _TASKTEMPLATE_ENV, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=929,
  serialized_end=1289,
)


_TASKTEMPLATEDEPLOYMENT = _descriptor.Descriptor(
  name='TaskTemplateDeployment',
  full_name='swarming.TaskTemplateDeployment',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='swarming.TaskTemplateDeployment.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='prod', full_name='swarming.TaskTemplateDeployment.prod', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='canary', full_name='swarming.TaskTemplateDeployment.canary', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='canary_chance', full_name='swarming.TaskTemplateDeployment.canary_chance', index=3,
      number=4, type=5, cpp_type=1, label=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1292,
  serialized_end=1431,
)


_BOTMONITORING = _descriptor.Descriptor(
  name='BotMonitoring',
  full_name='swarming.BotMonitoring',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='swarming.BotMonitoring.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dimension_key', full_name='swarming.BotMonitoring.dimension_key', index=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1433,
  serialized_end=1485,
)


_EXTERNALSCHEDULERCONFIG = _descriptor.Descriptor(
  name='ExternalSchedulerConfig',
  full_name='swarming.ExternalSchedulerConfig',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='swarming.ExternalSchedulerConfig.address', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='id', full_name='swarming.ExternalSchedulerConfig.id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dimensions', full_name='swarming.ExternalSchedulerConfig.dimensions', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='enabled', full_name='swarming.ExternalSchedulerConfig.enabled', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1487,
  serialized_end=1578,
)


_EXTERNALSERVICES_ISOLATE = _descriptor.Descriptor(
  name='Isolate',
  full_name='swarming.ExternalServices.Isolate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='server', full_name='swarming.ExternalServices.Isolate.server', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='namespace', full_name='swarming.ExternalServices.Isolate.namespace', index=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1701,
  serialized_end=1745,
)

_EXTERNALSERVICES_CIPD = _descriptor.Descriptor(
  name='CIPD',
  full_name='swarming.ExternalServices.CIPD',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='server', full_name='swarming.ExternalServices.CIPD.server', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='client_version', full_name='swarming.ExternalServices.CIPD.client_version', index=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1747,
  serialized_end=1793,
)

_EXTERNALSERVICES = _descriptor.Descriptor(
  name='ExternalServices',
  full_name='swarming.ExternalServices',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='isolate', full_name='swarming.ExternalServices.isolate', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cipd', full_name='swarming.ExternalServices.cipd', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_EXTERNALSERVICES_ISOLATE, _EXTERNALSERVICES_CIPD, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1581,
  serialized_end=1793,
)

_POOLSCFG.fields_by_name['pool'].message_type = _POOL
_POOLSCFG.fields_by_name['default_external_services'].message_type = _EXTERNALSERVICES
_POOLSCFG.fields_by_name['task_template'].message_type = _TASKTEMPLATE
_POOLSCFG.fields_by_name['task_template_deployment'].message_type = _TASKTEMPLATEDEPLOYMENT
_POOLSCFG.fields_by_name['bot_monitoring'].message_type = _BOTMONITORING
_POOL.fields_by_name['schedulers'].message_type = _SCHEDULERS
_POOL.fields_by_name['task_template_deployment_inline'].message_type = _TASKTEMPLATEDEPLOYMENT
_POOL.fields_by_name['external_schedulers'].message_type = _EXTERNALSCHEDULERCONFIG
_POOL.oneofs_by_name['task_deployment_scheme'].fields.append(
  _POOL.fields_by_name['task_template_deployment'])
_POOL.fields_by_name['task_template_deployment'].containing_oneof = _POOL.oneofs_by_name['task_deployment_scheme']
_POOL.oneofs_by_name['task_deployment_scheme'].fields.append(
  _POOL.fields_by_name['task_template_deployment_inline'])
_POOL.fields_by_name['task_template_deployment_inline'].containing_oneof = _POOL.oneofs_by_name['task_deployment_scheme']
_SCHEDULERS.fields_by_name['trusted_delegation'].message_type = _TRUSTEDDELEGATION
_TRUSTEDDELEGATION_TAGLIST.containing_type = _TRUSTEDDELEGATION
_TRUSTEDDELEGATION.fields_by_name['require_any_of'].message_type = _TRUSTEDDELEGATION_TAGLIST
_TASKTEMPLATE_CACHEENTRY.containing_type = _TASKTEMPLATE
_TASKTEMPLATE_CIPDPACKAGE.containing_type = _TASKTEMPLATE
_TASKTEMPLATE_ENV.containing_type = _TASKTEMPLATE
_TASKTEMPLATE.fields_by_name['cache'].message_type = _TASKTEMPLATE_CACHEENTRY
_TASKTEMPLATE.fields_by_name['cipd_package'].message_type = _TASKTEMPLATE_CIPDPACKAGE
_TASKTEMPLATE.fields_by_name['env'].message_type = _TASKTEMPLATE_ENV
_TASKTEMPLATEDEPLOYMENT.fields_by_name['prod'].message_type = _TASKTEMPLATE
_TASKTEMPLATEDEPLOYMENT.fields_by_name['canary'].message_type = _TASKTEMPLATE
_EXTERNALSERVICES_ISOLATE.containing_type = _EXTERNALSERVICES
_EXTERNALSERVICES_CIPD.containing_type = _EXTERNALSERVICES
_EXTERNALSERVICES.fields_by_name['isolate'].message_type = _EXTERNALSERVICES_ISOLATE
_EXTERNALSERVICES.fields_by_name['cipd'].message_type = _EXTERNALSERVICES_CIPD
DESCRIPTOR.message_types_by_name['PoolsCfg'] = _POOLSCFG
DESCRIPTOR.message_types_by_name['Pool'] = _POOL
DESCRIPTOR.message_types_by_name['Schedulers'] = _SCHEDULERS
DESCRIPTOR.message_types_by_name['TrustedDelegation'] = _TRUSTEDDELEGATION
DESCRIPTOR.message_types_by_name['TaskTemplate'] = _TASKTEMPLATE
DESCRIPTOR.message_types_by_name['TaskTemplateDeployment'] = _TASKTEMPLATEDEPLOYMENT
DESCRIPTOR.message_types_by_name['BotMonitoring'] = _BOTMONITORING
DESCRIPTOR.message_types_by_name['ExternalSchedulerConfig'] = _EXTERNALSCHEDULERCONFIG
DESCRIPTOR.message_types_by_name['ExternalServices'] = _EXTERNALSERVICES

PoolsCfg = _reflection.GeneratedProtocolMessageType('PoolsCfg', (_message.Message,), dict(
  DESCRIPTOR = _POOLSCFG,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.PoolsCfg)
  ))
_sym_db.RegisterMessage(PoolsCfg)

Pool = _reflection.GeneratedProtocolMessageType('Pool', (_message.Message,), dict(
  DESCRIPTOR = _POOL,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.Pool)
  ))
_sym_db.RegisterMessage(Pool)

Schedulers = _reflection.GeneratedProtocolMessageType('Schedulers', (_message.Message,), dict(
  DESCRIPTOR = _SCHEDULERS,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.Schedulers)
  ))
_sym_db.RegisterMessage(Schedulers)

TrustedDelegation = _reflection.GeneratedProtocolMessageType('TrustedDelegation', (_message.Message,), dict(

  TagList = _reflection.GeneratedProtocolMessageType('TagList', (_message.Message,), dict(
    DESCRIPTOR = _TRUSTEDDELEGATION_TAGLIST,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:swarming.TrustedDelegation.TagList)
    ))
  ,
  DESCRIPTOR = _TRUSTEDDELEGATION,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.TrustedDelegation)
  ))
_sym_db.RegisterMessage(TrustedDelegation)
_sym_db.RegisterMessage(TrustedDelegation.TagList)

TaskTemplate = _reflection.GeneratedProtocolMessageType('TaskTemplate', (_message.Message,), dict(

  CacheEntry = _reflection.GeneratedProtocolMessageType('CacheEntry', (_message.Message,), dict(
    DESCRIPTOR = _TASKTEMPLATE_CACHEENTRY,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:swarming.TaskTemplate.CacheEntry)
    ))
  ,

  CipdPackage = _reflection.GeneratedProtocolMessageType('CipdPackage', (_message.Message,), dict(
    DESCRIPTOR = _TASKTEMPLATE_CIPDPACKAGE,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:swarming.TaskTemplate.CipdPackage)
    ))
  ,

  Env = _reflection.GeneratedProtocolMessageType('Env', (_message.Message,), dict(
    DESCRIPTOR = _TASKTEMPLATE_ENV,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:swarming.TaskTemplate.Env)
    ))
  ,
  DESCRIPTOR = _TASKTEMPLATE,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.TaskTemplate)
  ))
_sym_db.RegisterMessage(TaskTemplate)
_sym_db.RegisterMessage(TaskTemplate.CacheEntry)
_sym_db.RegisterMessage(TaskTemplate.CipdPackage)
_sym_db.RegisterMessage(TaskTemplate.Env)

TaskTemplateDeployment = _reflection.GeneratedProtocolMessageType('TaskTemplateDeployment', (_message.Message,), dict(
  DESCRIPTOR = _TASKTEMPLATEDEPLOYMENT,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.TaskTemplateDeployment)
  ))
_sym_db.RegisterMessage(TaskTemplateDeployment)

BotMonitoring = _reflection.GeneratedProtocolMessageType('BotMonitoring', (_message.Message,), dict(
  DESCRIPTOR = _BOTMONITORING,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.BotMonitoring)
  ))
_sym_db.RegisterMessage(BotMonitoring)

ExternalSchedulerConfig = _reflection.GeneratedProtocolMessageType('ExternalSchedulerConfig', (_message.Message,), dict(
  DESCRIPTOR = _EXTERNALSCHEDULERCONFIG,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.ExternalSchedulerConfig)
  ))
_sym_db.RegisterMessage(ExternalSchedulerConfig)

ExternalServices = _reflection.GeneratedProtocolMessageType('ExternalServices', (_message.Message,), dict(

  Isolate = _reflection.GeneratedProtocolMessageType('Isolate', (_message.Message,), dict(
    DESCRIPTOR = _EXTERNALSERVICES_ISOLATE,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:swarming.ExternalServices.Isolate)
    ))
  ,

  CIPD = _reflection.GeneratedProtocolMessageType('CIPD', (_message.Message,), dict(
    DESCRIPTOR = _EXTERNALSERVICES_CIPD,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:swarming.ExternalServices.CIPD)
    ))
  ,
  DESCRIPTOR = _EXTERNALSERVICES,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:swarming.ExternalServices)
  ))
_sym_db.RegisterMessage(ExternalServices)
_sym_db.RegisterMessage(ExternalServices.Isolate)
_sym_db.RegisterMessage(ExternalServices.CIPD)


# @@protoc_insertion_point(module_scope)
