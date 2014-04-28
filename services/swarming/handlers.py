# Copyright 2013 The Swarming Authors. All rights reserved.
# Use of this source code is governed by the Apache v2.0 license that can be
# found in the LICENSE file.

"""Main entry point for Swarming service.

This file contains the URL handlers for all the Swarming service URLs,
implemented using the webapp2 framework.
"""

import collections
import datetime
import functools
import json
import logging
import time
import urllib

import webapp2

from google.appengine import runtime
from google.appengine.api import app_identity
from google.appengine.api import datastore_errors
from google.appengine.api import modules
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from common import swarm_constants
from common import test_request_message
from components import auth
from components import auth_ui
from components import datastore_utils
from components import ereporter2
from components import utils
from server import admin_user
from server import bot_management
from server import dimension_mapping
from server import errors
from server import result_helper
from server import task_glue
from server import user_manager
from stats import daily_stats
from stats import machine_stats
from stats import requestor_daily_stats
from stats import runner_stats
from stats import runner_summary

import template


_NUM_USER_TEST_RUNNERS_PER_PAGE = 50
_NUM_RECENT_ERRORS_TO_DISPLAY = 10

_DELETE_MACHINE_STATS_URL = '/delete_machine_stats'

_SECURE_CHANGE_WHITELIST_URL = '/secure/change_whitelist'
_SECURE_GET_RESULTS_URL = '/secure/get_result'
_SECURE_MAIN_URL = '/secure/main'
_SECURE_USER_PROFILE_URL = '/secure/user_profile'


# Ignore these failures, there's nothing to do.
# TODO(maruel): Store them in the db and make this runtime configurable.
IGNORED_LINES = (
  # Probably originating from appstats.
  '/base/data/home/runtimes/python27/python27_lib/versions/1/google/'
      'appengine/_internal/django/template/__init__.py:729: UserWarning: '
      'api_milliseconds does not return a meaningful value',
)

# Ignore these exceptions.
IGNORED_EXCEPTIONS = (
  'DeadlineExceededError',
  # These occurs during a transaction.
  'Timeout',
)

# Function that is used to determine if an error entry should be ignored.
should_ignore_error_record = functools.partial(
    ereporter2.should_ignore_error_record, IGNORED_LINES, IGNORED_EXCEPTIONS)


def DaysToShow(request):
  """Find the number of days to show, according to the request.

  Args:
    request: A dictionary that might contain the days value, otherwise return
        the default days_to_show value.

  Returns:
    The number of days to show.
  """
  days_to_show = 7
  try:
    days_to_show = int(request.get('days', days_to_show))
  except ValueError:
    # Stick with the default value.
    pass

  return days_to_show


def GetModulesVersions():
  """Returns the current versions on the instance.

  TODO(maruel): Move in components/.
  """
  return [('default', i) for i in modules.get_versions()]


# Helper class for displaying the sort options in html templates.
SortOptions = collections.namedtuple('SortOptions', ['key', 'name'])


def require_cronjob(f):
  """Enforces cronjob."""
  @functools.wraps(f)
  def hook(self, *args, **kwargs):
    if self.request.headers.get('X-AppEngine-Cron') != 'true':
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      msg = 'Only internal cron jobs can do this'
      logging.error(msg)
      self.abort(403, msg)
      return
    return f(self, *args, **kwargs)
  return hook


def require_taskqueue(task_name):
  """Enforces the task is run with a specific task queue."""
  def decorator(f):
    @functools.wraps(f)
    def hook(self, *args, **kwargs):
      if self.request.headers.get('X-AppEngine-QueueName') != task_name:
        self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
        msg = 'Only internal task %s can do this' % task_name
        logging.error(msg)
        self.abort(403, msg)
        return
      return f(self, *args, **kwargs)
    return hook
  return decorator


### Handlers


