#!/usr/bin/python
# Copyright 2015 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Machine Provider agent for GCE instances."""

import argparse
import base64
import datetime
import httplib2
import json
import logging
import logging.handlers
import os
import pwd
import shutil
import socket
import string
import subprocess
import sys
import tempfile
import time
import traceback
import urllib2
import urlparse


THIS_DIR = os.path.dirname(__file__)

LOG_DIR = os.path.join(THIS_DIR, 'logs')
LOG_FILE = os.path.join(LOG_DIR, '%s.log' % os.path.basename(__file__))

AGENT_UPSTART_CONFIG_DEST = '/etc/init/machine-provider-agent.conf'
AGENT_UPSTART_CONFIG_TMPL = os.path.join(
    THIS_DIR, 'machine-provider-agent.conf.tmpl')
AGENT_UPSTART_JOB = 'machine-provider-agent'
CHROME_BOT = 'chrome-bot'
METADATA_BASE_URL = 'http://metadata/computeMetadata/v1'
PUBSUB_BASE_URL = 'https://pubsub.googleapis.com/v1/projects'
SWARMING_BOT_DIR = '/b/s'
SWARMING_BOT_ZIP = os.path.join(SWARMING_BOT_DIR, 'swarming_bot.zip')
SWARMING_UPSTART_CONFIG_DEST = '/etc/init/swarming-start-bot.conf'
SWARMING_UPSTART_CONFIG_SRC = os.path.join(THIS_DIR, 'swarming-start-bot.conf')


class Error(Exception):
  pass


class RequestError(Error):
  def __init__(self, response, content):
    self.response = response
    self.content = content


# 404
class NotFoundError(RequestError):
  pass


# 409
class ConflictError(RequestError):
  pass


def configure_logging():
  """Sets up the log file."""
  class TimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
      datefmt = datefmt or '%Y-%m-%d %H:%M:%S'
      return time.strftime(datefmt, time.localtime(record.created))

  class SeverityFilter(logging.Filter):
    def filter(self, record):
      record.severity = record.levelname[0]
      return True

  if not os.path.exists(LOG_DIR):
    os.mkdir(LOG_DIR)

  logger = logging.getLogger()
  logger.setLevel(logging.DEBUG)

  log_file = logging.handlers.RotatingFileHandler(LOG_FILE, backupCount=100)
  log_file.addFilter(SeverityFilter())
  log_file.setFormatter(TimeFormatter('%(asctime)s %(severity)s: %(message)s'))
  logger.addHandler(log_file)

  # Log all uncaught exceptions.
  def log_exception(exception_type, value, stack_trace):
    logging.error(
        ''.join(traceback.format_exception(exception_type, value, stack_trace)),
    )
  sys.excepthook = log_exception

  # Rotate log files once on startup to get per-execution log files.
  if os.path.exists(LOG_FILE):
    log_file.doRollover()


def get_metadata(key=''):
  """Retrieves the specified metadata from the metadata server.

  Args:
    key: The key whose value should be returned from the metadata server.

  Returns:
    The value associated with the metadata key.

  Raises:
    httplib2.ServerNotFoundError: If the metadata server cannot be found.
      Probably indicates that this script is not running on a GCE instance.
    NotFoundError: If the metadata key could not be found.
  """
  response, content = httplib2.Http().request(
      '%s/%s' % (METADATA_BASE_URL, key),
      headers={'Metadata-Flavor': 'Google'},
      method='GET',
  )
  if response['status'] == '404':
    raise NotFoundError(response, content)
  return content


class AuthorizedHTTPRequest(httplib2.Http):
  """Subclass for HTTP requests authorized with service account credentials."""

  def __init__(self, service_account='default'):
    super(AuthorizedHTTPRequest, self).__init__()
    self._expiration_time = datetime.datetime.now()
    self._service_account = service_account
    self._token = None
    self.refresh_token()

  @property
  def service_account(self):
    return self._service_account

  @property
  def token(self):
    return self._token

  def refresh_token(self):
    """Fetches and caches the token from the metadata server."""
    token = json.loads(get_metadata(
        'instance/service-accounts/%s/token' % self.service_account,
    ))
    seconds = token['expires_in'] - 60
    self._expiration_time = (
        datetime.datetime.now() + datetime.timedelta(seconds=seconds)
    )
    self._token = token['access_token']

  def request(self, *args, **kwargs):
    # Tokens fetched from the metadata server are valid for at least
    # 10 more minutes, so the token will still be valid for the request
    # (i.e. no risk of refreshing to a token that is about to expire).
    if self._expiration_time < datetime.datetime.now():
      self.refresh_token()
    kwargs['headers'] = kwargs.get('headers', {}).copy()
    kwargs['headers']['Authorization'] = 'Bearer %s' % self.token
    return super(AuthorizedHTTPRequest, self).request(*args, **kwargs)


