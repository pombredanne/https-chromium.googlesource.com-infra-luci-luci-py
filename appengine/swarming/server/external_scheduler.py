# Copyright 2018 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Helper functions for interacting with an external scheduler."""


from server import pools_config
from server import task_queues


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
