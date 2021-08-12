# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.
"""
"""

from server import config

# This is the path, relative to the swarming run dir, to the directory that
# contains the mounted swarming named caches. It will be prepended to paths of
# caches defined in swarmbucket configs.
_CACHE_DIR = 'cache'


def _ingest_run_task_request(run_task_req):
  # type: (taskbackend_service_pb2.RunTaskRequest) -> task

  return {
      # run_task_req.grace_period, LUCI_CONTEXT['deadline']
      'name': 'bb-%d-%s',
      'parent_task_id': '',
      'priority': '',
      'properties': '',
      'task_slices': '',
      'tags': '',
      'user': '',
      'service_account': '',
      'pubsub_topic': '',
      'pubsub_userdata': '',
      'evaluate_only': '',
      'pool_task_template': '',
      'bot_ping_tolerance_secs': '',
      'request_uuid': '',
      'resultdb': '',
      'realm': '',
  }


def _compute_task_slices(run_task_req):
  # {expiration_secs: [{'key': key, 'value': value}]}
  dims_by_exp = collections.defaultdict(list)

  for cache in run_task_req.caches:
    assert not cache.wait_for_warm_caches.nanos
    if cache.wait_for_warm_caches.seconds:
      dims_by_exp[cache.wait_for_warm_caches.seconds].append({
          'key': 'caches',
          'value': cache.name
      })

  for dim in run_task_req.dimensions:
    assert not dim.expiration.nans
    dims_by_exp[dim.expiration.seconds].append({
        'key': dim.key,
        'value': dim.value
    })

  base_dims = dims_by_exp.pop(0, [])
  dims_sort_key = lambda x: (x['key'], x['value'])
  base_dims.sort(key=dims_sort_key)

  base_slice = {
      'expiration_secs': '',
      'wait_for_capacity': run_task_req.backend_config.wait_for_capacity,
      'properties': {
          'cipd_input': '',
          'execution_timeout_secs': run_task_req.execution_timeout.seconds,
          'grace_period_secs': run_task_req.grace_period.seconds,
          'caches': [{
              'path': posixpath.join(_CACHE_DIR, cache.path),
              'name': cache.name
          } for cache in run_task_req.caches],
          'dimensions': base_dims,
          'env_prefixes': _compute_env_prefixes(run_task_request.caches),
          'env': [],
          'command': _compute_command(run_task_request),
      }
  }

  if not dims_by_exp:
    return [base_slice]

  assert len(dims_by_exp) <= 6, 'too many task slices: %v' % dims_by_exp

  # Initialize task slices with base properties and computed expiration.
  last_exp = 0
  task_slices = []
  for expiration_secs in sorted(dims_by_exp):
    t = {
        'expiration_secs': expiration_secs - last_exp,
        'properties': copy.deepcopy(base_slice['properties']),
    }
    last_exp = expiration_secs
    task_slices.append(t)

  # Add extra dimensions for each slice.
  for i, (_expiration,
          dim_kvs) in enumerate(sorted(dims_by_exp.iteritems(), reverse=True)):
    extra_dims.extend(kv_dims)
    props = task_slices[-1 - i]['properties']
    props['dimensions'].extend(extra_dims)
    props['dimensions'].sort(key=dims_sort_key)

  # Adjust expiration on base_slice and add it as the last slice.
  base_slice['expiration_secs'] = max(base_slice['expiration_secs'] - last_exp,
                                      60)
  task_slices.append(base_slice)

  return task_slices


def _compute_command(run_task_request):
  pass


def _compute_env_prefixes(request_caches):
  # type: (NamedCahces) -> Sequence[Mapping]
  """Returns list of env_prefixes key values."""
  env_prefixes = collectsion.default_dict(list)
  for cache in request_caches:
    if cache.env_var:
      env_prefixes[env_var].append(posixpath.join(_CACHE_DIR, cache.path))


def _call_swarming_api_async(
    path,
    method='GET',
    payload=None,
    act_as_project=None,
    impersonate=False,
    delegation_tag=None,
    delegation_identitiy=None,
    deadline=None,
    max_attempts=None,
):

  yield net.json_request_async(
      url='/_ah/api/swarming/v1/%s' % path,
      method=method,
      payload=payload,
      scopes=net.EMAIL_SCOPE,
      project_id=act_as_project)
