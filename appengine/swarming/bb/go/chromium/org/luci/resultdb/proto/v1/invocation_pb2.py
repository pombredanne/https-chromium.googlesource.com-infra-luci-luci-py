# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: go.chromium.org/luci/resultdb/proto/v1/invocation.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.api import field_behavior_pb2 as google_dot_api_dot_field__behavior__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from bb.go.chromium.org.luci.resultdb.proto.v1 import common_pb2 as go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_common__pb2
from bb.go.chromium.org.luci.resultdb.proto.v1 import predicate_pb2 as go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_predicate__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='go.chromium.org/luci/resultdb/proto/v1/invocation.proto',
  package='luci.resultdb.v1',
  syntax='proto3',
  serialized_options=b'Z/go.chromium.org/luci/resultdb/proto/v1;resultpb',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n7go.chromium.org/luci/resultdb/proto/v1/invocation.proto\x12\x10luci.resultdb.v1\x1a\x1fgoogle/api/field_behavior.proto\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x33go.chromium.org/luci/resultdb/proto/v1/common.proto\x1a\x36go.chromium.org/luci/resultdb/proto/v1/predicate.proto\"\xc9\x04\n\nInvocation\x12\x14\n\x04name\x18\x01 \x01(\tB\x06\xe0\x41\x03\xe0\x41\x05\x12\x31\n\x05state\x18\x02 \x01(\x0e\x32\".luci.resultdb.v1.Invocation.State\x12\x37\n\x0b\x63reate_time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x06\xe0\x41\x03\xe0\x41\x05\x12*\n\x04tags\x18\x05 \x03(\x0b\x32\x1c.luci.resultdb.v1.StringPair\x12\x36\n\rfinalize_time\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x03\xe0\x41\x03\x12,\n\x08\x64\x65\x61\x64line\x18\x07 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\x12\x1c\n\x14included_invocations\x18\x08 \x03(\t\x12:\n\x10\x62igquery_exports\x18\t \x03(\x0b\x32 .luci.resultdb.v1.BigQueryExport\x12\x17\n\ncreated_by\x18\n \x01(\tB\x03\xe0\x41\x03\x12\x19\n\x11producer_resource\x18\x0b \x01(\t\x12\r\n\x05realm\x18\x0c \x01(\t\x12\x39\n\x0fhistory_options\x18\r \x01(\x0b\x32 .luci.resultdb.v1.HistoryOptions\"I\n\x05State\x12\x15\n\x11STATE_UNSPECIFIED\x10\x00\x12\n\n\x06\x41\x43TIVE\x10\x01\x12\x0e\n\nFINALIZING\x10\x02\x12\r\n\tFINALIZED\x10\x03J\x04\x08\x03\x10\x04\"\x81\x03\n\x0e\x42igQueryExport\x12\x14\n\x07project\x18\x01 \x01(\tB\x03\xe0\x41\x02\x12\x14\n\x07\x64\x61taset\x18\x02 \x01(\tB\x03\xe0\x41\x02\x12\x12\n\x05table\x18\x03 \x01(\tB\x03\xe0\x41\x02\x12\x44\n\x0ctest_results\x18\x04 \x01(\x0b\x32,.luci.resultdb.v1.BigQueryExport.TestResultsH\x00\x12H\n\x0etext_artifacts\x18\x06 \x01(\x0b\x32..luci.resultdb.v1.BigQueryExport.TextArtifactsH\x00\x1aG\n\x0bTestResults\x12\x38\n\tpredicate\x18\x01 \x01(\x0b\x32%.luci.resultdb.v1.TestResultPredicate\x1aG\n\rTextArtifacts\x12\x36\n\tpredicate\x18\x01 \x01(\x0b\x32#.luci.resultdb.v1.ArtifactPredicateB\r\n\x0bresult_type\"d\n\x0eHistoryOptions\x12 \n\x18use_invocation_timestamp\x18\x01 \x01(\x08\x12\x30\n\x06\x63ommit\x18\x02 \x01(\x0b\x32 .luci.resultdb.v1.CommitPositionB1Z/go.chromium.org/luci/resultdb/proto/v1;resultpbb\x06proto3'
  ,
  dependencies=[google_dot_api_dot_field__behavior__pb2.DESCRIPTOR,google_dot_protobuf_dot_timestamp__pb2.DESCRIPTOR,go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_common__pb2.DESCRIPTOR,go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_predicate__pb2.DESCRIPTOR,])



