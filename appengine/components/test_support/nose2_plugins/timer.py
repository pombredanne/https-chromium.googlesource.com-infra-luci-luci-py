# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from __future__ import print_function

import logging
import os
import sys
import threading
import traceback

from nose2.events import Plugin

log = logging.getLogger('nose2.plugins.timer')


def _show_all_stacktraces():
  """This is used to show where the threads are stucked."""
  frames = sys._current_frames()
  for th in threading.enumerate():
    print('Thread:%s' % th.name, file=sys.stderr)
    if th.ident is None:
      print('not started, skipped', file=sys.stderr)
      continue
    traceback.print_stack(frames[th.ident], limit=None)

  sys.stderr.flush()
  # os._exit is necessary to exit whole process.
  os._exit(1)


class Timer(Plugin):
  alwaysOn = True

  def __init__(self):
    self._timer = None

  def startTest(self, event):
    self._timer = threading.Timer(30, _show_all_stacktraces)
    self._timer.start()
    log.debug('start %s', event.test)

  def stopTest(self, event):
    self._timer.cancel()
    log.debug('stop %s', event.test)
