# !/usr/bin/env vpython
# coding: utf-8
# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from components import net
from google.appengine.ext import ndb


def mock_pubsub_requests(assert_equal_func, mock_func):
  @ndb.tasklet
  def mocked_request(scopes, **kwargs):  # pylint: disable=unused-argument
    assert_equal_func(['https://www.googleapis.com/auth/pubsub'], scopes)
    future = ndb.Future()
    future.set_result(None)
    raise ndb.Return(future)

  mock_func(net, 'json_request_async', mocked_request)
  return None
