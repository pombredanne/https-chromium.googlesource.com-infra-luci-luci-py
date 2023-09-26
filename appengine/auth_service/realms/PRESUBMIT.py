# Copyright 2023 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

USE_PYTHON3 = True


def CheckPermissionsFooter(input_api, output_api):
  if input_api.change.AffectedFiles(file_filter="permissions.py"):
    return ["UPDATE PERMISSIONS CFG!!!!"]
  return []