class FilterParams(object):
  def __init__(
      self, status, test_name_filter, show_successfully_completed,
      machine_id_filter):
    self.status = status
    self.test_name_filter = test_name_filter
    self.show_successfully_completed = show_successfully_completed
    self.machine_id_filter = machine_id_filter

  def generate_page_url(
      self, current_page=None, sort_by=None,
      include_filters=False):
    """Generates an URL that points to the current page with similar options.

    If an option is listed as None, don't include it to allow the html page to
    ensure it can add its desired option.

    Args:
      current_page: The current page to display.
      sort_by: The value to sort the runners by.
      include_filters: True if the filters should be included in the url.

    Returns:
      query url page for the requested filtering settings.
    """
    params = {}
    if current_page:
      params['page'] = str(current_page)
    if sort_by:
      params['sort_by'] = sort_by
    if include_filters:
      if self.status is not None:
        params['status'] = self.status
      if self.show_successfully_completed is not None:
        params['show_successfully_completed'] = str(
            self.show_successfully_completed)
      if self.test_name_filter is not None:
        params['test_name_filter'] = self.test_name_filter
      if self.machine_id_filter is not None:
        params['machine_id_filter'] = self.machine_id_filter
    return '?' + urllib.urlencode(params)

  def get_shards(self, sort_by=None, ascending=None, limit=None, offset=None):
    """Returns a query with the given parameters, also applying the filters.

    Args:
      sort_by: The value to sort the runners by.
      ascending: True if the runners should be sorted in ascending order.
      limit: The maximum number of runners the query should return.
      offset: Number of queries to skip.

    Returns:
      The TestRunner query that is properly adjusted and filtered.
    """
    # TODO(maruel): Use cursors!
    # If we are filtering for running runners, then we will test for inequality
    # on the started field. App engine requires any fields used in an
    # inequality be the first sorts that are applied to the query.
    sort_by_first = 'started' if self.status == 'running' else None

    query = task_glue.GetTestRunners(
        sort_by, ascending, limit, offset, sort_by_first)

    return task_glue.ApplyFilters(
        query,
        self.status,
        self.show_successfully_completed,
        self.test_name_filter,
        self.machine_id_filter)

  def filter_selects_as_html(self):
    """Generates the HTML filter select values, with the proper defaults set.

    Returns:
      The HTML representing the filter select options.
    """
    # TODO(maruel): Use jinja2 instead.
    html = ('Ran Successfully:'
            '<select name="show_successfully_completed" form="filter">')

    if self.show_successfully_completed:
      html += ('<option value="True" selected="True">Yes</option>'
               '<option value="False">No</option>')
    else:
      html += ('<option value="True">Yes</option>'
               '<option value="False" selected="True">No</option>')

    html += ('</select>'
             'Status:'
             '<select name="status" form="filter">')

    if self.status == 'pending':
      html += ('<option value="all">All</option>'
               '<option value="pending" selected="True">Pending Only</option>'
               '<option value="running">Running Only</option>'
               '<option value="done">Done Only</option>')
    elif self.status == 'running':
      html += ('<option value="all">All</option>'
               '<option value="pending">Pending Only</option>'
               '<option value="running" selected="True">Running Only</option>'
               '<option value="done">Done Only</option>')
    elif self.status == 'done':
      html += ('<option value="all">All</option>'
               '<option value="pending">Pending Only</option>'
               '<option value="running">Running Only</option>'
               '<option value="done" selected="True">Done Only</option>')
    else:
      html += ('<option value="all">All</option>'
               '<option value="pending">Pending Only</option>'
               '<option value="running">Running Only</option>'
               '<option value="done">Done Only</option>')

    html += '</select>'
    return html


class MainHandler(auth.AuthenticatingHandler):
  """Handler for the main page of the web server.

  This handler lists all pending requests and allows callers to manage them.
  """
  def parse_filters(self):
    """Parse the filters from the request."""
    return FilterParams(
      self.request.get('status', 'all'),
      self.request.get('test_name_filter', ''),
      # Compare to 'False' so that the default value for invalid user input
      # is True.
      self.request.get('show_successfully_completed', '') != 'False',
      self.request.get('machine_id_filter', ''))

  @auth.require(auth.READ, 'swarming/management')
  def get(self):
    # Build info for test requests table.
    sort_by = self.request.get('sort_by')
    sort_split = sort_by.split('_', 1)
    ascending = not sort_split[0]
    sort_key = sort_split[1] if len(sort_split) > 1 else ''

    # Make sure that the sort key is a valid option.
    if sort_key not in task_glue.ACCEPTABLE_SORTS:
      sort_key = 'created'
      ascending = False

    sorted_by_message = '<p>Currently sorted by: '
    if not ascending:
      sorted_by_message += 'Reverse '
    sorted_by_message += task_glue.ACCEPTABLE_SORTS[sort_key] + '</p>'

    # Prase and load the filters
    params = self.parse_filters()

    runner_count_async = params.get_shards().count_async()

    try:
      page = int(self.request.get('page', 1))
    except ValueError:
      # TODO(maruel): Stop silently ignoring invalid values (in general,
      # everywhere).
      page = 1

    runners = [
      task_glue.make_runner_view(runner)
      for runner in params.get_shards(
          sort_key,
          ascending=ascending,
          limit=_NUM_USER_TEST_RUNNERS_PER_PAGE,
          offset=_NUM_USER_TEST_RUNNERS_PER_PAGE * (page - 1))
    ]
    errors_found = errors.SwarmError.query(
        default_options=ndb.QueryOptions(
          limit=_NUM_RECENT_ERRORS_TO_DISPLAY)).order(
              -errors.SwarmError.created).fetch()

    sort_options = []
    for key, value in task_glue.ACCEPTABLE_SORTS.iteritems():
      # Add the leading _ to the non-reversed key to show it is not to be
      # reversed.
      sort_options.append(SortOptions('_' + key, value))
      sort_options.append(SortOptions('reverse_' + key, 'Reverse ' + value))

    selected_sort = '_' if ascending else 'reverse_'
    selected_sort += sort_key

    total_pages = (runner_count_async.get_result() /
                   _NUM_USER_TEST_RUNNERS_PER_PAGE)

    # Ensure the shown page is capped to a page with content.
    page = min(page, total_pages + 1)

    params = {
      'current_page': page,
      'errors': errors_found,
      'filter_selects': params.filter_selects_as_html(),
      'machine_id_filter': params.machine_id_filter,
      'runners': runners,
      'selected_sort': selected_sort,
      'sort_options': sort_options,
      'sorted_by_message': sorted_by_message,
      'test_name_filter': params.test_name_filter,
      # Add 1 so the pages are 1-indexed.
      'total_pages': map(str, range(1, total_pages + 1, 1)),
      'url_no_filters': params.generate_page_url(page, sort_by),
      'url_no_page': params.generate_page_url(
          sort_by=sort_by, include_filters=True),
      'url_no_sort_by_or_filters': params.generate_page_url(
          page, include_filters=False),
    }
    self.response.out.write(template.render('index.html', params))


