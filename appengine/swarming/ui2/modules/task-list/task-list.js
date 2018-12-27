import { $, $$ } from 'common-sk/modules/dom'
import { errorMessage } from 'elements-sk/errorMessage'
import { html, render } from 'lit-html'
import { ifDefined } from 'lit-html/directives/if-defined';
import { jsonOrThrow } from 'common-sk/modules/jsonOrThrow'
import naturalSort from 'javascript-natural-sort/naturalSort'
import * as query from 'common-sk/modules/query'
import { stateReflector } from 'common-sk/modules/stateReflector'

import '../swarming-app'

import { column, processTasks } from './task-list-helpers'
import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'


const taskCol = (col, bot, ele) => html`
<td>${column(col, bot, ele)}</td>`;

const taskRow = (task, ele) => html`
<tr class="task-row">
  ${ele._cols.map((col) => taskCol(col,task,ele))}
</tr>`;

const template = (ele) => html`
<swarming-app id=swapp
              client_id=${ele.client_id}
              ?testing_offline=${ele.testing_offline}>
  <header>
    <div class=title>Swarming Task List</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Task List</a>
        <a href=/oldui/tasklist>Old Task List</a>
        <a href=/tasklist>Task List</a>
      </aside>
  </header>
  <main>
    <h2 class=message ?hidden=${ele.loggedInAndAuthorized}>${ele._message}</h2>


    <table class=bot-table ?hidden=${!ele.loggedInAndAuthorized}>
      <thead>
        <tr>
          <th>name</th>
        </tr>
      </thead>
      <tbody>${ele._tasks.map((task) => taskRow(task, ele))}</tbody>
    </table>

  </main>
  <footer></footer>
</swarming-app>`;

// How many items to load on the first load of bots
// This is a relatively low number to make the initial page load
// seem snappier. After this, we can go up (see BATCH LOAD) to
// reduce the number of queries, since the user can expect to wait
// a bit more when their interaction (e.g. adding a filter) causes
// more data to be fetched.
const INITIAL_LOAD = 100;
// How many items to load on subsequent fetches.
// This number was picked from experience and experimentation.
const BATCH_LOAD = 200;

window.customElements.define('task-list', class extends SwarmingAppBoilerplate {

  constructor() {
    super(template);
    this._tasks = [];
    this._forcedColumns = ['name'];

    this._cols = ['name', 'state', 'bot', 'created_ts', 'pending_ts',
                  'duration', 'pool'];

    this._filters = [];

    this._limit = 0;
    this._showAll = true;

    this._message = 'You must sign in to see anything useful.';
    this._fetchController = null;
  }

  connectedCallback() {
    super.connectedCallback();

    this.addEventListener('log-in', (e) => {
      this._fetch();
      this.render();
    });
  }

  _fetch() {
    if (!this.loggedInAndAuthorized) {
      return;
    }
    if (this._fetchController) {
      // Kill any outstanding requests that use the filters
      this._fetchController.abort();
    }
    // Make a fresh abort controller for each set of fetches. AFAIK, they
    // cannot be re-used once aborted.
    this._fetchController = new AbortController();
    let extra = {
      headers: {'authorization': this.auth_header},
      signal: this._fetchController.signal,
    };
    // Fetch the bots
    this.app.addBusyTasks(1);
    let queryParams = '?TODO';
    fetch(`/_ah/api/swarming/v1/tasks/list?${queryParams}`, extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._tasks = [];
        const maybeLoadMore = (json) => {
          this._tasks = this._tasks.concat(processTasks(json.items));
          this.render();
          // Special case: Don't load all the bots when filters is empty to avoid
          // loading many many bots unintentionally. A user can over-ride this
          // with the showAll button.
          if ((this._filters.length || this._showAll) && json.cursor) {
            this._limit = BATCH_LOAD;
            queryParams = '?TODO+json.cursor';
            fetch(`/_ah/api/swarming/v1/tasks/list?${queryParams}`, extra)
              .then(jsonOrThrow)
              .then(maybeLoadMore)
              .catch((e) => this.fetchError(e, 'tasks/list (paging)'));
          } else {
            this.app.finishedTask();
          }
        }
        maybeLoadMore(json);
      })
      .catch((e) => this.fetchError(e, 'tasks/list'));
  }
  render() {
    // Incorporate any data changes before rendering.
    super.render();
  }

});
