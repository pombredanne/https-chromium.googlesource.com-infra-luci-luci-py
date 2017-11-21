# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import time


class RpcMethodHandler(object):

  def __init__(self, request_message, response_message, behavior):
    """An implementation of a single RPC method.

    Args:
      request_message: The request message type for this pRPC method.
      response_message: The response message type for this pRPC method.
      behavior: This object's application-specific business logic as
        a callable value that takes a request value and a ServicerContext object
        and returns a response value.
    """
    self.handler = behavior
    self.request_message = request_message
    self.response_message = response_message


class GenericRpcHandler(object):
  """An implementation of arbitrarily many RPC methods."""

  def __init__(self, service_name, method_handlers):
    """Create a new GenericRpcHandler which handles many methods in one service.

    Args:
      service_name: a string of the form 'package.subpackage.Service'
      method_handlers: a dictionary of the form {'MethodName': RpcMethodHandler}
    """
    self.service_name = service_name
    self.method_handlers = method_handlers

  def service(self, handler_call_details):
    """Services an RPC (or not).

    Args:
      handler_call_details: A HandlerCallDetails describing the RPC.

    Returns:
      An RpcMethodHandler with which the RPC may be serviced, or None to
        indicate that this object will not be servicing the RPC.
    """
    return self.method_handlers.get(handler_call_details.method)


class HandlerCallDetails(object):

  def __init__(self, method, invocation_metadata):
    """Describes an RPC that has just arrived for service.

    Attributes:
      method: The method name of the RPC.
      invocation_metadata: The metadata from the invocation side of the RPC.
    """
    self.method = method
    self.invocation_metadata = invocation_metadata


class ServicerContext(object):
  """A context object passed to method implementations."""

  def __init__(self):
    self._start_time = time.time()
    self.timeout = None
    self.active = True
    self.code = None
    self.details = None
    self.invocation_metadata = {}

  def time_remaining(self):
    """Describes the length of allowed time remaining for the RPC.

    Returns:
      A nonnegative float indicating the length of allowed time in seconds
      remaining for the RPC to complete before it is considered to have timed
      out, or None if no deadline was specified for the RPC.
    """
    if self._timeout is None:
      return None
    now = time.time()
    return max(0, self._start_time + self._timeout - now)

  def cancel(self):
    """Cancels the RPC.

    Idempotent and has no effect if the RPC has already terminated.
    """
    self.active = False

  def set_code(self, code):
    """Accepts the status code of the RPC.

    This method need not be called by method implementations if they wish the
    gRPC runtime to determine the status code of the RPC.

    Args:
      code: The integer status code of the RPC to be transmitted to the
        invocation side of the RPC.
    """
    self.code = code

  def set_details(self, details):
    """Accepts the service-side details of the RPC.

    This method need not be called by method implementations if they have no
    details to transmit.

    Args:
      details: The details string of the RPC to be transmitted to
        the invocation side of the RPC.
    """
    self.details = details
