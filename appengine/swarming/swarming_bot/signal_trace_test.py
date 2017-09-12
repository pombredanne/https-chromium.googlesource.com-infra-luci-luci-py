#!/usr/bin/env python
# Copyright 2017 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import logging
import os
import signal
import subprocess
import sys
import unittest


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class Test(unittest.TestCase):
  def _run(self, cmd, sig):
    p = subprocess.Popen(
        [sys.executable, '-u', '-c', cmd], stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, cwd=THIS_DIR)
    p.stdout.read(1)
    os.kill(p.pid, signal.SIGUSR1)
    return p.communicate()

  def test_SIGUSR1(self):
    cmd = (
        'import signal_trace,sys,time; signal_trace.register(); '
        'sys.stdout.write("1"); sys.stdout.flush(); time.sleep(60)')
    out, err = self._run(cmd, signal.SIGUSR1)
    self.assertEqual('', out)
    self.assertEqual(
        '** SIGUSR1 received **\n  File "<string>", line 1, in <module>\n', err)


if __name__ == '__main__':
  os.chdir(THIS_DIR)
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.CRITICAL)
  unittest.main()
