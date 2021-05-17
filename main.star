#!/usr/bin/env lucicfg
# Copyright 2021 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Config to generate Tricium config for luci-py analyzer."""

# This file defined here only to generate tricium-prod.cfg for the luci-py
# analyzer. This should be deleted after Tricium is merged into CV.
# See crbug.com/1185933.

lucicfg.check_version("1.24.2", "Please update depot_tools")

luci.project(
    name = "luci-py",
    buildbucket = "cr-buildbucket.appspot.com",
    logdog = "luci-logdog.appspot.com",
    milo = "luci-milo.appspot.com",
    notify = "luci-notify.appspot.com",
    scheduler = "luci-scheduler.appspot.com",
    swarming = "chromium-swarm.appspot.com",
    tricium = "tricium-prod.appspot.com",
    acls = [
        # Publicly readable.
        acl.entry(
            roles = [
                acl.BUILDBUCKET_READER,
                acl.LOGDOG_READER,
                acl.PROJECT_CONFIGS_READER,
                acl.SCHEDULER_READER,
            ],
            groups = "all",
        ),
        # Allow committers to use CQ and to force-trigger and stop CI builds.
        acl.entry(
            roles = [
                acl.SCHEDULER_OWNER,
                acl.CQ_COMMITTER,
            ],
            groups = "project-infra-committers",
        ),
        # Ability to launch CQ dry runs.
        acl.entry(
            roles = acl.CQ_DRY_RUNNER,
            groups = "project-infra-tryjob-access",
        ),
        # Group with bots that have write access to the Logdog prefix.
        acl.entry(
            roles = acl.LOGDOG_WRITER,
            groups = "luci-logdog-chromium-writers",
        ),
    ],
)

# Tell lucicfg what files it is allowed to touch.
lucicfg.config(
    config_dir = "generated",
    tracked_files = [
        "tricium-prod.cfg",
    ],
    fail_on_warnings = True,
    lint_checks = ["default"],
)

luci.bucket(
    name = "try",
    acls = [
        acl.entry(
            roles = acl.BUILDBUCKET_TRIGGERER,
            # Allow Tricium to trigger analyzer tryjobs.
            users = [
                "tricium-prod@appspot.gserviceaccount.com",
            ],
            groups = [
                "project-infra-tryjob-access",
                "service-account-cq",
            ],
        ),
    ],
)

luci.cq_group(
    name = "luci-py",
    watch = cq.refset(
        repo = "https://chromium.googlesource.com/infra/luci/luci-py",
        refs = ["refs/heads/main", "refs/heads/master"]
    ),
    tree_status_host = None,
    retry_config = cq.RETRY_NONE,
)

# This Tricium analyzer is defined here in project separate from "infra" until
# Tricium is merged into CV. See crbug.com/1185933.
luci.cq_tryjob_verifier(
    builder = 'infra:try/luci-py-analysis',
    cq_group = "luci-py",
    owner_whitelist = ["project-infra-tryjob-access"],
    mode_allowlist = [cq.MODE_ANALYZER_RUN],
)
