# coding=utf-8
# Copyright 2012 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import argparse
import datetime
import getpass
import hashlib
import os
import subprocess
import sys


ROOT_DIR = os.path.dirname(os.path.abspath(
    __file__.decode(sys.getfilesystemencoding())))
sys.path.append(os.path.join(ROOT_DIR, '..', 'third_party'))

import colorama

# Use a variable because it is corrupting my text editor from the 80s.
hello_world = u'hello_🌐'

def parse_args(use_isolate_server, use_swarming):
  """Process arguments for the example scripts."""
  os.chdir(ROOT_DIR)
  colorama.init()

  parser = argparse.ArgumentParser(description=sys.modules['__main__'].__doc__)
  if use_isolate_server:
    parser.add_argument(
        '-I', '--isolate-server', required=True,
        metavar='URL', default=os.environ.get('ISOLATE_SERVER', ''),
        help='Isolate server to use (default: ISOLATE_SERVER env var)')
  if use_swarming:
    task_name = (u'%s-%s-%s' % (
        getpass.getuser(),
        datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'),
        hello_world)).encode('utf-8')
    group = parser.add_argument_group('Swarming')
    group.add_argument(
        '-S', '--swarming',
        metavar='URL', default=os.environ.get('SWARMING_SERVER', ''),
        required=True,
        help='Server to use (default: SWARMING_SERVER env var)')
    group.add_argument(
        '-t', '--task-name', default=task_name, metavar='NAME',
        help='Task name, default is based on time; %(default)s')
    group.add_argument(
        '--idempotent', action='store_true',
        help='Tells Swarming to reused previous task result if possible')
    group.add_argument(
        '-d', '--dimensions', nargs=2, action='append', default=[],
        metavar='XX', help='Dimensions to request')
    group.add_argument(
        '--service-account',
        help='Name of a service account to run the task as. Only literal "bot" '
             'string can be specified currently (to run the task under bot\'s '
             'account). Don\'t use task service accounts if not given '
             '(default).')
    group.add_argument(
        '--priority', metavar='INT', type=int, help='Priority to use')
  parser.add_argument('-v', '--verbose', action='count', default=0)
  return parser.parse_args()


def note(text):
  """Prints a formatted note."""
  print(
      colorama.Fore.YELLOW + colorama.Style.BRIGHT + '\n-> ' + text +
      colorama.Fore.RESET)


def run(cmd, verbose):
  """Prints the command it runs then run it."""
  cmd = cmd[:]
  cmd.extend(['--verbose'] * verbose)
  for i in cmd:
    assert isinstance(i, str), repr(i)
  print(
      'Running: %s%s%s' %
      (colorama.Fore.GREEN, ' '.join(cmd), colorama.Fore.RESET))
  cmd = [sys.executable, os.path.join('..', cmd[0])] + cmd[1:]
  if sys.platform != 'win32':
    cmd = ['time', '-p'] + cmd
  subprocess.check_call(cmd)


def capture(cmd):
  """Prints the command it runs then return stdout."""
  print(
      'Running: %s%s%s' %
      (colorama.Fore.GREEN, ' '.join(cmd), colorama.Fore.RESET))
  cmd = [sys.executable, os.path.join('..', cmd[0])] + cmd[1:]
  return subprocess.check_output(cmd)


def isolate(tempdir, isolate_server, verbose):
  """Archives the payload."""
  # All the files are put in a temporary directory. This is done so the current
  # directory doesn't have the following files created:
  # - hello_🌐.isolated
  # - hello_🌐.isolated.state
  isolated = os.path.join(tempdir, hello_world + u'.isolated')
  note('Archiving to %s' % isolate_server)
  run(
      [
        'isolate.py',
        'archive',
        '--isolate', os.path.join(
            u'payload', hello_world + u'.isolate').encode('utf-8'),
        '--isolated', isolated.encode('utf-8'),
        '--isolate-server', isolate_server,
      ], verbose)
  with open(isolated, 'rb') as f:
    return hashlib.sha1(f.read()).hexdigest()