_INVOCATION_STATE = _descriptor.EnumDescriptor(
  name='State',
  full_name='luci.resultdb.v1.Invocation.State',
  filename=None,
  file=DESCRIPTOR,
  create_key=_descriptor._internal_create_key,
  values=[
    _descriptor.EnumValueDescriptor(
      name='STATE_UNSPECIFIED', index=0, number=0,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='ACTIVE', index=1, number=1,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FINALIZING', index=2, number=2,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
    _descriptor.EnumValueDescriptor(
      name='FINALIZED', index=3, number=3,
      serialized_options=None,
      type=None,
      create_key=_descriptor._internal_create_key),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=759,
  serialized_end=832,
)
_sym_db.RegisterEnumDescriptor(_INVOCATION_STATE)


_INVOCATION = _descriptor.Descriptor(
  name='Invocation',
  full_name='luci.resultdb.v1.Invocation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='luci.resultdb.v1.Invocation.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\003\340A\005', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='state', full_name='luci.resultdb.v1.Invocation.state', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='create_time', full_name='luci.resultdb.v1.Invocation.create_time', index=2,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\003\340A\005', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='tags', full_name='luci.resultdb.v1.Invocation.tags', index=3,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='finalize_time', full_name='luci.resultdb.v1.Invocation.finalize_time', index=4,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\003', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='deadline', full_name='luci.resultdb.v1.Invocation.deadline', index=5,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='included_invocations', full_name='luci.resultdb.v1.Invocation.included_invocations', index=6,
      number=8, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='bigquery_exports', full_name='luci.resultdb.v1.Invocation.bigquery_exports', index=7,
      number=9, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='created_by', full_name='luci.resultdb.v1.Invocation.created_by', index=8,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\003', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='producer_resource', full_name='luci.resultdb.v1.Invocation.producer_resource', index=9,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='realm', full_name='luci.resultdb.v1.Invocation.realm', index=10,
      number=12, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='history_options', full_name='luci.resultdb.v1.Invocation.history_options', index=11,
      number=13, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _INVOCATION_STATE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=253,
  serialized_end=838,
)


_BIGQUERYEXPORT_TESTRESULTS = _descriptor.Descriptor(
  name='TestResults',
  full_name='luci.resultdb.v1.BigQueryExport.TestResults',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='predicate', full_name='luci.resultdb.v1.BigQueryExport.TestResults.predicate', index=0,
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
  serialized_start=1067,
  serialized_end=1138,
)

_BIGQUERYEXPORT_TEXTARTIFACTS = _descriptor.Descriptor(
  name='TextArtifacts',
  full_name='luci.resultdb.v1.BigQueryExport.TextArtifacts',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='predicate', full_name='luci.resultdb.v1.BigQueryExport.TextArtifacts.predicate', index=0,
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
  serialized_start=1140,
  serialized_end=1211,
)

_BIGQUERYEXPORT = _descriptor.Descriptor(
  name='BigQueryExport',
  full_name='luci.resultdb.v1.BigQueryExport',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='project', full_name='luci.resultdb.v1.BigQueryExport.project', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='dataset', full_name='luci.resultdb.v1.BigQueryExport.dataset', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='table', full_name='luci.resultdb.v1.BigQueryExport.table', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=b'\340A\002', file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='test_results', full_name='luci.resultdb.v1.BigQueryExport.test_results', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='text_artifacts', full_name='luci.resultdb.v1.BigQueryExport.text_artifacts', index=4,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[_BIGQUERYEXPORT_TESTRESULTS, _BIGQUERYEXPORT_TEXTARTIFACTS, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='result_type', full_name='luci.resultdb.v1.BigQueryExport.result_type',
      index=0, containing_type=None,
      create_key=_descriptor._internal_create_key,
    fields=[]),
  ],
  serialized_start=841,
  serialized_end=1226,
)


_HISTORYOPTIONS = _descriptor.Descriptor(
  name='HistoryOptions',
  full_name='luci.resultdb.v1.HistoryOptions',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='use_invocation_timestamp', full_name='luci.resultdb.v1.HistoryOptions.use_invocation_timestamp', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='commit', full_name='luci.resultdb.v1.HistoryOptions.commit', index=1,
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
  serialized_start=1228,
  serialized_end=1328,
)

_INVOCATION.fields_by_name['state'].enum_type = _INVOCATION_STATE
_INVOCATION.fields_by_name['create_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_INVOCATION.fields_by_name['tags'].message_type = go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_common__pb2._STRINGPAIR
_INVOCATION.fields_by_name['finalize_time'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_INVOCATION.fields_by_name['deadline'].message_type = google_dot_protobuf_dot_timestamp__pb2._TIMESTAMP
_INVOCATION.fields_by_name['bigquery_exports'].message_type = _BIGQUERYEXPORT
_INVOCATION.fields_by_name['history_options'].message_type = _HISTORYOPTIONS
_INVOCATION_STATE.containing_type = _INVOCATION
_BIGQUERYEXPORT_TESTRESULTS.fields_by_name['predicate'].message_type = go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_predicate__pb2._TESTRESULTPREDICATE
_BIGQUERYEXPORT_TESTRESULTS.containing_type = _BIGQUERYEXPORT
_BIGQUERYEXPORT_TEXTARTIFACTS.fields_by_name['predicate'].message_type = go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_predicate__pb2._ARTIFACTPREDICATE
_BIGQUERYEXPORT_TEXTARTIFACTS.containing_type = _BIGQUERYEXPORT
_BIGQUERYEXPORT.fields_by_name['test_results'].message_type = _BIGQUERYEXPORT_TESTRESULTS
_BIGQUERYEXPORT.fields_by_name['text_artifacts'].message_type = _BIGQUERYEXPORT_TEXTARTIFACTS
_BIGQUERYEXPORT.oneofs_by_name['result_type'].fields.append(
  _BIGQUERYEXPORT.fields_by_name['test_results'])
_BIGQUERYEXPORT.fields_by_name['test_results'].containing_oneof = _BIGQUERYEXPORT.oneofs_by_name['result_type']
_BIGQUERYEXPORT.oneofs_by_name['result_type'].fields.append(
  _BIGQUERYEXPORT.fields_by_name['text_artifacts'])
_BIGQUERYEXPORT.fields_by_name['text_artifacts'].containing_oneof = _BIGQUERYEXPORT.oneofs_by_name['result_type']
_HISTORYOPTIONS.fields_by_name['commit'].message_type = go_dot_chromium_dot_org_dot_luci_dot_resultdb_dot_proto_dot_v1_dot_common__pb2._COMMITPOSITION
DESCRIPTOR.message_types_by_name['Invocation'] = _INVOCATION
DESCRIPTOR.message_types_by_name['BigQueryExport'] = _BIGQUERYEXPORT
DESCRIPTOR.message_types_by_name['HistoryOptions'] = _HISTORYOPTIONS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Invocation = _reflection.GeneratedProtocolMessageType('Invocation', (_message.Message,), {
  'DESCRIPTOR' : _INVOCATION,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.invocation_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.Invocation)
  })
_sym_db.RegisterMessage(Invocation)

BigQueryExport = _reflection.GeneratedProtocolMessageType('BigQueryExport', (_message.Message,), {

  'TestResults' : _reflection.GeneratedProtocolMessageType('TestResults', (_message.Message,), {
    'DESCRIPTOR' : _BIGQUERYEXPORT_TESTRESULTS,
    '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.invocation_pb2'
    # @@protoc_insertion_point(class_scope:luci.resultdb.v1.BigQueryExport.TestResults)
    })
  ,

  'TextArtifacts' : _reflection.GeneratedProtocolMessageType('TextArtifacts', (_message.Message,), {
    'DESCRIPTOR' : _BIGQUERYEXPORT_TEXTARTIFACTS,
    '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.invocation_pb2'
    # @@protoc_insertion_point(class_scope:luci.resultdb.v1.BigQueryExport.TextArtifacts)
    })
  ,
  'DESCRIPTOR' : _BIGQUERYEXPORT,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.invocation_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.BigQueryExport)
  })
_sym_db.RegisterMessage(BigQueryExport)
_sym_db.RegisterMessage(BigQueryExport.TestResults)
_sym_db.RegisterMessage(BigQueryExport.TextArtifacts)

HistoryOptions = _reflection.GeneratedProtocolMessageType('HistoryOptions', (_message.Message,), {
  'DESCRIPTOR' : _HISTORYOPTIONS,
  '__module__' : 'go.chromium.org.luci.resultdb.proto.v1.invocation_pb2'
  # @@protoc_insertion_point(class_scope:luci.resultdb.v1.HistoryOptions)
  })
_sym_db.RegisterMessage(HistoryOptions)


DESCRIPTOR._options = None
_INVOCATION.fields_by_name['name']._options = None
_INVOCATION.fields_by_name['create_time']._options = None
_INVOCATION.fields_by_name['finalize_time']._options = None
_INVOCATION.fields_by_name['created_by']._options = None
_BIGQUERYEXPORT.fields_by_name['project']._options = None
_BIGQUERYEXPORT.fields_by_name['dataset']._options = None
_BIGQUERYEXPORT.fields_by_name['table']._options = None
# @@protoc_insertion_point(module_scope)
