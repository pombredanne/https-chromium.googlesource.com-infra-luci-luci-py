# Copyright 2020 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Functions to communicate with ResultDB for swarming tasks."""

import logging
import uuid

from google.appengine.api import app_identity

from components import net
from components import prpc
from components import utils

from server import config


def create_invocation(task_run_id):
  """This is wrapper for CreateInvocation API.

  Returns:
    update-token for created invocation.
  """
  hostname = app_identity.get_default_version_hostname()
  response_headers = {}
  _call_resultdb_recorder_api(
      'CreateInvocation', {
          'requestId': str(uuid.uuid4()),
          'invocationId': _get_invocation_id(task_run_id),
          'invocation': {
              'producerResource': '//%s/tasks/%s' % (hostname, task_run_id),
          }
      }, response_headers)
  return response_headers.get('update-token')


def finalize_invocation(task_run_id, interrupted):
  """This is wrapper for FinalizeInvocation API."""

  try:
    _call_resultdb_recorder_api('FinalizeInvocation', {
        'name': _get_invocation_id(task_run_id),
        'interrupted': interrupted,
    })
  except net.Error as ex:
    if 'X-Prpc-Grpc-Code' not in ex.headers:
      logging.exception('No X-Prpc-Grpc-Code in response headers: %s', ex.headers)
      return

    if prpc.StatusCode.FAILED_PRECONDITION.value != int(
        ex.headers['X-Prpc-Grpc-Code']):
      logging.exception('X-Prpc-Grpc-Code is not FAILED_PRECONDITION: %s',
                        ex.headers['X-Prpc-Grpc-Code'])
      return

    logging.info('Got FAILED_CONDITION in response headers')


### Private code


def _get_invocation_id(task_run_id):
  hostname = app_identity.get_default_version_hostname()
  return 'task:%s:%s' % (hostname, task_run_id)


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
