# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""This module defines Isolate Server frontend pRPC handlers."""

import datetime
import logging

from components import prpc
from components import stats_framework
from components import utils

from google.protobuf import timestamp_pb2

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


class Service(object):
  """Service implements the pRPC service in isolated.proto."""

  DESCRIPTION = isolated_prpc_pb2.ServiceServiceDescription

  def Stats(self, request, context):
    res = None
    if request.resolution == isolated_pb2.MINUTE:
      res = 'minutes'
    if request.resolution == isolated_pb2.HOUR:
      res = 'hours'
    if request.resolution == isolated_pb2.DAY:
      res = 'days'
    if not res:
      # TODO(maruel): What's the right type?
      raise Exception('Unexpected resolution')

    if request.number < 1 or request.number > 1000:
      # TODO(maruel): What's the right type?
      raise Exception('Invalid number')

    if request.latest.seconds:
      now = request.latest.ToDatetime()
    else:
      now = utils.utcnow()
    # Round time to the minute.
    now = datetime.datetime(*now.timetuple()[:5], tzinfo=now.tzinfo)
    entities = stats_framework.get_stats(
        stats.STATS_HANDLER, res, now, request.number, False)
    out = isolated_pb2.StatsResponse()
    out.latest.FromDatetime(now)
    for s in entities:
      _stats_to_proto(s.values, s.to_datetime(), out.measurements.add())
    logging.info('Found %d entities', len(entities))
    return out


def get_routes():
  s = prpc.Server()
  s.add_service(Service())
  return s.get_routes()
