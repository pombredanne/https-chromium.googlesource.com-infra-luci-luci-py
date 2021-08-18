# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""This module implements base functionality of Swarming prpc services."""

import cgi
import functools
import logging
import sys

from components.prpc import codes

import handlers_exceptions

EXCEPTIONS_TO_CODE = {
    handlers_exceptions.BadRequestException: codes.StatusCode.INVALID_ARGUMENT,
    handlers_exceptions.PermissionException: codes.StatusCode.PERMISSION_DENIED,
    handlers_exceptions.InternalException: codes.StatusCode.INTERNAL,
}


def PRPCMethod(func):

  @functools.wraps(func)
  def wrapper(self, request, prpc_context):
    return self.Run(func, request, prpc_context)

  wrapper.wrapped = func
  return wrapper


class SwarmingPRPCService(object):
  """Abstract base class for prpc API services."""

  def Run(self, handler, request, prpc_context):
    response = None
    try:
      response = handler(self, request, prpc_context)
    except Exception as e:
      if not self.ProcessException(e, prpc_context):
        raise e.__class__, e, sys.exc_info()[2]

    return response

  def ProcessException(self, e, prpc_context):
    # type: (Exception, context.ServicerContext) -> Boolean
    """Returns True if the exception was converted to a pRPC status code."""
    logging.exception(e)
    logging.info(e.message)
    exc_type = type(e)
    code = EXCEPTIONS_TO_CODE.get(exc_type)
    if code is None:
      prpc_context.set_code(codes.StatusCode.INTERNAL)
      prpc_context.set_details('Potential programming error.')
      return False  # Re-raise any exception from programming errors.

    prpc_context.set_code(code)
    prpc_context.set_details(cgi.escape(e.message, quote=True))
    return True
