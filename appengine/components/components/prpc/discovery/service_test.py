#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import sys
import unittest

from google.protobuf import descriptor_pb2
from google.protobuf import text_format

import service
import test_pb2  # must be imported to registeer messages
import test_prpc_pb2


class TestService(object):
  DESCRIPTION = test_prpc_pb2.TestServiceServiceDescription


EXPECTED_FILES = '''
file {
  name: "test.proto"
  package: "discovery_test"
  dependency: "imported1_test.proto"
  message_type {
    name: "HelloRequest"
  }
  message_type {
    name: "HelloResponse"
    field {
      name: "imported"
      number: 1
      label: LABEL_OPTIONAL
      type: TYPE_MESSAGE
      type_name: ".discovery_test.Imported1"
    }
  }
  service {
    name: "TestService"
    method {
      name: "Hello"
      input_type: ".discovery_test.HelloRequest"
      output_type: ".discovery_test.HelloResponse"
      options {
      }
    }
  }
  syntax: "proto3"
}
file {
  name: "imported1_test.proto"
  package: "discovery_test"
  dependency: "imported2_test.proto"
  message_type {
    name: "Imported1"
    field {
      name: "imported"
      number: 1
      label: LABEL_OPTIONAL
      type: TYPE_MESSAGE
      type_name: ".discovery_test.Imported2"
    }
  }
  syntax: "proto3"
}
file {
  name: "imported2_test.proto"
  package: "discovery_test"
  message_type {
    name: "Imported2"
    field {
      name: "x"
      number: 1
      label: LABEL_OPTIONAL
      type: TYPE_INT32
    }
  }
  syntax: "proto3"
}
'''


class DiscoveryServiceTests(unittest.TestCase):
  def test(self):
    res = service._response_for([TestService()])
    self.assertEquals(
        res.services, ['discovery_test.TestService', 'discovery.Discovery'])

    expected_files = descriptor_pb2.FileDescriptorSet()
    text_format.Merge(EXPECTED_FILES, expected_files)
    for f in expected_files.file:
      self.assertIn(f, res.description.file)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
