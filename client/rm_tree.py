#!/usr/bin/env vpython

import logging
import os
import subprocess
import sys
import time

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(THIS_DIR, 'third_party'))

from depot_tools import fix_encoding
from utils import file_path
from utils import fs


def main():
  target_dir = os.path.join(THIS_DIR, 'blink_web_tests')
  dir1 = os.path.join(THIS_DIR, 'blink_web_tests_del1')
  if sys.platform == 'win32':
    subprocess.check_output(['xcopy', '/e', '/i', '/q', target_dir, dir1])
  else:
    subprocess.check_output(['cp', '-r', target_dir, dir1])

  # remove with original file_path.rmtree()
  start = time.time()
  file_path.rmtree(dir1)
  elapsed = time.time() - start
  print('file_path.rmtree() took %s sec' % elapsed)

  # remove with native rm
  if sys.platform == 'win32':
    dir2 = os.path.join(THIS_DIR, 'blink_web_tests_del2')
    dir3 = os.path.join(THIS_DIR, 'blink_web_tests_del3')
    dir4 = os.path.join(THIS_DIR, 'blink_web_tests_del4')
    subprocess.check_output(['xcopy', '/e', '/i', '/q', target_dir, dir2])
    subprocess.check_output(['xcopy', '/e', '/i', '/q', target_dir, dir3])
    subprocess.check_output(['xcopy', '/e', '/i', '/q', target_dir, dir4])

    start = time.time()
    fs.rmtree_powershell(dir2)
    elapsed = time.time() - start
    print('fm.rmtree_powershell() took %s sec' % elapsed)

    start = time.time()
    fs.rmtree_rmdir(dir3)
    elapsed = time.time() - start
    print('fm.rmtree_rmdir() took %s sec' % elapsed)

    start = time.time()
    fs.rmtree_del_rmdir(dir4)
    elapsed = time.time() - start
    print('fm.rmtree_del_rmdir() took %s sec' % elapsed)
  else:
    subprocess.check_output(['cp', '-r', target_dir, dir2])

    start = time.time()
    fs.rmtree_native_posix(dir2)
    elapsed = time.time() - start
    print('fm.rmtree_native_posix() took %s sec' % elapsed)


if __name__ == '__main__':
  logging.basicConfig(level=logging.DEBUG)
  fix_encoding.fix_encoding()
  main()
