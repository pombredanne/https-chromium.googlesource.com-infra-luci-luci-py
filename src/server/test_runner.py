# Copyright 2013 Google Inc. All Rights Reserved.

"""Test Runner.

A test runner represents a given configuration of a given test request running
on a given machine.
"""



import datetime
import logging

from google.appengine.ext import blobstore
from google.appengine.ext import db
from common import blobstore_helper
from common import test_request_message
from server import test_request

# The maximum number of times to retry a runner that has failed for a swarm
# related reasons (like the machine timing out).
MAX_AUTOMATIC_RETRIES = 3

# Number of times to try a transaction before giving up. Since most likely the
# recoverable exceptions will only happen when datastore is overloaded, it
# doesn't make much sense to extensively retry many times.
MAX_TRANSACTION_RETRY_COUNT = 3

# Number of days to keep old runners around for.
SWARM_FINISHED_RUNNER_TIME_TO_LIVE_DAYS = 14


# MOE: start_strip
# This is removed from the public version because the public version should
# be run on python2.7 (or later), which has the builtin total_seconds() function
# for timedelta.
def TotalSeconds(time_delta):
  return ((time_delta.microseconds +
           (time_delta.seconds + time_delta.days * 24 * 3600) * 10**6) /
          10**6)
# MOE: end_strip


def _GetCurrentTime():
  """Gets the current time.

  This function is defined so that it can be easily mocked out in tests.

  Returns:
    The current time as a datetime.datetime object.
  """
  return datetime.datetime.now()


class TestRunner(db.Model):
  # The test being run.
  request = db.ReferenceProperty(test_request.TestRequest, required=True,
                                 collection_name='runners')

  # The name of the request's configuration being tested.
  config_name = db.StringProperty()

  # The hash of the configuration. Required in order to match machines.
  config_hash = db.StringProperty(required=True)

  # The 0 based instance index of the request's configuration being tested.
  config_instance_index = db.IntegerProperty()

  # The number of instances running on the same configuration as ours.
  num_config_instances = db.IntegerProperty()

  # The machine that is running or ran the test. This attribute is only valid
  # once a machine has been assigned to this runner.
  # TODO(user): Investigate making this a reference to the MachineAssignment.
  # It would require ensuring the MachineAssignment is created when this value
  # is set.
  machine_id = db.StringProperty()

  # A list of the old machines ids that this runner previous ran on. This is
  # useful for knowing when a ping is from an older machine.
  old_machine_ids = db.ListProperty(str)

  # Used to indicate if the runner has finished, either successfully or not.
  done = db.BooleanProperty(default=False)

  # The time at which this runner was created.  The runner may not have
  # started executing yet.
  created = db.DateTimeProperty(auto_now_add=True)

  # The time at which this runner was executed on a remote machine.  If the
  # runner isn't executing or ended, then the value is None and we use the
  # fact that it is None to identify if a test was started or not.
  started = db.DateTimeProperty()

  # The number of times that this runner has been retried for swarm failures
  # (such as the machine that is running it timing out).
  automatic_retry_count = db.IntegerProperty(default=0)

  # The last time a ping was recieved from the remote machine currently
  # running the test. This is used to determine if a machine has become
  # unresponse, which causes the runner to become aborted.
  ping = db.DateTimeProperty()

  # The time at which this runner ended.  This attribute is valid only when
  # the runner has ended (i.e. done == True). Until then, the value is
  # unspecified.
  ended = db.DateTimeProperty(auto_now=True)

  # True if the test run finished and succeeded.  This attribute is valid only
  # when the runner has ended. Until then, the value is unspecified.
  ran_successfully = db.BooleanProperty()

  # The stringized array of exit_codes for each actions of the test.
  exit_codes = db.StringProperty()

  # Contains any swarm specific errors that occured that caused the result
  # string to not get correct setup with the runner output (i.e. the runner
  # timed out so there was no data).
  errors = db.StringProperty()

  # The blobstore reference to the full output of the test.  This key valid only
  # when the runner has ended (i.e. done == True). Until then, it is None.
  result_string_reference = blobstore.BlobReferenceProperty()

  def delete(self):  # pylint: disable-msg=C6409
    # We delete the blob referenced by this model because no one
    # else will ever care about it or try to reference it, so we
    # are just cleaning up the blobstore.
    if self.result_string_reference:
      self.result_string_reference.delete()

    db.Model.delete(self)

  def GetName(self):
    """Gets a name for this runner.

    Returns:
      The  name for this runner, or None if unable to get the name.
    """
    try:
      return '%s:%s' % (self.request.name, self.config_name)
    except db.ReferencePropertyResolveError as e:
      # Sometimes the test runner is unable to resolve the TestRequest
      # member.
      logging.warning(e)
      return None

  def GetConfiguration(self):
    """Gets the configuration associated with this runner.

    Returns:
      A configuration dictionary for this runner.
    """
    config = self.request.GetConfiguration(self.config_name)
    assert config is not None
    return config

  def GetResultString(self):
    """Get the result string for the runner.

    Returns:
      The string representing the output for this runner or an empty string
      if the result hasn't been written yet.
    """
    if self.errors:
      assert self.result_string_reference is None
      return self.errors

    if not self.result_string_reference:
      return ''

    return blobstore_helper.GetBlobstore(self.result_string_reference.key())

  def GetDimensionsString(self):
    """Get a string representing the dimensions this runner requires.

    Returns:
      The string representing the dimensions for this runner.
    """
    return test_request_message.Stringize(self.GetConfiguration().dimensions)

  def GetWaitTime(self):
    """Get the number of seconds between creation and execution start.

    Returns:
      The number of seconds the runner waited, if the runner hasn't started yet
      return 0.
    """
    if not self.started:
      return 0

    time_delta = self.started - self.created
    # MOE: start_strip
    # TODO(user): Replace with total_seconds() once python2.7 is used
    return TotalSeconds(time_delta)
    # MOE: end_strip_and_replace return time_delta.total_seconds())

  def GetMessage(self):
    """Get the message string representing this test runner.

    Returns:
      A string represent this test runner request.
    """
    message = ['Test Request Message:']
    message.append(self.request.message)

    message.append('')
    message.append('Test Runner Message:')
    message.append('Configuration Name: ' + self.config_name)
    message.append('Configuration Instance Index: %d / %d' %
                   (self.config_instance_index, self.num_config_instances))

    return '\n'.join(message)


