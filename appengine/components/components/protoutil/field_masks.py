# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Utility functions for google.protobuf.field_mask_pb2.FieldMask."""

from google.protobuf import struct_pb2


def trim_message(msg, field_mask):
  """Clears msg fields that are not in the field_mask.

  Args:
    msg: a google.protobuf.message.Message instance.
    field_mask: a google.protobuf.field_mask_pb2.FieldMask instance.
  """
  _trim(msg, _field_mask_to_dict(field_mask))


def _trim(msg, mask):
  if isinstance(msg, struct_pb2.Struct):
    for k, v in msg.fields.items():
      fm = mask.get(k)
      if fm is None:
        msg.fields.pop(k)
      elif v.struct_value and len(fm) > 0:
        _trim(v.struct_value, fm)
  else:
    for f, v in msg.ListFields():
      fm = mask.get(f.name)
      if fm is None:
        msg.ClearField(f.name)
      elif f.message_type and len(fm) > 0:
        _trim(v, fm)


def _field_mask_to_dict(field_mask):
  ret = {}
  for path in field_mask.paths:
    cur = ret
    for comp in path.split('.'):
      cur = cur.setdefault(comp, {})
  return ret
