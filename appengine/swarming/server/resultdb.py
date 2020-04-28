# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Functions to communicate with ResultDB for swarming tasks."""

import uuid

from google.appengine.api import app_identity

from components import net
from components import prpc
from components import utils

from server import config


def create_invocation(task_id):
  """This is wrapper for CreateInvocation API.

  Returns:
    update-token for created invocation.
  """
  hostname = app_identity.get_default_version_hostname()
  response_headers = {}
  _call_resultdb_recorder_api(
      'CreateInvocation', {
          'requestId': str(uuid.uuid4()),
          'invocationId': 'task:%s:%s' % (hostname, task_id),
          'invocation': {
              'producerResource': '//%s/tasks/%s' % (hostname, task_id),
          }
      }, response_headers)
  return response_headers.get('update-token')


def finalize_invocation(task_id, interrupted):
  """This is wrapper for FinalizeInvocation API."""

  hostname = app_identity.get_default_version_hostname()
  try:
    _call_resultdb_recorder_api('FinalizeInvocation', {
        'name': 'task:%s:%s' % (hostname, task_id),
        'interrupted': interrupted,
    })
  except net.Error as ex:
    if 'X-Prpc-Grpc-Code' not in ex.headers:
      raise

    if prpc.StatusCode.INVALID_ARGUMENT.value != int(
        ex.headers['X-Prpc-Grpc-Code']):
      raise

    # Ignore INVALID_ARGUMENT errors, this may happen if task itself finalized
    # invocation.


### Private code


def _call_resultdb_recorder_api(method, request, response_headers=None):
  cfg = config.settings()
  rdb_url = cfg.resultdb.server
  utils.validate_root_service_url(rdb_url)

  # See Recoder API for ResultDB in
  # https://chromium.googlesource.com/infra/luci/luci-go/+/HEAD/resultdb/proto/rpc/v1/recorder.proto
  # But beware that proto JSON serialization uses camelCase, not snake_case.
  net.json_request(
      url='%s/prpc/luci.resultdb.rpc.v1.Recorder/%s' % (rdb_url, method),
      method='POST',
      payload=request,
      scopes=[net.EMAIL_SCOPE],
      response_headers=response_headers)
