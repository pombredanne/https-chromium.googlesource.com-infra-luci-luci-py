// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { $, $$ } from "common-sk/modules/dom";
import { errorMessage } from "elements-sk/errorMessage";
import { html } from "lit-html";
import { ifDefined } from "lit-html/directives/if-defined";
import { jsonOrThrow } from "common-sk/modules/jsonOrThrow";
import { stateReflector } from "common-sk/modules/stateReflector";

import "elements-sk/checkbox-sk";
import "elements-sk/icon/add-circle-outline-icon-sk";
import "elements-sk/icon/remove-circle-outline-icon-sk";
import "elements-sk/styles/buttons";
import "../dialog-pop-over";
import "../stacked-time-chart";
import "../swarming-app";

import * as human from "common-sk/modules/human";
import * as query from "common-sk/modules/query";

import { applyAlias } from "../alias";
import {
  casLink,
  canRetry,
  cipdLink,
  durationChart,
  hasRichOutput,
  humanState,
  firstDimension,
  parseRequest,
  parseResult,
  richLogsLink,
  sliceSchedulingDeadline,
  stateClass,
  taskCost,
  taskSchedulingDeadline,
  taskInfoClass,
  wasDeduped,
  wasPickedUp,
} from "./task-page-helpers";
import {
  botListLink,
  botPageLink,
  humanDuration,
  parseDuration,
  taskListLink,
  taskPageLink,
  b64toUtf8,
} from "../util";
import { TasksService } from "../services/tasks";

import SwarmingAppBoilerplate from "../SwarmingAppBoilerplate";

/**
 * @module swarming-ui/modules/task-page
 * @description <h2><code>task-page<code></h2>
 *
 * <p>
 *   Task Page shows the request, results, stats, and standard output of a task.
 * </p>
 *
 * <p>This is a top-level element.</p>
 *
 * @attr testing_offline - If true, the real login flow won't be used.
 *    Instead, dummy data will be used. Ideal for local testing.
 */

const extractPrimaryHostname = (botId) => {
  if (!botId) {
    return botId;
  }
  const parts = botId.split("--");
  if (parts.length == 2) {
    return parts[0];
  }
  if (parts.length > 2) {
    throw Error("Unable to parse composed bot_id: " + botId);
  }
  return botId;
};

const cloudLoggingURL = (project, query, start, end) => {
  let url = `https://console.cloud.google.com/logs/query`;
  url += `;query=${encodeURIComponent(query)}`;
  if (start) {
    url += `;cursorTimestamp=${start.toISOString()}`;
    if (end) {
      const range = [start, end].map((e) => e.toISOString()).join("/");
      url += `;timeRange=${encodeURIComponent(range)}`;
    }
  }
  url += `?project=${project}`;
  return url;
};

const serverLogBaseQuery =
  `resource.type="gae_app"\n` +
  // limit logs that we care
  [
    `protoPayload.resource:"/internal/"`, // cron, task queue
    `protoPayload.resource:"/swarming/api/v1/bot/"`, // requests from bots
    `protoPayload.method!="GET"`, // POST, PUT, DELETE etc
  ].join(" OR ") +
  "\n";

const serverLogTimeRange = (request, result) => {
  if (!request.createdTs) return [null, null];
  const timeStart = new Date(request.createdTs.getTime() - 60 * 1000);
  const tsEnd = result.completedTs || result.abandonedTs;
  const timeEnd = tsEnd ? new Date(tsEnd.getTime() + 60 * 1000) : new Date();
  return [timeStart, timeEnd];
};

const serverTaskLogsURL = (project, taskId, request, result) => {
  // cut the last character that represents try number
  const query = serverLogBaseQuery + taskId.slice(0, -1);
  const [timeStart, timeEnd] = serverLogTimeRange(request, result);
  return cloudLoggingURL(project, query, timeStart, timeEnd);
};

const serverBotLogsURL = (project, request, result) => {
  const query = serverLogBaseQuery + result.botId;
  const [timeStart, timeEnd] = serverLogTimeRange(request, result);
  return cloudLoggingURL(project, query, timeStart, timeEnd);
};

const botLogsURL = (botProjectID, botZone, request, result) => {
  // limit logs that we care
  const hostName = extractPrimaryHostname(result.botId);
  const query = `labels."compute.googleapis.com/resource_name":"${hostName}"`;
  let timeStart;
  let timeEnd;
  if (result.startedTs) {
    timeStart = new Date(result.startedTs.getTime() - 60 * 1000);
    const tsEnd = result.completedTs || result.abandonedTs;
    timeEnd = tsEnd ? new Date(tsEnd.getTime() + 60 * 1000) : new Date();
  }
  return cloudLoggingURL(botProjectID, query, timeStart, timeEnd);
};

const idAndButtons = (ele) => {
  if (!ele._taskId || ele._notFound) {
    return html`
<div class=id_buttons>
  <input id=id_input placeholder="Task ID" @change=${ele._updateID}></input>
  <span class=message>Enter a Task ID to get started.</span>
</div>`;
  }
  return html`
<div class=id_buttons>
  <input id=id_input placeholder="Task ID" @change=${ele._updateID}></input>
  <button title="Retry the task"
          @click=${ele._promptRetry} class=retry
          ?hidden=${!canRetry(ele._request)}>retry</button>
  <button title="Re-queue the task, but don't run it automatically"
          @click=${ele._promptDebug} class=debug>debug</button>
  <button title="Cancel a pending task, so it does not start"
          ?hidden=${ele._result.state !== "PENDING"}
          ?disabled=${!ele.permissions.cancel_task}
          @click=${ele._promptCancel} class=cancel>cancel</button>
  <button title="Kill a running task, so it stops as soon as possible"
          ?hidden=${ele._result.state !== "RUNNING"}
          ?disabled=${!ele.permissions.cancel_task}
          @click=${ele._promptCancel} class=kill>kill</button>
</div>`;
};

const slicePicker = (ele) => {
  if (!ele._taskId || ele._notFound) {
    return "";
  }
  if (!(ele._request.taskSlices && ele._request.taskSlices.length > 1)) {
    return "";
  }

  return html` <div class="slice-picker">
    ${ele._request.taskSlices.map((_, idx) => sliceTab(ele, idx))}
  </div>`;
};

const sliceTab = (ele, idx) => html`
  <div
    class="tab"
    ?selected=${ele._currentSliceIdx === idx}
    @click=${() => ele._setSlice(idx)}
  >
    Task Slice ${idx + 1}
  </div>
`;

