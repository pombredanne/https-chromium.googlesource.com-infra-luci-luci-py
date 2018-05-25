# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Discovery service implementation."""

from google.protobuf import descriptor_pb2
from google.protobuf import descriptor_pool

import service_pb2
import service_prpc_pb2


class FileNotFound(Exception):
  """Raised when a proto file is not found."""
  def __init__(self, name):
    super(FileNotFound, self).__init__(
        'Proto file "%s" is not found in the default protobuf descriptor pool. '
        'Ensure all _pb2.py are imported.')


class _Discovery(object):
  DESCRIPTION = service_prpc_pb2.DiscoveryServiceDescription

  def __init__(self, describe_response):
    self.describe_response = describe_response

  def Describe(self, _request, _ctx):
    return self.describe_response


def _response_for(services):
  pool = descriptor_pool.Default()
  files = {}

  def ensure_file(name):
    if name in files:
      return
    desc = pool.FindFileByName(name)
    if not desc:
      raise FileNotFound(name)
    proto = descriptor_pb2.FileDescriptorProto()
    desc.file.CopyToProto(proto)
    files[name] = proto

    for dep in proto.dependency:
      ensure_file(dep)

  descriptions = [s.DESCRIPTION for s in services]
  descriptions.append(service_prpc_pb2.DiscoveryServiceDescription)

  service_names = []
  for description in descriptions:
    descriptor = description['descriptor']
    ensure_file(descriptor.file.name)
    service_names.append(descriptor.name)

  return service_pb2.DescribeResponse(
      description=descriptor_pb2.FileDescriptorSet(file=files.values()),
      services=service_names,
  )


def discovery_service(services):
  """Returns a Discovery service for the services.

  Returns a Discovery service that describes the services.
  This enables RPC Explorer and prpc command line tool.

  Assumes proto filename uniqnes for all files that the services depend on
  directly or indirectly. Protobuf reflection assumes that too.
  """
  return _Discovery(_response_for(services))