class RedirectToMainHandler(webapp2.RequestHandler):
  """Handler to redirect requests to base page secured main page."""

  def get(self):
    self.redirect(_SECURE_MAIN_URL)


class MachineListHandler(auth.AuthenticatingHandler):
  """Handler for the machine list page of the web server.

  This handler lists all the machines that have ever polled the server and
  some basic information about them.
  """

  @auth.require(auth.READ, 'swarming/management')
  def get(self):
    sort_by = self.request.get('sort_by', 'machine_id')
    if sort_by not in machine_stats.ACCEPTABLE_SORTS:
      self.abort(400, 'Invalid sort_by query parameter')

    dead_machine_cutoff = (
        datetime.datetime.utcnow() - machine_stats.MACHINE_DEATH_TIMEOUT)
    machines = []
    for machine in machine_stats.GetAllMachines(sort_by):
      m = machine.to_dict()
      m['html_class'] = (
          'dead_machine' if machine.last_seen < dead_machine_cutoff else '')
      # Add a delete option for each machine assignment.
      # TODO(maruel): This should not be generated via python.
      m['command_string'] = task_glue.GenerateButtonWithHiddenForm(
          'Delete',
          '%s?r=%s' % (_DELETE_MACHINE_STATS_URL, machine.key.string_id()),
          machine.key.string_id())
      machines.append(m)

    sort_options = [
        SortOptions(k, v) for k, v in machine_stats.ACCEPTABLE_SORTS.iteritems()
    ]
    params = {
        'machine_update_time': machine_stats.MACHINE_UPDATE_TIME,
        'machines': machines,
        'selected_sort': sort_by,
        'sort_options': sort_options,
    }
    self.response.out.write(template.render('machine_list.html', params))


class ApiBots(auth.AuthenticatingHandler):
  """Returns the list of known swarming bots."""

  @auth.require(auth.READ, 'swarming/management')
  def get(self):
    params = {
        'machine_death_timeout': machine_stats.MACHINE_DEATH_TIMEOUT,
        'machine_update_time': machine_stats.MACHINE_UPDATE_TIME,
        'machines': [m.to_dict() for m in machine_stats.MachineStats.query()],
    }
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.headers['Cache-Control'] = 'no-cache, no-store'
    self.response.write(utils.encode_to_json(params))


class DeleteMachineStatsHandler(auth.AuthenticatingHandler):
  """Handler to delete a machine assignment."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/clients')
  def post(self):
    key = self.request.get('r')

    if key and machine_stats.DeleteMachineStats(key):
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      self.response.out.write('Machine Assignment removed.')
    else:
      self.response.set_status(204)


class TestRequestHandler(auth.AuthenticatingHandler):
  """Handles test requests from clients."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/clients')
  def post(self):
    # Validate the request.
    if not self.request.get('request'):
      self.abort(400, 'No request parameter found.')

    # TODO(vadimsh): Store identity of a user that posted the request.
    try:
      result = task_glue.ExecuteTestRequest(self.request.get('request'))
    except test_request_message.Error as e:
      message = str(e)
      logging.error(message)
      self.abort(400, message)

    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.out.write(json.dumps(result))


