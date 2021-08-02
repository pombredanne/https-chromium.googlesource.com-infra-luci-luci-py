# [VPYTHON:BEGIN]
# wheel: <
#  name: "infra/python/wheels/six-py2_py3"
#  version: "version:1.12.0"
# >
# [VPYTHON:END]

import file_path
import logging
import os
import sys

import six


def main(argv):
  dirpath = six.ensure_text(argv[1])
  logging.debug(file_path.get_recursive_size(dirpath))
  logging.info('file_path.get_recursive_size() ended')


if __name__ == '__main__':
  if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf8')
  logging.basicConfig(level=logging.DEBUG)
  main(sys.argv)
