#!/usr/bin/env vpython3
# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import sys
import subprocess

def main():
  # The Nsjail commandline arguments should look like:
  # [path_to_this_file, '--config', path_to_config, "--", cmd_to_run]
  if len(sys.argv) < 5 or sys.argv[1] != '--config':
    return 1
  return subprocess.call(sys.argv[4:])

if __name__ == '__main__':
  sys.exit(main())