class ResultHandler(auth.AuthenticatingHandler):
  """Handles test results from remote test runners."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/bots')
  def post(self):
    # TODO(user): Share this code between all the request handlers so we
    # can always see how often a request is being sent.
    connection_attempt = self.request.get(swarm_constants.COUNT_KEY)
    if connection_attempt:
      logging.info('This is the %s connection attempt from this machine to '
                   'POST these results', connection_attempt)

    logging.debug('Received Result: %s', self.request.url)

    # TODO(vadimsh): Check that machine that posts the result is same as
    # machine that claimed the runner.
    runner_key = self.request.get('r', '')
    runner = task_glue.GetRunnerFromUrlSafeKey(runner_key)

    if not runner:
      # If the runner is gone, it probably already received results from
      # a different machine and was naturally deleted. We can't do anything
      # with the results now, so just ignore them.
      msg = ('The runner, with key %s, has already been deleted, results lost.'
             % runner_key)
      logging.info(msg)
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      self.response.out.write(msg)
      return

    # Find the high level success/failure from the URL. We assume failure if
    # we can't find the success parameter in the request.
    success = self.request.get('s', 'False') == 'True'
    exit_codes = urllib.unquote_plus(self.request.get('x'))
    overwrite = self.request.get('o', 'False') == 'True'
    machine_id = urllib.unquote_plus(self.request.get('id'))

    # TODO(vadimsh): Verify machine_id matches credentials that are used for
    # current request (i.e. auth.get_current_identity()).

    # TODO(user): The result string should probably be in the body of the
    # request.
    result_string = urllib.unquote_plus(self.request.get(
        swarm_constants.RESULT_STRING_KEY))
    if isinstance(result_string, unicode):
      result_string = result_string.encode(
          runner.request.get().GetTestCase().encoding)

    # Mark the runner as pinging now to prevent it from timing out while
    # the results are getting stored.
    task_glue.PingRunner(runner_key, machine_id)

    results = result_helper.StoreResults(result_string)
    if not task_glue.UpdateTestResult(
        runner,
        machine_id,
        success=success,
        exit_codes=exit_codes,
        results=results,
        overwrite=overwrite):
      self.abort(400, 'Failed to update the runner results.')
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Successfully update the runner results.')


class TaskCleanupDataHandler(webapp2.RequestHandler):
  """Deletes orphaned blobs."""

  @require_taskqueue('cleanup')
  def post(self):
    try:
      # All the things that need to be deleted.
      queries = [
          errors.QueryOldErrors(),
          dimension_mapping.QueryOldDimensionMapping(),
          task_glue.QueryOldRunners(),
          daily_stats.QueryOldDailyStats(),
          requestor_daily_stats.QueryOldRequestorDailyStats(),
          runner_stats.QueryOldRunnerStats(),
          runner_summary.QueryOldWaitSummaries(),
          result_helper.QueryOldResults(),
          result_helper.QueryOldResultChunks(),
      ]
      datastore_utils.incremental_map(
          queries, ndb.delete_multi_async, max_inflight=50)
    except datastore_errors.Timeout:
      logging.info('Ran out of time while cleaning up data. Triggering '
                   'another cleanup.')
      taskqueue.add(method='POST', url='/internal/taskqueue/cleanup_data',
                    queue_name='cleanup')
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class CronAbortStaleRunnersHandler(webapp2.RequestHandler):
  """Aborts stale runners."""

  @require_cronjob
  def get(self):
    task_glue.AbortStaleRunners()
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class CronTriggerCleanupDataHandler(webapp2.RequestHandler):
  """Triggers task to delete orphaned blobs."""

  @require_cronjob
  def get(self):
    taskqueue.add(method='POST', url='/internal/taskqueue/cleanup_data',
                  queue_name='cleanup')
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class CronTriggerGenerateDailyStats(webapp2.RequestHandler):
  """Triggers task to generate daily stats."""

  @require_cronjob
  def get(self):
    taskqueue.add(method='POST', url='/internal/taskqueue/generate_daily_stats',
                  queue_name='stats')
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class CronTriggerGenerateRecentStats(webapp2.RequestHandler):
  """Triggers task to generate recent stats."""

  @require_cronjob
  def get(self):
    taskqueue.add(method='POST',
                  url='/internal/taskqueue/generate_recent_stats',
                  queue_name='stats')
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class DeadBotsCountHandler(webapp2.RequestHandler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    cutoff = machine_stats.utcnow() - machine_stats.MACHINE_DEATH_TIMEOUT
    count = machine_stats.MachineStats.query().filter(
        machine_stats.MachineStats.last_seen < cutoff).count()
    self.response.out.write(str(count))


class CronDetectHangingRunnersHandler(webapp2.RequestHandler):
  """Emails reports of runners that have been waiting too long."""

  @require_cronjob
  def get(self):
    hanging_runners = task_glue.GetHangingRunners()
    if hanging_runners:
      subject = 'Hanging Runners on %s' % app_identity.get_application_id()

      hanging_dimensions = set(runner.dimensions for runner in hanging_runners)
      body = ('The following dimensions have hanging runners (runners that '
              'have been waiting more than %d minutes to run).\n' % (
                  task_glue.TIME_BEFORE_RUNNER_HANGING_IN_MINS) +
              '\n'.join(hanging_dimensions) +
              '\n\nHere are the hanging runner names:\n' +
              '\n'.join(runner.name for runner in hanging_runners)
             )

      admin_user.EmailAdmins(subject, body)
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class TaskGenerateDailyStatsHandler(webapp2.RequestHandler):
  """Generates new daily stats."""

  @require_taskqueue('stats')
  def post(self):
    yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    daily_stats.GenerateDailyStats(yesterday)
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class TaskGenerateRecentStatsHandler(webapp2.RequestHandler):
  """Generates new recent stats."""

  @require_taskqueue('stats')
  def post(self):
    runner_summary.GenerateSnapshotSummary()
    runner_summary.GenerateWaitSummary()
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class CronSendEreporter2MailHandler(webapp2.RequestHandler):
  """Sends email containing the errors found in logservice."""

  @require_cronjob
  def get(self):
    request_id_url = self.request.host_url + '/secure/ereporter2/request/'
    report_url = self.request.host_url + '/secure/ereporter2/report'
    result = ereporter2.generate_and_email_report(
        None,
        should_ignore_error_record,
        admin_user.GetAdmins(),
        request_id_url,
        report_url,
        ereporter2.REPORT_TITLE_TEMPLATE,
        ereporter2.REPORT_CONTENT_TEMPLATE,
        {})
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    if result:
      self.response.write('Success.')
    else:
      # Do not HTTP 500 since we do not want it to be retried.
      self.response.write('Failed.')


class Ereporter2ReportHandler(auth.AuthenticatingHandler):
  """Returns all the recent errors as a web page."""

  @auth.require(auth.READ, 'swarming/management')
  def get(self):
    """Reports the errors logged and ignored.

    Arguments:
      start: epoch time to start looking at. Defaults to the messages since the
             last email.
      end: epoch time to stop looking at. Defaults to now.
    """
    request_id_url = '/secure/ereporter2/request/'
    end = int(float(self.request.get('end', 0)) or time.time())
    start = int(
        float(self.request.get('start', 0)) or
        ereporter2.get_default_start_time() or 0)
    module_versions = GetModulesVersions()
    report, ignored = ereporter2.generate_report(
        start, end, module_versions, should_ignore_error_record)
    env = ereporter2.get_template_env(start, end, module_versions)
    content = ereporter2.report_to_html(
        report, ignored,
        ereporter2.REPORT_HEADER_TEMPLATE,
        ereporter2.REPORT_CONTENT_TEMPLATE,
        request_id_url, env)
    out = template.render('ereporter2_report.html', {'content': content})
    self.response.write(out)


class Ereporter2RequestHandler(auth.AuthenticatingHandler):
  """Dumps information about single logged request."""

  @auth.require(auth.READ, 'swarming/management')
  def get(self, request_id):
    # TODO(maruel): Add UI.
    data = ereporter2.log_request_id_to_dict(request_id)
    if not data:
      self.abort(404, detail='Request id was not found.')
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    json.dump(data, self.response, indent=2, sort_keys=True)


class ShowMessageHandler(auth.AuthenticatingHandler):
  """Show the full text of a test request."""

  @auth.require(auth.READ, 'swarming/management')
  def get(self):
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'

    runner_key = self.request.get('r', '')
    runner = task_glue.GetRunnerFromUrlSafeKey(runner_key)

    if runner:
      self.response.write(utils.encode_to_json(runner.GetAsDict()))
    else:
      self.response.set_status(404)
      self.response.out.write('{}')


class UploadStartSlaveHandler(auth.AuthenticatingHandler):
  """Accept a new start slave script."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/management')
  def post(self):
    script = self.request.get('script', '')
    if not script:
      self.abort(400, 'No script uploaded')

    bot_management.StoreStartSlaveScript(script)
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


