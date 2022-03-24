# !/usr/bin/env vpython
# coding: utf-8
# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from components import net
from google.appengine.ext import ndb


def mock_pubsub_requests(assert_equal_func, fail_func, mock_func):
  requests = [
      {
          'url': 'https://pubsub.googleapis.com/v1/'
          'projects/some-project/topics/some-topic:publish',
          'method': 'POST',
          'payload': {
              'attributes': {
                  'a': 1,
                  'b': 2
              },
              'data': 'bXNn',
          },
      },
  ]

  def mocked_request(url, method, payload, scopes):
    requests = [
        {
            'url': 'https://pubsub.googleapis.com/v1/'
            'projects/some-project/topics/some-topic:publish',
            'method': 'POST',
            'payload': {
                'attributes': {
                    'a': 1,
                    'b': 2
                },
                'data': 'bXNn',
            },
        },
    ]
    assert_equal_func(['https://www.googleapis.com/auth/pubsub'], scopes)
    request = {
        'method': method,
        'payload': payload,
        'url': url,
    }
    if not requests:  # pragma: no cover
      fail_func('Unexpected request:\n%r' % request)
    expected = requests.pop(0)
    response = expected.pop('response', None)
    if isinstance(response, net.Error):
      raise response
    future = ndb.Future()
    future.set_result(response)
    return future

  mock_func(net, 'json_request_async', mocked_request)
  return requests
