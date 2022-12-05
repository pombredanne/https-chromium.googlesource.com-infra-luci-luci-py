# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""This module implements base functionality of Swarming prpc services."""

import cgi
import functools
import logging

from google.appengine.api import datastore_errors

from components import auth
from components.prpc import codes

import handlers_exceptions
import endpoints

EXCEPTIONS_TO_CODE = {
    handlers_exceptions.NotFoundException: codes.StatusCode.NOT_FOUND,
    handlers_exceptions.BadRequestException: codes.StatusCode.INVALID_ARGUMENT,
    datastore_errors.BadValueError: codes.StatusCode.INVALID_ARGUMENT,
    handlers_exceptions.PermissionException: codes.StatusCode.PERMISSION_DENIED,
    handlers_exceptions.InternalException: codes.StatusCode.INTERNAL,
    auth.AuthorizationError: codes.StatusCode.PERMISSION_DENIED,
    endpoints.NotFoundException: codes.StatusCode.NOT_FOUND,
    endpoints.BadRequestException: codes.StatusCode.INVALID_ARGUMENT,
}


def prpc_method(func):

  @functools.wraps(func)
  def wrapper(self, request, prpc_context):
    return self.Run(func, request, prpc_context)

  wrapper.wrapped = func
  return wrapper


class SwarmingPRPCService(object):
  """Abstract base class for prpc API services."""

  def Run(self, handler, request, prpc_context):
    try:
      response = handler(self, request, prpc_context)
      return response
    except Exception as e:
      code = process_exception(e, prpc_context)
      if code is None:
        raise


def process_exception(e, prpc_context):
  """Sets prpc codes for recognized exceptions. Returns status code if exception
  type is known, otherwise will return None."""
  logging.exception(e)
  exc_type = type(e)
  code = EXCEPTIONS_TO_CODE.get(exc_type)
  if code is None:
    prpc_context.set_code(codes.StatusCode.INTERNAL)
    prpc_context.set_details('Potential programming error.')
    return None

  prpc_context.set_code(code)
  prpc_context.set_details(e.message)

  return code