class StatsHandler(webapp2.RequestHandler):
  """Show all the collected swarm stats."""

  def get(self):
    days_to_show = DaysToShow(self.request)

    weeks_daily_stats = daily_stats.GetDailyStats(
        datetime.datetime.utcnow().date() -
        datetime.timedelta(days=days_to_show))
    # Reverse the daily stats so that the newest data is listed first, which
    # makes more sense when listing these values in a table.
    weeks_daily_stats.reverse()

    max_days_to_show = min(daily_stats.DAILY_STATS_LIFE_IN_DAYS,
                           runner_summary.WAIT_SUMMARY_LIFE_IN_DAYS)
    params = {
        'daily_stats': weeks_daily_stats,
        'days_to_show': days_to_show,
        'max_days_to_show': range(1, max_days_to_show),
        'runner_wait_stats': runner_summary.GetRunnerWaitStats(days_to_show),
    }
    self.response.out.write(template.render('stats.html', params))


class GetMatchingTestCasesHandler(auth.AuthenticatingHandler):
  """Get all the keys for any test runners that match a given test case name."""

  @auth.require(auth.READ, 'swarming/clients')
  def get(self):
    test_case_name = self.request.get('name', '')

    matches = task_glue.GetAllMatchingTestRequests(test_case_name)
    keys = []
    for match in matches:
      keys.extend(key.urlsafe() for key in match.runner_keys)

    logging.info('Found %d keys in %d TestRequests', len(keys), len(matches))
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    if keys:
      self.response.write(utils.encode_to_json(keys))
    else:
      self.response.set_status(404)
      self.response.write('[]')


class GetNewestMatchingTestCasesHandler(auth.AuthenticatingHandler):
  """Gets all the runner keys owned by the newest test request with this name.
  """

  @auth.require(auth.READ, 'swarming/clients')
  def get(self):
    test_case_name = self.request.get('name', '')

    match = task_glue.GetNewestMatchingTestRequests(test_case_name)
    keys = [key.urlsafe() for key in match.runner_keys]

    logging.info('Found %d keys in the newest TestRequests', len(keys))
    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    if keys:
      self.response.write(utils.encode_to_json(keys))
    else:
      self.response.set_status(404)
      self.response.write('[]')


# TODO(vadimsh): Remove once final ACLs structure is in place.
class SecureGetResultHandler(auth.AuthenticatingHandler):
  """Show the full result string from a test runner."""

  @auth.require(auth.READ, 'swarming/management')
  def get(self):
    SendRunnerResults(self.response, self.request.get('r', ''))


class GetResultHandler(auth.AuthenticatingHandler):
  """Show the full result string from a test runner."""

  @auth.require(auth.READ, 'swarming/clients')
  def get(self):
    SendRunnerResults(self.response, self.request.get('r', ''))


class GetSlaveCodeHandler(auth.AuthenticatingHandler):
  """Returns a zip file with all the files required by a slave.

  Optionally specify the hash version to download. If so, the returned data is
  cacheable.
  """

  @auth.require(auth.READ, 'swarming/bots')
  def get(self, version=None):
    if version:
      expected = bot_management.SlaveVersion()
      if version != expected:
        logging.error('Requested Swarming bot %s, have %s', version, expected)
        self.abort(404)
      self.response.headers['Cache-Control'] = 'public, max-age=3600'
    else:
      self.response.headers['Cache-Control'] = 'no-cache, no-store'
    self.response.headers['Content-Type'] = 'application/octet-stream'
    self.response.headers['Content-Disposition'] = (
        'attachment; filename="swarm_bot.zip"')
    self.response.out.write(bot_management.SlaveCodeZipped())


