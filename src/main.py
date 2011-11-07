#!/usr/bin/python2.4
#
# Copyright 2011 Google Inc. All Rights Reserved.
#
# while testing on a linux box. Do the following:
#


import datetime
import logging
import os.path


from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import util
from common import test_request_message
from server import base_machine_provider
from server import machine_manager
from server import machine_provider
from server import test_manager


# An instance of the test runner manager.  This is used to assign test requests
# to different runners, and keep track of them.
_test_manager = None

# An instance of machine manager.  This is used to manage a set of machines.
_machine_manager = None


class MainHandler(webapp.RequestHandler):
  """Handler for the main page of the web server.

  This handler lists all pending requests and allows callers to manage them.
  """

  def GetTimeString(self, dt):
    """Convert the datetime object to a user-friendly string.

    Arguments:
      dt: a datetime.datetime object.

    Returns:
      A string representing the datetime object to show in the web UI.
    """
    s = '--'

    if dt:
      midnight_today = datetime.datetime.now().replace(hour=0, minute=0,
                                                       second=0, microsecond=0)
      midnight_yesterday = midnight_today - datetime.timedelta(days=1)
      if dt > midnight_today:
        s = dt.strftime('Today at %H:%M')
      elif dt > midnight_yesterday:
        s = dt.strftime('Yesterday at %H:%M')
      else:
        s = dt.strftime('%d %b at %H:%M')

    return s

  def get(self):  # pylint: disable-msg=C6409
    """Handles HTTP GET requests for this handler's URL."""
    # Build info for test requests table.
    # TODO(user): eventually we will want to show only runner that are
    # either pending or running.  The number of ended runners will grow
    # unbounded with time.
    #
    # Once we have labels for usernames, we can also show a second table
    # specific to a user to show him his terminated jobs, so allow him to
    # retry from there.
    show_success = self.request.get('s', 'False') != 'False'

    # After some initial usage, it was determined that it was more convenient
    # to show the list of tests in reverse chronological order.
    runners = []
    query = test_manager.TestRunner.all()
    query.order('-created')
    for runner in query:
      runner.name_string = runner.GetName()
      runner.key_string = str(runner.key())
      runner.status_string = '&nbsp;'
      runner.requested_on_string = self.GetTimeString(runner.created)
      runner.started_string = '--'
      runner.ended_string = '--'
      runner.command_string = '&nbsp;'
      runner.failed_test_class_string = ''

      if runner.machine_id == 0:
        runner.status_string = 'Pending'
        runner.command_string = ('<a href="cancel?r=%s">Cancel</a>' %
                                 runner.key_string)
      elif runner.machine_id >= 0:
        runner.status_string = ('<a title="On machine %d, click for details" '
                                'href="#machine_%d">Running</a>' %
                                (runner.machine_id, runner.machine_id))
        runner.started_string = self.GetTimeString(runner.started)
      else:
        # If this runner successfully completed, and we are not showing them,
        # just ignore it.
        if runner.ran_successfully and not show_success:
          continue

        runner.started_string = self.GetTimeString(runner.started)
        runner.ended_string = self.GetTimeString(runner.ended)

        if runner.ran_successfully:
          runner.status_string = ('<a title="Click to see results" '
                                  'href="get_result?r=%s">Succeeded</a>' %
                                  runner.key_string)
        else:
          runner.failed_test_class_string = 'failed_test'
          runner.command_string = ('<a href="retry?r=%s">Retry</a>' %
                                   runner.key_string)
          runner.status_string = ('<a title="Click to see results" '
                                  'href="get_result?r=%s">Failed</a>' %
                                  runner.key_string)

      runners.append(runner)

    # Build info for acquired machines table.
    machines = []
    for machine in machine_manager.Machine.all():
      machine.status_name = 'Unknown'
      if machine.status == base_machine_provider.MachineStatus.WAITING:
        machine.status_name = 'Waiting'
      elif machine.status == base_machine_provider.MachineStatus.READY:
        machine.status_name = 'Ready'
      elif machine.status == base_machine_provider.MachineStatus.STOPPED:
        machine.status_name = 'Stopped'
      elif machine.status == base_machine_provider.MachineStatus.DONE:
        machine.status_name = 'Done'

      # See if the machine is idle or not.
      idle = test_manager.IdleMachine.gql('WHERE id = :1', machine.id).get()
      if idle:
        machine.action_name = 'Idle'
      else:
        runner = (test_manager.TestRunner.gql('WHERE machine_id = :1',
                                              machine.id).get())
        if runner:
          if runner.started:
            machine.action_name = ('Running <a href="#runner_%s">%s</a>' %
                                   (str(runner.key()), runner.GetName()))
          else:
            machine.action_name = ('Assigned <a href="#runner_%s">%s</a>' %
                                   (str(runner.key()), runner.GetName()))
        else:
          machine.action_name = 'No runner?'

      machines.append(machine)

    if users.get_current_user():
      topbar = ('%s | <a href="%s">Sign out</a>' %
                (users.get_current_user().nickname(),
                 users.create_logout_url('/')))
    else:
      topbar = '<a href="%s">Sign in</a>' % users.create_login_url('/')

    if show_success:
      enable_success_message = """
        <a href="?s=False">Hide successfully completed tests</a>
      """
    else:
      enable_success_message = """
        <a href="?s=True">Show successfully completed tests too</a>
      """

    params = {
        'topbar': topbar,
        'runners': runners,
        'machines': machines,
        'enable_success_message': enable_success_message,
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, params))