const taskInfoTable = (ele, request, result, currentSlice) => {
  if (!ele._taskId || ele._notFound) {
    return "";
  }
  if (!currentSlice.properties) {
    currentSlice.properties = {};
  }
  return html`
    <table class="task-info request-info ${taskInfoClass(ele, result)}">
      <tbody>
        <tr>
          <td>Name</td>
          <td>${request.name}</td>
        </tr>
        ${stateLoadBlock(ele, request, result)}
        ${requestBlock(request, result, currentSlice)}
        ${dimensionBlock(currentSlice.properties.dimensions || [])}
        ${casBlock(
          "CAS Inputs",
          ele._app._server_details.cas_viewer_server,
          currentSlice.properties.casInputRoot || {}
        )}
        <tr ?hidden=${!result.resultdbInfo}>
          <td>ResultDB</td>
          <td>Enabled</td>
        </tr>
        ${arrayInTable(
          currentSlice.properties.outputs,
          "Expected outputs",
          (output) => output
        )}
        ${commitBlock(request.tagMap)}
        <tr class="details">
          <td>More Details</td>
          <td>
            <button @click=${ele._toggleDetails} ?hidden=${ele._showDetails}>
              <add-circle-outline-icon-sk></add-circle-outline-icon-sk>
            </button>
            <button @click=${ele._toggleDetails} ?hidden=${!ele._showDetails}>
              <remove-circle-outline-icon-sk></remove-circle-outline-icon-sk>
            </button>
          </td>
        </tr>
      </tbody>
      <tbody ?hidden=${!ele._showDetails}>
        ${executionBlock(
          currentSlice.properties,
          currentSlice.properties.env || [],
          currentSlice.properties.envPrefixes || []
        )}
        ${arrayInTable(request.tags, "Tags", (tag) => tag)}
        <tr>
          <td>Execution timeout</td>
          <td>
            ${humanDuration(currentSlice.properties.executionTimeoutSecs)}
          </td>
        </tr>
        <tr>
          <td>I/O timeout</td>
          <td>${humanDuration(currentSlice.properties.ioTimeoutSecs)}</td>
        </tr>
        <tr>
          <td>Grace period</td>
          <td>${humanDuration(currentSlice.properties.gracePeriodSecs)}</td>
        </tr>

        ${cipdBlock(currentSlice.properties.cipdInput, result)}
        ${arrayInTable(
          currentSlice.properties.caches,
          "Named Caches",
          (cache) => cache.name + ":" + cache.path
        )}
      </tbody>
    </table>
  `;
};

const stateLoadBlock = (ele, request, result) => html`
  <tr>
    <td>State</td>
    <td class=${stateClass(result)}>
      ${humanState(result, ele._currentSliceIdx)}
    </td>
  </tr>
  ${countBlocks(
    result,
    ele._capacityCounts[ele._currentSliceIdx],
    ele._pendingCounts[ele._currentSliceIdx],
    ele._runningCounts[ele._currentSliceIdx],
    ele._currentSlice.properties || {}
  )}
  <tr ?hidden=${!result.dedupedFrom} class="highlighted">
    <td><b>Deduped From</b></td>
    <td>
      <a href=${taskPageLink(result.dedupedFrom)} target="_blank">
        ${result.dedupedFrom}
      </a>
    </td>
  </tr>
  <tr ?hidden=${!result.dedupedFrom}>
    <td>Deduped On</td>
    <td title=${request.createdTs}>${request.human_createdTs}</td>
  </tr>
`;

const countBlocks = (
  result,
  capacityCount,
  pendingCount,
  runningCount,
  properties
) => html`
  <tr ?hidden=${!capacityCount}>
    <td class=${result.state === "PENDING" ? "bold" : ""}>
      ${result.state === "PENDING" ? "Why Pending?" : "Fleet Capacity"}
    </td>
    <td>
      ${count(capacityCount, "count")}
      <a href=${botListLink(properties.dimensions)}>bots</a>
      could possibly run this task (${count(capacityCount, "busy")} busy,
      ${count(capacityCount, "dead")} dead,
      ${count(capacityCount, "quarantined")} quarantined,
      ${count(capacityCount, "maintenance")} maintenance)
    </td>
  </tr>
  <tr ?hidden=${!pendingCount || !runningCount}>
    <td>Similar Load</td>
    <td>
      ${count(pendingCount)}
      <a
        href=${taskListLink(
          (properties.dimensions || []).concat({
            key: "state",
            value: "PENDING",
          })
        )}
      >
        similar pending tasks</a
      >, ${count(runningCount)}
      <a
        href=${taskListLink(
          (properties.dimensions || []).concat({
            key: "state",
            value: "RUNNING",
          })
        )}
      >
        similar running tasks</a
      >
    </td>
  </tr>
`;

const count = (obj, value) => {
  if (!obj || (value && obj[value] === undefined)) {
    return html`<span class="italic">&lt;counting&gt</span>`;
  }
  if (value) {
    return obj[value];
  }
  return obj;
};

const requestBlock = (request, result, currentSlice) => html`
  <tr>
    <td>Priority</td>
    <td>${request.priority}</td>
  </tr>
  <tr>
    <td>Wait for Capacity</td>
    <td>${!!currentSlice.waitForCapacity}</td>
  </tr>
  <tr>
    <td>Slice Scheduling Deadline</td>
    <td>${sliceSchedulingDeadline(currentSlice, request)}</td>
  </tr>
  <tr>
    <td>User</td>
    <td>${request.user || "--"}</td>
  </tr>
  <tr>
    <td>Authenticated</td>
    <td>${request.authenticated}</td>
  </tr>
  <tr ?hidden=${!request.serviceAccount}>
    <td>Service Account</td>
    <td>${request.serviceAccount}</td>
  </tr>
  <tr ?hidden=${!request.realm}>
    <td>Realm</td>
    <td>${request.realm}</td>
  </tr>
  <tr ?hidden=${!currentSlice.properties.secretBytes}>
    <td>Has Secret Bytes</td>
    <td
      title="The secret bytes are present on the machine, but not in the UI/API"
    >
      true
    </td>
  </tr>
  <tr ?hidden=${!request.parentTaskId}>
    <td>Parent Task</td>
    <td>
      <a href=${taskPageLink(request.parentTaskId)}>
        ${request.parentTaskId}
      </a>
    </td>
  </tr>
  <tr ?hidden=${!result}>
    <td>Child Tasks</td>
    <td>
      <a
        href=${taskListLink(
          [{ key: "parent_task_id-tag", value: result.runId }],
          [],
          result.startedTs,
          result.completedTs
        )}
      >
        Task List
      </a>
    </td>
  </tr>
`;

const dimensionBlock = (dimensions) => html`
  <tr>
    <td rowspan=${dimensions.length + 1}>
      Dimensions <br />
      <a
        title="The list of bots that matches the list of dimensions"
        href=${botListLink(dimensions)}
        >Bots</a
      >
      <a
        title="The list of tasks that matches the list of dimensions"
        href=${taskListLink(dimensions)}
        >Tasks</a
      >
    </td>
  </tr>
  ${dimensions.map(dimensionRow)}
`;

const dimensionRow = (dimension) => html`
  <tr>
    <td class="break-all">
      <b class="dim_key">${dimension.key}:</b>${applyAlias(
        dimension.value,
        dimension.key
      )}
    </td>
  </tr>
`;

