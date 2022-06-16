# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import collections
import logging

# Helpers are in separate modules so this one exposes only the public interface.
from components.prpc import encoding
from components.prpc import headers
from components.prpc.codes import StatusCode
from components.prpc.context import ServicerContext

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
HandlerCallDetails = collections.namedtuple('HandlerCallDetails', [
  'method',               # full method name <service>.<method>
  'invocation_metadata',  # (k, v) pairs list with metadata sent by the client
])
class FlaskServerHandler(object):
  def __init__(self, server, flask):
    self.flask = flask
    self.request = self.flask.request
    self.response = None
    self.server = server

  def pRcpHandler(self, service, method):
    self.response = self.flask.make_response()

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
    context = ServicerContext()
    content = self._handle(context, service, method)
    origin = self.request.headers.get('Origin')
    if origin:
      self.response.headers['Access-Control-Allow-Origin'] = origin
      self.response.headers['Vary'] = 'Origin'
      self.response.headers['Access-Control-Allow-Credentials'] = 'true'
    self.response.status_code = _PRPC_TO_HTTP_STATUS[context._code]
    self.response.headers['X-Prpc-Grpc-Code'] = str(context._code.value)
    self.response.headers['Access-Control-Expose-Headers'] = (
        'X-Prpc-Grpc-Code')
    self.response.headers['X-Content-Type-Options'] = 'nosniff'
    if content is not None:
      self.response.headers['Content-Type'] = encoding.Encoding.media_type(
          context._response_encoding)
      self.response.response = content
    elif context._details is not None:
      # webapp2 will automatically encode strings as utf-8.
      # http://webapp2.readthedocs.io/en/latest/guide/response.html
      #
      # TODO(nodir,mknyszek): Come up with an actual test for this.
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      self.response.response = context._details
    return self.response

  def _handle(self, context, service, method):
    """Generates the response content and sets the context appropriately.

    Sets context._request_encoding and context._response_encoding.

    Args:
      context: a context.ServicerContext.
      service: the service being targeted by this pRPC call.
      method: the method being invoked by this pRPC call.

    Returns:
      content: the binary or textual content of the RPC response. Note
        that this may be None in the event that an error occurs.
    """
    try:
      parsed_headers = headers.parse_headers(self.request.headers)
      context._request_encoding = parsed_headers.content_type
      context._response_encoding = parsed_headers.accept
    except ValueError as e:
      logging.warning('Error parsing headers: %s', e)
      context.set_code(StatusCode.INVALID_ARGUMENT)
      context.set_details(e.message)
      return None

    if service not in self.server._services:
      context.set_code(StatusCode.UNIMPLEMENTED)
      context.set_details('Service %s does not exist' % service)
      return None
    rpc_handler = self.server._services[service].methods.get(method)
    if rpc_handler is None:
      context.set_code(StatusCode.UNIMPLEMENTED)
      context.set_details('Method %s does not exist' % method)
      return None
    request_message, response_message, handler = rpc_handler

    request = request_message()
    try:
      decoder = encoding.get_decoder(parsed_headers.content_type)
      decoder(self.request.values, request)
    except Exception as e:
      logging.warning('Failed to decode request: %s', e, exc_info=True)
      context.set_code(StatusCode.INVALID_ARGUMENT)
      context.set_details('Error parsing request: %s' % e.message)
      return None

    context._timeout = parsed_headers.timeout
    context._invocation_metadata = parsed_headers.invocation_metadata

    # Only ipv6 addresses have ':' in them. Assume everything else is ipv4.
    if ':' in self.request.remote_addr:
      context._peer = 'ipv6:[%s]' % self.request.remote_addr
    else:
      context._peer = 'ipv4:%s' % self.request.remote_addr

    call_details = HandlerCallDetails(
        method='%s.%s' % (service, method),
        invocation_metadata=context.invocation_metadata())

    try:
      # TODO(nodir,mknyszek): Poll for context to hit timeout or be
      # canceled.
      response = self.server._run_interceptors(request, context, call_details,
                                               handler, 0)
    except Exception:
      logging.exception('Service implementation threw an exception')
      context.set_code(StatusCode.INTERNAL)
      context.set_details('Service implementation threw an exception')
      return None

    if response is None:
      if context._code == StatusCode.OK:
        context.set_code(StatusCode.INTERNAL)
        context.set_details('Service implementation didn\'t return a response')
      return None

    if not isinstance(response, response_message):
      logging.error('Service implementation response has incorrect type')
      context.set_code(StatusCode.INTERNAL)
      context.set_details('Service implementation returned invalid value')
      return None

    try:
      encoder = encoding.get_encoder(parsed_headers.accept)
      content = encoder(response)
    except Exception:
      logging.exception('Failed to encode response')
      context.set_code(StatusCode.INTERNAL)
      context.set_details('Error serializing response')
      return None

    return content

    # pylint: disable=unused-argument
  def options(self, service, method):
    """Sends an empty response with CORS headers for origins, if allowed."""
    origin = self.request.headers.get('Origin')

    if origin and self.server.allow_cors and (
        not self.server.allowed_origins
        or origin in self.server.allowed_origins):
      self.response.headers['Access-Control-Allow-Origin'] = origin
      self.response.headers['Vary'] = 'Origin'
      self.response.headers['Access-Control-Allow-Credentials'] = 'true'
      self.response.headers['Access-Control-Allow-Headers'] = \
          'Origin, Content-Type, Accept, Authorization'
      self.response.headers['Access-Control-Allow-Methods'] = \
          'OPTIONS, POST'
      self.response.headers['Access-Control-Max-Age'] = '600'
