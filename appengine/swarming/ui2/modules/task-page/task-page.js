// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { html, render } from 'lit-html'
import { jsonOrThrow } from 'common-sk/modules/jsonOrThrow'

import 'elements-sk/styles/buttons'
import '../swarming-app'

import { humanState, parseRequest } from './task-page-helpers'
import { taskPageLink } from '../util'

import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'


/**
 * @module swarming-ui/modules/task-page
 * @description <h2><code>task-page<code></h2>
 *
 * <p>
 *   TODO
 * </p>
 *
 */

const dimension_block = (dimensions) => html`
<tr>
  <td rowspan=${dimensions.length+1}>
    Dimensions
    <!-- TODO(kjlubick) add links to bots/tasks-->
  </td>
</tr>
${dimensions.map(dimension_row)}
`;

const dimension_row = (dimension) => html`
<tr>
  <td><b>${dimension.key}:</b> ${dimension.value}</td>
</tr>
`;

const isolate_block = (title, ref) => {
  if (!ref.isolated) {
    return '';
  }
  const url = ref.isolatedserver + '/browse?namespace='+ref.namespace +
              '&hash=' + ref.isolated;
  return html`
<tr>
  <td>${title}</td>
  <td>
    <a href=${url}>
      ${ref.isolated}
    </a>
  </td>
</tr>`
};

const outputs_block = (outputs) => {
  if (!outputs || !outputs.length) {
    return '';
  }
  return html`
<tr>
  <td rowspan=${outputs.length+1}>Expected outputs</td>
</tr>
${outputs.map(output_row)}`;
}

const output_row = (output) => html`
<tr>
  <td>${output}</td>
</tr>
`;


const commit_block = (tagMap) => {
  if (!tagMap || !tagMap.source_revision) {
    return '';
  }
    return html`
<tr>
  <td>Associated Commit</td>
  <td>
    <a href=${ele._request.tagMap.source_repo.replace('%s',
              ele._request.tagMap.source_revision)}>
      ${ele._request.tagMap.source_revision.substring(0, 12)}
    </a>
  </td>
</tr>
`};


const taskInfo = (ele) => html`
<div class=id_buttons>
  <input class=id_input></input>
  <button>refresh</button>
  <button>retry</button>
  <button>debug</button>
</div>

<!-- TODO(kjlubick) slices-->

<table class=task-info ?hidden=${false && "TODO"}>
  <tr>
    <td>Name</td>
    <td>${ele._request.name}</td>
  </tr>
  <tr>
    <td>State</td>
    <td>${humanState(ele._result)}</td>
  </tr>
  <tr>
    <td>
      ${ele._result.state === 'PENDING' ?
      'Why Pending' : 'Fleet Capacity'}
    </td>
    <!-- TODO(kjlubick) counts. don't forget itallics-->
    <td>
      11 bots could possibly run this task
      (1 busy, 2 dead, 3 quarantined, 4 maintenance)
    </td>
  </tr>
  <tr>
    <td>Similar Load</td>
    <!-- TODO(kjlubick) more counts -->
    <td>57 similar pending tasks, 123 similar running tasks</td>
  </tr>

  <tr ?hidden=${!ele._result.deduped_from}>
    <td><b>Deduped From</b></td>
    <td><a href=${taskPageLink(ele._result.deduped_from)}</td>
  </tr>
  <tr ?hidden=${!ele._result.deduped_from}>
    <td>Deduped On</td>
    <td title=${ele._request.created_ts}>
      ${ele._request.human_created_ts}
    </td>
  </tr>

  <tr>
    <td>Priority</td>
    <td>${ele._request.priority}</td>
  </tr>
  <tr>
    <td>Wait for Capacity</td>
    <td>TODO</td>
  </tr>
  <tr>
    <td>Slice Expires</td>
    <td>TODO</td>
  </tr>
  <tr>
    <td>User</td>
    <td>${ele._request.user || 'None'}</td>
  </tr>
  <tr>
    <td>Authenticated</td>
    <td>${ele._request.authenticated}</td>
  </tr>
  <tr ?hidden=${!ele._request.service_account}>
    <td>Service Account</td>
    <td>${ele._request.service_account}</td>
  </tr>
  <tr ?hidden=${!ele._currentSlice.properties.secret_bytes}>
    <td>Has Secret Bytes</td>
    <td title="The secret bytes on present on the machine, but not in the UI/API">true</td>
  </tr>
  <tr ?hidden=${!ele._request.parent_task_id}>
    <td>Parent Task</td>
    <td>
      <a href=${taskPageLink(ele._request.parent_task_id)}>
        ${ele._request.parent_task_id}
      </a>
    </td>
  </tr>
  ${dimension_block(ele._currentSlice.properties.dimensions || [])}
  ${isolate_block('Isolated Inputs', ele._currentSlice.properties.inputs_ref || {})}
  ${outputs_block(ele._currentSlice.properties.outputs || [])}
  ${commit_block(ele._request.tagMap)}
  <!-- TODO(kjlubick) details -->
</table>
`;


const taskLogs = (ele) => html`
  Task logs goes here
`;

const template = (ele) => html`
<swarming-app id=swapp
              client_id=${ele.client_id}
              ?testing_offline=${ele.testing_offline}>
  <header>
    <div class=title>Swarming Task Page</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/oldui/botlist>Old Bot List</a>
        <a href=/tasklist>Task List</a>
      </aside>
  </header>
  <main>
    <div class=left>
    ${taskInfo(ele)}
    </div>
    <div class=right>
    ${taskLogs(ele)}
    </div>
  </main>
  <footer></footer>
</swarming-app>
`;

window.customElements.define('task-page', class extends SwarmingAppBoilerplate {

  constructor() {
    super(template);

    this._taskId = 'task000';
    this._request = {};
    this._result = {};
    this._currentSlice = {
      properties: {},
    };

    // Allows us to abort fetches that are tied to the id when the id changes.
    this._fetchController = null;
  }

  connectedCallback() {
    super.connectedCallback();

    this._loginEvent = (e) => {
      this._fetch();
      this.render();
    };
    this.addEventListener('log-in', this._loginEvent);
    this.render();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.removeEventListener('log-in', this._loginEvent);
  }

  _fetch() {
    if (!this.loggedInAndAuthorized || !this._taskId) {
      return;
    }
    if (this._fetchController) {
      // Kill any outstanding requests that use the filters
      this._fetchController.abort();
    }
    // Make a fresh abort controller for each set of fetches. AFAIK, they
    // cannot be re-used once aborted.
    this._fetchController = new AbortController();
    const extra = {
      headers: {'authorization': this.auth_header},
      signal: this._fetchController.signal,
    };
    this.app.addBusyTasks(2);
    fetch(`/_ah/api/swarming/v1/task/${this._taskId}/request`, extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._request = parseRequest(json);
        // TODO(kjlubick): default this to the one that ran.
        this._currentSlice = this._request.task_slices[0];
        this.app.finishedTask();
        this.render();
      })
      .catch((e) => this.fetchError(e, 'task/request'));
    fetch(`/_ah/api/swarming/v1/task/${this._taskId}/result?include_performance_stats=true`, extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._result = json;
        this.app.finishedTask();
        this.render();
      })
      .catch((e) => this.fetchError(e, 'task/result'));
  }

  render() {
    super.render();
  }

});