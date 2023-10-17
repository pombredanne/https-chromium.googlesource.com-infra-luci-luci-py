#!/usr/bin/env vpython
# Copyright 2013 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import datetime
import sys
import unittest

from test_support import test_env
test_env.setup_test_env()

from google.appengine.ext import ndb

from components import protorpc_utils
from test_support import test_case


class Rambling(ndb.Model):
  """Fake statistics."""
  a = ndb.IntegerProperty()
  b = ndb.FloatProperty()
  c = ndb.DateTimeProperty()
  d = ndb.DateProperty()

  def to_dict(self):
    out = super(Rambling, self).to_dict()
    out['e'] = datetime.timedelta(seconds=1.1)
    out['f'] = '\xc4\xa9'
    return out


class ProtorpcJSONTest(test_case.TestCase):
  def test_json(self):
    r = Rambling(
        a=2,
        b=0.2,
        c=datetime.datetime(2012, 1, 2, 3, 4, 5, 6),
        d=datetime.date(2012, 1, 2))
    actual = protorpc_utils.to_json_encodable([r])
    # Confirm that default is tight encoding and sorted keys.
    expected = [
      {
        'a': 2,
        'b': 0.2,
        'c': u'2012-01-02 03:04:05',
        'd': u'2012-01-02',
        'e': 1,
        'f': u'\u0129',
      },
    ]
    self.assertEqual(expected, actual)

    self.assertEqual([0, 1], protorpc_utils.to_json_encodable(range(2)))
    self.assertEqual([0, 1], protorpc_utils.to_json_encodable(i for i in (0, 1)))
    if sys.version_info.major == 2:
      self.assertEqual([0, 1], protorpc_utils.to_json_encodable(xrange(2)))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
