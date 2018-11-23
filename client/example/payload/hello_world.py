#!/usr/bin/env python
# coding=utf-8
# Copyright 2012 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This script is meant to be run on a Swarming bot."""

import os
import sys
import tarfile


def main():
  # Extract all files into output directory.
  t = tarfile.open('foo.tar.gz')
  t.extractall(sys.argv[2])
  return 0


if __name__ == '__main__':
  sys.exit(main())
