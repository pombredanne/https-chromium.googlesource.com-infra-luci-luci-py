#!/bin/bash
# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

cfgopt= '--config unittest.cfg'
attr='!no_run'

# Python2
echo "Running tests in python2"

echo "Tests in swarming dir and packages"
./test.py -v ${cfgopt} -A "${attr},!run_later" -s .
./test.py -v ${cfgopt} -A "${attr},run_later" -s .

echo "Tests in swarming/swarming_bot dir and packages"
./test.py -v ${cfgopt} -A "${attr},!run_later" -s ./swarming_bot
./test.py -v ${cfgopt} -A "${attr},run_later" -s ./swarming_bot

echo "Smoke test"
./local_smoke_test.py

# Python3
echo "Running tests in python3"
vpy3cmd="vpython3 ./test.py"

echo "Tests in swarming dir and packages"
${vpy3cmd} -v ${cfgopt} --python3 -A "${attr},!run_later" -s .
${vpy3cmd} ./test.py -v ${cfgopt} --python3 -A "${attr},run_later" -s .

echo "Tests in swarming/swarming_bot dir and packages"
${vpy3cmd} -v ${cfgopt} --python3 -A "${attr},!run_later" -s ./swarming_bot
${vpy3cmd} -v ${cfgopt} --python3 -A "${attr},run_later" -s ./swarming_bot
