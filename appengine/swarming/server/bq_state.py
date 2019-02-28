# coding: utf-8
# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Common code to stream rows to BigQuery."""

import datetime
import logging

from google.appengine.api import app_identity
from google.appengine.api import memcache
from google.appengine.ext import ndb

from components import net
from components import utils
import bqh


### Models


class BqState(ndb.Model):
  """Stores the last BigQuery successful writes.

  Key id: table_name.

  By storing the successful writes, this enables not having to read from BQ. Not
  having to sync state *from* BQ means one less RPC that could fail randomly.
  """
  # Disable memcache, so that deleting the entity takes effect without having to
  # clear memcache.
  _use_memcache = False

  # Last time this entity was updated.
  ts = ndb.DateTimeProperty(indexed=False)

  # When in backfill more, the oldest item that was processed. If it's over 18
  # months old, don't look at it.
  oldest = ndb.DateTimeProperty(indexed=False)
  # When in streaming mode, the most recent item that was processed.
  recent = ndb.DateTimeProperty(indexed=False)


### Private APIs.


def _send_to_bq_raw(dataset, table_name, rows):
  """Sends the rows to BigQuery.

  Arguments:
    dataset: BigQuery dataset name that contains the table.
    table_name: BigQuery table to stream the rows to.
    rows: list of (row_id, row) rows to sent to BQ.

  Returns:
    indexes of rows that failed to be sent.
  """
  # BigQuery API doc:
  # https://cloud.google.com/bigquery/docs/reference/rest/v2/tabledata/insertAll
  url = (
      'https://www.googleapis.com/bigquery/v2/projects/%s/datasets/%s/tables/'
      '%s/insertAll') % (app_identity.get_application_id(), dataset, table_name)
  payload = {
    'kind': 'bigquery#tableDataInsertAllRequest',
    # Do not fail entire request because of one bad row.
    # We handle invalid rows below.
    'skipInvalidRows': True,
    'ignoreUnknownValues': False,
    'rows': [
      {'insertId': row_id, 'json': bqh.message_to_dict(row)}
      for row_id, row in rows
    ],
  }
  res = net.json_request(
      url=url, method='POST', payload=payload, scopes=bqh.INSERT_ROWS_SCOPE,
      deadline=600)

  dropped = 0
  failed = []
  # Use this error message string to detect the error where we're pushing data
  # that is too old. This can occasionally happen as a cron job looks for old
  # entity and by the time it's sending them BigQuery doesn't accept them, just
  # skip these and log a warning.
  out_of_time = (
      'You can only stream to date range within 365 days in the past '
      'and 183 days in the future relative to the current date')
  # https://cloud.google.com/bigquery/docs/reference/rest/v2/tabledata/insertAll#response
  for line in res.get('insertErrors', []):
    i = line['index']
    err = line['errors'][0]
    if err['reason'] == 'invalid' and out_of_time in err['message']:
      # Silently drop it. The rationale is that if it is not skipped, the loop
      # will get stuck on it.
      dropped += 1
      continue
    if not failed:
      # Log the error for the first entry, useful to diagnose schema failure.
      logging.error('Failed to insert row %s: %r', i, err)
    failed.append(i)
  if dropped:
    logging.warning('%d old rows silently dropped', dropped)
  return failed


### Public API.


def cron_trigger_tasks(table_name, baseurl, task_name):
  """Triggers tasks to send rows to BigQuery via time based slicing.

  It triggers one per per 1 minute slice of time to process. It will process up
  to 2 minutes before now, and up to 18 months ago. It tries to go both ways,
  both keeping up in with new items, and backfilling.

  This function is expected to be called once per minute.

  It may trigger up to 120 tasks, 60 each ways. If BqState wasn't stored, it
  starts 7 days ago, to accelerate the processing each ways, so that 2 weeks of
  BigQuery rows will be filed within 24*7=168 minutes.

  The function limits itself to 15 seconds, so it may trigger less tasks,
  depending on how each utils.enqueue_task() call takes.

  This function stores in BqState the timestamps of last enqueued events.

  Arguments:
    table_name: BigQuery table name. Also used as the key id to use for the
        BqState entity.
    baseurl: url for the task queue, which the timestamp will be appended to.
    task_name: task name the URL represents.

  Returns:
    total number of task queues triggered.
  """
  OLDEST = datetime.timedelta(days=183)
  RECENT_OFFSET = datetime.timedelta(seconds=120)
  ITEMS = 60
  minute = datetime.timedelta(seconds=60)
  start = utils.utcnow()
  # Cut the seconds.
  start_rounded = datetime.datetime(*start.timetuple()[:5] + (0,))
  recent_cutoff = start_rounded - RECENT_OFFSET
  oldest_cutoff = start_rounded - OLDEST

  total = 0
  state = BqState.get_by_id(table_name)
  if not state or not state.oldest:
    state = BqState(
        id=table_name, ts=start, oldest=recent_cutoff, recent=recent_cutoff)
    state.put()

  # This cannot happen.
  assert state.oldest.second == 0, state.oldest
  assert state.recent.second == 0, state.recent

  # First trigger recent row(s). Up to 20 in one shot.
  for _ in xrange(ITEMS):
    if (state.recent >= recent_cutoff or
        (utils.utcnow() - start).total_seconds() > 15):
      break
    state.recent += minute
    t = state.recent.strftime(u'%Y-%m-%dT%H:%M')
    if not utils.enqueue_task(baseurl + t, task_name):
      return False
    state.ts = utils.utcnow()
    state.put()

  # Then trigger for backfill of old rows.
  for _ in xrange(ITEMS):
    if (state.oldest <= oldest_cutoff or
        (utils.utcnow() - start).total_seconds() > 15):
      break
    state.oldest -= minute
    t = state.oldest.strftime(u'%Y-%m-%dT%H:%M')
    if not utils.enqueue_task(baseurl + t, task_name):
      return False
    state.ts = utils.utcnow()
    state.put()
  return True


def send_to_bq(table_name, rows):
  """Sends rows to a BigQuery table.

  Iterates until all rows are sent.
  """
  failures = 0
  if rows:
    logging.info('Sending %d rows', len(rows))
    while rows:
      failed = _send_to_bq_raw('swarming', table_name, rows)
      if not failed:
        break
      failures += len(failed)
      logging.warning('Failed to insert %s rows', len(failed))
      rows = [rows[i] for i in failed]
  return failures
