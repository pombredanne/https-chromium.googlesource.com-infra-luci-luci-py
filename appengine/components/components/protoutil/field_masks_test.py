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

import field_masks
import test_proto_pb2


class ParsePathTests(unittest.TestCase):
  def parse(self, path):
    return field_masks.parse_path(path, test_proto_pb2.Msg.DESCRIPTOR)

  def test_str(self):
    actual = self.parse('str')
    expected = ('str',)
    self.assertEqual(actual, expected)

  def test_str_invalid_char(self):
    with self.assertRaisesRegexp(ValueError, r'invalid unquoted string "str@"'):
      self.parse('str@')

  def test_str_repeated(self):
    actual = self.parse('strs')
    expected = ('strs',)
    self.assertEqual(actual, expected)

  def test_str_repeated_trailing_star(self):
    actual = self.parse('strs.*')
    expected = ('strs', field_masks.STAR)
    self.assertEqual(actual, expected)

  def test_map_num_key(self):
    actual = self.parse('map_num_str.1')
    expected = ('map_num_str', 1)
    self.assertEqual(actual, expected)

  def test_map_num_key_negative(self):
    actual = self.parse('map_num_str.-1')
    expected = ('map_num_str', -1)
    self.assertEqual(actual, expected)

  def test_map_num_key_invalid(self):
    with self.assertRaisesRegexp(ValueError, r'integer key'):
      self.parse('map_num_str.a')

  def test_map_num_key_invalid_with_correct_prefix(self):
    with self.assertRaisesRegexp(ValueError, r'integer key'):
      self.parse('map_num_str.1a')

  def test_map_str_key_unquoted(self):
    actual = self.parse('map_str_num.a')
    expected = ('map_str_num', 'a')
    self.assertEqual(actual, expected)

  def test_map_str_key_unquoted_longer(self):
    actual = self.parse('map_str_num.ab')
    expected = ('map_str_num', 'ab')
    self.assertEqual(actual, expected)

  def test_map_str_key_quoted(self):
    actual = self.parse('map_str_num.`a`')
    expected = ('map_str_num', 'a')
    self.assertEqual(actual, expected)

  def test_map_str_key_quoted_with_period(self):
    actual = self.parse('map_str_num.`a.b`')
    expected = ('map_str_num', 'a.b')
    self.assertEqual(actual, expected)

  def test_map_str_key_star(self):
    actual = self.parse('map_str_num.*')
    expected = ('map_str_num', field_masks.STAR)
    self.assertEqual(actual, expected)

  def test_map_bool_key_true(self):
    actual = self.parse('map_bool_str.true')
    expected = ('map_bool_str', True)
    self.assertEqual(actual, expected)

  def test_map_bool_key_false(self):
    actual = self.parse('map_bool_str.false')
    expected = ('map_bool_str', False)
    self.assertEqual(actual, expected)

  def test_map_bool_key_invalid(self):
    with self.assertRaisesRegexp(ValueError, r'boolean key'):
      self.parse('map_bool_str.not-a-bool')

  def test_map_bool_key_star(self):
    actual = self.parse('map_bool_str.*')
    expected = ('map_bool_str', field_masks.STAR)
    self.assertEqual(actual, expected)

  def test_msg_str(self):
    actual = self.parse('msg.str')
    expected = ('msg', 'str')
    self.assertEqual(actual, expected)

  def test_msg_unexpected_field(self):
    with self.assertRaisesRegexp(ValueError, r'field "msg.x" does not exist'):
      self.parse('msg.x')

  def test_msg_unexpected_subfield(self):
    with self.assertRaisesRegexp(ValueError, r'"msg.msg.x" does not exist'):
      self.parse('msg.msg.x')

  def test_msg_msgs_str(self):
    actual = self.parse('msgs.*.str')
    expected = ('msgs', field_masks.STAR, 'str')
    self.assertEqual(actual, expected)

  def test_msg_map_num_str(self):
    actual = self.parse('msg.map_num_str.1')
    expected = ('msg', 'map_num_str', 1)
    self.assertEqual(actual, expected)

  def test_map_str_map_num(self):
    actual = self.parse('map_str_msg.num')
    expected = ('map_str_msg', 'num')
    self.assertEqual(actual, expected)

  def test_map_str_map_num_star(self):
    actual = self.parse('map_str_msg.*')
    expected = ('map_str_msg', field_masks.STAR)
    self.assertEqual(actual, expected)

  def test_map_str_map_num_star_str(self):
    actual = self.parse('map_str_msg.*.str')
    expected = ('map_str_msg', field_masks.STAR, 'str')
    self.assertEqual(actual, expected)

  def test_trailing_period(self):
    with self.assertRaisesRegexp(ValueError, r'unexpected end'):
      self.parse('str.')

  def test_trailing_period_period(self):
    with self.assertRaisesRegexp(ValueError, r'cannot start with a period'):
      self.parse('str..')


