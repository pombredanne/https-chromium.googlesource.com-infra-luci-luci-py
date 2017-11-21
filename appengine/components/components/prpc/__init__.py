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

import webapp2

from google.protobuf import symbol_database

# Helpers are in separate modules so this one exposes only the public interface.
from components.prpc import helpers
from components.prpc import types

# pylint: disable=pointless-string-statement


class StatusCode(object):
  """Mirrors grpc_status_code in the gRPC Core."""
  OK                  = (0, 'ok')
  CANCELLED           = (1, 'cancelled')
  UNKNOWN             = (2, 'unknown')
  INVALID_ARGUMENT    = (3, 'invalid argument')
  DEADLINE_EXCEEDED   = (4, 'deadline exceeded')
  NOT_FOUND           = (5, 'not found')
  ALREADY_EXISTS      = (6, 'already exists')
  PERMISSION_DENIED   = (7, 'permission denied')
  RESOURCE_EXHAUSTED  = (8, 'resource exhausted')
  FAILED_PRECONDITION = (9, 'failed precondition')
  ABORTED             = (10, 'aborted')
  OUT_OF_RANGE        = (11, 'out of range')
  UNIMPLEMENTED       = (12, 'unimplemented')
  INTERNAL            = (13, 'internal')
  UNAVAILABLE         = (14, 'unavailable')
  DATA_LOSS           = (15, 'data loss')
  UNAUTHENTICATED     = (16, 'unauthenticated')


class Server(object):
  """Server represents a pRPC server that handles a set of services.

  Server is intended to mimic gRPC's Server as an abstraction, but provides
  a simpler interface via add_service and get_routes.
  """

  def __init__(self):
    self._generic_handlers = {}

  def add_service(self, servicer):
    """Registers a servicer for a service with the server.

    Args:
      servicer: A servicer which represents a service. It must have a
        DESCRIPTION of the service and implements handlers for each service
        method.

    Raises:
      ValueError: when trying to add another handler for the same service name.
    """
    sym_db = symbol_database.Default()
    service = servicer.DESCRIPTION

    # Construct handler.
    methods = {
      method.name: types.RpcMethodHandler(
        sym_db.GetSymbol(method.input_type),
        sym_db.GetSymbol(method.output_type),
        getattr(servicer, method.name)
          if hasattr(servicer, method.name)
          else None,
      )
      for method in service.method
    }
    handler = types.GenericRpcHandler(service.name, methods)

    # Register handler with internal server state.
    if service.name in self._generic_handlers:
      raise ValueError(
          'Tried to double-register handlers for service %s' % service.name)
    self._generic_handlers[service.name] = handler

  def get_routes(self):
    """Returns a list of webapp2.Route for all the routes the API handles."""
    return [webapp2.Route('/prpc/<service>/<method>',
                          handler=self._handler(),
                          methods=['POST', 'OPTIONS'])]

  def _handler(server):  # pylint: disable=no-self-argument
    """Returns a RequestHandler class with access to this server's data."""
    # Note that this method takes 'server' instead of 'self'; this is to
    # let the inner class use the canonical 'self.request' without shadowing
    # the reference to the outer instance.

    class Handler(webapp2.RequestHandler):

      def finalize(self, context, content=''):
        """Writes body and headers of webapp2.Response based on context.

        Args:
          context: types.ServicerContext used to set response headers
          content: if no errors were found, will be written to the body

        Returns:
          response: a webapp2.Response derived from self.response
        """
        origin = self.request.headers.get('Origin')
        if origin:
          self.response.headers['Access-Control-Allow-Origin'] = origin
          self.response.headers['Vary'] = 'Origin'
          self.response.headers['Access-Control-Allow-Credentials'] = 'true'

        if context.code is None:
          context.code = StatusCode.OK
        elif context.code != StatusCode.OK:
          if not context.details:
            context.details = context.code[1]
          content = context.details

        # TODO(agable): Set HTTP response code from gRPC response code as well.
        self.response.headers['X-Prpc-Grpc-Code'] = str(context.code[0])
        self.response.headers['Access-Control-Expose-Headers'] = (
            'X-Prpc-Grpc-Code')
        self.response.out.write(content)
        return self.response

      def post(self, service, method):
        """Handles all requests to all services and methods."""
        context = types.ServicerContext()

        try:
          content_type, accept = helpers.process_headers(
              context, self.request.headers)
        except ValueError as e:
          self.set_status(400)
          self.response.out.write(e.message)
          return

        if service not in server._generic_handlers:
          context.set_code(StatusCode.UNIMPLEMENTED)
          context.set_details('Service %s does not exist' % service)
          return self.finalize(context)
        call_details = types.HandlerCallDetails(
            method, context.invocation_metadata)
        rpc_handler = server._generic_handlers[service].service(call_details)
        if rpc_handler is None:
          context.set_code(StatusCode.UNIMPLEMENTED)
          context.set_details('Method %s does not exist' % method)
          return self.finalize(context)

        request = rpc_handler.request_message()

        try:
          decoder = helpers.get_decoder(content_type)
          decoder(self.request.body, request)
        except Exception:
          context.set_code(StatusCode.INTERNAL)
          context.set_details('Error parsing request')
          return self.finalize(context)

        try:
          # TODO(agable): Poll for context to hit timeout or be canceled.
          response = rpc_handler.handler(request, context)
        except Exception as e:
          # TODO(agable): Add really good logging for this. Because we're still
          # returning a valid response to the client, this won't result in
          # stacktraces in logs, so we need to log them ourselves.
          context.set_code(StatusCode.UNKNOWN)
          context.set_details('Service implementation threw an exception')
          return self.finalize(context)

        if response is None:
          return self.finalize(context)

        if not isinstance(response, rpc_handler.response_message):
          context.set_code(StatusCode.UNKNOWN)
          context.set_details('Service implementation returned invalid value')
          return self.finalize(context)

        try:
          encoder = helpers.get_encoder(accept)
          content = encoder(response)
          self.response.headers['Content-Type'] = helpers.Encoding.header(
              accept)
        except Exception:
          context.set_code(StatusCode.INTERNAL)
          context.set_details('Error serializing response')
          return self.finalize(context)

        return self.finalize(context, content)

      def options(self, _service, _method):
        """Sends an empty response with headers for CORS for all requests."""
        origin = self.request.headers.get('Origin')
        if origin:
          self.response.headers['Access-Control-Allow-Origin'] = origin
          self.response.headers['Vary'] = 'Origin'
          self.response.headers['Access-Control-Allow-Credentials'] = 'true'
          self.response.headers['Access-Control-Allow-Headers'] = [
              'Origin', 'Content-Type', 'Accept', 'Authorization']
          self.response.headers['Access-Control-Allow-Methods'] = [
              'OPTIONS', 'POST']
          self.response.headers['Access-Control-Max-Age'] = '600'

    return Handler
