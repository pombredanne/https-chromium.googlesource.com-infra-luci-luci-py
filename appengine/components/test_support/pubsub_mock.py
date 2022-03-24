# !/usr/bin/env vpython
# coding: utf-8
# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

from components import pubsub


def mock_pubsub_requests(mock_func):
  mock_func(pubsub, 'publish_multi', lambda _topic, _message: None)
  return None
