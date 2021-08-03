import logging
import os
import shutil
import subprocess
import sys
import time


CMDSUFFFIX = ''
if sys.platform == 'win32':
  CMDSUFFFIX = '.exe'

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SRCDIR = os.path.join(BASEDIR, 'src')
DATADIR = os.path.join(SRCDIR, 'data')

SCRIPT = os.path.join(SRCDIR, 'benchmark.py')


def main():
  # Python3
  dir1 = os.path.join(BASEDIR, 'dir1')
  if os.path.isdir(dir1):
    shutil.rmtree(dir1)
  shutil.copytree(DATADIR, dir1)
  logging.info('Running script with Python3')
  vpython_spec = os.path.join(SRCDIR, '.vpython3')
  subprocess.check_output(['vpython3' + CMDSUFFFIX, '-vpython-spec', vpython_spec, '-vpython-log-level', 'debug', SCRIPT, dir1])

  # Python2
  dir2 = os.path.join(BASEDIR, 'dir2')
  if os.path.isdir(dir2):
    shutil.rmtree(dir2)
  shutil.copytree(DATADIR, dir2)
  logging.info('Running script with Python2')
  vpython_spec = os.path.join(SRCDIR, '.vpython')
  subprocess.check_output(['vpython' + CMDSUFFFIX, '-vpython-spec', vpython_spec,  '-vpython-log-level', 'debug', SCRIPT, dir2])


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  main()
