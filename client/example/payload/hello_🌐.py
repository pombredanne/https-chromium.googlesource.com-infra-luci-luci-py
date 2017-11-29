#!/usr/bin/env python
# coding=utf-8
# Copyright 2012 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This script is meant to be run on a Swarming slave."""

import os
import sys


def main():
  print('Hello world: ' + sys.argv[1])
  if len(sys.argv) == 3:
    # Write a file in ${ISOLATED_OUTDIR}.
    with open(os.path.join(sys.argv[2], u'da 💣.txt'), 'wb') as f:
      r = u'FOO:%r' % os.environ.get('FOO')
      f.write(r.encode('utf-8'))
  return 0


if __name__ == '__main__':
  sys.exit(main())