class NormalizePathsTests(unittest.TestCase):

  def test_empty(self):
    actual = field_masks.normalize_paths([])
    expected = set()
    self.assertEqual(actual, expected)

  def test_normal(self):
    actual = field_masks.normalize_paths([
        ('a',),
        ('b',),
    ])
    expected = {('a',), ('b',)}
    self.assertEqual(actual, expected)

  def test_redundancy_one_level(self):
    actual = field_masks.normalize_paths([
        ('a',),
        ('a', 'b'),
    ])
    expected = {('a',)}
    self.assertEqual(actual, expected)

  def test_redundancy_second_level(self):
    actual = field_masks.normalize_paths([
        ('a',),
        ('a', 'b', 'c'),
    ])
    expected = {('a',)}
    self.assertEqual(actual, expected)


class ParseFieldTreeTests(unittest.TestCase):
  def test_empty(self):
    actual = field_masks.parse_field_tree([])
    expected = {}
    self.assertEqual(actual, expected)

  def test_simple(self):
    actual = field_masks.parse_field_tree([('ab',)])
    expected = {'ab': {}}
    self.assertEqual(actual, expected)

  def test_simple_simple(self):
    actual = field_masks.parse_field_tree([
        ('ab',),
        ('cd',),
    ])
    expected = {'ab': {}, 'cd': {}}
    self.assertEqual(actual, expected)

  def test_simple_nested(self):
    actual = field_masks.parse_field_tree([
        ('a', 'b'),
        ('a', 'c'),
    ])
    expected = {'a': {'b': {}, 'c': {}}}
    self.assertEqual(actual, expected)

  def test_redunant(self):
    actual = field_masks.parse_field_tree([
        ('a',),
        ('a', 'b'),
    ])
    expected = {'a': {}}
    self.assertEqual(actual, expected)

  def test_redunant_star(self):
    actual = field_masks.parse_field_tree([
        ('a', field_masks.STAR),
        ('a', 'b', 'c'),
    ])
    expected = {'a': {}}
    self.assertEqual(actual, expected)


class MustIncludeTests(unittest.TestCase):
  def test_all(self):
    tree = {}
    path = ('a', )
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.INCLUDE_RECURSIVELY)

  def test_include_recursively(self):
    tree = {'a': {}}
    path = ('a', )
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.INCLUDE_RECURSIVELY)

  def test_include_recursively_second_level(self):
    tree = {'a': {'b': {}}}
    path = ('a', 'b')
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.INCLUDE_RECURSIVELY)

  def test_include_recursively_star(self):
    tree = {'a': {field_masks.STAR: {'b': {}}}}
    path = ('a', 'x', 'b')
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.INCLUDE_RECURSIVELY)

  def test_include_partially(self):
    tree = {'a': {'b': {}}}
    path = ('a', )
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.INCLUDE_PARTIALLY)

  def test_include_partially_second_level(self):
    tree = {'a': {'b': {'c': {}}}}
    path = ('a', 'b')
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.INCLUDE_PARTIALLY)

  def test_include_partially_star(self):
    tree = {'a': {field_masks.STAR: {'b': {}}}}
    path = ('a', 'x')
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.INCLUDE_PARTIALLY)

  def test_exclude(self):
    tree = {'a': {}}
    path = ('b',)
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.EXCLUDE)

  def test_exclude_second_level(self):
    tree = {'a': {'b': {}}}
    path = ('a', 'c')
    self.assertEqual(
        field_masks.must_include(tree, path),
        field_masks.EXCLUDE)


