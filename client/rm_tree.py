#!/usr/bin/env vpython

import sys
import os
import time
import subprocess

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(THIS_DIR, 'third_party'))

from depot_tools import fix_encoding
from utils import file_path


def main():
  target_dir = os.path.join(THIS_DIR, 'blink_web_tests')
  dir1 = os.path.join(THIS_DIR, 'blink_web_tests_del1')
  dir2 = os.path.join(THIS_DIR, 'blink_web_tests_del2')
  subprocess.check_output(['cp', '-r', target_dir, dir1])
  subprocess.check_output(['cp', '-r', target_dir, dir2])

  # remove with original file_path.rmtree()
  start = time.time()
  file_path.rmtree(dir1)
  elapsed = time.time() - start
  print('file_path.rmtree() took %s sec' % elapsed)

  # remove with native rm
  start = time.time()
  out = subprocess.check_output(['rm', '-rf', dir2])
  print(out)
  elapsed = time.time() - start
  print('rm -rf took %s sec' % elapsed)


if __name__ == '__main__':
  fix_encoding.fix_encoding()
  main()
