#!/bin/bash

go run go.chromium.org/luci/client/cmd/cas archive \
  -cas-instance chromium-swarm \
  -paths .:utils \
  -paths .:third_party \
  -paths .:blink_web_tests \
  -paths .:rm_tree.py
