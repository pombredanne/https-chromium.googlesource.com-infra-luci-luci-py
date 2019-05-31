# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Endpoints version of is_member API."""

import endpoints
from protorpc import message_types
from protorpc import messages
from protorpc import remote

from . import acl
from .. import api
from .. import endpoints_support
from .. import model


### ProtoRPC Messages


MembershipRequest = endpoints.ResourceContainer(
  message_types.VoidMessage,
  group=messages.StringField(1, required=True),
  identity=messages.StringField(2, required=True))


class MembershipResponse(messages.Message):
  is_member = messages.BooleanField(1)


AuthorizationRequest = endpoints.ResourceContainer(
  message_types.VoidMessage,
  identity=messages.StringField(1, required=True),
  project=messages.StringField(2, required=True),
  bucket=messages.StringField(3, required=True),
  service=messages.StringField(4, required=True))

class AuthorizationResponse(messages.Message):
  is_authorized = messages.BooleanField(1)

### API


def normalize_identity(identity):
  if ':' not in identity:
    identity = 'user:%s' % identity
  try:
    identity = model.Identity.from_bytes(identity)
  except ValueError as e:
    raise endpoints.BadRequestException('Invalid identity: %s.' % e)
  return identity

@endpoints_support.endpoints_api(name='auth', version='v1')
class AuthService(remote.Service):
  """Verifies if a given identity authorized a specific action.

  Action is authorized within a specific bucket in a project
  against a service.
  """

  @endpoints_support.endpoints_method(
      MembershipRequest, MembershipResponse,
      http_method='GET',
      path='/membership')
  @api.require(acl.has_access)
  def membership(self, request):
    identity = normalize_identity(request.identity)
    is_member = api.is_group_member(request.group, identity)
    return MembershipResponse(is_member=is_member)

  @endpoints_support.endpoints_method(
    AuthorizationRequest, AuthorizationResponse,
    http_method='GET',
    path='/authorized')
  @api.require(acl.has_access)
  def authorized(self, request):
    identity = normalize_identity(request.identity)
    authorized = api.can_perform_action(
      request.project,
      request.bucket,
      request.service,
      request.action,
      identity)
    return AuthorizationResponse(is_authorized=authorized)
