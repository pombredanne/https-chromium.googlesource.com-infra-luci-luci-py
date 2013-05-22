#!/usr/bin/python2.7
#
# Copyright 2012 Google Inc. All Rights Reserved.

"""A helper script for wrapping url calls."""





import hashlib
import httplib
import logging
import math
import os
import random
import socket
import time
import urllib
import urllib2
import urlparse


COUNT_KEY = 'UrlOpenAttempt'
RESULT_STRING_KEY = 'result_output'

# The index of the query elements from urlparse.
QUERY_INDEX = 4


def UrlOpen(url, data=None, files=None, max_tries=5, wait_duration=None,
            method='POST'):
  """Attempts to open the given url multiple times.

  UrlOpen will attempt to open the the given url several times, stopping
  if it succeeds at reaching the url. It also includes an additional data pair
  in the data that is sent to indicate how many times it has attempted to
  connect so far.

  Args:
    url: The url to open.
    data: The unencoded data to send to the url. This must be a mapping object.
    files: Files to upload with the url, in the format (key, filename, value).
        This is only valid when the method is POSTFORM.
    max_tries: The maximum number of times to try sending this data. Must be
        greater than 0.
    wait_duration: The number of seconds to wait between successive attempts.
        This must be greater than or equal to 0. If no value is given then a
        random value between 0.1 and 10 will be chosen each time (with
        exponential back off to give later retries a longer wait).
    method: Indicates if the request should be a GET or POST request.

  Returns:
    The reponse from the url contacted. If it failed to connect or is given
    invalid arguments, then it returns None.
  """

  if max_tries <= 0:
    logging.error('Invalid number of tries, %d, passed in.', max_tries)
    return None

  if wait_duration and wait_duration < 0:
    logging.error('Invalid wait duration, %d, passed in.', wait_duration)
    return None

  data = data or {}

  if COUNT_KEY in data:
    logging.error('%s already existed in the data passed into UlrOpen. It '
                  'would be overwritten. Aborting UrlOpen', COUNT_KEY)
    return None

  url_response = None
  for attempt in range(max_tries):
    data[COUNT_KEY] = attempt
    try:
      encoded_data = urllib.urlencode(data)

      if method == 'POSTFORM':
        content_type, body = EncodeMultipartFormData(fields=data.iteritems(),
                                                     files=files)
        # We must ensure body isn't None to ensure the request is a POST.
        body = body or ''
        request = urllib2.Request(url, data=body)
        request.add_header('Content-Type', content_type)
        request.add_header('Content-Length', len(body))

        url_response = urllib2.urlopen(request).read()
      elif method == 'POST':
        # Simply specifying data to urlopen makes it a POST.
        url_response = urllib2.urlopen(url, encoded_data).read()
      else:
        url_parts = list(urlparse.urlparse(url))
        url_parts[QUERY_INDEX] = encoded_data
        url = urlparse.urlunparse(url_parts)
        url_response = urllib2.urlopen(url).read()
    except urllib2.HTTPError as e:
      if e.code >= 500:
        # The HTTPError was due to a server error, so retry the attempt.
        logging.warning('Able to connect to %s on attempt %d.\nException: %s ',
                        url, attempt, e)
      else:
        # This HTTPError means we reached the server and there was a problem
        # with the request, so don't retry.
        logging.exception('Able to connect to %s but an exception was '
                          'thrown.\n%s', url, e)
        return None
    except (httplib.HTTPException, socket.error, urllib2.URLError) as e:
      logging.warning('Unable to open url %s on attempt %d.\nException: %s',
                      url, attempt, e)

      if wait_duration is None:
        duration = random.random() * 3 + math.pow(1.5, (attempt + 1))
        duration = min(10, max(0.1, duration))
      else:
        duration = wait_duration

      # Only sleep if we are going to try again.
      if attempt != max_tries - 1:
        time.sleep(duration)

    if url_response is not None:
      logging.info('Opened given url, %s, and got a response of length %d.',
                   url, len(url_response))
      return url_response

  logging.error('Unable to open given url, %s, after %d attempts.',
                url, max_tries)
  return None


def DownloadFile(local_file, url):
  """Downloads the data from the given url and saves it in the local_file.

  Args:
    local_file: Where to save the data downloaded from the url.
    url: Where to fetch the data from.

  Returns:
    True if the file is successfully downloaded.
  """
  local_file = os.path.abspath(local_file)

  url_data = UrlOpen(url, method='GET')

  if url_data is None:
    return False

  try:
    with open(local_file, 'wb') as f:
      f.write(url_data)
  except IOError as e:
    logging.error('Failed to write to %s\n%s', local_file, e)
    return False

  return True


def _ConvertToAscii(value):
  """Convert the given value to an ascii string.

  Args:
    value: The value to convert.

  Returns:
    The value as an ascii string.
  """
  if isinstance(value, str):
    return value
  if isinstance(value, unicode):
    return value.encode('utf-8')

  return str(value)


def EncodeMultipartFormData(fields=None, files=None):
  """Encodes a Multipart form data object.

  This recipe is taken from http://code.activestate.com/recipes/146306/,
  although it has been slighly modified.

  Args:
    fields: a sequence (name, value) elements for
      regular form fields.
    files: a sequence of (name, filename, value) elements for data to be
      uploaded as files.

  Returns:
    content_type: for httplib.HTTP instance
    body: for httplib.HTTP instance
  """
  fields = fields or []
  files = files or []

  boundary = hashlib.md5(str(time.time())).hexdigest()
  body_list = []
  for (key, value) in fields:
    key = _ConvertToAscii(key)
    value = _ConvertToAscii(value)

    body_list.append('--' + boundary)
    body_list.append('Content-Disposition: form-data; name="%s"' % key)
    body_list.append('')
    body_list.append(value)
    body_list.append('--' + boundary)
    body_list.append('')

  for (key, filename, value) in files:
    key = _ConvertToAscii(key)
    filename = _ConvertToAscii(filename)
    value = _ConvertToAscii(value)

    body_list.append('--' + boundary)
    body_list.append('Content-Disposition: form-data; name="%s"; '
                     'filename="%s"' % (key, filename))
    # Other contents types are possible, but swarm is currently only using
    # this type.
    body_list.append('Content-Type: application/octet-stream')
    body_list.append('')
    body_list.append(value)
    body_list.append('--' + boundary)
    body_list.append('')

  if len(body_list) > 1:
    body_list[-2] += '--'

  body = '\r\n'.join(body_list)
  content_type = 'multipart/form-data; boundary=%s' % boundary

  return content_type, body
