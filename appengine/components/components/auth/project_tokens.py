# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Project token implementation.

See delegation.proto for general idea behind it.
"""

import collections
import datetime
import hashlib
import json
import logging
import urllib

from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.runtime import apiproxy_errors

from components import utils

from . import api
from . import service_account

__all__ = [
  'project_token',
  'project_token_async',
  'ProjectToken',
  'ProjectTokenCreationError',
]


# Tokens that are larger than this (before base64 encoding) are rejected.
MAX_TOKEN_SIZE = 8 * 1024

# How much clock drift between machines we can tolerate, in seconds.
ALLOWED_CLOCK_DRIFT_SEC = 30

class BadTokenError(Exception):
  """Raised on fatal errors (like bad signature). Results in 403 HTTP code."""


class TransientError(Exception):
  """Raised on errors that can go away with retry. Results in 500 HTTP code."""


class ProjectTokenCreationError(Exception):
  """Raised on project token creation errors."""


class ProjectTokenAuthorizationError(ProjectTokenCreationError):
  """Raised on authorization error during project token creation."""


# A minted project token returned by project_token_async and project_token.
ProjectToken = collections.namedtuple('ProjectToken', [
  'token',  # urlsafe base64 encoded blob with delegation token.
  'expiry',  # datetime.datetime of expiration.
])


## Token creation.

def _urlfetch_async(**kwargs):
  """To be mocked in tests."""
  return ndb.get_context().urlfetch(**kwargs)


@ndb.tasklet
def _authenticated_request_async(url, method='GET', payload=None, params=None):
  """Sends an authenticated JSON API request, returns deserialized response.

  Raises:
    ProjectTokenCreationError if request failed or response is malformed.
    ProjectTokenAuthorizationError on HTTP 401 or 403 response from auth service.
  """
  scope = 'https://www.googleapis.com/auth/userinfo.email'
  access_token = service_account.get_access_token(scope)[0]
  headers = {
    'Accept': 'application/json; charset=utf-8',
    'Authorization': 'Bearer %s' % access_token,
  }

  if payload is not None:
    assert method in ('CREATE', 'POST', 'PUT'), method
    headers['Content-Type'] = 'application/json; charset=utf-8'
    payload = utils.encode_to_json(payload)

  if utils.is_local_dev_server():
    protocols = ('http://', 'https://')
  else:
    protocols = ('https://',)
  assert url.startswith(protocols) and '?' not in url, url
  if params:
    url += '?' + urllib.urlencode(params)

  try:
    res = yield _urlfetch_async(
        url=url,
        payload=payload,
        method=method,
        headers=headers,
        follow_redirects=False,
        deadline=10,
        validate_certificate=True)
  except (apiproxy_errors.DeadlineExceededError, urlfetch.Error) as e:
    raise ProjectTokenCreationError(str(e))

  if res.status_code in (401, 403):
    logging.error('Token server HTTP %d: %s', res.status_code, res.content)
    raise ProjectTokenAuthorizationError(
        'HTTP %d: %s' % (res.status_code, res.content))

  if res.status_code >= 300:
    logging.error('Token server HTTP %d: %s', res.status_code, res.content)
    raise ProjectTokenCreationError(
        'HTTP %d: %s' % (res.status_code, res.content))

  try:
    content = res.content
    if content.startswith(")]}'\n"):
      content = content[5:]
    json_res = json.loads(content)
  except ValueError as e:
    raise ProjectTokenCreationError('Bad JSON response: %s' % e)
  raise ndb.Return(json_res)


@ndb.tasklet
def project_token_async(
    project_id,
    oauth_scopes,
    min_validity_duration_sec=5*60,
    tags=None,
    token_server_url=None):
  """Creates a project token by contacting the token server.

  Memcaches the token.

  Args:
    project_id (str): For which project to obtain a token.
      This is the LUCI project for which the call is expected to issue
      an identity token.
      Example: 'chromium'
    oauth_scopes (str): List of OAuth scopes for the project token.
      Example: 'https://www.googleapis.com/auth/cloud-platform.read-only'
    min_validity_duration_sec (int): defines requested lifetime of a new token.
      It will bet set as tokens' TTL if there's no existing cached tokens with
      sufficiently long lifetime. Default is 5 minutes.
    tags (list of str): optional list of key:value pairs to embed into the
      token. Services that accept the token may use them for additional
      authorization decisions.
    token_server_url (str): the URL for the token service that will mint the
      token. Defaults to the URL provided by the primary auth service.

  Returns:
    ProjectToken as ndb.Future.


  Raises:
    ValueError if args are invalid.
    ProjectTokenCreationError if could not create a token.
    ProjectTokenAuthorizationError on HTTP 403 response from auth service.
  """

  # Validate validity durations.
  assert isinstance(min_validity_duration_sec, int), min_validity_duration_sec
  assert min_validity_duration_sec >= 5

  # Validate tags.
  tags = sorted(tags or [])
  for tag in tags:
    parts = tag.split(':', 1)
    if len(parts) != 2 or parts[0] == '' or parts[1] == '':
      raise ValueError('Bad project token tag: %r' % tag)

  # Grab the token service URL.
  if not token_server_url:
    token_server_url = api.get_request_auth_db().token_server_url
    if not token_server_url:
      raise ProjectTokenCreationError('Token server URL is not configured')

  if isinstance(oauth_scopes, str):
    oauth_scopes = [oauth_scopes]

  # End of validation.

  # See MintProjectTokenRequest in
  # https://github.com/luci/luci-go/blob/master/tokenserver/api/minter/v1/token_minter.proto.
  req = {
    'luci_project': project_id,
    'oauth_scope': oauth_scopes,
    'min_validity_duration': min_validity_duration_sec,
    'audit_tags': tags,
  }

  # Get from cache.
  cache_key_hash = hashlib.sha256(
      token_server_url + '\n' + json.dumps(req, sort_keys=True)).hexdigest()
  cache_key = 'project_token/v2/%s' % cache_key_hash
  ctx = ndb.get_context()
  token = yield ctx.memcache_get(cache_key)
  min_validity_duration = datetime.timedelta(seconds=min_validity_duration_sec)
  now = utils.utcnow()
  if token and token.expiry - min_validity_duration > now:
    logging.info(
        'Fetched cached project token: fingerprint=%s',
        utils.get_token_fingerprint(token.token))
    raise ndb.Return(token)

  # Request a new one.
  logging.info(
      'Minting a project token for %r',
      {k: v for k, v in req.iteritems() if v},
  )
  res = yield _authenticated_request_async(
      '%s/prpc/tokenserver.minter.TokenMinter/MintProjectToken' %
          token_server_url,
      method='POST',
      payload=req)

  project_token = res.get('access_token')
  if not project_token or not isinstance(project_token, basestring):
    logging.error('Bad MintProjectToken response: %s', res)
    raise ProjectTokenCreationError('Bad response, no token')

  service_account_email = res.get('service_account_email')
  if not service_account_email or (
      not isinstance(service_account_email, basestring)):
    logging.error('Bad MintProjectToken response: %s', res)
    raise ProjectTokenCreationError('Bad response, no service account email')

  expiry = res.get('expiry')
  if not isinstance(expiry, int):
    logging.error('Bad MintProjectToken response: %s', res)
    raise ProjectTokenCreationError(
        'Unexpected response, expiry is absent or not a number')

  token = ProjectToken(
      token=str(project_token),
      expiry=expiry,
  )

  logging.info(
      'Token server "%s" generated project token, fingerprint=%s)',
      res.get('serviceVersion'),
      utils.get_token_fingerprint(token.token)
  )

  # Put to cache. Refresh the token 10 sec in advance.
  # TODO(fmatenaar): Calculate this value from expiry.
  actual_validity_duration_sec = 20
  if actual_validity_duration_sec > 10:
    yield ctx.memcache_add(
        cache_key, token, time=actual_validity_duration_sec - 10)

  raise ndb.Return(token)


def project_token(**kwargs):
  """Blocking version of project_token_async."""
  return project_token_async(**kwargs).get_result()