class CleanupResultsHandler(auth.AuthenticatingHandler):
  """Delete the Test Runner with the given key."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/bots')
  def post(self):
    self.response.headers['Content-Type'] = 'test/plain'

    key = self.request.get('r', '')
    if task_glue.DeleteRunnerFromKey(key):
      self.response.out.write('Key deleted.')
    else:
      self.response.out.write('Key deletion failed.')
      logging.warning('Unable to delete runner [key: %s]', str(key))


class CancelHandler(auth.AuthenticatingHandler):
  """Cancel a test runner that is not already running."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/management')
  def post(self):
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'

    runner_key = self.request.get('r', '')
    # Make sure found runner is not yet running.
    if task_glue.AbortRunner(runner_key, reason='Runner cancelled by user.'):
      self.response.out.write('Runner canceled.')
    else:
      self.response.out.write('Unable to cancel runner')
      self.response.set_status(400)


class RetryHandler(auth.AuthenticatingHandler):
  """Retry a test runner again."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/management')
  def post(self):
    runner_key = self.request.get('r', '')
    if task_glue.RetryRunner(runner_key):
      # TODO(maruel): Return the new TaskRequest key.
      # TODO(maruel): Use json encoded return values for the APIs.
      self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
      self.response.out.write('Runner set for retry.')
    else:
      self.response.out.write('Unable to retry runner')
      self.response.set_status(400)


class RegisterHandler(auth.AuthenticatingHandler):
  """Handler for the register_machine of the Swarm server.

  Attempt to find a matching job for the querying machine.
  """

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/bots')
  def post(self):
    # Validate the request.
    if not self.request.body:
      self.abort(400, 'Request must have a body')

    attributes_str = self.request.get('attributes')
    try:
      attributes = json.loads(attributes_str)
    except (TypeError, ValueError) as e:
      message = 'Invalid attributes: %s: %s' % (attributes_str, e)
      logging.error(message)
      self.abort(400, message)

    # TODO(vadimsh): Ensure attributes['id'] matches credentials used
    # to authenticate the request (i.e. auth.get_current_identity()).
    try:
      response = json.dumps(
          task_glue.ExecuteRegisterRequest(attributes, self.request.host_url))
    except runtime.DeadlineExceededError as e:
      # If the timeout happened before a runner was assigned there are no
      # problems. If the timeout occurred after a runner was assigned, that
      # runner will timeout (since the machine didn't get the details required
      # to run it) and it will automatically get retried when the machine
      # "timeout".
      message = str(e)
      logging.warning(message)
      self.abort(500, message)
    except test_request_message.Error as e:
      message = str(e)
      logging.error(message)
      self.abort(400, message)

    self.response.headers['Content-Type'] = 'application/json; charset=utf-8'
    self.response.out.write(response)


class RunnerPingHandler(auth.AuthenticatingHandler):
  """Handler for runner pings to the server.

  The runner pings are used to let the server know a runner is still working, so
  it won't consider it stale.
  """

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/bots')
  def post(self):
    # TODO(vadimsh): Any machine can send ping on behalf of any other machine.
    # Ensure 'id' matches credentials used to authenticate the request (i.e.
    # auth.get_current_identity()).
    key = self.request.get('r', '')
    machine_id = self.request.get('id', '')
    if not task_glue.PingRunner(key, machine_id):
      self.abort(400, 'Runner failed to ping.')

    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


# A basic helper class for holding the runner summary for a dimension.
RunnerSummary = collections.namedtuple(
    'RunnerSummary', ['dimensions', 'pending_runners', 'running_runners'])


def GenerateHistoryHoursSelect():
  """Returns the HTML to generate a select box for the hours to show."""
  # Allow up to a day, by the hour.
  options_hours = ''.join(
      '<option value=\'%d\'>%d hours</option>' % (i, i) for i in range(1, 25))

  # Allow multiple days, up to 4 weeks.
  options_days = ''.join(
      '<option value=\'%d\'>%d days</option>' % (i * 24, i)
      for i in range(2, 29))

  return (
      '<select id="hours_to_show" onchange="document.location.href=\'?hours=\' '
      '+ this.value"><option>-</option>%s%s</select>' %
      (options_hours, options_days))


class StatsTasksHandler(webapp2.RequestHandler):
  """Handler for displaying a summary of the current runners."""

  def get(self):
    try:
      hours = int(self.request.get('hours', '24'))
    except ValueError:
      self.abort(400, 'Invalid hours')

    if hours <= 24:
      time_frame = '%d hours' % hours
    else:
      time_frame = '%d days' % (hours/24)

    # Start querying all the summaries for the graph.
    summary_cutoff_time = (datetime.datetime.utcnow() -
                           datetime.timedelta(hours=hours))
    summaries_future = runner_summary.RunnerSummary.query(
        runner_summary.RunnerSummary.time > summary_cutoff_time).fetch_async()

    # Get a snapshot of the current state of pending and running runners.
    snapshot_summary = [
        RunnerSummary(test_request_message.Stringize(d), s[0], s[1])
        for d, s in runner_summary.GetRunnerSummaryByDimension().iteritems()
    ]
    total_pending = sum(r.pending_runners for r in snapshot_summary)
    total_running = sum(r.running_runners for r in snapshot_summary)

    # Start the graph dict for each dimension.
    runner_summary_graphs = dict(
        (s.dimensions, {'data': [], 'id': i, 'title': s.dimensions})
        for i, s in enumerate(snapshot_summary))

    # Convert the runner summaries to the graph array.
    for summary in summaries_future.get_result():
      # It seems possible to get a summary that we don't have a snapshot for.
      # Got crashes but unable to repo, so add logging to try and catch
      # this case.
      if summary.dimensions in runner_summary_graphs:
        runner_summary_graphs[summary.dimensions]['data'].append(
            [summary.time.isoformat(), summary.pending, summary.running])
      else:
        logging.error('\'%s\' wasn\'t in set of runner summaries [%s]',
                      summary.dimensions, runner_summary_graphs.keys())

    params = {
        'hours_select': GenerateHistoryHoursSelect(),
        'runner_summary_graphs': runner_summary_graphs.values(),
        'snapshot_summary': snapshot_summary,
        'time_frame': time_frame,
        'total_pending_runners': total_pending,
        'total_running_runners': total_running,
    }
    self.response.out.write(template.render('stats_tasks.html', params))


class StatsDailyHandler(webapp2.RequestHandler):
  """Handler for generating the html page to display the daily stats."""

  # A mapping of the element's variable name, and the name that should be
  # displayed to the user.
  ELEMENTS_TO_GRAPH = [
      ('shards_failed', 'Shards Failed'),
      ('shards_finished', 'Shards Finished'),
      ('shards_aborted', 'Shards Aborted'),
      ('total_running_time', 'Total Running Time'),
      ('total_wait_time', 'Total Wait Time'),
  ]

  def _GetGraphableDailyStats(self, days):
    """Convert the daily_stats into a list of graphs objects for visualization.

    Args:
      days: A list of daily stats to split into components.

    Returns:
      A list of dictionaries with the graph title and an array that can be
      passed to the data visualization tool.
    """
    graphs_to_show = [
        {
          'data_array': [['Date', title_name]],
          'element_id': element_name,
          'title': title_name,
        } for element_name, title_name in self.ELEMENTS_TO_GRAPH
    ]
    for stat in days:
      date_str = stat.date.isoformat()
      for i, element in enumerate(self.ELEMENTS_TO_GRAPH):
        graphs_to_show[i]['data_array'].append(
            [date_str, int(getattr(stat, element[0]))])

    return graphs_to_show

  def get(self):
    days_to_show = DaysToShow(self.request)

    params = {
        'graphs': self._GetGraphableDailyStats(daily_stats.GetDailyStats(
            datetime.datetime.utcnow().date() -
            datetime.timedelta(days=days_to_show))),
        'max_days_to_show': range(1, daily_stats.DAILY_STATS_LIFE_IN_DAYS),
    }
    self.response.out.write(template.render('stats_daily.html', params))


class StatsWaitsHandler(webapp2.RequestHandler):
  """Handler for displaying the wait times, broken by minute, per dimensions."""

  def get(self):
    days_to_show = DaysToShow(self.request)

    params = {
        'days_to_show': days_to_show,
        'max_days_to_show': range(1, runner_summary.WAIT_SUMMARY_LIFE_IN_DAYS),
        'wait_breakdown': runner_summary.GetRunnerWaitStatsBreakdown(
            days_to_show),
    }
    self.response.out.write(template.render('stats_waits.html', params))


class ServerPingHandler(webapp2.RequestHandler):
  """Handler to ping when checking if the server is up.

  This handler should be extremely lightweight. It shouldn't do any
  computations, it should just state that the server is up.
  """

  def get(self):
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Server up')


class UserProfileHandler(auth.AuthenticatingHandler):
  """Handler for the user profile page of the web server.

  This handler lists user info, such as their IP whitelist and settings.
  """

  @auth.require(auth.READ, 'swarming/management')
  def get(self):
    display_whitelists = sorted(
        (
          {
            'ip': w.ip,
            'key': w.key.id,
            'password': w.password,
            'url': _SECURE_CHANGE_WHITELIST_URL,
          } for w in user_manager.MachineWhitelist().query()),
        key=lambda x: x['ip'])

    params = {
        'change_whitelist_url': _SECURE_CHANGE_WHITELIST_URL,
        'whitelists': display_whitelists,
    }
    self.response.out.write(template.render('user_profile.html', params))


class ChangeWhitelistHandler(auth.AuthenticatingHandler):
  """Handler for making changes to a user whitelist."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/management')
  def post(self):
    ip = self.request.get('i', self.request.remote_addr)

    # Make sure a password '' sent by the form is stored as None.
    password = self.request.get('p', None) or None

    add = self.request.get('a')
    if add == 'True':
      user_manager.AddWhitelist(ip, password)
    elif add == 'False':
      user_manager.DeleteWhitelist(ip)
    else:
      self.abort(400, 'Invalid \'a\' parameter.')

    self.redirect(_SECURE_USER_PROFILE_URL, permanent=True)


