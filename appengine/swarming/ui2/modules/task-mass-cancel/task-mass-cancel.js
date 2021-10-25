// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import {$$} from 'common-sk/modules/dom';
import {errorMessage} from 'elements-sk/errorMessage';
import {html, render} from 'lit-html';
import {jsonOrThrow} from 'common-sk/modules/jsonOrThrow';
import {until} from 'lit-html/directives/until';

import {floorSecond} from '../task-list/task-list-helpers';
import {initPropertyFromAttrOrProperty} from '../util';

// query.fromObject is more readable than just 'fromObject'
import * as query from 'common-sk/modules/query';

import 'elements-sk/checkbox-sk';
import 'elements-sk/styles/buttons';

/**
 * @module swarming-ui/modules/task-mass-cancel
 * @description <h2><code>task-mass-cancel<code></h2>
 *
 * <p>
 * task-mass-cancel offers an interface for the user to cancel multiple tasks
 * (and hopefully avoid doing so on accident).
 * </p>
 *
 * @fires tasks-canceling-started
 * @fires tasks-canceling-finished
 */

const listItem = (tag) => html`<li>${tag}</li>`;

const template = (ele) => html`
  <div>
    You are about to cancel all PENDING bots with the following tags:
    <ul>
      ${ele.tags.map(listItem)}
    </ul>
    <div>
      <checkbox-sk ?checked=${ele._both}
                   ?disabled=${ele._started}
                   @click=${ele._toggleBoth}
                   tabindex=0>
      </checkbox-sk> Also include RUNNING tasks.
    </div>

    This is about ${ele._count()} tasks.
    Once you start the process, the only way to partially stop it is to close this
    browser window.

    If that sounds good, click the button below.
  </div>

  <button class=cancel ?disabled=${!ele._readyToCancel || ele._started}
                       @click=${ele._cancelAll}>
    Cancel the tasks
  </button>

  <div>
    <div ?hidden=${!ele._started}>
      Progress: ${ele._progress} canceled${ele._finished ? ' - DONE.': '.'}
    </div>
    <div>
      Note: tasks queued for cancellation will be canceled as soon as possible, but there may
      be some delay between when this dialog box is closed and all tasks actually being canceled.
    </div>
  </div>
`;

function fetchError(e, loadingWhat) {
  const message = `Unexpected error loading ${loadingWhat}: ${e.message}`;
  console.error(message);
  errorMessage(message, 5000);
}

function nowInSeconds() {
  // convert milliseconds to seconds
  return Math.round(Date.now() / 1000);
}

const CANCEL_BATCH_SIZE = 100;