const casBlock = (title, host, ref) => {
  if (!ref.digest) {
    return "";
  }
  return html` <tr>
    <td>${title}</td>
    <td>
      <a href=${casLink(host, ref)} target="_blank">
        ${ref.digest.hash}/${ref.digest.sizeBytes}
      </a>
    </td>
  </tr>`;
};

const missingCasBlock = (title, host, missingCas) => {
  if (!missingCas) {
    return "";
  }
  const casInputs = missingCas || [];
  return html` <tr>
    <td>${title}</td>
    <td class="exception">
      ${casInputs.map((input) => missingCasRowSet(host, input))}
    </td>
  </tr>`;
};

const missingCasRowSet = (host, input) => html`
<tr>
  <tr>
    <td>
      <b>Instance: </b>
      ${input.casInstance}
    </td>
  </tr>
  <tr>
    <td>
      <b>Digest: </b>
      <a href=${casLink(host, input)} target='_blank'>
        ${input.digest.hash}/${input.digest.sizeBytes}
      </a>
    </td>
  </tr>
</tr>
`;

const arrayInTable = (array, label, keyFn) => {
  if (!array || !array.length) {
    return html` <tr>
      <td>${label}</td>
      <td>--</td>
    </tr>`;
  }
  return html` <tr>
      <td rowspan=${array.length + 1}>${label}</td>
    </tr>
    ${array.map(arrayRow(keyFn))}`;
};

const arrayRow = (keyFn) => {
  return (key) => html`
    <tr>
      <td class="break-all">${keyFn(key)}</td>
    </tr>
  `;
};

const commitBlock = (tagMap) => {
  if (!tagMap || !tagMap.source_revision) {
    return "";
  }
  return html`
    <tr>
      <td>Associated Commit</td>
      <td>
        <a href=${tagMap.source_repo.replace("%s", tagMap.source_revision)}>
          ${tagMap.source_revision.substring(0, 12)}
        </a>
      </td>
    </tr>
  `;
};

const executionBlock = (properties, env, envPrefixes) => html`
  <tr>
    <td>Command</td>
    <td class="code break-all">
      ${(properties.command || []).join(" ") || "--"}
    </td>
  </tr>
  <tr>
    <td>Relative Cwd</td>
    <td class="code break-all">${properties.relativeCwd || "--"}</td>
  </tr>
  ${arrayInTable(env, "Environment Vars", (env) => env.key + "=" + env.value)}
  ${arrayInTable(
    envPrefixes,
    "Environment Prefixes",
    (prefix) => prefix.key + "=" + prefix.value.join(":")
  )}
  <tr>
    <td>Idempotent</td>
    <td>${!!properties.idempotent}</td>
  </tr>
`;

const missingCipdBlock = (title, missingCipd) => {
  if (!missingCipd) {
    return "";
  }

  const missingCipdPackages = missingCipd || [];
  return html`
    <tr>
      <td>${title}</td>
      <td class="exception">
        ${missingCipdPackages.map((pkg) => missingCipdRowSet(pkg))}
      </td>
    </tr>
  `;
};

const missingCipdRowSet = (cipd) => html`
  <tr>
    <td>
      <b>Path: </b>
      ${cipd.path}
    </td>
  </tr>
  <tr>
    <td>
      <b>Package: </b>
      ${cipd.packageName}
    </td>
  </tr>
  <tr>
    <td>
      <b>Version: </b>
      ${cipd.version}
    </td>
  </tr>
`;

const cipdBlock = (cipdInput, result) => {
  if (!cipdInput) {
    return html` <tr>
      <td>Uses CIPD</td>
      <td>false</td>
    </tr>`;
  }
  // TODO(jonahhooper) Remove hacky "deep copy" used here.
  // The cipdInput object gets some fields added in other parts of the UI.
  // pPRPC before https://chromium.googlesource.com/infra/luci/luci-py/+/442e2aee5c8eddc235e593fbfb54f8697351cb1d
  // rejected unknown fields.
  // Just to double make sure there are no backcompat issues with this change and any possible rollbacks of the above
  // mentioned change, keeping this hack for now.
  cipdInput = JSON.parse(JSON.stringify(cipdInput));
  const requestedPackages = cipdInput.packages || [];
  const actualPackages = (result.cipdPins && result.cipdPins.packages) || [];
  for (let i = 0; i < requestedPackages.length; i++) {
    const p = requestedPackages[i];
    p.requested = `${p.packageName}:${p.version}`;
    // This makes the key assumption that the actual cipd array is in the same order
    // as the requested one. Otherwise, there's no easy way to match them up, because
    // of the wildcards (e.g. requested is foo/${platform} and actual is foo/linux-amd64)
    if (actualPackages[i]) {
      p.actual = `${actualPackages[i].packageName}:${actualPackages[i].version}`;
    }
  }
  let packageName = "(available when task is run)";
  if (result.cipdPins && result.cipdPins.clientPackage) {
    packageName = result.cipdPins.clientPackage.packageName;
  }
  // We always need to at least double the number of packages because we
  // show the path and then the requested.  If the actual package info
  // is available, we triple the number of packages to account for that.
  let cipdRowspan = requestedPackages.length;
  if (actualPackages.length) {
    cipdRowspan *= 3;
  } else {
    cipdRowspan *= 2;
  }
  // Add one because rowSpan counts from 1.
  cipdRowspan += 1;
  return html`
    <tr>
      <td>CIPD server</td>
      <td>
        <a href=${cipdInput.server}>${cipdInput.server}</a>
      </td>
    </tr>
    <tr>
      <td>CIPD version</td>
      <td class="break-all">
        ${cipdInput.clientPackage && cipdInput.clientPackage.version}
      </td>
    </tr>
    <tr>
      <td>CIPD package name</td>
      <td>${packageName}</td>
    </tr>
    <tr>
      <td rowspan=${cipdRowspan}>CIPD packages</td>
    </tr>
    ${requestedPackages.map((pkg) =>
      cipdRowSet(pkg, cipdInput, !!actualPackages.length)
    )}
  `;
};

const cipdRowSet = (pkg, cipdInput, actualAvailable) => html`
  <tr>
    <td>${pkg.path}/</td>
  </tr>
  <tr>
    <td class="break-all">
      <span class="cipd-header">Requested: </span>${pkg.requested}
    </td>
  </tr>
  <tr ?hidden=${!actualAvailable}>
    <td class="break-all">
      <span class="cipd-header">Actual: </span>
      <a
        href=${cipdLink(pkg.actual, cipdInput.server)}
        target="_blank"
        rel="noopener"
      >
        ${pkg.actual}
      </a>
    </td>
  </tr>
`;

