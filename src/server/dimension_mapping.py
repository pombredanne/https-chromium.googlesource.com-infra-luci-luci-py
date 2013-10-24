#!/usr/bin/python2.7
#
# Copyright 2013 Google Inc. All Rights Reserved.

"""Implements the DimensionMapping class.

This class assists in storing what runner dimensions have been seen (for use in
queries) as well as converted a dimension hash back to the string that generated
it.
"""


import datetime
import logging

from google.appengine.ext import ndb


# The number of days to keep a dimension around before deleting it (assuming
# if isn't seen again).
DIMENSION_MAPPING_DAYS_TO_LIVE = 30


class DimensionMapping(ndb.Model):
  """This class uses ndb so that app engine will automatically cache it.

  The key of this class is the hash of the dimension string.
  """
  # The raw config string.
  dimensions = ndb.StringProperty()

  # Don't use auto_now_add so we control exactly what the time is set to
  # (since we later need to compare this value, so we need to know if it was
  # made with .now() or .utcnow()).
  last_seen = ndb.DateProperty()

  def _pre_put_hook(self):  # pylint: disable=g-bad-name
    """Stores the time this dimension was last seen."""
    self.last_seen = datetime.datetime.utcnow().date()


def DeleteOldDimensionMapping():
  """Deletes mapping that haven't been seen in DIMENSION_MAPPING_DAYS_TO_LIVE.

  Returns:
    The list of Futures for all the async delete calls.
  """
  logging.debug('DeleteOldDimensions starting')
  old_cutoff = (datetime.datetime.utcnow().date() -
                datetime.timedelta(days=DIMENSION_MAPPING_DAYS_TO_LIVE))

  futures = ndb.delete_multi_async(
      DimensionMapping.query(DimensionMapping.last_seen < old_cutoff,
                             default_options=ndb.QueryOptions(keys_only=True)))

  logging.debug('DeleteOldDimension done')
  return futures
