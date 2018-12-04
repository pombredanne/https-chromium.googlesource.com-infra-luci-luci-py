# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This module defines Isolate Server frontend pRPC handlers."""

import datetime
import logging

from components import prpc
from components.prpc.codes import StatusCode
from components import stats_framework
from components import utils

from proto import isolated_pb2
from proto import isolated_prpc_pb2

import stats


def _stats_to_proto(s, dt, out):
  """Converts a stats._Snapshot to isolated_pb2.Stats."""
  out.ts.FromDatetime(dt)
  out.uploads = s.uploads
  out.uploads_bytes = s.uploads_bytes
  out.downloads = s.downloads
  out.downloads_bytes = s.downloads_bytes
  out.contains_requests = s.contains_requests
  out.contains_lookups = s.contains_lookups
  out.requests = s.requests
  out.failures = s.failures


class IsolatedService(object):
  """Service implements the pRPC service in isolated.proto."""

  DESCRIPTION = isolated_prpc_pb2.IsolatedServiceDescription

  def Stats(self, request, context):
    res = None
    if request.resolution == isolated_pb2.MINUTE:
      res = 'minutes'
    if request.resolution == isolated_pb2.HOUR:
      res = 'hours'
    if request.resolution == isolated_pb2.DAY:
      res = 'days'
    if not res:
      context.set_code(StatusCode.INVALID_ARGUMENT)
      context.set_details('Invalid resolution')
      return

    if not 1 <= request.limit <= 1000:
      context.set_code(StatusCode.INVALID_ARGUMENT)
      context.set_details('Invalid limit; must be between 1 and 1000')
      return

    if request.latest.seconds:
      now = request.latest.ToDatetime()
    else:
      now = utils.utcnow()
    # Round time to the minute.
    now = datetime.datetime(*now.timetuple()[:5], tzinfo=now.tzinfo)
    entities = stats_framework.get_stats(
        stats.STATS_HANDLER, res, now, request.limit, False)
    out = isolated_pb2.StatsResponse()
    for s in entities:
      _stats_to_proto(s.values, s.timestamp, out.measurements.add())
    logging.info('Found %d entities', len(entities))
    return out


def get_routes():
  s = prpc.Server()
  s.add_service(IsolatedService())
  return s.get_routes()
