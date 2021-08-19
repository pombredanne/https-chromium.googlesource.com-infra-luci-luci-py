# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""Functions that convert internal to/from Backend API's protoc objects."""

import collections
import copy
import posixpath

from components import utils
from server import task_request

# This is the path, relative to the swarming run dir, to the directory that
# contains the mounted swarming named caches. It will be prepended to paths of
# caches defined in swarmbucket configs.
_CACHE_DIR = 'cache'

# TODO(crbug/1236848): Replace 'assert's with raised exceptions.


def _compute_task_request(run_task_req):
  # type: (backend_pb2.RunTaskRequest) -> task_request.TaskRequest

  # Notes: resultdb is handled by bbagent
  slices = _compute_task_slices(run_task_req)
  task_request.TaskRequest(
      created_ts=utils.utcnow(),
      task_slices=slices,
      expiration_ts=slices[-1].expiration_secs,
      realm=run_task_req.realm,
      name='bb-%d-%s' % (run_task_req.build_id, 'TODO:builder_id?'),
      manual_tags=run_task_req.backend_config.fields['tags'],
      priority=run_task_req.backend_config.fields['priority'],
      pubsub_topic=run_task_req.backend_config.fields['pubsub_topic'],
      pubsub_userdata=run_task_req.backend_config.fields['pubsub_userdata'],
      pubsub_auth_token=run_task_req.backend_config.fields['pubsub_auth_token'],
      bot_ping_tolerance_secs=run_task_req.backend_config
      .fields['bot_ping_tolerance'],
      service_account=run_task_req.backend_config.fields['service_account'],
      parent_task_id=run_task_req.backend_config.fields['parent_run_id'],
      user=run_task_req.backend_config.fields['user'])


def _compute_task_slices(run_task_req):
  # type: (backend_pb2.RunTaskRequest)
  #   -> Sequence[task_request.TaskSlice]

  # {expiration_secs: {'key1': [value1, ...], 'key2': [value1, ...]}
  dims_by_exp = collections.defaultdict(lambda: collections.defaultdict(list))

  for cache in run_task_req.caches:
    assert not cache.wait_for_warm_cache.nanos
    if cache.wait_for_warm_cache.seconds:
      dims_by_exp[cache.wait_for_warm_cache.seconds]['caches'].append(
          cache.name)

  for dim in run_task_req.dimensions:
    assert not dim.expiration.nanos
    dims_by_exp[dim.expiration.seconds][dim.key].append(dim.value)

  base_dims = dims_by_exp.pop(0, {})
  for key, values in base_dims.iteritems():
    values.sort()

  # TODO(crbug/1236848): Add remaining TaskSlice fields.
  # TODO(crbug/1236848): Validate backend_config.fields have the expected
  # value types.
  # NOTES:
  #  - secret_bytes added to command args
  #  - env and env_prefixes handled by bbagent
  #  - cache env_prefixes not set here, but passed in `-cache-base` in command args
  #    instead
  base_slice = task_request.TaskSlice(
      # In bb-on-swarming, `wait_for_capacity` is only used for the last slice
      # (base_slice) to give named caches some time to show up.
      wait_for_capacity=bool(
          run_task_req.backend_config.fields['wait_for_capacity']),
      expiration_secs=int(run_task_req.start_deadline.seconds -
                          utils.time_time()),
      properties=task_request.TaskProperties(
          caches=[
              task_request.CacheEntry(
                  path=posixpath.join(_CACHE_DIR, cache.path), name=cache.name)
              for cache in run_task_req.caches
          ],
          dimensions_data=base_dims,
          execution_timeout_secs=run_task_req.execution_timeout.seconds,
          grace_period_secs=run_task_req.grace_period.seconds,
          containment=_ingest_containment(
              run_task_req.backend_config.fields['containment']),
          command=_compute_command(run_task_req),
          has_secret_bytes=False,  # ?
      ),
  )

  if not dims_by_exp:
    return [base_slice]

  # Initialize task slices with base properties and computed expiration.
  last_exp = 0
  task_slices = []
  for expiration_secs in sorted(dims_by_exp):
    task_slices.append(
        task_request.TaskSlice(
            expiration_secs=expiration_secs - last_exp,
            properties=copy.deepcopy(base_slice.properties),
        ))
    last_exp = expiration_secs

  # Add extra dimensions for all slices.
  extra_dims = collections.defaultdict(list)
  for i, (_exp,
          dims) in enumerate(sorted(dims_by_exp.iteritems(), reverse=True)):
    for key, values in dims.iteritems():
      extra_dims[key].extend(values)

    props = task_slices[-1 - i].properties
    for key, values in extra_dims.iteritems():
      props.dimensions.setdefault(key, []).extend(values)
      props.dimensions[key].sort()

  # Adjust expiration on base_slice and add it as the last slice.
  base_slice.expiration_secs = max(base_slice.expiration_secs - last_exp, 60)
  task_slices.append(base_slice)

  return task_slices


def _compute_command(run_task_req):
  args = ['<run_task_req.agent>'] + run_task_req.agent_args[:]
  # args.append('-secrets=<run_task_req.secrets>')
  # args.append('-task=id={SWARMING_TASK_ID}')
  # args.append('-cache-base=%s' % _CACHE_DIR)
  return args


def _ingest_containment(containment):
  pass
