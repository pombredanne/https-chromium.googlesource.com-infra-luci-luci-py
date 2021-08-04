import file_path
import logging
import os
import sys
import time

import six


def main(argv):
  dirpath = six.ensure_text(argv[1])
  logging.debug(file_path.get_recursive_size(dirpath))
  logging.info('file_path.get_recursive_size() ended')
  file_path.rmtree(dirpath)
  logging.info('file_path.rmtree() ended')


if __name__ == '__main__':
  if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf8')
  logging.basicConfig(level=logging.DEBUG)
  logging.debug('Python version %s', sys.version_info)
  main(sys.argv)