def AtomicAssignID(key, machine_id):
  """Function to be run by db.run_in_transaction().

  Args:
    key: key of the test runner object to assign the machine_id to.
    machine_id: machine_id of the machine we're trying to assign.

  Raises:
    TxRunnerAlreadyAssignedError: If runner has already been assigned a machine.
  """
  runner = db.get(key)
  if runner and not runner.started:
    runner.machine_id = str(machine_id)
    runner.started = datetime.datetime.now()
    runner.ping = datetime.datetime.now()
    runner.put()
  else:
    # Tell caller to abort this operation.
    raise TxRunnerAlreadyAssignedError


def AssignRunnerToMachine(machine_id, runner, atomic_assign):
  """Will try to atomically assign runner.machine_id to machine_id.

  This function is thread safe and can be called simultaneously on the same
  runner. It will ensure all but one concurrent requests will fail.

  It uses a transaction to run atomic_assign to assign the given machine_id
  inside attribs to the given runner. If the transaction succeeds, it will
  return True which means runner.machine_id = machine_id. However, based on
  datastore documentation, it is possible for datastore to throw exceptions
  on the transaction, and we have no way to conclude if the machine_id of
  the runner was set or not.

  After investigating a few alternative approaches, we decided to return
  False in such situations. This means the runner.machine_id (1) 'might' or
  (2) 'might not' have been changed, but we return False anyways. In case
  (2) no harm, no foul. In case (1), the runner is assumed running but is
  actually not. We expect the timeout event to fire at some future time and
  restart the runner.

  An alternate solution would be to delete that runner and recreate it, set
  the correct created timestamp, etc. which seems a bit more messy. We might
  switch to that if this starts to break at large scales.

  Args:
    machine_id: the machine_id of the machine.
    runner: test runner object to assign the machine to.
    atomic_assign: function pointer to be done atomically.

  Returns:
    True is succeeded, False otherwise.
  """
  for _ in range(MAX_TRANSACTION_RETRY_COUNT):
    try:
      db.run_in_transaction(atomic_assign, runner.key(), machine_id)
      return True
    except TxRunnerAlreadyAssignedError:
      # The runner is already assigned to a machine. Abort.
      break
    except db.TransactionFailedError:
      # This exception only happens if there is a problem with datastore,
      # e.g.high contention, capacity cap, etc. It ensures the operation isn't
      # done so we can safely retry.
      # Since we are on the main server thread, we avoid sleeping between
      # calls.
      continue
    except (db.Timeout, db.InternalError):
      # These exceptions do NOT ensure the operation is done. Based on the
      # Discussion above, we assume it hasn't been assigned.
      logging.exception('Un-determined fate for runner=%s', runner.GetName())
      break

  return False


