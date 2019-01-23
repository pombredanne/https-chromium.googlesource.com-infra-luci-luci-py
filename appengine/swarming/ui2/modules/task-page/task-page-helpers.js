// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { sanitizeAndHumanizeTime } from '../util'

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

export function parseRequest(request) {
  if (!request) {
    return {};
  }
  request.tagMap = {};
  request.tags = request.tags || [];
  for (const tag of request.tags) {
    const split = tag.split(':', 1);
    const key = split[0];
    const rest = tag.substring(key.length + 1);
    request.tagMap[key] = rest;
  };

  TASK_TIMES.forEach((time) => {
    sanitizeAndHumanizeTime(request, time);
  });
  return request;
}

const TASK_TIMES = ['abandoned_ts', 'completed_ts', 'created_ts', 'modified_ts',
                    'started_ts'];
