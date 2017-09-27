# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Handlers decorators."""

import functools
import logging
import os


DISABLE_UI = os.environ.get('LUCI_DISABLE_UI_ROUTES', '0')

def forbid_ui_if_disabled(method):
  @functools.wraps(method)
  def wrapper(self, *args, **kwargs):
    if DISABLE_UI == '1':
      self.abort(
          405,
          detail='UI is disabled.')
    return method(self, *args, **kwargs)
  return wrapper

def silence(*exceptions):
  """Eats the exceptions listed and log a warning instead of an error.

  Sets the error code to HTTP 500. This will cause taskqueue to be automatically
  retried.
  """
  def decorator(f):
    @functools.wraps(f)
    def hook(self, *args, **kwargs):
      try:
        return f(self, *args, **kwargs)
      except tuple(exceptions) as e:  # pylint: disable=catching-non-exception
        logging.warning('Silencing exception %s', e)
        self.abort(500)
    return hook
  return decorator


def require_cronjob(f):
  """Enforces cronjob."""
  @functools.wraps(f)
  def hook(self, *args, **kwargs):
    if self.request.headers.get('X-AppEngine-Cron') != 'true':
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      msg = 'Only internal cron jobs can do this'
      logging.error(msg)
      self.abort(403, msg)
      return
    return f(self, *args, **kwargs)
  return hook


def require_taskqueue(task_name):
  """Enforces the task is run with a specific task queue."""
  def decorator(f):
    @functools.wraps(f)
    def hook(self, *args, **kwargs):
      actual_name = self.request.headers.get('X-AppEngine-QueueName')
      if actual_name != task_name:
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        msg = 'Only internal task %s can do this' % task_name
        if actual_name:
          msg += '; got %s' % actual_name
        logging.error(msg)
        self.abort(403, msg)
        return
      return f(self, *args, **kwargs)
    return hook
  return decorator