class TrimTests(unittest.TestCase):

  def trim(self, msg, *mask_paths):
    field_masks.trim_message(msg, field_mask_pb2.FieldMask(paths=mask_paths))

  def test_scalar_trim(self):
    msg = test_proto_pb2.Msg(num=1)
    self.trim(msg, 'str')
    self.assertEqual(msg, test_proto_pb2.Msg())

  def test_scalar_leave(self):
    msg = test_proto_pb2.Msg(num=1)
    self.trim(msg, 'num')
    self.assertEqual(msg, test_proto_pb2.Msg(num=1))

  def test_scalar_repeated_trim(self):
    msg = test_proto_pb2.Msg(nums=[1, 2])
    self.trim(msg, 'str')
    self.assertEqual(msg, test_proto_pb2.Msg())

  def test_scalar_repeated_leave(self):
    msg = test_proto_pb2.Msg(nums=[1, 2])
    self.trim(msg, 'nums')
    self.assertEqual(msg, test_proto_pb2.Msg(nums=[1, 2]))

  def test_scalar_map_str_num_trim(self):
    msg = test_proto_pb2.Msg(map_str_num={'1': 1, '2': 2})
    self.trim(msg, 'str')
    self.assertEqual(msg, test_proto_pb2.Msg())

  # def test_scalar_map_num_str_trim(self):
  #   msg = test_proto_pb2.Msg(map_str_num={1: '1', 2: '2'})
  #   self.trim(msg)
  #   self.assertEqual(msg, test_proto_pb2.Msg())

  def test_submessage_trim(self):
    msg = test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1))
    self.trim(msg, 'str')
    self.assertEqual(msg, test_proto_pb2.Msg())

  def test_submessage_leave_whole(self):
    msg = test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1))
    self.trim(msg, 'msg')
    self.assertEqual(msg, test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1)))

  def test_submessage_leave_part(self):
    msg = test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1, str='x'))
    self.trim(msg, 'msg.num')
    self.assertEqual(msg, test_proto_pb2.Msg(msg=test_proto_pb2.Msg(num=1)))

  # def test_submessage_repeated_trim(self):
  #   msg = test_proto_pb2.Msg(
  #       msgs=[test_proto_pb2.Msg(num=1), test_proto_pb2.Msg(num=2)])
  #   self.trim(msg)
  #   self.assertEqual(msg, test_proto_pb2.Msg())

  # def test_submessage_repeated_leave_whole(self):
  #   msg = test_proto_pb2.Msg(
  #       msgs=[test_proto_pb2.Msg(num=1), test_proto_pb2.Msg(num=2)])
  #   expected = test_proto_pb2.Msg(
  #       msgs=[test_proto_pb2.Msg(num=1), test_proto_pb2.Msg(num=2)])
  #   self.trim(msg, 'msgs')
  #   self.assertEqual(msg, expected)

  # def test_submessage_repeated_leave_part(self):
  #   msg = test_proto_pb2.Msg(msgs=[
  #       test_proto_pb2.Msg(num=1, str='x'),
  #       test_proto_pb2.Msg(num=2, str='y'),
  #   ])
  #   expected = test_proto_pb2.Msg(msgs=[
  #       test_proto_pb2.Msg(num=1),
  #       test_proto_pb2.Msg(num=2),
  #   ])
  #   self.trim(msg, 'msgs.num')
  #   self.assertEqual(msg, expected)

  # def test_map_trim(self):
  #   msg = test_proto_pb2.Msg(mapping={'a': test_proto_pb2.Msg()})
  #   self.trim(msg)
  #   self.assertEqual(msg, test_proto_pb2.Msg())

  # def test_map_leave_key(self):
  #   msg = test_proto_pb2.Msg(
  #       mapping={'a': test_proto_pb2.Msg()},
  #       num=1)
  #   self.trim(msg, 'mapping.a')
  #   self.assertEqual(
  #       msg,
  #       test_proto_pb2.Msg(mapping={'a': test_proto_pb2.Msg()}))

  # def test_struct_leave_submessage_part(self):
  #   s = struct_pb2.Struct()
  #   s.update(dict(m=dict(num=1, str='a')))

  #   expected = struct_pb2.Struct()
  #   expected.update(dict(m=dict(num=1)))

  #   field_masks.trim_message(s, make_mask('m.num'))
  #   self.assertEqual(s, expected)


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
