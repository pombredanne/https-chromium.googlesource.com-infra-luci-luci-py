# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""A stripped-down implementation of the gRPC interface for Python on AppEngine.

The Server class itself also provides the bulk of the implementation which
actually runs on AppEngine (and therefore couldn't include Cython). It acts
as a webapp2.RequestHandler, and exposes a .get_routes() method for the host
application to call.

https://github.com/grpc/grpc/tree/master/src/python/grpcio/grpc
"""

from components.prpc.server_base import HandlerCallDetails, ServerBase
import logging
import webapp2

# Helpers are in separate modules so this one exposes only the public interface.
from components.prpc import encoding
from components.prpc import headers
from components.prpc.codes import StatusCode
from components.prpc.context import ServicerContext


class Server(ServerBase):
  """
    Implement a webapp2.RequestHandler, and get_routes() method for the host
    application to call.
  """

  def get_routes(self, prefix=''):
    """Returns a list of webapp2.Route for all the routes the API handles."""
    return [
        webapp2.Route(
            '%s/prpc/<service>/<method>' % prefix,
            handler=self._handler(),
            methods=['POST', 'OPTIONS'])
    ]

  def _response_body_writer(self, response, body):
    response.out.write(body)

  def _response_status_write(self, response, status):
    response.status = status

  def _handler(self):
    """Returns a RequestHandler class with access to this server's data."""

    # Alias self as server here for readability.
    server = self

    class Handler(webapp2.RequestHandler):

      def post(self, service, method):
        """Writes body and headers of webapp2.Response.

        Args:
          service: the service being targeted by this pRPC call.
          method: the method being invoked by this pRPC call.

        Returns:
          response: a webapp2.Response.
        """
        server._post_handler(service, method, self.request, self.response)
        return self.response

      # pylint: disable=unused-argument
      def options(self, service, method):
        """Sends an empty response with CORS headers for origins, if allowed."""
        server._options_handler(self.request, self.response)

    return Handler
