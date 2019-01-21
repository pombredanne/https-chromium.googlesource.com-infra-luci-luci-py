// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

export function humanState(result) {
  if (!result || !result.state) {
    return '';
  }
  const state = result.state;
  if (state === 'COMPLETED') {
    if (result.failure) {
      return 'COMPLETED (FAILURE)';
    }
    if (result.try_number == '0') {
      return 'COMPLETED (DEDUPED)';
    }
    return 'COMPLETED (SUCCESS)';
  }
  return state;
}