#!/bin/bash

go run go.chromium.org/luci/client/cmd/swarming trigger \
  -server https://chromium-swarm.appspot.com \
  -digest 373502f85465c7aa69215657e3dca17cfa2ab247a4b6138c11fb5f032f9153a5/343 \
  -dimension pool=chromium.tests \
  -dimension os=Linux \
  -dimension gce=1 \
  -- vpython rm_tree.py
