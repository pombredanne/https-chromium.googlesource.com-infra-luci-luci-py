#!/usr/bin/env vpython
# Copyright 2016 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import json
import sys
import unittest

from test_support import test_env
test_env.setup_test_env()

from protorpc import messages
from protorpc import remote
import endpoints
import flask
import mock

from test_support import test_case
import adapter


class Msg(messages.Message):
  s = messages.StringField(1)
  s2 = messages.StringField(2)


CONTAINER = endpoints.ResourceContainer(Msg, x=messages.StringField(3))


@endpoints.api('Service', 'v1')
class EndpointsService(remote.Service):
  @endpoints.method(Msg, Msg)
  def post(self, _request):
    return Msg()

  @endpoints.method(Msg, Msg, http_method='GET')
  def get(self, _request):
    return Msg()

  @endpoints.method(CONTAINER, Msg, http_method='GET')
  def get_container(self, _request):
    return Msg()

  @endpoints.method(Msg, Msg)
  def post_403(self, _request):
    raise endpoints.ForbiddenException('access denied')


class EndpointsWebapp2TestCase(test_case.TestCase):
  def test_decode_message_post(self):
    request = webapp2.Request(
        {
            'QUERY_STRING': 's2=b',
        },
        method='POST',
        body='{"s": "a"}',
    )
    msg = adapter.decode_message(EndpointsService.post.remote, request)
    self.assertEqual(msg.s, 'a')
    self.assertEqual(msg.s2, None)  # because it is not a ResourceContainer.

  def test_decode_message_get(self):
    request = webapp2.Request(
        {
            'QUERY_STRING': 's=a',
        },
        method='GET',
        route_kwargs={'s2': 'b'},
    )
    msg = adapter.decode_message(EndpointsService.get.remote, request)
    self.assertEqual(msg.s, 'a')
    self.assertEqual(msg.s2, 'b')

  def test_decode_message_get_resource_container(self):
    request = webapp2.Request(
        {
            'QUERY_STRING': 's=a',
        },
        method='GET',
        route_kwargs={
            's2': 'b',
            'x': 'c'
        },
    )
    rc = adapter.decode_message(EndpointsService.get_container.remote, request)
    self.assertEqual(rc.s, 'a')
    self.assertEqual(rc.s2, 'b')
    self.assertEqual(rc.x, 'c')

  def test_handle_403(self):
    app = adapter.api_server([EndpointsService], base_path='/_ah/api')
    with app.test_client() as client:
      response = client.post('/_ah/api/Service/v1/post_403')
    self.assertEqual(response.status, '403 FORBIDDEN')
    self.assertEqual(json.loads(response.data),
                     {'error': {
                         'message': 'access denied',
                     }})

  def test_api_routes(self):
    routes = sorted(
        [r.template for r in adapter.api_routes([EndpointsService])])
    self.assertEqual(
        routes,
        [
            # Each route appears twice below because each route has two
            # different handlers, one for HTTP OPTIONS and the other for
            # user-defined methods.
            '/_ah/api/Service/v1/get',
            '/_ah/api/Service/v1/get',
            '/_ah/api/Service/v1/get_container',
            '/_ah/api/Service/v1/get_container',
            '/_ah/api/Service/v1/post',
            '/_ah/api/Service/v1/post',
            '/_ah/api/Service/v1/post_403',
            '/_ah/api/Service/v1/post_403',
            '/_ah/api/discovery/v1/apis',
            '/_ah/api/discovery/v1/apis/<name>/<version>/rest',
            '/_ah/api/explorer',
            '/_ah/api/static/proxy.html',
        ])

  def test_discovery_routing(self):
    app = adapter.api_server([EndpointsService], base_path='/api')
    with app.test_client() as client:
      response = client.get('/api/discovery/v1/apis/Service/v1/rest')
    data = json.loads(response.data)
    self.assertEqual(data['id'], 'Service:v1')

  def test_directory_routing(self):
    app = adapter.api_server([EndpointsService], base_path='/api')
    with app.test_client() as client:
      response = client.get('/api/discovery/v1/apis')
    data = json.loads(response.data)
    self.assertEqual(len(data.get('items', [])), 1)
    self.assertEqual(data['items'][0]['id'], 'Service:v1')

  def test_proxy_routing(self):
    app = flask.Flask(__name__)
    rule, endpoint, view_func, methods = adapter.explorer_proxy_route('/api')
    app.add_url_rule(rule,
                     endpoint=endpoint,
                     view_func=view_func,
                     methods=methods)
    with app.test_client() as client:
      response = client.get('/api/static/proxy.html')
    self.assertIn('/api', response.data)

  def test_redirect_routing(self):
    app = flask.Flask(__name__)
    rule, endpoint, view_func, methods = adapter.explorer_redirect_route('/api')
    app.add_url_rule(rule,
                     endpoint=endpoint,
                     view_func=view_func,
                     methods=methods)

    with app.test_client() as client:
      response = client.get('/api/explorer')
    self.assertEqual(response.status, '302 FOUND')


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  unittest.main()
