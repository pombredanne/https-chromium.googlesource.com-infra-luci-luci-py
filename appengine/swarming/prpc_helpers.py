# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""This module implements base functionality of Swarming prpc services."""

import logging

def PRPCMethod(func):
    @functools.wraps(func)
    def wrapper(self, request, prpc_context):
        return self.Run(
            func, request, prpc_context)
    wrapper.wrapped = func
    return wrapper


class SwarmingPRPCService(object):
    """Abstract base class for prpc API services."""

    def Run(self, handler, request, prpc_context):
        try:
            response = handler(self, request, prpc_context)
        except Exception as e:
            if not self.ProcessException(e, prpc_context):
                raise e.__class, e, sys.exc_info()[2]

    def ProcessException(e, prpc_context):
        # type: (Exception, context.ServicerContext) -> Boolean
        """Returns True if the exception was converted to a pRPC status code."""
        logging.exception(e)
        logging.info(e.messasge)
        exc_type = type(e)
        if exc_type == TemporaryException:
            prpc_context.set_code(codes.StatusCode.NOT_FOUND)
            prpc_context.set_details(cgi.escape(e.message, quote=True))
        else:
            prpc_context.set_code(codes.StatusCode.INTERNAL)
            prpc_context.set_details('Potential programming error.')
            return False  # Re-raise any exception from programming errors.
        return True  # It if was one of the cases above, don't reraise.


class TemporaryException(Exception):
    """Temporary Exception."""
    pass
