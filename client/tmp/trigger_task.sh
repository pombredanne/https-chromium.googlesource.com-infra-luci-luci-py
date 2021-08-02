#!/bin/bash

digest=`go run go.chromium.org/luci/client/cmd/cas archive -cas-instance chromium-swarm -paths .:src | cut -d\  -f4`

go run go.chromium.org/luci/client/cmd/swarming trigger \
  -server https://chromium-swarm.appspot.com \
  -dimension pool=chromium.tests  \
  -dimension cpu=x86-64 \
  -dimension cores=8 \
  -dimension os=Windows-10 \
  -dimension gce=1 \
  -dimension ssd=0 \
  -digest $digest \
  -- python.exe .\\src\\benchmark.py
