#!/bin/bash
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

# test starting from current dir and sub packages
./test.py -v --config unittest.cfg -A '!run_later' -s .
./test.py -v --config unittest.cfg -A 'run_later' -s .

# test swarming_bot tests
./test.py -v --config unittest.cfg -A '!run_later' -s ./swarming_bot
./test.py -v --config unittest.cfg -A 'run_later' -s ./swarming_bot
