#!/bin/bash

digest=$1

# Linux
#   GCE https://chromium-swarm.appspot.com/task?id=51c1ae40d1cd0a10
#   GCE https://chromium-swarm.appspot.com/task?id=51c1af6cefd88910
#   GCE without make_tree_deleteable() https://chromium-swarm.appspot.com/task?id=51c1b2ddf56ebf10
#   GCE without make_tree_deleteable() https://chromium-swarm.appspot.com/task?id=51c1b3e72bc27010
# go run go.chromium.org/luci/client/cmd/swarming trigger \
#   -server https://chromium-swarm.appspot.com \
#   -digest $digest \
#   -dimension pool=chromium.tests \
#   -dimension os=Linux \
#   -dimension gce=1 \
#   -- vpython rm_tree.py

# Windows
#   GCE https://chromium-swarm.appspot.com/task?id=51bebf8b39588110
#   GCE https://chromium-swarm.appspot.com/task?id=51c0f4c2309aae10
#   Lab, Win7 https://chromium-swarm.appspot.com/task?id=51c19b2c6db72110
#   Lab, Win10 https://chromium-swarm.appspot.com/task?id=51c1a97664ff2e10
#   GCE, Win10 without make_tree_deleteable()   https://chromium-swarm.appspot.com/task?id=51c1b4c9ff258d10
#   Lab, Win10 without make_tree_deleteable()   https://chromium-swarm.appspot.com/task?id=51c1b55fd6a03710
go run go.chromium.org/luci/client/cmd/swarming trigger \
  -server https://chromium-swarm.appspot.com \
  -digest $digest \
  -dimension pool=chromium.tests \
  -dimension os=Windows-10 \
  -dimension gce=0 \
  -- vpython rm_tree.py