class RemoteErrorHandler(auth.AuthenticatingHandler):
  """Handler to log an error reported by remote machine."""

  # TODO(vadimsh): Implement XSRF token support.
  xsrf_token_enforce_on = ()

  @auth.require(auth.UPDATE, 'swarming/bots')
  def post(self):
    # TODO(vadimsh): Log machine identity as well.
    error_message = self.request.get('m', '')
    error = errors.SwarmError(
        name='Remote Error Report', message=error_message,
        info='Remote machine address: %s' % self.request.remote_addr)
    error.put()

    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.out.write('Success.')


def ip_whitelist_authentication(request):
  """Check to see if the request is from a whitelisted machine.

  Will use the remote machine's IP and provided password (if any).

  Args:
    request: WebAPP request sent by remote machine.

  Returns:
    auth.Identity of a machine if IP is whitelisted, None otherwise.
  """
  assert request.remote_addr
  is_whitelisted = user_manager.IsWhitelistedMachine(
      request.remote_addr, request.get('password', None))

  # IP v6 addresses contain ':' that is not allowed in identity name.
  if is_whitelisted:
    return auth.Identity(
        auth.IDENTITY_BOT, request.remote_addr.replace(':', '-'))

  # Log the error.
  error = errors.SwarmError(
      name='Authentication Failure', message='Handler: %s' % request.url,
      info='Remote machine address: %s' % request.remote_addr)
  error.put()

  return None


