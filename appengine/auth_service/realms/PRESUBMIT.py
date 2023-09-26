# Copyright 2023 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

USE_PYTHON3 = True
PRESUBMIT_VERSION = '2.0.0'


def CheckPermissionsFooter(input_api, output_api):
  for file in input_api.change.AffectedFiles():
    if "permissions.py" in str(file):
      return [
          output_api.PresubmitPromptWarning(
              '''
                Change detected in permissions.py, if changing the
                PermissionsDB, please go make the same change at
                configs/chrome-infra-auth-dev/permissions.cfg
              ''')
      ]
  return []
