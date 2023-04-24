# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

use_relative_paths = True

deps = {
  'appengine/swarming/ui2/nodejs/': {
    'packages': [
      {
        'package': 'infra/3pp/tools/nodejs/${{platform}}',
        'version': 'version:2@16.11.1',
      }
    ],
    'dep_type': 'cipd',
    'condition': 'checkout_x64',
  },

  # luci-go clients are used for client/run_isolated.py and integration tests.
  'luci-go': {
    'packages': [
      {
        'package': 'infra/tools/luci/cas/${{platform}}',
        'version': 'git_revision:e91834850a06011c64eb9a24f317371194bde3de',
      },
      {
        'package': 'infra/tools/luci/fakecas/${{platform}}',
        'version': 'git_revision:8ed1f3ebaa59594f4b1abbd328296a963980e954',
      },
      {
        'package': 'infra/tools/luci/isolate/${{platform}}',
        'version': 'git_revision:56489f37e8efab64d8b92670e35c1122634b9cae',
      },
      {
        'package': 'infra/tools/luci/swarming/${{platform}}',
        'version': 'git_revision:d86b13e04182ecf83a5b797d6d0e8af619d48554',
      }
    ],
    'dep_type': 'cipd',
    'condition': 'checkout_x64',
  },

  # Nsjail is used for our unit tests.
  'nsjail': {
    'packages': [
      {
        'package': 'infra/3pp/tools/nsjail/${{platform}}',
        'version': 'version:2@3.0.chromium.1',
      }
    ],
    "condition": "checkout_linux",
    'dep_type': 'cipd',
  },
}
