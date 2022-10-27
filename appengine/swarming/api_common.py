# Copyright 2022 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

import endpoints
import message_conversion
from components import datastore_utils
from components import utils
from server import task_queues
from server import bot_management
from server import realms
from server import task_scheduler
from server import task_request
from server import task_pack

#TODO(jonahhooper) documentation


def _get_or_raise(key):
  """Returns an entity or raises an endpoints exception if it does not exist."""
  result = key.get()
  if not result:
    raise endpoints.NotFoundException('%s not found.' % key.id())
  return result


def get_bot(bot_id):
  # Check permission.
  # The caller needs to have global permission, or any permissions of the
  # pools that the bot belongs to.
  realms.check_bot_get_acl(bot_id)

  bot = bot_management.get_info_key(bot_id).get()
  deleted = False

  if not bot:
    # If there is not BotInfo, look if there are BotEvent child of this
    # entity. If this is the case, it means the bot was deleted but it's
    # useful to show information about it to the user even if the bot was
    # deleted.
    events = bot_management.get_events_query(bot_id).fetch(1)
    if events:
      bot = bot_management.BotInfo(
          key=bot_management.get_info_key(bot_id),
          dimensions_flat=task_queues.bot_dimensions_to_flat(
              events[0].dimensions),
          state=events[0].state,
          external_ip=events[0].external_ip,
          authenticated_as=events[0].authenticated_as,
          version=events[0].version,
          quarantined=events[0].quarantined,
          maintenance_msg=events[0].maintenance_msg,
          task_id=events[0].task_id,
          last_seen_ts=events[0].ts)
      # message_conversion.bot_info_to_rpc calls `is_dead` and this property
      # require `composite` to be calculated. The calculation is done in
      # _pre_put_hook usually. But the BotInfo shouldn't be stored in this case,
      # as it's already deleted.
      bot.composite = bot._calc_composite()
      deleted = True

  return (bot, deleted)


def delete_bot(bot_id):
  """Deletes the bot corresponding to a provided bot_id.

  At that point, the bot will not appears in the list of bots but it is still
  possible to get information about the bot with its bot id is known, as
  historical data is not deleted.

  It is meant to remove from the DB the presence of a bot that was retired,
  e.g. the VM was shut down already. Use 'terminate' instead of the bot is
  still alive."""
  # Check permission.
  # The caller needs to have global permission, or a permission in any pools
  # that the bot belongs to.
  realms.check_bot_delete_acl(bot_id)

  bot_info_key = bot_management.get_info_key(bot_id)
  _get_or_raise(bot_info_key)  # raises 404 if there is no such bot
  # It is important to note that the bot is not there anymore, so it is not
  # a member of any task queue.
  task_queues.cleanup_after_bot(bot_id)
  bot_info_key.delete()


def get_bot_events(bot_id, start, end, limit, cursor):
  realms.check_bot_get_acl(bot_id)
  q = bot_management.get_events_query(bot_id)
  if start:
    q = q.filter(bot_management.BotEvent.ts >= start)
  if end:
    q = q.filter(bot_management.BotEvent.ts < end)
  items, cursor = datastore_utils.fetch_page(q, limit, cursor)
  return items, cursor


def terminate_bot(bot_id):
  # Check permission.
  # The caller needs to have global permission, or a permission in any pools
  # that the bot belongs to.
  realms.check_bot_terminate_acl(bot_id)

  bot_key = bot_management.get_info_key(bot_id)
  _get_or_raise(bot_key)  # raises 404 if there is no such bot
  try:
    # Craft a special priority 0 task to tell the bot to shutdown.
    request = task_request.create_termination_task(bot_id,
                                                   wait_for_capacity=True)
  except (datastore_errors.BadValueError, TypeError, ValueError) as e:
    raise endpoints.BadRequestException(e.message)

  result_summary = task_scheduler.schedule_request(request,
                                                   enable_resultdb=False)
  return task_pack.pack_result_summary_key(result_summary.key)
