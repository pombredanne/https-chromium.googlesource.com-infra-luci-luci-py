# Copyright 2013 Google Inc. All Rights Reserved.

"""Test Request.

Test Request objects represent one test request from one client.  The client
can be a build machine requesting a test after a build or it could be a
developer requesting a test from their own build.
"""



from google.appengine.ext import db
from common import dimensions_utils
from common import test_request_message


def GetTestCase(request_message):
  """Returns a TestCase object representing this Test Request message.

  Args:
    request_message: The request message to convert.

  Returns:
    A TestCase object representing this Test Request.

  Raises:
    test_request_message.Error: If the request's message isn't valid.
  """
  request_object = test_request_message.TestCase()
  errors = []
  if not request_object.ParseTestRequestMessageText(request_message, errors):
    raise test_request_message.Error('\n'.join(errors))

  return request_object


class TestRequest(db.Model):
  # The message received from the caller, formatted as a Test Case as
  # specified in
  # http://code.google.com/p/swarming/wiki/SwarmFileFormat.
  message = db.TextProperty()

  # The time at which this request was received.
  requested_time = db.DateTimeProperty(auto_now_add=True)

  # The name for this test request.
  name = db.StringProperty()

  def GetTestCase(self):
    """Returns a TestCase object representing this Test Request.

    Returns:
      A TestCase object representing this Test Request.

    Raises:
      test_request_message.Error: If the request's message isn't valid.
    """
    # NOTE: because _request_object is not declared with db.Property, it will
    # not be persisted to the data store.  This is used as a transient cache of
    # the test request message to keep from evaluating it all the time
    request_object = getattr(self, '_request_object', None)
    if not request_object:
      request_object = GetTestCase(self.message)
      self._request_object = request_object

    return request_object

  def GetConfiguration(self, config_name):
    """Gets the named configuration.

    Args:
      config_name: The name of the configuration to get.

    Returns:
      A configuration dictionary for the named configuration, or None if the
      name is not found.
    """
    for configuration in self.GetTestCase().configurations:
      if configuration.config_name == config_name:
        return configuration

    return None

  def GetConfigurationDimensionHash(self, config_name):
    """Gets the hash of the named configuration.

    Args:
      config_name: The name of the configuration to get the hash for.

    Returns:
      The hash of the configuration.
    """
    return dimensions_utils.GenerateDimensionHash(
        self.GetConfiguration(config_name).dimensions)

  def GetAllKeys(self):
    """Get all the keys representing the TestRunners owned by this instance.

    Returns:
      A list of all the keys.
    """
    # We can only access the runner if this class has been saved into the
    # database.
    if self.is_saved():
      return [runner.key() for runner in self.runners]
    else:
      return []

  def DeleteIfNoMoreRunners(self):
    # Delete this request if we have deleted all the runners that were created
    # because of it.
    if self.runners.count() == 0:
      self.delete()


def GetAllMatchingTestRequests(test_case_name):
  """Returns a list of all Test Request that match the given test_case_name.

  Args:
    test_case_name: The test case name to search for.

  Returns:
    A list of all Test Requests that have |test_case_name| as their name.
  """
  # Perform the query in a transaction to ensure that it gets the most recent
  # data, otherwise it is possible for one machine to add tests, and then be
  # unable to find them through this function after.
  query = db.run_in_transaction(TestRequest.gql, 'WHERE name = :1',
                                test_case_name)

  return [request for request in query]
