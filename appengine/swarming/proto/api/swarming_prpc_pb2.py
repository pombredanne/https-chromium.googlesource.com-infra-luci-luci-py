# Generated by the pRPC protocol buffer compiler plugin.  DO NOT EDIT!
# source: swarming.proto

import base64
import zlib

from google.protobuf import descriptor_pb2

# Includes description of the swarming.proto and all of its transitive
# dependencies. Includes source code info.
FILE_DESCRIPTOR_SET = descriptor_pb2.FileDescriptorSet()
FILE_DESCRIPTOR_SET.ParseFromString(zlib.decompress(base64.b64decode(
    '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')))
_INDEX = {
    f.name: {
      'descriptor': f,
      'services': {s.name: s for s in f.service},
    }
    for f in FILE_DESCRIPTOR_SET.file
}


BotAPIServiceDescription = {
  'file_descriptor_set': FILE_DESCRIPTOR_SET,
  'file_descriptor': _INDEX[u'swarming.proto']['descriptor'],
  'service_descriptor': _INDEX[u'swarming.proto']['services'][u'BotAPI'],
}
