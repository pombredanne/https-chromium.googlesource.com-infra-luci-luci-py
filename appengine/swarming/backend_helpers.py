# Copyright 2021 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""
"""



def _ingest_run_task_request(run_task_req):
    # type: (taskbackend_service_pb2.RunTaskRequest) -> task

    return {
        # run_task_req.grace_period, LUCI_CONTEXT['deadline']
        'name': 'bb-%d-%s' ,
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

    base_slice = {
        'expiration_secs': run_task_req.execution_timeout.seconds,
        'wait_for_capacity': run_task_req.backend_config.wait_for_capacity,
        'properties': {

            }
        }


def _call_swarming_api_async(path, method='GET',
                             payload=None, act_as_project=None,
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
