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
  flask = type('flask', (object), {
      "reqeust": object,
      "make_response": function
  })


class FlaskServer(ServerBase):
  def get_routes(self, prefix=''):
    return [('%s/prpc/<service>/<method>' % prefix, self._flaskhandler(),
             ['POST', 'OPTIONS'])]

  def _flaskhandler(self):
    server = self

    class FlaskHandler(object):
      def __init__(self):
        self.request = flask.request
        self.response = None

      def pRcphandler(self, service, method):
        self.response = flask.make_response()

        if self.request.method == 'POST':
          self.post(service, method)
        elif self.request.method == 'OPTIONS':
          self.options(service, method)

        return self.response

      def post(self, service, method):
        """Writes body and headers of flask.Response.

        Args:
          service: the service being targeted by this pRPC call.
          method: the method being invoked by this pRPC call.

        Returns:
          response: a flask.Response.
        """
        response_body = server._default_routes_post_request_response(
            service, method, self.request, self.response)
        self.response.response = response_body
        return self.response

      # pylint: disable=unused-argument
      def options(self, service, method):
        server._default_routes_options_request_response(self.request,
                                                        self.response)

    return FlaskHandler.pRcphandler
