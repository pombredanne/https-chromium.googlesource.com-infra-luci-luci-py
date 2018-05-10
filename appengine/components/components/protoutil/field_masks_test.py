#!/usr/bin/env python
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import copy
import sys
import unittest

from test_support import test_env
test_env.setup_test_env()

# google.protobuf package requires some python package magic hacking.
from components import utils
utils.fix_protobuf_package()

from google.protobuf import field_mask_pb2
from google.protobuf import struct_pb2

import field_masks
import test_proto_pb2


def make_mask(*paths):
  return field_mask_pb2.FieldMask(paths=list(paths))


class TrimTests(unittest.TestCase):

  def test_scalar_trim(self):
    msg = test_proto_pb2.Msg(num=1)
    field_masks.trim_message(msg, make_mask())
    self.assertEqual(msg, test_proto_pb2.Msg())

  def test_scalar_leave(self):
    msg = test_proto_pb2.Msg(num=1)
    field_masks.trim_message(msg, make_mask('num'))
    self.assertEqual(msg, test_proto_pb2.Msg(num=1))

  def test_submessage_trim(self):
    msg = test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1))
    field_masks.trim_message(msg, make_mask())
    self.assertEqual(msg, test_proto_pb2.Msg())

  def test_submessage_leave_whole(self):
    msg = test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1))
    field_masks.trim_message(msg, make_mask('msg'))
    self.assertEqual(msg, test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1)))

  def test_submessage_leave_part(self):
    msg = test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1, str='x'))
    field_masks.trim_message(msg, make_mask('msg.num'))
    self.assertEqual(msg, test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1)))

  def test_struct_trim(self):
    s = struct_pb2.Struct()
    s.update(dict(a=1))
    field_masks.trim_message(s, make_mask())
    self.assertEqual(s, struct_pb2.Struct())

  def test_struct_leave_scalar(self):
    s = struct_pb2.Struct()
    s.update(dict(a=1))

    actual = copy.deepcopy(s)
    field_masks.trim_message(actual, make_mask('a'))
    self.assertEqual(actual, s)

  def test_struct_leave_submessage_part(self):
    s = struct_pb2.Struct()
    s.update(dict(m=dict(num=1, str='a')))

    expected = struct_pb2.Struct()
    expected.update(dict(m=dict(num=1)))

    field_masks.trim_message(s, make_mask('m.num'))
    self.assertEqual(s, expected)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
