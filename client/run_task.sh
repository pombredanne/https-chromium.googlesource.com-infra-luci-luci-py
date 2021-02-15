#!/bin/bash

digest=$1

# Linux
# go run go.chromium.org/luci/client/cmd/swarming trigger \
#   -server https://chromium-swarm.appspot.com \
#   -digest $digest \
#   -dimension pool=chromium.tests \
#   -dimension os=Linux \
#   -dimension gce=1 \
#   -- vpython rm_tree.py

# Windows
go run go.chromium.org/luci/client/cmd/swarming trigger \
  -server https://chromium-swarm.appspot.com \
  -digest $digest \
  -dimension pool=chromium.tests \
  -dimension os=Windows \
  -dimension gce=1 \
  -- vpython rm_tree.py
