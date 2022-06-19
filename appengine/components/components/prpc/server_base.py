# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""A stripped-down implementation of the gRPC interface for Python on AppEngine.

The Server class itself also provides the bulk of the implementation which
actually runs on AppEngine (and therefore couldn't include Cython).
Subclasses should override get_routes() method for the host application to call.

https://github.com/grpc/grpc/tree/master/src/python/grpcio/grpc
"""

import collections
import httplib

from google.protobuf import symbol_database

# Helpers are in separate modules so this one exposes only the public interface.
from components.prpc import discovery
from components.prpc.codes import StatusCode

_Service = collections.namedtuple('_Service', ['servicer', 'methods'])


class ServerBase(object):
  """Server represents a pRPC server that handles a set of services.

  Server is intended to vaguely mimic gRPC's Server as an abstraction, but
  provides a simpler interface via add_service and get_routes.
  """
  __all__ = [
      'HandlerCallDetails',
      'Server',
      'StatusCode',
  ]

  # pylint: disable=pointless-string-statement

  _PRPC_TO_HTTP_STATUS = {
      StatusCode.OK: httplib.OK,
      StatusCode.CANCELLED: httplib.NO_CONTENT,
      StatusCode.INVALID_ARGUMENT: httplib.BAD_REQUEST,
      StatusCode.DEADLINE_EXCEEDED: httplib.SERVICE_UNAVAILABLE,
      StatusCode.NOT_FOUND: httplib.NOT_FOUND,
      StatusCode.ALREADY_EXISTS: httplib.CONFLICT,
      StatusCode.PERMISSION_DENIED: httplib.FORBIDDEN,
      StatusCode.RESOURCE_EXHAUSTED: httplib.SERVICE_UNAVAILABLE,
      StatusCode.FAILED_PRECONDITION: httplib.PRECONDITION_FAILED,
      StatusCode.OUT_OF_RANGE: httplib.BAD_REQUEST,
      StatusCode.UNIMPLEMENTED: httplib.NOT_IMPLEMENTED,
      StatusCode.INTERNAL: httplib.INTERNAL_SERVER_ERROR,
      StatusCode.UNAVAILABLE: httplib.SERVICE_UNAVAILABLE,
      StatusCode.UNAUTHENTICATED: httplib.UNAUTHORIZED,
  }

  # Details about the RPC call passed to the interceptors.
  HandlerCallDetails = collections.namedtuple(
      'HandlerCallDetails',
      [
          'method',  # full method name <service>.<method>
          # (k, v) pairs list with metadata sent by the client
          'invocation_metadata',
      ])

  def __init__(self, allow_cors=True, allowed_origins=None):
    """Initializes a new Server.

    Args:
      allow_cors: opttional boolean. True if CORS should be allowed.
      allowed_origins: optional collection of allowed origins. Only used
        when cors is allowed. If empty, all origins will be allowed, otherwise
        only listed origins will be allowed.

    """
    self._services = {}
    self._interceptors = ()
    self._discovery_service = discovery.Discovery()
    self.add_service(self._discovery_service)
    self.allow_cors = allow_cors
    self.allowed_origins = set(allowed_origins or [])

  def add_interceptor(self, interceptor):
    """Adds an interceptor to the interceptor chain.

    Interceptors can be used to examine or modify requests before they reach
    the real handlers. The API is vaguely similar to grpc.ServerInterceptor.

    An interceptor is a callback that accepts following arguments:
      request: deserialized request message.
      context: an instance of ServicerContext.
      call_details: an instance of HandlerCallDetails.
      continuation: a callback that resumes the processing, accepts
        (request, context, call_details).

    An interceptor may decide NOT to call the continuation if it handles the
    request itself.

    Args:
      interceptor: an interceptor callback to add to the chain.
    """
    self._interceptors = self._interceptors + (interceptor, )

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
    pkg = servicer.DESCRIPTION['file_descriptor'].package
    desc = servicer.DESCRIPTION['service_descriptor']

    # Construct handler.
    methods = {
        method.name: (
            # Fully-qualified proto type names will always begin with a '.'
            # which GetSymbol doesn't strip out.
            sym_db.GetSymbol(method.input_type[1:]),
            sym_db.GetSymbol(method.output_type[1:]),
            getattr(servicer, method.name),
        )
        for method in desc.method if hasattr(servicer, method.name)
    }

    full_name = desc.name
    if pkg:
      full_name = '%s.%s' % (pkg, desc.name)

    # Register handler with internal server state.
    if desc.name in self._services:
      raise ValueError('Tried to double-register handlers for service %s' %
                       desc.name)
    self._services[full_name] = _Service(servicer, methods)

    self._discovery_service.add_service(servicer.DESCRIPTION)

  def get_routes(self, prefix=''):
    """Returns a list of routes the API handles."""
    raise NotImplementedError("Get_routes must be implemented")

  def _run_interceptors(self, request, context, call_details, handler, idx):
    """Runs the request via interceptors chain starting from given index.

    Args:
      request: deserialized request proto.
      context: a context.ServicerContext.
      handler: a final handler, given as callback (request, context): response.
      idx: an index in the interceptor chain to start from.

    Returns:
      Response message.
    """
    if idx == len(self._interceptors):
      return handler(request, context)

    def continuation(request, context, call_details):
      return self._run_interceptors(request, context, call_details, handler,
                                    idx + 1)

    interceptor = self._interceptors[idx]
    return interceptor(request, context, call_details, continuation)
