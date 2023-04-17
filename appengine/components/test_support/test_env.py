# Copyright 2013 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import os
import sys

# /appengine/
ROOT_DIR = os.path.dirname(
    os.path.dirname(os.path.realpath(os.path.abspath(__file__))))

_INITIALIZED = False


def setup_test_env(app_id='sample-app'):
  """Sets up App Engine test environment."""
  global _INITIALIZED
  if _INITIALIZED:
    return
  _INITIALIZED = True

  # For depot_tools.
  sys.path.insert(
      0, os.path.join(ROOT_DIR, '..', '..', 'client', 'third_party'))
  # For 'from components import ...' and 'from test_support import ...'.
  sys.path.insert(0, ROOT_DIR)
  sys.path.insert(0, os.path.join(ROOT_DIR, '..', 'third_party_local'))

  from tool_support import gae_sdk_utils
  gae_sdk_utils.setup_gae_env()
  gae_sdk_utils.setup_env(None, app_id, 'v1a', None)

  from components import utils
  utils.fix_protobuf_package()

  # For endpoints.
  sys.path.insert(0, os.path.join(ROOT_DIR, 'components', 'third_party'))
