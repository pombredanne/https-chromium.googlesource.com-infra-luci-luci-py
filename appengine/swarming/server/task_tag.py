# Copyright 2019 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Known Task request tags.

TaskRequest.tags contains a list of `label:value` tags. This module is about
creating the search space for these, so the user can navigate then search via
tags.

Each label is an entity group for scalability. Entities are append-only for
performance.

Graph of the schema:

    +----Root----+
    |TaskTagLabel|
    |id=<name>   |
    +------------+
             ^
             |
          +--+-------------+--------...-------+
          |                |                  |
    +------------+  +------------+     +------------+
    |TaskTagValue|  |TaskTagValue|     |TaskTagValue|
    |id=<value>  |  |id=<value>  | ... |id=<value>  |
    +------------+  +------------+     +------------+
"""

from google.appengine.ext import ndb

### Private stuff.


def _label_key(label):
  """Returns the ndb.Key for a TaskTagLabel."""
  if not label:
    raise ValueError('Empty label is not valid')
  return ndb.Key(TaskTagLabel, label)


def _value_key(label_key, value):
  """Returns the ndb.Key for a TaskTagValue."""
  if not value:
    raise ValueError('Empty value is not valid')
  return ndb.Key(TaskTagValue, value, parent=label_key)


### Models.


class TaskTagLabel(ndb.Model):
  """A task tag label.

  Key id is the tag label. It must be at most 500 utf-8 encoded bytes.
  It's a root entity.
  """


class TaskTagValue(ndb.Model):
  """A valid value for a tag label.

  Key id is the tag value. It must be at most 500 utf-8 encoded bytes.
  Parent is a TaskTagLabel.
  """


### Public API.


def yield_labels():
  """Yields all the valid label names."""
  q = TaskTagLabel.query().order(TaskTagLabel.key)
  return (k.string_id() for k in q.iter(keys_only=True))


def yield_label_values(label):
  """Yields all the valid label values."""
  q = TaskTagValue.query(ancestor=_label_key(label)).order(TaskTagValue.key)
  return (k.string_id() for k in q.iter(keys_only=True))


@ndb.tasklet
def add_label_value(label, value):
  """Adds a new tag to the known tags DB."""
  assert not ndb.in_transaction()

  label_key = _label_key(label)
  value_key = _value_key(label_key, value)

  # Only look in memcache for entity presence, do not touch the DB. The reason
  # is that by definition, when an entity is not present it will be a cache-miss
  # and a full DB lookup. The worst case scenario if the entity exists in the DB
  # but is not in memcache is an unnecessary PUT and the hot case is no DB
  # operation.
  label_future = label_key.get_async(use_datastore=False)
  value_future = value_key.get_async(use_datastore=False)
  put_futures = []
  label_entity = yield label_future

  # The put_async() will add back the entity to memcache.
  if not label_entity:
    put_futures.append(TaskTagLabel(key=label_key).put_async())
  value_entity = yield value_future
  if not value_entity:
    put_futures.append(TaskTagValue(key=value_key).put_async())
  for future in put_futures:
    yield future