const taskTimingSection = (ele, request, result) => {
  if (!ele._taskId || ele._notFound || wasDeduped(result)) {
    // Don't show timing info when task was deduped because the info
    // in the result is from the original task, which can be confusing
    // when juxtaposed with the data from this task.
    return "";
  }
  const performanceStats = result.performanceStats || {};
  return html`
    <div class="title">Task Timing Information</div>
    <div class="horizontal layout wrap">
      <table class="task-info task-timing left">
        <tbody>
          <tr>
            <td>Created</td>
            <td title=${request.createdTs}>${request.human_createdTs}</td>
          </tr>
          <tr ?hidden=${!wasPickedUp(result)}>
            <td>Started</td>
            <td title=${result.startedTs}>${result.human_startedTs}</td>
          </tr>
          <tr>
            <td>Scheduling Deadline</td>
            <td>${taskSchedulingDeadline(request)}</td>
          </tr>
          <tr ?hidden=${!result.completedTs}>
            <td>Completed</td>
            <td title=${result.completedTs}>${result.human_completedTs}</td>
          </tr>
          <tr ?hidden=${!result.abandonedTs}>
            <td>Abandoned</td>
            <td title=${result.abandonedTs}>${result.human_abandonedTs}</td>
          </tr>
          <tr>
            <td>Last updated</td>
            <td title=${result.modifiedTs}>${result.human_modifiedTs}</td>
          </tr>
          <tr>
            <td>Pending Time</td>
            <td class="pending">${result.human_pending}</td>
          </tr>
          <tr>
            <td>Total Overhead</td>
            <td class="overhead">
              ${humanDuration(performanceStats.botOverhead)}
            </td>
          </tr>
          <tr>
            <td>Running Time</td>
            <td
              class="running"
              title="An asterisk indicates the task is still running and thus the time is dynamic."
            >
              ${result.human_duration}
            </td>
          </tr>
        </tbody>
      </table>
      <!-- Overheads calculated from task result is not accurate.
    It contains only the overheads for cipd package installation, task inputs download, task outputs upload.
    But there are other overheads that are not negligible, such as named cache install/uninstall, removing working dirs.
  <div class=right>
    <stacked-time-chart
      labels='["Pending", "Overhead", "Running", "Overhead"]'
      colors='["#E69F00", "#D55E00", "#0072B2", "#D55E00"]'
      .values=${durationChart(result)}>
    </stacked-time-chart>
  </div>
  -->
    </div>
  `;
};

const logsSection = (ele, request, result) => {
  if (!ele._taskId || ele._notFound) {
    return "";
  }
  let botLogsCloudProject = null;
  let botProjectID = null;
  let botZone = null;
  if (result && result.botDimensions) {
    for (const dim of result.botDimensions) {
      if (dim.key == "gcp") botProjectID = dim.value[0];
      if (dim.key == "zone") {
        botZone = dim.value.reduce((a, b) => (a.length > b.length ? a : b));
      }
    }
    // Use result.bot_logs_cloud_project to fetch logs when it's not null
    botLogsCloudProject = result.botLogsCloudProject;
    if (!!botLogsCloudProject) {
      botProjectID = botLogsCloudProject;
    }
  }
  const showBotLogsLink = !!botProjectID;
  return html`
    <div class="title">Logs Information</div>
    <div class="horizontal layout wrap">
      <table class="task-info left">
        <tbody>
          <tr>
            <td>Task related server Logs</td>
            <td>
              <a
                href=${serverTaskLogsURL(
                  ele._project_id,
                  ele._taskId,
                  request,
                  result
                )}
                target="_blank"
              >
                View on Cloud Console
              </a>
            </td>
          </tr>
          <tr>
            <td>Bot related server Logs</td>
            <td>
              <a
                href=${serverBotLogsURL(ele._project_id, request, result)}
                target="_blank"
                ?hidden=${!result.botId}
              >
                View on Cloud Console
              </a>
              <p ?hidden=${result.botId}>--</p>
            </td>
          </tr>
          <tr>
            <td>Bot Logs</td>
            <td>
              <a
                href=${botLogsURL(botProjectID, botZone, request, result)}
                target="_blank"
                ?hidden=${!showBotLogsLink}
              >
                View on Cloud Console
              </a>
              <p ?hidden=${showBotLogsLink}>--</p>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  `;
};

const taskExecutionSection = (ele, request, result, currentSlice) => {
  if (!ele._taskId || ele._notFound) {
    return "";
  }
  if (!result || !wasPickedUp(result)) {
    return html`
      <div class="title">Task Execution</div>
      <div class="task-execution">
        This space left blank until a bot is assigned to the task.
      </div>
    `;
  }
  if (wasDeduped(result)) {
    // Don't show timing info when task was deduped because the info
    // in the result is from the original task, which can be confusing
    // when juxtaposed with the data from this task.
    return html` <div class="title">Task was Deduplicated</div>

      <p class="deduplicated">
        This task was deduplicated from task
        <a href=${taskPageLink(result.dedupedFrom)}>${result.dedupedFrom}</a>.
        For more information on deduplication, see
        <a
          href="https://chromium.googlesource.com/infra/luci/luci-py/+/master/appengine/swarming/doc/Detailed-Design.md#task-deduplication"
        >
          the docs</a
        >.
      </p>`;
  }

  if (!currentSlice.properties) {
    currentSlice.properties = {};
  }
  // Pre-process the dimensions so we can highlight those that were matched
  // against, with a bold on the subset of dimensions that matched.
  const botDimensions = result.botDimensions || [];
  const usedDimensions = currentSlice.properties.dimensions || [];

  for (const dim of botDimensions) {
    for (const d of usedDimensions) {
      if (d.key === dim.key) {
        dim.highlight = true;
      }
    }
    dim.values = [];
    if (!dim.value) continue;
    // despite the name, dim.value is an array of values
    for (const v of dim.value) {
      const newValue = { name: applyAlias(v, dim.key) };
      for (const d of usedDimensions) {
        if (d.key === dim.key && d.value === v) {
          newValue.bold = true;
        }
      }
      dim.values.push(newValue);
    }
  }

  return html`
<div class=title>Task Execution</div>
<table class=task-execution>
  <tr>
    <td>Bot assigned to task</td>
    <td><a href=${botPageLink(result.botId)}>${result.botId}</td>
  </tr>
  <tr>
    <td>Bot idle since</td>
    <td>${result.human_botIdleSinceTs}</td>
  </tr>
  <tr>
    <td rowspan=${botDimensions.length + 1}>
      Dimensions
    </td>
  </tr>
  ${botDimensions.map((dim) => botDimensionRow(dim, usedDimensions))}
  <tr>
    <td>Exit Code</td>
    <td>${result.exitCode}</td>
  </tr>
  <tr>
    <td>Failure</td>
    <td class=${result.failure ? "failed_task" : ""}>${!!result.failure}</td>
  </tr>
  <tr>
    <td>Internal Failure</td>
    <td class=${result.internalFailure ? "exception" : ""}>${
    result.internalFailure
  }</td>
  </tr>
  <tr>
    <td>Cost (USD)</td>
    <td>$${taskCost(result)}</td>
  </tr>
  ${missingCasBlock(
    "Missing CAS Input(s)",
    ele._app._server_details.cas_viewer_server,
    result.missingCas
  )}
  ${missingCipdBlock("Missing CIPD Package(s)", result.missingCipd)}
  ${casBlock(
    "CAS Outputs",
    ele._app._server_details.cas_viewer_server,
    result.casOutputRoot || {}
  )}
  <tr>
    <td>Bot Version</td>
    <td>${result.botVersion}</td>
  </tr>
  <tr>
    <td>Server Version</td>
    <td>${result.serverVersions}</td>
  </tr>
</table>`;
};

