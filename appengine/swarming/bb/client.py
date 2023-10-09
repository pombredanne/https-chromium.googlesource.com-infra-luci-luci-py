# Copyright 2023 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Class to create a buildbucket client with associated RPCs."""

from components import prpc

from bb.go.chromium.org.luci.buildbucket.proto import builds_service_prpc_pb2


def get_token_from_secret_bytes(secret_bytes):
  pass


class BuildBucketClient:
  def __init__(self, hostname, secret_bytes):
    self.client = prpc.Client(
        hostname=hostname,
        service_description=builds_service_prpc_pb2.BuildsServiceDescription)
    self.token = get_token_from_secret_bytes(secret_bytes)

  def StartBuildTask(self, req):
    return self.client.StartBuildTask(
        req, metadata={"x-buildbucket-token": self.token})
