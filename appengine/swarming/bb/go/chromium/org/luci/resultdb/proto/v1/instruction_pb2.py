# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/resultdb/proto/v1/instruction.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/resultdb/proto/v1/instruction.proto',
  package='luci.resultdb.v1',
  syntax='proto3',
  serialized_options=b'Z/go.chromium.org/luci/resultdb/proto/v1;resultpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n8go.chromium.org/luci/resultdb/proto/v1/instruction.proto\x12\x10luci.resultdb.v1\"C\n\x0cInstructions\x12\x33\n\x0cinstructions\x18\x01 \x03(\x0b\x32\x1d.luci.resultdb.v1.Instruction\"\xd1\x01\n\x0bInstruction\x12\n\n\x02id\x18\x01 \x01(\t\x12/\n\x04type\x18\x02 \x01(\x0e\x32!.luci.resultdb.v1.InstructionType\x12\x44\n\x15targeted_instructions\x18\x03 \x03(\x0b\x32%.luci.resultdb.v1.TargetedInstruction\x12?\n\x12instruction_filter\x18\x04 \x01(\x0b\x32#.luci.resultdb.v1.InstructionFilter\"o\n\x11InstructionFilter\x12K\n\x0einvocation_ids\x18\x01 \x01(\x0b\x32\x31.luci.resultdb.v1.InstructionFilterByInvocationIDH\x00\x42\r\n\x0b\x66ilter_type\"L\n\x1fInstructionFilterByInvocationID\x12\x16\n\x0einvocation_ids\x18\x01 \x03(\t\x12\x11\n\trecursive\x18\x02 \x01(\x08\"\x9b\x01\n\x13TargetedInstruction\x12\x34\n\x07targets\x18\x01 \x03(\x0e\x32#.luci.resultdb.v1.InstructionTarget\x12=\n\x0c\x64\x65pendencies\x18\x02 \x03(\x0b\x32\'.luci.resultdb.v1.InstructionDependency\x12\x0f\n\x07\x63ontent\x18\x03 \x01(\t\"F\n\x15InstructionDependency\x12\x15\n\rinvocation_id\x18\x01 \x01(\t\x12\x16\n\x0einstruction_id\x18\x02 \x01(\t*\\\n\x11InstructionTarget\x12\"\n\x1eINSTRUCTION_TARGET_UNSPECIFIED\x10\x00\x12\t\n\x05LOCAL\x10\x01\x12\n\n\x06REMOTE\x10\x02\x12\x0c\n\x08PREBUILT\x10\x03*f\n\x0fInstructionType\x12 \n\x1cINSTRUCTION_TYPE_UNSPECIFIED\x10\x00\x12\x14\n\x10STEP_INSTRUCTION\x10\x01\x12\x1b\n\x17TEST_RESULT_INSTRUCTION\x10\x02\x42\x31Z/go.chromium.org/luci/resultdb/proto/v1;resultpbb\x06proto3'
)

_INSTRUCTIONTARGET = _descriptor.EnumDescriptor(
  name='InstructionTarget',
  full_name='luci.resultdb.v1.InstructionTarget',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INSTRUCTION_TARGET_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='LOCAL', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='REMOTE', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='PREBUILT', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=780,
  serialized_end=872,
)
_sym_db.RegisterEnumDescriptor(_INSTRUCTIONTARGET)

InstructionTarget = enum_type_wrapper.EnumTypeWrapper(_INSTRUCTIONTARGET)
_INSTRUCTIONTYPE = _descriptor.EnumDescriptor(
  name='InstructionType',
  full_name='luci.resultdb.v1.InstructionType',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INSTRUCTION_TYPE_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='STEP_INSTRUCTION', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='TEST_RESULT_INSTRUCTION', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=874,
  serialized_end=976,
)
_sym_db.RegisterEnumDescriptor(_INSTRUCTIONTYPE)

InstructionType = enum_type_wrapper.EnumTypeWrapper(_INSTRUCTIONTYPE)
INSTRUCTION_TARGET_UNSPECIFIED = 0
LOCAL = 1
REMOTE = 2
PREBUILT = 3
INSTRUCTION_TYPE_UNSPECIFIED = 0
STEP_INSTRUCTION = 1
TEST_RESULT_INSTRUCTION = 2



_INSTRUCTIONS = _descriptor.Descriptor(
  name='Instructions',
  full_name='luci.resultdb.v1.Instructions',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='instructions', full_name='luci.resultdb.v1.Instructions.instructions', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=78,
  serialized_end=145,
)


_INSTRUCTION = _descriptor.Descriptor(
  name='Instruction',
  full_name='luci.resultdb.v1.Instruction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='luci.resultdb.v1.Instruction.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='type', full_name='luci.resultdb.v1.Instruction.type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='targeted_instructions', full_name='luci.resultdb.v1.Instruction.targeted_instructions', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='instruction_filter', full_name='luci.resultdb.v1.Instruction.instruction_filter', index=3,
      number=4, type=11, cpp_type=10, label=1,
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
  serialized_start=148,
  serialized_end=357,
)


