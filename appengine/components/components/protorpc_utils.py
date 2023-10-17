# Copyright 2013 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Utilities which rely on the deprecated protorpc library."""

import datetime
import inspect
import json
import sys

from components.utils import DATE_FORMAT, DATETIME_FORMAT

from protorpc import messages
from protorpc.remote import protojson



def to_json_encodable(data):
  """Converts data into json-compatible data."""
  if isinstance(data, messages.Message):
    # protojson.encode_message returns a string that is already encoded json.
    # Load it back into a json-compatible representation of the data.
    return json.loads(protojson.encode_message(data))
  if isinstance(data, unicode) or data is None:
    return data
  if isinstance(data, str):
    return data.decode('utf-8')
  if isinstance(data, (int, float, long)):
    # Note: overflowing is an issue with int and long.
    return data
  if isinstance(data, (list, set, tuple)):
    return [to_json_encodable(i) for i in data]
  if isinstance(data, dict):
    assert all(isinstance(k, basestring) for k in data), data
    return {
      to_json_encodable(k): to_json_encodable(v) for k, v in data.items()
    }

  if isinstance(data, datetime.datetime):
    # Convert datetime objects into a string, stripping off milliseconds. Only
    # accept naive objects.
    if data.tzinfo is not None:
      raise ValueError('Can only serialize naive datetime instance')
    return data.strftime(DATETIME_FORMAT)
  if isinstance(data, datetime.date):
    return data.strftime(DATE_FORMAT)
  if isinstance(data, datetime.timedelta):
    # Convert timedelta into seconds, stripping off milliseconds.
    return int(data.total_seconds())

  if hasattr(data, 'to_dict') and callable(data.to_dict):
    # This takes care of ndb.Model.
    return to_json_encodable(data.to_dict())

  if hasattr(data, 'urlsafe') and callable(data.urlsafe):
    # This takes care of ndb.Key.
    return to_json_encodable(data.urlsafe())

  if inspect.isgenerator(data):
    return [to_json_encodable(i) for i in data]

  if sys.version_info.major == 2 and isinstance(data, xrange):
    # Handle it like a list. Sadly, xrange is not a proper generator so it has
    # to be checked manually.
    return [to_json_encodable(i) for i in data]

  assert False, 'Don\'t know how to handle %r' % data
  return None


def encode_to_json(data):
  """Converts any data as a json string."""
  return json.dumps(
      to_json_encodable(data),
      sort_keys=True,
      separators=(',', ':'),
      encoding='utf-8')
