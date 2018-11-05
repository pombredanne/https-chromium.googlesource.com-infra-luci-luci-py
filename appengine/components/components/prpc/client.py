# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""pRPC client."""

from google.appengine.ext import ndb
from google.protobuf import symbol_database

from components import net
from components.prpc import codes
from components.prpc import encoding

class Error(Exception):
  """A base class for pRPC client-side errors."""


class RpcError(Error):
  """Raised when an RPC terminated with non-OK status.

  Use attribute status_code of type codes.StatusCode to decide
  how to handle the error.
  """

  def __init__(self, message, status_code, metadata):
    super(RpcError, self).__init__(message)
    self.status_code = status_code
    self.metadata = metadata


class ProtocolError(Error):
  """Server returned malformed pRPC response."""


def service_account_credentials(service_account_key=None):
  """Returns credentials that use GAE service account.

  The returned value can be used as "credentials" argument in RPC method calls.
  For service_account_key, see components/net.py.
  """
  def mutation(request):
    request['scopes'] = [net.EMAIL_SCOPE]
    request['service_account_key'] = service_account_key
  return mutation


def delegation_key_credentials(delegation_token):
  """Returns credentials that use a LUCI delegation token.

  The returned value can be used as "credentials" argument in RPC method calls.
  For service_account_key, see components/net.py.
  """
  def mutation(request):
    request['delegation_token'] = delegation_token
  return mutation


def composite_call_credentials(*call_credentials):
  def mutation(request):
    for mut in call_credentials:
      mut(request)
  return mutation


class Client(object):
  """A client of a pRPC service.

  For each RPC method, a client has two instance methods,
  one sync method with the same name, and one async method with "_async"
  suffix.
  An async method returns an ndb.Future of the response.
  For example, for an RPC "Ping", the class will have methods Ping and
  Ping_async.

  Both async and async methods accept arguments:
    request: the request message.
    timeout: optional RPC timeout in seconds. Defaults to 10s.
    metadata: optional dict of call metadata. Will be available to the server.
    credentials: optional call credentials. Create them using credential
      functions in this module.
  """

  def __init__(
      self, hostname, service_description, insecure=False):
    """Initializes a new pRPC Client.

    Args:
      hostname: hostname of the pRPC server, e.g. "app.example.com".
        Must not contain a schema.
      service_description: a service description object from a generated
        _prpc_pb2.py file.
      insecure: True if the client must use HTTP, as opposed to HTTPS.
        Useful for local servers.
    """
    self._hostname = hostname
    self._insecure = insecure

    pkg = service_description['file_descriptor'].package
    desc = service_description['service_descriptor']
    self._full_service_name = desc.name
    if pkg:
      self._full_service_name = '%s.%s' % (pkg, desc.name)

    for method in desc.method:
      self._generate_rpc_method(method)

  def _generate_rpc_method(self, method_desc):
    url = 'http%s://%s/prpc/%s/%s' % (
        '' if self._insecure else 's',
        self._hostname,
        self._full_service_name,
        method_desc.name,
    )
    sym_db = symbol_database.Default()
    response_py_type = sym_db.GetSymbol(method_desc.output_type[1:])
    assert response_py_type, 'response type for %s.%s not found' % (
        self._full_service_name, method_desc.name)

    @ndb.tasklet
    def method_async(
        request, timeout=None, metadata=None, credentials=None):
      # The signature of this function must match
      # https://grpc.io/grpc/python/grpc.html#grpc.UnaryUnaryMultiCallable.__call__

      # Ensure timeout is set, such that we use same values for deadline
      # parameter in net.request_async and X-Prpc-Timeout value are same.
      # Default to 10s, which is the default used in net.request_async.
      timeout = timeout or 10

      # Prepare request.
      # The protocol is documented in
      # https://godoc.org/go.chromium.org/luci/grpc/prpc#hdr-Protocol
      request = dict(
          url=url,
          method='POST',
          payload=request.SerializeToString(),
          headers=(metadata or {}).copy(),
          scopes=None,
          delegation_token=None,
          deadline=timeout,
      )
      if credentials:
        assert hasattr(credentials, '__call__'), (
          'credentials must be created using credentials functions in '
          'components.prpc.client module')
        credentials(request)

      binary_mime_type = encoding.Encoding.header(encoding.Encoding.BINARY)
      request['headers'].update(**{
        'Content-Type': binary_mime_type,
        'Accept': binary_mime_type,
        'X-Prpc-Timeout': '%dS' % timeout,
      })

      # Send request and check response status code.
      try:
        res_bytes = yield net.request_async(**request)
        # Unfortunately, net module does not expose headers of HTTP 200
        # responses.
        # Assume (HTTP OK => pRPC OK).
      except net.Error as ex:
        # net.Error means HTTP status code was not 200.
        try:
          code = codes.INT_TO_CODE[int(ex.headers['X-Prpc-Grpc-Code'])]
        except (ValueError, KeyError, TypeError):
          raise ProtocolError(
              'response does not contain a valid X-Prpc-Grpc-Code header')
        msg = ex.response.decode('utf-8', 'ignore')
        raise RpcError(msg, code, ex.headers)

      # Status code is OK.
      # Parse the response and return it.
      res = response_py_type()
      res.MergeFromString(res_bytes)
      raise ndb.Return(res)

    # Expose two class methods for each RPC method: one async and one sync.
    setattr(self, method_desc.name + '_async', method_async)
    setattr(
        self, method_desc.name,
        lambda *args, **kwargs: method_async(*args, **kwargs).get_result())