_INSTRUCTIONFILTER = _descriptor.Descriptor(
  name='InstructionFilter',
  full_name='luci.resultdb.v1.InstructionFilter',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='invocation_ids', full_name='luci.resultdb.v1.InstructionFilter.invocation_ids', index=0,
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
    _descriptor.OneofDescriptor(
      name='filter_type', full_name='luci.resultdb.v1.InstructionFilter.filter_type',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=359,
  serialized_end=470,
)


_INSTRUCTIONFILTERBYINVOCATIONID = _descriptor.Descriptor(
  name='InstructionFilterByInvocationID',
  full_name='luci.resultdb.v1.InstructionFilterByInvocationID',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='invocation_ids', full_name='luci.resultdb.v1.InstructionFilterByInvocationID.invocation_ids', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='recursive', full_name='luci.resultdb.v1.InstructionFilterByInvocationID.recursive', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  serialized_start=472,
  serialized_end=548,
)


_TARGETEDINSTRUCTION = _descriptor.Descriptor(
  name='TargetedInstruction',
  full_name='luci.resultdb.v1.TargetedInstruction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='targets', full_name='luci.resultdb.v1.TargetedInstruction.targets', index=0,
      number=1, type=14, cpp_type=8, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='dependencies', full_name='luci.resultdb.v1.TargetedInstruction.dependencies', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='content', full_name='luci.resultdb.v1.TargetedInstruction.content', index=2,
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
  serialized_start=551,
  serialized_end=706,
)


_INSTRUCTIONDEPENDENCY = _descriptor.Descriptor(
  name='InstructionDependency',
  full_name='luci.resultdb.v1.InstructionDependency',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='invocation_id', full_name='luci.resultdb.v1.InstructionDependency.invocation_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='instruction_id', full_name='luci.resultdb.v1.InstructionDependency.instruction_id', index=1,
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
  serialized_start=708,
  serialized_end=778,
)

_INSTRUCTIONS.fields_by_name['instructions'].message_type = _INSTRUCTION
_INSTRUCTION.fields_by_name['type'].enum_type = _INSTRUCTIONTYPE
_INSTRUCTION.fields_by_name['targeted_instructions'].message_type = _TARGETEDINSTRUCTION
_INSTRUCTION.fields_by_name['instruction_filter'].message_type = _INSTRUCTIONFILTER
_INSTRUCTIONFILTER.fields_by_name['invocation_ids'].message_type = _INSTRUCTIONFILTERBYINVOCATIONID
_INSTRUCTIONFILTER.oneofs_by_name['filter_type'].fields.append(
  _INSTRUCTIONFILTER.fields_by_name['invocation_ids'])
_INSTRUCTIONFILTER.fields_by_name['invocation_ids'].containing_oneof = _INSTRUCTIONFILTER.oneofs_by_name['filter_type']
_TARGETEDINSTRUCTION.fields_by_name['targets'].enum_type = _INSTRUCTIONTARGET
_TARGETEDINSTRUCTION.fields_by_name['dependencies'].message_type = _INSTRUCTIONDEPENDENCY
DESCRIPTOR.message_types_by_name['Instructions'] = _INSTRUCTIONS
DESCRIPTOR.message_types_by_name['Instruction'] = _INSTRUCTION
DESCRIPTOR.message_types_by_name['InstructionFilter'] = _INSTRUCTIONFILTER
DESCRIPTOR.message_types_by_name['InstructionFilterByInvocationID'] = _INSTRUCTIONFILTERBYINVOCATIONID
DESCRIPTOR.message_types_by_name['TargetedInstruction'] = _TARGETEDINSTRUCTION
DESCRIPTOR.message_types_by_name['InstructionDependency'] = _INSTRUCTIONDEPENDENCY
DESCRIPTOR.enum_types_by_name['InstructionTarget'] = _INSTRUCTIONTARGET
DESCRIPTOR.enum_types_by_name['InstructionType'] = _INSTRUCTIONTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Instructions = _reflection.GeneratedProtocolMessageType('Instructions', (_message.Message,), {
  'DESCRIPTOR' : _INSTRUCTIONS,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.instruction_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.Instructions)
  })
_sym_db.RegisterMessage(Instructions)

Instruction = _reflection.GeneratedProtocolMessageType('Instruction', (_message.Message,), {
  'DESCRIPTOR' : _INSTRUCTION,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.instruction_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.Instruction)
  })
_sym_db.RegisterMessage(Instruction)

InstructionFilter = _reflection.GeneratedProtocolMessageType('InstructionFilter', (_message.Message,), {
  'DESCRIPTOR' : _INSTRUCTIONFILTER,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.instruction_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.InstructionFilter)
  })
_sym_db.RegisterMessage(InstructionFilter)

InstructionFilterByInvocationID = _reflection.GeneratedProtocolMessageType('InstructionFilterByInvocationID', (_message.Message,), {
  'DESCRIPTOR' : _INSTRUCTIONFILTERBYINVOCATIONID,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.instruction_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.InstructionFilterByInvocationID)
  })
_sym_db.RegisterMessage(InstructionFilterByInvocationID)

TargetedInstruction = _reflection.GeneratedProtocolMessageType('TargetedInstruction', (_message.Message,), {
  'DESCRIPTOR' : _TARGETEDINSTRUCTION,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.instruction_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.TargetedInstruction)
  })
_sym_db.RegisterMessage(TargetedInstruction)

InstructionDependency = _reflection.GeneratedProtocolMessageType('InstructionDependency', (_message.Message,), {
  'DESCRIPTOR' : _INSTRUCTIONDEPENDENCY,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.instruction_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.InstructionDependency)
  })
_sym_db.RegisterMessage(InstructionDependency)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
