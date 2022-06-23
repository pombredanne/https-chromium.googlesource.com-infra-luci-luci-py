# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging

# Helpers are in separate modules so this one exposes only the public interface.
from components.prpc import encoding
from components.prpc import headers
from components.prpc.codes import StatusCode
from components.prpc.context import ServicerContext
from components.prpc.server_base import HandlerCallDetails, ServerBase

try:
  import flask
except ImportError:
  flask = None


class FlaskServer(ServerBase):
  def get_routes(self, prefix=''):
    return [('%s/prpc/<service>/<method>' % prefix, self._prpcHandler,
             ['POST', 'OPTIONS'])]

  def _prpcHandler(self, service, method):
    request = flask.request
    response = flask.make_response()

    if request.method == 'POST':
      self._post(service, method, request, response)
    elif request.method == 'OPTIONS':
      self._options(request, response)

    return response

  def _post(self, service, method, request, response):
    """Writes body and headers of flask.Response.

    Args:
      service: the service being targeted by this pRPC call.
      method: the method being invoked by this pRPC call.

    Returns:
      response: a flask.Response.
    """
    response_body = self._default_routes_post_request_response(
        service, method, request, response)
    response.response = response_body
    return response

  def _options(self, request, response):
    self._default_routes_options_request_response(request, response)
    return response
