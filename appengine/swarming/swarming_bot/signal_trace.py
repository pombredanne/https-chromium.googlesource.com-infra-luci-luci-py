# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Prints stack trace on SIGUSR1 and starts interactive console on SIGUSR2."""

import code
import traceback
import signal
import sys
import traceback


def _dump(_sig, frame):
  """Dumps the stack trace of all threads."""
  sys.stderr.write('** SIGUSR1 received **\n')
  traceback.print_stack(frame, file=sys.stderr)


def _debug(_sig, frame):
  """Starts an interactive prompt in the main thread."""
  d = {'_frame': frame}
  d.update(frame.f_globals)
  d.update(frame.f_locals)
  code.InteractiveConsole(d).interact(
      'Signal received : entering python shell.\nTraceback:\n%s' % (
      ''.join(traceback.format_stack(frame))))


def register():
  """Registers an handler to catch SIGUSR1 and print a stack trace."""
  if sys.platform not in ('cygwin', 'win32'):
    signal.signal(signal.SIGUSR1, _dump)
    signal.signal(signal.SIGUSR2, _debug)