const botDimensionRow = (dim, usedDimensions) => html`
  <tr>
    <td class=${dim.highlight ? "highlight" : ""}>
      <b class="dim_key">${dim.key}:</b>${dim.values.map(botDimensionValue)}
    </td>
  </tr>
`;

const botDimensionValue = (value) =>
  html`<span class="break-all dim ${value.bold ? "bold" : ""}"
    >${value.name}</span
  >`;

const performanceStatsSection = (ele, performanceStats) => {
  if (!ele._taskId || ele._notFound || !performanceStats) {
    return "";
  }
  return html` <div class="title">Performance Stats</div>
    <table class="performance-stats">
      <tr>
        <td
          title="This includes time taken to download inputs, isolate outputs, and setup CIPD"
        >
          Total Overhead
        </td>
        <td>${humanDuration(performanceStats.botOverhead || 0)}</td>
      </tr>
      <tr>
        <td>Cache trimming before the task</td>
        <td>${humanDuration(performanceStats.cacheTrim.duration || 0)}</td>
      </tr>
      <tr>
        <td>Installing CIPD packages</td>
        <td>
          ${humanDuration(performanceStats.packageInstallation.duration || 0)}
        </td>
      </tr>
      <tr>
        <td>Installing Named Caches</td>
        <td>
          ${humanDuration(performanceStats.namedCachesInstall.duration || 0)}
        </td>
      </tr>
      <tr>
        <td>Uninstalling Named Caches</td>
        <td>
          ${humanDuration(performanceStats.namedCachesUninstall.duration || 0)}
        </td>
      </tr>
      <tr>
        <td>Downloading Inputs</td>
        <td>
          ${humanDuration(performanceStats.isolatedDownload.duration || 0)}
        </td>
      </tr>
      <tr>
        <td>Uploading Outputs</td>
        <td>${humanDuration(performanceStats.isolatedUpload.duration || 0)}</td>
      </tr>
      <tr>
        <td>Cleanup directories</td>
        <td>${humanDuration(performanceStats.cleanup.duration || 0)}</td>
      </tr>
      <tr>
        <td>Initial bot cache</td>
        <td>
          ${performanceStats.isolatedDownload.initialNumberItems || 0} items;
          ${human.bytes(performanceStats.isolatedDownload.initialSize || 0)}
        </td>
      </tr>
      <tr>
        <td>Inputs (downloaded)</td>
        <td>
          ${performanceStats.isolatedDownload.numItemsCold || 0} items;
          ${human.bytes(
            performanceStats.isolatedDownload.totalBytesItemsCold || 0
          )}
        </td>
      </tr>
      <tr>
        <td>Inputs (cached)</td>
        <td>
          ${performanceStats.isolatedDownload.numItemsHot || 0} items;
          ${human.bytes(
            performanceStats.isolatedDownload.totalBytesItemsHot || 0
          )}
        </td>
      </tr>
      <tr>
        <td>Outputs (uploaded)</td>
        <td>
          ${performanceStats.isolatedUpload.numItemsCold || 0} items;
          ${human.bytes(
            performanceStats.isolatedUpload.totalBytesItemsCold || 0
          )}
        </td>
      </tr>
      <tr>
        <td>Outputs (cached)</td>
        <td>
          ${performanceStats.isolatedUpload.numItemsHot || 0} items;
          ${human.bytes(
            performanceStats.isolatedUpload.totalBytesItemsHot || 0
          )}
        </td>
      </tr>
    </table>`;
};

const reproduceSection = (ele, currentSlice) => {
  if (!ele._taskId || ele._notFound) {
    return "";
  }
  const casRef =
    (currentSlice.properties && currentSlice.properties.casInputRoot) || {};
  const casDigest =
    casRef.digest && `${casRef.digest.hash}/${casRef.digest.sizeBytes}`;
  const hostUrl = window.location.hostname;
  return html`
    <div class="title">Reproducing the task locally</div>
    <div class="reproduce">
      <div ?hidden=${!casDigest}>
        <div>Download inputs files into directory <i>foo</i>:</div>
        <div class="code bottom_space">
          # (if needed, use "\\\${platform}" as-is) cipd install
          "infra/tools/luci/cas/\\\${platform}" -root bar<br />
          # (if needed) ./bar/cas login<br />
          ./bar/cas download -cas-instance ${casRef.casInstance} -digest
          ${casDigest} -dir foo
        </div>
      </div>

      <div>Run this task locally:</div>
      <div class="code bottom_space">
        # (if needed, use "\\\${platform}" as-is) cipd install
        "infra/tools/luci/swarming/\\\${platform}" -root bar<br />
        # (if needed) ./bar/swarming login<br />
        # '-realm' is only needed if resultdb is enabled for the task.<br />
        # Please use a realm that has 'role/resultdb.invocationCreator' in the
        realms.cfg of your project.<br />
        ./bar/swarming reproduce -S ${hostUrl} -realm project:foo ${ele._taskId}
      </div>

      <div>Download output results into directory <i>foo</i>:</div>
      <div class="code bottom_space">
        # (if needed, use "\\\${platform}" as-is) cipd install
        "infra/tools/luci/swarming/\\\${platform}" -root bar<br />
        # (if needed) ./bar/swarming login<br />
        ./bar/swarming collect -S ${hostUrl} -output-dir=foo ${ele._taskId}
      </div>
    </div>
  `;
};

const taskLogs = (ele) => {
  if (!ele._taskId || ele._notFound) {
    return "";
  }
  return html` <div class="horizontal layout">
      <div class="output-picker">
        <div class="tab" selected>Raw Output</div>
        <div class="tab" ?hidden=${!hasRichOutput(ele)}>
          <a
            rel="noopener"
            target="_blank"
            href=${ifDefined(richLogsLink(ele))}
          >
            Rich Output
          </a>
        </div>
        <checkbox-sk
          id="wide_logs"
          ?checked=${ele._wideLogs}
          @click=${ele._toggleWidth}
        >
        </checkbox-sk>
        <span>Full Width Logs</span>
      </div>
    </div>
    <div class="code stdout tabbed ${ele._wideLogs ? "wide" : "break-all"}">
      ${ele._stdout.map(logBlock)}
    </div>`;
};