def AutomaticallyRetryRunner(runner):
  """Attempt to automaticlly retry runner.

  This runner will only be retried if it has't already been automatically
  retried too many times.

  Args:
    runner: The runner to retry.

  Returns:
    True if the runner was successfully setup to get run again.
  """
  if runner.automatic_retry_count < MAX_AUTOMATIC_RETRIES:
    # Don't change the created time since it is not the user's fault
    # we are retrying it (so it should have high prority to run again).
    runner.old_machine_ids.append(runner.machine_id)
    runner.machine_id = None
    runner.done = False
    runner.started = None
    runner.ping = None
    runner.automatic_retry_count += 1
    runner.put()
    return True

  return False


def PingRunner(key, machine_id):
  """Pings the runner, if the key is valid.

  Args:
    key: The key of the runner to ping.
    machine_id: The machine id of the machine pinging.

  Returns:
    True if the runner is successfully pinged.
  """
  try:
    runner = TestRunner.get(key)
  except (db.BadKeyError, db.KindError, db.BadArgumentError) as e:
    logging.error('Failed to find runner, %s', str(e))
    return False

  if not runner:
    logging.error('Failed to find runner')
    return False

  if machine_id != runner.machine_id:
    if machine_id in runner.old_machine_ids:
      # This can happen if the network on the slave went down and the server
      # thought it was dead and retried the test.
      if (runner.machine_id is None and
          AssignRunnerToMachine(machine_id, runner, AtomicAssignID)):
        logging.info('Ping from older machine has resulted in runner '
                     'reconnecting to the machine')

        # The runner stored in the db was updated by AssignRunnerToMachine,
        # so the local runner needed to get updated to contain the same values.
        runner = TestRunner.get(key)
        runner.automatic_retry_count -= 1
        runner.old_machine_ids.remove(machine_id)
        runner.put()
      else:
        logging.info('Recieved a ping from an older machine, pretending to '
                     'accept ping.')
      return True
    else:
      logging.error('Machine ids don\'t match, expected %s but got %s',
                    runner.machine_id, machine_id)
      return False

  if runner.started is None or runner.done:
    logging.error('Trying to ping a runner that is not currently running')
    return False

  runner.ping = datetime.datetime.now()
  runner.put()
  return True


def GetTestRunners(sort_by, ascending, limit, offset):
  """Get the list of the test runners.

  Args:
    sort_by: The string of the attribute to sort the test runners by.
    ascending: True if the runner should be sorted in ascending order.
    limit: The machine number of test runners to return.
    offset: The offset from the complete set of sorted elements and the returned
        list.

  Returns:
    An iterator of test runners in the given range.
  """
  # If we recieve an invalid sort_by parameter, just default to machine_id.
  if not sort_by in TestRunner.properties():
    sort_by = 'machine_id'

  if not ascending:
    sort_by += ' DESC'

  return TestRunner.gql('ORDER BY %s' % sort_by).run(limit=limit, offset=offset)


def DeleteRunnerFromKey(key):
  """Delete the runner that the given key refers to.

  Args:
    key: The key corresponding to the runner to be deleted.

  Returns:
    True if a matching TestRunner was found and deleted.
  """
  runner = None
  try:
    runner = TestRunner.get(key)
  except (db.BadKeyError, db.KindError):
    # We don't need to take any special action with bad keys.
    pass

  if not runner:
    logging.debug('No matching Test Runner found for key, %s', key)
    return False

  DeleteRunner(runner)

  return True


def DeleteRunner(runner):
  """Delete the given runner.

  Args:
    runner: The runner to delete.
  """
  request = runner.request
  runner.delete()
  request.DeleteIfNoMoreRunners()


def DeleteOldRunners():
  """Clean up all runners that are older than a certain age and done."""
  logging.debug('DeleteOldRunners starting')

  old_cutoff = (
      _GetCurrentTime() -
      datetime.timedelta(days=SWARM_FINISHED_RUNNER_TIME_TO_LIVE_DAYS))

  db.delete(TestRunner.gql('WHERE ended < :1', old_cutoff))

  logging.debug('DeleteOldRunners done')


def DeleteOrphanedBlobs():
  """Remove all the orphaned blobs."""
  logging.debug('DeleteOrphanedBlobs starting')

  blobstore_query = blobstore.BlobInfo.all().order('creation')
  blobs_deleted = 0

  try:
    for blob in blobstore_query:
      if not TestRunner.gql('WHERE result_string_reference = :1',
                            blob.key()).count(limit=1):
        blobstore.delete_async(blob.key())
        blobs_deleted += 1
  except db.Timeout:
    logging.warning('Hit a timeout error while deleting orphaned blobs, some '
                    'orphans may still exist')

  logging.debug('DeleteOrphanedBlobs done')

  return blobs_deleted


class TxRunnerAlreadyAssignedError(Exception):
  """Simple exception class signaling a transaction fail."""
  pass
