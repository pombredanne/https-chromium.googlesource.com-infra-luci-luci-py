# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Helper functions for interacting with an external scheduler."""

import logging

from components.prpc import client

from proto import plugin_pb2
from proto import plugin_prpc_pb2

from server import pools_config
from server import task_queues


def _get_client(address):
  """Get a prpc client instance for given address."""
  return client.Client(
      address, plugin_prpc_pb2.ExternalSchedulerServiceDescription,
      # TODO(akeshet): Don't use insecure=True, this is just
      # for local testing.
      insecure=True)


def _bot_pool_cfg(bot_dimensions):
  """Determine a bot's pool_cfg, if it exists.

  Arguments:
  - bot_dimensions: The dimensions of the bot as a dictionary in
          {string key: list of string values} format.

  Returns:
    PoolConfig for the bot if it exists, or None otherwise.
  """
  pools = bot_dimensions.get(u'pool')
  if not pools:
    return None
  if len(pools) == 1:
    return pools_config.get_pool_config(pools[0])
  else:
    logging.warning('Bot with dimensions %s was found to be in multiple '
                    'pools. Unable to determine pool config.',
                    bot_dimensions)
    
  return None


def _config_for_dimensions(pool_cfg, dimensions_flat):
  """Determine an external scheduler for pool config and dimension set."""
  if not pool_cfg or not pool_cfg.external_schedulers:
    return None
  for e in pool_cfg.external_schedulers:
    if e.enabled and e.dimensions.issubset(dimensions_flat):
      return e
  return None


def config_for_bot(bot_dimensions):
  """Determine external scheduler to use for bot, if appropriate.

  Arguments:
  - bot_dimensions: The dimensions of the bot as a dictionary in
          {string key: list of string values} format.

  Returns:
    pool_config.ExternalSchedulerConfig for external scheduler to use for
    this bot, if it exists, or None otherwise.
  """
  pool_cfg = _bot_pool_cfg(bot_dimensions)
  bot_dimensions_flat = set(task_queues.dimensions_to_flat(bot_dimensions))
  return _config_for_dimensions(pool_cfg, bot_dimensions_flat)


def config_for_task(request):
  """Determine external scheduler to use for task, if appropriate.

  Arguments:
    request: a task_request.TaskRequest instance.
  
  Returns:
    pool_config.ExternalSchedulerConfig for external scheduler to use for
    this bot, if it exists, or None otherwise.
  """
  s0 = request.task_slice(0)
  pool = s0.properties.pool
  pool_cfg = pools_config.get_pool_config(pool)
  if not pool_cfg or not pool_cfg.external_schedulers:
    return None
  
  # Determine the dimension intersection across all task slices.
  common_dimensions = set(
      task_queues.dimensions_to_flat(s0.properties.dimensions))
  for i in range(1, request.num_task_slices):
    s = request.task_slice(i)
    common_dimensions.intersection_update(
        task_queues.dimensions_to_flat(s.properties.dimensions))

  return _config_for_dimensions(pool_cfg, common_dimensions)


def assign_task(es_cfg, bot_dimensions):
  """Calls external scheduler for a single idle bot with given dimensions.

  Arguments:
    es_cfg: pool_config.ExternalSchedulerConfig instance.
    bot_dimensions: dimensions {string key: list of string values}
  
  Returns:
    Task id string, or None.
  """
  bot_id = bot_dimensions[u'id'][0]
  logging.debug('Using external scheduler address: %s id: %s for bot %s',
                es_cfg.address, es_cfg.id, bot_id)

  idle_bot = plugin_pb2.IdleBot()
  idle_bot.bot_id = bot_id
  idle_bot.dimensions.extend(task_queues.dimensions_to_flat(bot_dimensions))

  req = plugin_pb2.AssignTasksRequest()
  req.scheduler_id = es_cfg.id
  req.idle_bots.extend([idle_bot])
  req.time.GetCurrentTime()

  c = _get_client(es_cfg.address)

  # TODO(akeshet): Catch or handle errors appropriately.
  resp = c.AssignTasks(req)

  if not resp or not resp.assignments:
    return None
  
  assert len(resp.assignments) == 1
  assert resp.assignments[0].bot_id == bot_id

  return resp.assignments[0].task_id

# TODO(akeshet): Add a blocking and non-blocking variant of this.
def notify_request(es_cfg, request, result_summary):
  """Calls external scheduler to notify it of a task state.

  Arguments:
    request: task_request.TaskRequest
    result_summary: task_result.TaskResultSummary
  """
  c = _get_client(es_cfg.address)

  item = plugin_pb2.NotifyTasksItem()
  # TODO(akeshet): This time should possibly come from the read time from
  # datastore, rather than the local server clock.
  item.time.GetCurrentTime()
  # TODO(akeshet/maruel): Is task_id what we want, or do we want the task's
  # key?
  item.task.id = request.task_id
  item.task.tags.extend(request.tags)
  for i in range(request.num_task_slices):
    s = request.task_slice(i)
    flat_dimensions = task_queues.dimensions_to_flat(s.properties.dimensions)
    s_pb = plugin_pb2.SliceSpec()
    s_pb.dimensions.extend(flat_dimensions)
    item.task.slices.extend([s_pb])

  item.task.state = result_summary.state

  # TODO(akeshet): Set item.bot_id appropriately, based on if the task
  # is currently on a bot.

  # TODO(akeshet): set enqueuet_time on item correctly.
  
  req = plugin_pb2.NotifyTasksRequest()
  req.notifications.extend([item])
  req.scheduler_id = es_cfg.id

  c = _get_client(es_cfg.address)
  resp = c.NotifyTasks(req)
  