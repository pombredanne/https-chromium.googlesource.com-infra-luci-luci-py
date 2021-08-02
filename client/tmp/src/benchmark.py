import file_path
import logging
import os
import sys

import six


def main():
  dirpath = os.path.abspath(os.path.dirname(__file__))
  dirpath = six.ensure_text(dirpath)
  logging.debug(file_path.get_recursive_size(dirpath))
  logging.info('file_path.get_recursive_size() ended')


if __name__ == '__main__':
  if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf8')
  logging.basicConfig(level=logging.DEBUG)
  main()