// See comment on this._stdout for explanation on how breaking the logs up
// increases page performance.
const logBlock = (log) => html`<div>${log}</div>`;

const retryOrDebugPrompt = (ele, sliceProps) => {
  const dimensions = sliceProps.dimensions || [];
  return html`
<div class=prompt>
  <h2>
    Are you sure you want to ${ele._isPromptDebug ? "debug" : "retry"}
    task ${ele._taskId}?
  </h2>
  <div>
    <div class=ib ?hidden=${!ele._isPromptDebug}>
      <span>Lease Duration</span>
      <input id=lease_duration value=4h></input>
    </div>
    <div class=ib>
      <checkbox-sk class=same-bot
          ?disabled=${!wasPickedUp(ele._result)}
          ?checked=${ele._useSameBot}
          @click=${ele._toggleSameBot}>
      </checkbox-sk>
      <span>Run task on the same bot</span>
    </div>
    <br>
  </div>
  <div>If you want to modify any dimensions (e.g. specify a bot's id), do so now.</div>
  <table ?hidden=${ele._useSameBot}>
    <thead>
      <tr>
        <th>Key</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody id=retry_inputs>
      ${dimensions.map(promptRow)}
      ${promptRow({ key: "", value: "" })}
    </tbody>
  </table>
</div>`;
};

const promptRow = (dim) => html`
<tr>
  <td><input value=${dim.key}></input></td>
  <td><input value=${dim.value}></input></td>
</tr>
`;

const template = (ele) => html`
<swarming-app id=swapp
              ?testing_offline=${ele.testing_offline}>
  <header>
    <div class=title>Swarming Task Page</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/tasklist>Task List</a>
        <a href=/bot>Bot Page</a>
      </aside>
  </header>
  <main class="horizontal layout wrap">
    <h2 class=message ?hidden=${ele.loggedInAndAuthorized}>${ele._message}</h2>

    <div class="left grow" ?hidden=${!ele.loggedInAndAuthorized}>
    ${idAndButtons(ele)}

    <h2 class=not_found ?hidden=${!ele._notFound || !ele._taskId}>
      Task not found
    </h2>


    ${slicePicker(ele)}

    ${taskInfoTable(ele, ele._request, ele._result, ele._currentSlice)}

    ${taskTimingSection(ele, ele._request, ele._result)}

    ${logsSection(ele, ele._request, ele._result)}

    ${taskExecutionSection(ele, ele._request, ele._result, ele._currentSlice)}

    ${performanceStatsSection(ele, ele._result.performanceStats)}

    ${reproduceSection(ele, ele._currentSlice)}
    </div>
    <div class="right grow" ?hidden=${!ele.loggedInAndAuthorized}>
    ${taskLogs(ele)}
    </div>
  </main>
  <footer></footer>
  <dialog-pop-over id=retry>
    <div class='retry-dialog content'>
      ${retryOrDebugPrompt(ele, ele._currentSlice.properties || {})}
      <div class="horizontal layout end">
        <button @click=${
          ele._closePopups
        } class=cancel tabindex=0>Cancel</button>
        <button @click=${ele._promptCallback} class=ok tabindex=0>OK</button>
      </div>
    </div>
  </dialog-pop-over>
  <dialog-pop-over id=cancel>
    <div class='cancel-dialog content'>
      Are you sure you want to ${ele._prompt} task ${ele._taskId}?
      <div class="horizontal layout end">
        <button @click=${ele._closePopups} class=cancel tabindex=0>NO</button>
        <button @click=${ele._promptCallback} class=ok tabindex=0>YES</button>
      </div>
    </div>
  </dialog-pop-over>
</swarming-app>
`;

// 100kb is the native page size on the server, so use this for efficiency.
// The value is hardcoded in task_result.py as TaskOutput.CHUNK_SIZE.
const STDOUT_REQUEST_SIZE = 100 * 1024;