class TestRequestHandler(webapp.RequestHandler):
  """Handles test requests from clients."""

  def post(self):  # pylint: disable-msg=C6409
    """Handles HTTP POST requests for this handler's URL."""
    # Validate the request.
    if not self.request.body:
      self.response.set_status(402)
      self.response.out.write('Request must have a body')
      return

    try:
      response = str(_test_manager.ExecuteTestRequest(self.request.body))
      # This enables our callers to use the response string as a JSON string.
      response = response.replace("'", '"')
    except test_request_message.Error, ex:
      message = str(ex)
      logging.exception(message)
      response = 'Error: %s' % message
    self.response.out.write(response)


class ResultHandler(webapp.RequestHandler):
  """Handles test results from remote test runners."""

  def post(self):  # pylint: disable-msg=C6409
    """Handles HTTP POST requests for this handler's URL."""
    logging.debug('Received Result: %s', self.request.url)
    _test_manager.HandleTestResults(self.request)


class PollHandler(webapp.RequestHandler):
  """Handles cron job to poll Machine Provider to execute pending requests."""

  def get(self):  # pylint: disable-msg=C6409
    """Handles HTTP GET requests for this handler's URL."""
    logging.debug('Polling')
    _machine_manager.ValidateMachines()
    _test_manager.AssignPendingRequests(self.request.host_url)
    _test_manager.AbortStaleRunners()
    self.response.out.write("""
    <html>
    <head>
    <title>Poll Done</title>
    </head>
    <body>Poll Done</body>
    </html>
    """)


class QuitHandler(webapp.RequestHandler):
  """Handles the quitquitquit request to shutdown the server."""

  def get(self):  # pylint: disable-msg=C6409
    # This is the only way to get the dev_appserver to stop serving.
    raise KeyboardInterrupt('Quit Request')  # pylint: disable-msg=W1010


class ShowMessageHandler(webapp.RequestHandler):
  """Show the full text of a test request."""

  def get(self):  # pylint: disable-msg=C6409
    """Handles HTTP GET requests for this handler's URL."""
    self.response.headers['Content-Type'] = 'text/plain'

    key = self.request.get('r', '')
    if key:
      runner = test_manager.TestRunner.get(key)

    if runner:
      self.response.out.write(runner.test_request.message)
    else:
      self.response.out.write('Cannot find message for: %s' % key)


class GetResultHandler(webapp.RequestHandler):
  """Show the full result string from a test runner."""

  def get(self):  # pylint: disable-msg=C6409
    """Handles HTTP GET requests for this handler's URL."""
    self.response.headers['Content-Type'] = 'text/plain'

    runner = None
    key = self.request.get('r', '')
    if key:
      runner = test_manager.TestRunner.get(key)

    if runner:
      self.response.out.write(runner.result_string)
    else:
      self.response.out.write('Cannot find message for: %s' % key)


class CancelHandler(webapp.RequestHandler):
  """Cancel a test runner that is not already running."""

  def get(self):  # pylint: disable-msg=C6409
    """Handles HTTP GET requests for this handler's URL."""
    self.response.headers['Content-Type'] = 'text/plain'

    key = self.request.get('r', '')
    if key:
      runner = test_manager.TestRunner.get(key)

    # Make sure found runner is not yet running.
    if runner and runner.machine_id == 0:
      _test_manager.AbortRunner(runner, reason='Runner is not already running.')
      self.response.out.write('Runner canceled.')
    else:
      self.response.out.write('Cannot find runner or too late to cancel: %s' %
                              key)


class RetryHandler(webapp.RequestHandler):
  """Retry a test runner again."""

  def get(self):  # pylint: disable-msg=C6409
    """Handles HTTP GET requests for this handler's URL."""
    self.response.headers['Content-Type'] = 'text/plain'

    key = self.request.get('r', '')
    if key:
      runner = test_manager.TestRunner.get(key)

    if runner:
      runner.machine_id = 0
      runner.started = None
      # Update the created time to make sure that retrying the runner does not
      # make it jump the queue and get executed before other runners for
      # requests added before the user pressed the retry button.
      runner.created = datetime.datetime.now()
      runner.ran_successfully = False
      runner.put()

      self.response.out.write('Runner set for retry.')
    else:
      self.response.out.write('Cannot find message for: %s' % key)


def main():
  # pylint: disable-msg=W0603
  global _test_manager, _machine_manager

  _machine_manager = machine_manager.MachineManager(
      machine_provider.MachineProvider())
  _test_manager = test_manager.TestRequestManager(_machine_manager)

  application = webapp.WSGIApplication([('/', MainHandler),
                                        ('/show_message', ShowMessageHandler),
                                        ('/get_result', GetResultHandler),
                                        ('/cancel', CancelHandler),
                                        ('/retry', RetryHandler),
                                        ('/test', TestRequestHandler),
                                        ('/result', ResultHandler),
                                        ('/tasks/poll', PollHandler),
                                        ('/tasks/quitquitquit', QuitHandler)],
                                       debug=True)
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
