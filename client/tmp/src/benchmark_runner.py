import logging
import os
import shutil
import subprocess
import sys
import time

import file_path


CMDSUFFFIX = ''
if sys.platform == 'win32':
  CMDSUFFFIX = '.exe'

BASEDIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
SRCDIR = os.path.join(BASEDIR, 'src')
DATADIR = os.path.join(SRCDIR, 'data')

SCRIPT = os.path.join('src', 'benchmark.py')


def main():
  # Python3
  logging.info('Running script with Python3')
  dir1 = os.path.join(BASEDIR, 'dir1')
  if os.path.isdir(dir1):
    shutil.rmtree(dir1)
  shutil.copytree(DATADIR, dir1)
  subprocess.check_output(['python' + CMDSUFFFIX, SCRIPT, dir1])
  
  # Python2
  logging.info('Running script with Python2')
  dir2 = os.path.join(BASEDIR, 'dir2')
  if os.path.isdir(dir2):
    shutil.rmtree(dir2)
  shutil.copytree(DATADIR, dir2)
  subprocess.check_output(['python' + CMDSUFFFIX, SCRIPT, dir2])


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  main()
