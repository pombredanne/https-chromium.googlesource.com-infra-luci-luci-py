# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from __future__ import print_function

import os
import sys

expected = ['file1.txt', 'file1_copy.txt', 'repeated_files.py']
actual = sorted(os.listdir(os.path.dirname(os.path.abspath(__file__))))
if expected != actual:
  print('Expected list doesn\'t match:', file=sys.stderr)
  print('%s\\n%s' % (','.join(expected), ','.join(actual)), file=sys.stderr)
  sys.exit(1)
print('Success')