window.customElements.define(
  "task-page",
  class extends SwarmingAppBoilerplate {
    constructor() {
      super(template);
      // Set empty values to allow empty rendering while we wait for
      // stateReflector (which triggers on DomReady). Additionally, these values
      // help stateReflector with types.
      this._taskId = "";
      this._showDetails = false;
      this._wideLogs = false;
      this._urlParamsLoaded = false;
      const idx = location.hostname.indexOf(".appspot.com");
      this._project_id = location.hostname.substring(0, idx);

      this._stateChanged = stateReflector(
        /* getState*/ () => {
          return {
            // provide empty values
            id: this._taskId,
            d: this._showDetails,
            w: this._wideLogs,
          };
        },
        /* setState*/ (newState) => {
          // default values if not specified.
          this._taskId = newState.id || this._taskId;
          this._showDetails = newState.d; // default to false
          this._wideLogs = newState.w; // default to false
          this._urlParamsLoaded = true;
          this._fetch();
          this.render();
        }
      );

      this._request = {};
      this._result = {};
      // For performance of rendering, we keep the stdout as an array
      // of strings that are drawn in individual divs. This has a large
      // performance boost over than the naive approach of drawing
      // a single large string in a single div due to the cost of
      // having to re-layout the entire large string. That cost is
      // roughly quadratic with respect to the length of the string
      // and while the browser is laying out the page, everything
      // else is locked up. Using divs (broken up on the last newline
      // of a log block), is better than simply splitting the logs
      // into spans, because having many large spans adjacent to
      // each other seems to incur a similar quadratic layout cost.
      // With the divs, the browser seems to only have to worry about
      // the layout of the last log block, which can still take
      // 200-300ms, but is a constant time, no matter how many
      // log chunks there are.
      this._stdout = [];
      this._stdoutOffset = 0;
      this._currentSlice = {};
      this._currentSliceIdx = -1;
      this._notFound = false;
      // When swarming does an automatic retry (or multiple), we should
      // fetch the results for those retries and display them.
      this._extraTries = [];
      // Track counts a set of parallel arrays, that is, the nth index in
      // each of these corresponds to the counts for the nth slice.
      // They will be filled in index by index when each fetch from
      // _fetchCounts returns a value.
      this._capacityCounts = [];
      this._pendingCounts = [];
      this._runningCounts = [];
      this._message = "You must sign in to see anything useful.";
      // Allows us to abort fetches that are tied to the id when the id changes.
      this._fetchController = null;
      // The callback for use when prompting to retry or debug
      this._promptCallback = () => {};
      this._isPromptDebug = false;
      this._useSameBot = false;

      this._logFetchPeriod = 10 * 1000; // default to 10s, overwritable for tests.
    }

    connectedCallback() {
      super.connectedCallback();

      this._loginEvent = (e) => {
        this._fetch();
        this.render();
      };
      this.addEventListener("log-in", this._loginEvent);
      this.render();
    }

    disconnectedCallback() {
      super.disconnectedCallback();
      this.removeEventListener("log-in", this._loginEvent);
    }

    _createTasksService() {
      return new TasksService(this.authHeader, this._fetchController.signal);
    }

    _cancelTask() {
      const body = {};
      if (this._result.state === "RUNNING") {
        body.kill_running = true;
      }
      this.app.addBusyTasks(1);
      fetch(`/_ah/api/swarming/v1/task/${this._taskId}/cancel`, {
        method: "POST",
        headers: {
          authorization: this.authHeader,
          "content-type": "application/json; charset=UTF-8",
        },
        body: JSON.stringify(body),
      })
        .then(jsonOrThrow)
        .then((response) => {
          this._closePopups();
          errorMessage("Request sent", 4000);
          this.render();
          this.app.finishedTask();
        })
        .catch((e) => this.fetchError(e, "task/cancel"));
    }

    _closePopups() {
      this._promptCallback = () => {};
      // close all dialogs
      $("dialog-pop-over", this).map((d) => d.hide());
    }

    // Look at the inputs in the prompt dialog for potential key:value pairs
    // or use just the id of the bot.
    _collectDimensions() {
      const newDimensions = [];
      if (this._useSameBot) {
        newDimensions.push(
          {
            key: "id",
            value: firstDimension(this._result.botDimensions, "id"),
          },
          {
            // pool is always a required dimension
            key: "pool",
            value: firstDimension(this._result.botDimensions, "pool"),
          }
        );
      } else {
        const inputRows = $("#retry_inputs tr", this);
        for (const row of inputRows) {
          const key = row.children[0].firstElementChild.value;
          const value = row.children[1].firstElementChild.value;
          if (key && value) {
            newDimensions.push({
              key: key,
              value: value,
            });
          }
        }
        if (!newDimensions.length) {
          errorMessage(
            "You must specify some dimensions (pool is required)",
            6000
          );
          return null;
        }
        if (!firstDimension(newDimensions, "pool")) {
          errorMessage("The pool dimension is required");
          return null;
        }
      }
      return newDimensions;
    }

    _debugTask() {
      const newTask = {
        expiration_secs: this._request.expirationSecs,
        name: `leased to ${this.profile.email} for debugging`,
        pool_task_template: 3, // SKIP
        priority: 20,
        properties: this._currentSlice.properties,
        realm: this._request.realm,
        service_account: this._request.serviceAccount,
        tags: ["debug_task:1"],
        user: this.profile.email,
      };

      const leaseDurationEle = $$("#lease_duration").value;
      const leaseDuration = parseDuration(leaseDurationEle);

      newTask.properties.command = [
        "python3",
        "-c",
        `import os, sys, time
print('Mapping task: ${location.origin}/task?id=${this._taskId}')
print('Files are mapped into: ' + os.getcwd())
print('')
print('Bot id: ' + os.environ['SWARMING_BOT_ID'])
print('Bot leased for: ${leaseDuration} seconds')
print('How to access this bot: http://go/swarming-ssh')
print('When done, reboot the host')
print('')
print('Some tests may fail without the following env vars set:')
print('PATH=' + os.environ['PATH'])
print('LUCI_CONTEXT=' + os.environ['LUCI_CONTEXT'])
sys.stdout.flush()
time.sleep(${leaseDuration})`,
      ];
      newTask.properties.execution_timeout_secs = leaseDuration;
      newTask.properties.io_timeout_secs = leaseDuration;
      const dims = this._collectDimensions();
      if (!dims) {
        return;
      }
      newTask.properties.dimensions = dims;
      this._newTask(newTask);
      this._closePopups();
    }

    _fetch() {
      if (
        !this.loggedInAndAuthorized ||
        !this._urlParamsLoaded ||
        !this._taskId
      ) {
        return;
      }
      if (this._fetchController) {
        // Kill any outstanding requests.
        this._fetchController.abort();
      }
      // Make a fresh abort controller for each set of fetches. AFAIK, they
      // cannot be re-used once aborted.
      this._fetchController = new AbortController();
      const extra = {
        headers: { authorization: this.authHeader },
        signal: this._fetchController.signal,
      };
      // re-fetch permissions with the task ID.
      this.app._fetchPermissions(extra, { task_id: this._taskId });
      this._fetchTaskInfo(extra);
      this._fetchStdOut(extra);
    }

    _fetchTaskInfo(extra) {
      this.app.addBusyTasks(2);
      let currIdx = -1;
      const taskService = this._createTasksService();
      taskService
        .request(this._taskId)
        .then((response) => {
          this._notFound = false;
          this._request = parseRequest(response);
          // Note, this triggers more fetch requests, which also adds to
          // app's busy task counts.
          this._fetchCounts(this._request, extra);
          // We need to set the slice if result has been loaded, otherwise
          // when the slice loads, it will take care of it for us.
          if (currIdx >= 0) {
            this._setSlice(currIdx); // calls render
          } else {
            this.render();
          }
          this.app.finishedTask();
        })
        .catch((e) => {
          if (e.status === 404) {
            this._request = {};
            this._notFound = true;
            this.render();
          }
          this.fetchError(e, "task/request");
        });
      this._extraTries = [];

      taskService
        .result(this._taskId, true)
        .then((response) => {
          this._result = parseResult(response);
          currIdx = +this._result.currentTaskSlice;
          this._setSlice(currIdx); // calls render
          this.app.finishedTask();
        })
        .catch((e) => this.prpcError(e, "task/result"));
    }

    _fetchStdOut(extra) {
      this.app.addBusyTasks(1);
      // Fetching stdout piece by piece like this is not perfect. Namely, the server
      // breaks at arbitrary byte points, and JS will treat that as the end of a
      // string, so this may not look good if we routinely break multi-byte
      // unicode characters apart.
      let previousState = "";
      const fetchNextStdout = () => {
        const tasksService = this._createTasksService();
        tasksService
          .stdout(this._taskId, this._stdoutOffset, STDOUT_REQUEST_SIZE)
          .then((resp) => {
            if (!previousState) {
              previousState = resp.state;
            }
            const s = resp.output ? b64toUtf8(resp.output) : "";
            // s.length returns number of UTF-8 code points
            // `offset` and `length` are in bytes
            const sLengthBytes = new Blob([s]).size;
            this._stdoutOffset += sLengthBytes;
            // Remove carriage returns for easier copy-paste and presentation.
            // https://crbug.com/944974
            const newLogs = s.replace(/\r\n/g, "\n");
            // split this log batch on the last newline
            const lastNewline = newLogs.lastIndexOf("\n");
            let block = newLogs;
            let remainder = "";
            if (lastNewline !== -1) {
              block = newLogs.substring(0, lastNewline + 1);
              remainder = newLogs.substring(lastNewline + 1);
            }
            // If the previous block doesn't end in newline, we assume this block
            // should be appended to that one.
            if (
              this._stdout.length &&
              !this._stdout[this._stdout.length - 1].endsWith("\n")
            ) {
              this._stdout[this._stdout.length - 1] += block;
              if (remainder) {
                this._stdout.push(remainder);
              }
            } else {
              // otherwise, just push what we have as a new block (usually this
              // is the first logs loaded).
              this._stdout.push(block);
              if (remainder) {
                this._stdout.push(remainder);
              }
            }

            this.render();

            if (resp.state !== previousState) {
              this._fetchTaskInfo(extra);
            }

            if (resp.state === "RUNNING" || resp.state === "PENDING") {
              if (sLengthBytes < STDOUT_REQUEST_SIZE) {
                // wait for more input because no new input from last fetch
                setTimeout(fetchNextStdout, this._logFetchPeriod);
              } else {
                // fetch right away because we are not at the end of input
                fetchNextStdout();
              }
            } else {
              // no more
              if (sLengthBytes < STDOUT_REQUEST_SIZE) {
                this.app.finishedTask();
              } else {
                // fetch right away because we are not at the end of input
                fetchNextStdout();
              }
            }
            previousState = resp.state;
          })
          .catch((e) => this.prpcError(e, "task/request"));
      };
      fetchNextStdout();
    }

    _fetchCounts(request, extra) {
      const numSlices = request.taskSlices.length;
      this.app.addBusyTasks(numSlices * 3);
      // reset current viewings
      this._capacityCounts = [];
      this._pendingCounts = [];
      this._runningCounts = [];
      for (let i = 0; i < numSlices; i++) {
        const bParams = {
          dimensions: [],
        };
        for (const dim of request.taskSlices[i].properties.dimensions) {
          bParams.dimensions.push(`${dim.key}:${dim.value}`);
        }
        fetch(
          `/_ah/api/swarming/v1/bots/count?${query.fromObject(bParams)}`,
          extra
        )
          .then(jsonOrThrow)
          .then((json) => {
            this._capacityCounts[i] = json;
            this.render();
            this.app.finishedTask();
          })
          .catch((e) => this.fetchError(e, "bots/count slice " + i, true));

        let start = new Date();
        start.setSeconds(0);
        // go back 24 hours, rounded to the nearest minute for better caching.
        start = "" + (start.getTime() - 24 * 60 * 60 * 1000);
        // convert to seconds, because that's what the API expects.
        start = start.substring(0, start.length - 3);
        const tParams = {
          start: [start],
          state: ["RUNNING"],
          tags: bParams.dimensions,
        };
        fetch(
          `/_ah/api/swarming/v1/tasks/count?${query.fromObject(tParams)}`,
          extra
        )
          .then(jsonOrThrow)
          .then((json) => {
            this._runningCounts[i] = json.count;
            this.render();
            this.app.finishedTask();
          })
          .catch((e) => this.fetchError(e, "tasks/running slice " + i, true));

        tParams.state = ["PENDING"];
        fetch(
          `/_ah/api/swarming/v1/tasks/count?${query.fromObject(tParams)}`,
          extra
        )
          .then(jsonOrThrow)
          .then((json) => {
            this._pendingCounts[i] = json.count;
            this.render();
            this.app.finishedTask();
          })
          .catch((e) => this.fetchError(e, "tasks/pending slice " + i, true));
      }
    }

    _fetchExtraTries(taskId, tries, extra) {
      this.app.addBusyTasks(tries);
      for (let i = 0; i < tries; i++) {
        fetch(`/_ah/api/swarming/v1/task/${taskId + (i + 1)}/result`, extra)
          .then(jsonOrThrow)
          .then((json) => {
            const result = parseResult(json);
            this._extraTries[i] = result;
            this.render();
            this.app.finishedTask();
          })
          .catch((e) => this.fetchError(e, "task/result"));
      }
    }

    // _newTask makes a request to the server to start a new task, given a request.
    _newTask(newTask) {
      newTask.properties.idempotent = false;
      this.app.addBusyTasks(1);
      this._createTasksService()
        .new(newTask)
        .then((response) => {
          if (response && response.taskId) {
            this._taskId = response.taskId;
            this._stateChanged();
            this._fetch();
            this.render();
            this.app.finishedTask();
          }
        })
        .catch((e) => this.prpcError(e, "newtask"));
    }

    _promptCancel() {
      this._prompt = "cancel";
      if (this._result.state === "RUNNING") {
        this._prompt = "kill";
      }
      this._promptCallback = this._cancelTask;
      this.render();
      $$("dialog-pop-over#cancel", this).show();
      $$("dialog-pop-over#cancel button.cancel", this).focus();
    }

    _promptDebug() {
      if (!this._request) {
        errorMessage("Task not yet loaded", 3000);
        return;
      }
      this._isPromptDebug = true;
      this._useSameBot = false;
      this._promptCallback = this._debugTask;
      this.render();
      $$("dialog-pop-over#retry", this).show();
      $$("dialog-pop-over#retry button.cancel", this).focus();
    }

    _promptRetry() {
      if (!this._request) {
        errorMessage("Task not yet loaded", 3000);
        return;
      }
      this._isPromptDebug = false;
      this._useSameBot = false;
      this._promptCallback = this._retryTask;
      this.render();
      $$("dialog-pop-over#retry", this).show();
      $$("dialog-pop-over#retry button.cancel", this).focus();
    }

    render() {
      super.render();
      const idInput = $$("#id_input", this);
      idInput.value = this._taskId;
    }

    _retryTask() {
      const newTask = {
        expiration_secs: this._request.expirationSecs,
        name: this._request.name + " (retry)",
        pool_task_template: 3, // SKIP
        priority: this._request.priority,
        properties: this._currentSlice.properties,
        service_account: this._request.serviceAccount,
        tags: this._request.tags,
        user: this.profile.email,
        resultdb: { enable: Boolean(this._result.resultdbInfo) },
        realm: this._request.realm,
      };
      newTask.tags.push("retry:1");

      const dims = this._collectDimensions();
      if (!dims) {
        return;
      }
      newTask.properties.dimensions = dims;

      this._newTask(newTask);
      this._closePopups();
    }

    _setSlice(idx) {
      this._currentSliceIdx = idx;
      if (!this._request.taskSlices) {
        return;
      }
      this._currentSlice = this._request.taskSlices[idx];
      this.render();
    }

    _toggleDetails(e) {
      this._showDetails = !this._showDetails;
      this._stateChanged();
      this.render();
    }

    _toggleSameBot(e) {
      // This prevents the checkbox from toggling twice.
      e.preventDefault();
      if (!wasPickedUp(this._result)) {
        return;
      }
      this._useSameBot = !this._useSameBot;
      this.render();
    }

    _toggleWidth(e) {
      // This prevents the checkbox from toggling twice.
      e.preventDefault();
      this._wideLogs = !this._wideLogs;
      this._stateChanged();
      this.render();
    }

    _updateID(e) {
      const idInput = $$("#id_input", this);
      this._taskId = idInput.value;
      this._stdout = []; // erase stdout when switching tasks.
      this._stdoutOffset = 0;
      this._stateChanged();
      this._fetch();
      this.render();
    }
  }
);