class PubSub(object):
  """Class for interacting with Cloud Pub/Sub."""

  def __init__(self, service_account='default'):
    self._http = AuthorizedHTTPRequest(service_account=service_account)

  def acknowledge(self, subscription, project, ack_ids):
    """Acknowledges the receipt of messages on a Cloud Pub/Sub subscription.

    Args:
      subscription: Name of the subscription.
      project: Project the subscription exists in.
      ack_ids: IDs of messages to acknowledge.

    Raises:
      NotFoundError: If the subscription and/or topic can't be found.
    """
    logging.info('Acknowledging %s', ', '.join(ack_ids))
    response, content = self._http.request(
        '%s/%s/subscriptions/%s:acknowledge' % (
            PUBSUB_BASE_URL, project, subscription),
        body=json.dumps({'ackIds': ack_ids}),
        method='POST',
    )
    if response['status'] == '404':
      raise NotFoundError(response, json.loads(content))
    return json.loads(content)

  def pull(self, subscription, project):
    """Polls for new messages on a Cloud Pub/Sub pull subscription.

    Args:
      subscription: Name of the pull subscription.
      project: Project the pull subscription exists in.

    Returns:
      A JSON response from the Pub/Sub service.

    Raises:
      NotFoundError: If the subscription and/or topic can't be found.
    """
    response, content = self._http.request(
        '%s/%s/subscriptions/%s:pull' % (
            PUBSUB_BASE_URL, project, subscription),
        body=json.dumps({'maxMessages': 1, 'returnImmediately': False}),
        method='POST',
    )
    if response['status'] == '404':
      raise NotFoundError(response, json.loads(content))
    return json.loads(content)


def listen():
  """Listens for Cloud Pub/Sub communication."""
  # Attributes tell us what subscription has been created for us to listen to.
  project = get_metadata('instance/attributes/pubsub_subscription_project')
  service_account = get_metadata('instance/attributes/pubsub_service_account')
  subscription = get_metadata('instance/attributes/pubsub_subscription')
  pubsub = PubSub(service_account=service_account)

  while True:
    logging.info('Polling for new messages')
    ack_ids = []
    start_time = time.time()
    response = pubsub.pull(subscription, project)
    for message in response.get('receivedMessages', []):
      ack_ids.append(message['ackId'])
      attributes = message['message'].get('attributes', {})
      message = base64.b64decode(message['message'].get('data', ''))
      logging.info(
          'Received message: %s\nID: %s\nAttributes: %s',
          message,
          ack_ids[-1],
          json.dumps(attributes, indent=2),
      )

      if message == 'CONNECT' and attributes.get('swarming_server'):
        if os.path.exists(SWARMING_UPSTART_CONFIG_DEST):
          os.remove(SWARMING_UPSTART_CONFIG_DEST)
        shutil.copy2(SWARMING_UPSTART_CONFIG_SRC, SWARMING_UPSTART_CONFIG_DEST)

        if not os.path.exists(SWARMING_BOT_DIR):
          os.mkdir(SWARMING_BOT_DIR)
        chrome_bot = pwd.getpwnam(CHROME_BOT)
        os.chown(SWARMING_BOT_DIR, chrome_bot.pw_uid, chrome_bot.pw_gid)

        if os.path.exists(SWARMING_BOT_ZIP):
          # Delete just the zip, not the whole directory so logs are kept.
          os.remove(SWARMING_BOT_ZIP)

        http = AuthorizedHTTPRequest(service_account=service_account)
        _, bot_code = http.request(
            urlparse.urljoin(attributes['swarming_server'], 'bot_code'),
            method='GET',
        )
        with open(SWARMING_BOT_ZIP, 'w') as fd:
          fd.write(bot_code)
        os.chown(SWARMING_BOT_ZIP, chrome_bot.pw_uid, chrome_bot.pw_gid)

        pubsub.acknowledge(subscription, project, ack_ids)
        subprocess.check_call(['/sbin/shutdown', '-r', 'now'])

    if ack_ids:
      pubsub.acknowledge(subscription, project, ack_ids)
    if time.time() - start_time < 1:
      # Iterate at most once per second (chosen arbitrarily).
      time.sleep(1)


def install():
  """Installs Upstart config for the Machine Provider agent."""
  with open(AGENT_UPSTART_CONFIG_TMPL) as f:
    template = f.read()
  config = string.Template(template).substitute(
      agent=os.path.abspath(__file__))

  if os.path.exists(AGENT_UPSTART_CONFIG_DEST):
    with open(AGENT_UPSTART_CONFIG_DEST) as f:
      existing_config = f.read()
    if config == existing_config:
      logging.info('Already installed: %s', AGENT_UPSTART_CONFIG_DEST)
      return
    else:
      logging.info('Reinstalling: %s', AGENT_UPSTART_CONFIG_DEST)
      os.remove(AGENT_UPSTART_CONFIG_DEST)
  else:
    logging.info('Installing: %s', AGENT_UPSTART_CONFIG_DEST)

  with open(AGENT_UPSTART_CONFIG_DEST, 'wb') as f:
    f.write(config)
  subprocess.check_call(['initctl', 'reload-configuration'])
  subprocess.check_call(['start', AGENT_UPSTART_JOB])


def main():
  configure_logging()

  parser = argparse.ArgumentParser()
  parser.add_argument(
      '-i',
      '--install',
      action='store_true',
      help='Install Upstart config for the Machine Provider agent.',
  )
  args = parser.parse_args()

  if args.install:
    return install()

  return listen()


if __name__ == '__main__':
  sys.exit(main())