def SendRunnerResults(response, key):
  """Sends the results of the runner specified by key.

  Args:
    response: Response to be sent to remote machine.
    key: Key identifying the runner.
  """
  results = task_glue.GetRunnerResults(key)

  if results:
    # Convert the output to utf-8 to ensure that the JSON library can
    # handle it without problems.
    # TODO(maruel): It is decoding from utf-8 to unicode. This is confused.
    results['output'] = results['output'].decode('utf-8', 'replace')
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    response.out.write(json.dumps(results))
  else:
    # TODO(maruel): Use 404 if not present.
    response.set_status(204)
    logging.info('Unable to provide runner results [key: %s]', key)


class WarmupHandler(webapp2.RequestHandler):
  def get(self):
    auth.warmup()
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.write('ok')


def CreateApplication():
  urls = [
      ('/', RedirectToMainHandler),
      ('/cleanup_results', CleanupResultsHandler),
      ('/get_matching_test_cases', GetMatchingTestCasesHandler),
      ('/get_newest_matching_test_cases', GetNewestMatchingTestCasesHandler),
      ('/get_result', GetResultHandler),
      ('/get_slave_code', GetSlaveCodeHandler),
      ('/get_slave_code/<version:[0-9a-f]{40}>', GetSlaveCodeHandler),
      ('/poll_for_test', RegisterHandler),
      ('/remote_error', RemoteErrorHandler),
      ('/result', ResultHandler),
      ('/runner_ping', RunnerPingHandler),

      ('/secure/ereporter2/report', Ereporter2ReportHandler),
      ('/secure/ereporter2/request/<request_id:[0-9a-fA-F]+>',
          Ereporter2RequestHandler),
      ('/secure/machine_list', MachineListHandler),
      ('/secure/retry', RetryHandler),
      ('/secure/show_message', ShowMessageHandler),

      ('/stats', StatsHandler),
      ('/stats/daily', StatsDailyHandler),
      ('/stats/tasks', StatsTasksHandler),
      ('/stats/waits', StatsWaitsHandler),

      ('/server_ping', ServerPingHandler),
      ('/test', TestRequestHandler),
      ('/upload_start_slave', UploadStartSlaveHandler),
      (_DELETE_MACHINE_STATS_URL, DeleteMachineStatsHandler),
      ('/secure/cancel', CancelHandler),
      (_SECURE_CHANGE_WHITELIST_URL, ChangeWhitelistHandler),
      (_SECURE_GET_RESULTS_URL, SecureGetResultHandler),
      (_SECURE_MAIN_URL, MainHandler),
      (_SECURE_USER_PROFILE_URL, UserProfileHandler),

      # The new APIs:
      ('/swarming/api/v1/bots', ApiBots),
      ('/swarming/api/v1/bots/dead/count', DeadBotsCountHandler),

      # Internal urls.

      # Cron jobs.
      ('/internal/cron/abort_stale_runners', CronAbortStaleRunnersHandler),
      ('/internal/cron/detect_hanging_runners',
          CronDetectHangingRunnersHandler),
      ('/internal/cron/ereporter2/mail', CronSendEreporter2MailHandler),
      ('/internal/cron/trigger_cleanup_data', CronTriggerCleanupDataHandler),
      ('/internal/cron/trigger_generate_daily_stats',
          CronTriggerGenerateDailyStats),
      ('/internal/cron/trigger_generate_recent_stats',
          CronTriggerGenerateRecentStats),

      # Task queues.
      ('/internal/taskqueue/cleanup_data', TaskCleanupDataHandler),
      ('/internal/taskqueue/generate_daily_stats',
          TaskGenerateDailyStatsHandler),
      ('/internal/taskqueue/generate_recent_stats',
          TaskGenerateRecentStatsHandler),

      ('/_ah/warmup', WarmupHandler),
  ]

  # Upgrade to Route objects so regexp work.
  routes = [webapp2.Route(*i) for i in urls]

  # Supported authentication mechanisms.
  auth.configure([
      auth.oauth_authentication,
      auth.cookie_authentication,
      auth.service_to_service_authentication,
      ip_whitelist_authentication,
  ])

  # Customize auth UI to show that it's running on swarming service.
  auth_ui.configure_ui(
      app_name='Swarming',
      app_version=modules.get_current_version_name(),
      app_revision_url=None)

  # Add routes with Auth REST API and Auth UI.
  routes.extend(auth_ui.get_rest_api_routes())
  routes.extend(auth_ui.get_ui_routes())

  return webapp2.WSGIApplication(routes, debug=True)