window.customElements.define('task-mass-cancel', class extends HTMLElement {
  constructor() {
    super();
    this._readyToCancel = false;
    this._started = false;
    this._finished = false;
    this._both = false;
    this._progress = 0;
  }

  connectedCallback() {
    initPropertyFromAttrOrProperty(this, 'auth_header');
    initPropertyFromAttrOrProperty(this, 'tags');
    // Used for when default was loaded via attribute.
    if (typeof this.tags === 'string') {
      this.tags = this.tags.split(',');
    }
    // sort for determinism
    this.tags.sort();
    this.render();
  }

  _cancelAll() {
    this._started = true;
    this.dispatchEvent(new CustomEvent('tasks-canceling-started', {bubbles: true}));
    this.render();

    const queryParams = query.fromObject({
      tags: this.tags,
      start: floorSecond(this._startTime),
      end: floorSecond(this._now ? Date.now() : this._endTime),
      limit: 200, // see https://crbug.com/908423
      fields: 'cursor,items/task_id',
      state: 'PENDING',
    });

    const extra = {
      headers: {'authorization': this.auth_header},
    };

    let tasks = [];
    fetch(`/_ah/api/swarming/v1/tasks/list?${queryParams}`, extra)
        .then(jsonOrThrow)
        .then((json) => {
          const maybeLoadMore = (json) => {
            tasks = tasks.concat(json.items);
            this.render();
            if (json.cursor) {
              const queryParams = query.fromObject({
                cursor: json.cursor,
                tags: this.tags,
                start: floorSecond(this._startTime),
                end: floorSecond(this._now ? Date.now() : this._endTime),
                limit: 200, // see https://crbug.com/908423
                fields: 'cursor,items/task_id',
                state: 'PENDING',
              });
              fetch(`/_ah/api/swarming/v1/tasks/list?${queryParams}`, extra)
                  .then(jsonOrThrow)
                  .then(maybeLoadMore)
                  .catch((e) => fetchError(e, 'bot-mass-delete/list (paging)'));
            } else {
              // Now that we have the complete list of tasks (e.g. no paging left)
              // cancel the tasks one at a time, updating this._progress to be the
              // number completed.
              const post = {
                headers: {'authorization': this.auth_header},
                method: 'POST',
              };

              if (this._both) {
                post.kill_running = true;
              }

              const deleteNext = (tasks) => {
                if (!tasks.length) {
                  this._finished = true;
                  this.render();
                  this.dispatchEvent(new CustomEvent('tasks-cancel-finished', {bubbles: true}));
                  return;
                }
                const toDelete = tasks.pop();
                fetch(`/_ah/api/swarming/v1/task/${toDelete.task_id}/cancel`, post)
                    .then(() => {
                      this._progress++;
                      this.render();
                      deleteNext(tasks);
                    }).catch((e) => fetchError(e, 'task-mass-cancel/cancel'));
              };
              deleteNext(tasks);
            }
          };
          maybeLoadMore(json);
        }).catch((e) => fetchError(e, 'task-mass-cancel/list'));
  }

  _count() {
    if (this._pendingCount === undefined || this._runningCount === undefined) {
      return '...';
    }
    if (this._both) {
      return this._pendingCount + this._runningCount;
    }
    return this._pendingCount;
  }

  _fetchCount() {
    if (!this.auth_header) {
      // This should never happen
      console.warn('no auth_header received, try refreshing the page?');
      return;
    }
    const extra = {
      headers: {'authorization': this.auth_header},
    };

    const pendingParams = query.fromObject({
      state: 'PENDING',
      tags: this.tags,
      // Search in the last week to get the count.  PENDING tasks should expire
      // well before then, so this should be pretty accurate.
      start: nowInSeconds() - 7*24*60*60,
      end: nowInSeconds(),
    });

    const pendingPromise = fetch(`/_ah/api/swarming/v1/tasks/count?${pendingParams}`, extra)
        .then(jsonOrThrow)
        .then((json) => {
          this._pendingCount = parseInt(json.count);
        }).catch((e) => fetchError(e, 'task-mass-cancel/pending'));

    const runningParams = query.fromObject({
      state: 'RUNNING',
      tags: this.tags,
      // Search in the last week to get the count.  RUNNING tasks should finish
      // well before then, so this should be pretty accurate.
      start: nowInSeconds() - 7*24*60*60,
      end: nowInSeconds(),
    });

    const runningPromise = fetch(`/_ah/api/swarming/v1/tasks/count?${runningParams}`, extra)
        .then(jsonOrThrow)
        .then((json) => {
          this._runningCount = parseInt(json.count);
        }).catch((e) => fetchError(e, 'task-mass-cancel/running'));

    // re-render when both have returned
    Promise.all([pendingPromise, runningPromise]).then(() => {
      this._readyToCancel = true;
      this.render();
    });
  }

  render() {
    render(template(this), this, {eventContext: this});
  }

  /** show prepares the UI to be shown to the user */
  show() {
    this._readyToCancel = false;
    this._started = false;
    this._finished = false;
    this._progress = 0;
    this._fetchCount();
    this.render();
  }

  _toggleBoth(e) {
    // This prevents a double event from happening.
    e.preventDefault();
    if (this._started) {
      return;
    }
    this._both = !this._both;
    this.render();
  }
});
