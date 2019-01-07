// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

/** @module swarming-ui/modules/task-list
 * @description <h2><code>bot-list</code></h2>
 *
 * <p>
 *  Task List shows a filterable list of all swarming tasks.
 * </p>
 *
 * <p>This is a top-level element.</p>
 *
 * @attr client_id - The Client ID for authenticating via OAuth.
 * @attr testing_offline - If true, the real OAuth flow won't be used.
 *    Instead, dummy data will be used. Ideal for local testing.
 */

import { $, $$ } from 'common-sk/modules/dom'
import { errorMessage } from 'elements-sk/errorMessage'
import { html, render } from 'lit-html'
import { ifDefined } from 'lit-html/directives/if-defined';
import { jsonOrThrow } from 'common-sk/modules/jsonOrThrow'

import 'elements-sk/checkbox-sk'
import 'elements-sk/icon/add-circle-icon-sk'
import 'elements-sk/icon/cancel-icon-sk'
import 'elements-sk/icon/expand-less-icon-sk'
import 'elements-sk/icon/expand-more-icon-sk'
import 'elements-sk/icon/more-vert-icon-sk'
import 'elements-sk/icon/search-icon-sk'
import 'elements-sk/select-sk'
import 'elements-sk/styles/buttons'
import '../sort-toggle'
import '../swarming-app'

import { appendPossibleColumns, column, getColHeader, processTasks, sortColumns, sortPossibleColumns, taskClass } from './task-list-helpers'
import { filterPossibleColumns, filterPossibleKeys,
         filterPossibleValues } from '../queryfilter'
import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'


const colHead = (col, ele) => html`
<th>${getColHeader(col)}
  <sort-toggle .key=${col} .currentKey=${ele._sort} .direction=${ele._dir}>
  </sort-toggle>
</th>`;

const taskCol = (col, bot, ele) => html`
<td>${column(col, bot, ele)}</td>`;

const taskRow = (task, ele) => html`
<tr class="task-row ${taskClass(task)}">
  ${ele._cols.map((col) => taskCol(col, task, ele))}
</tr>`;

const columnOption = (key, ele) => html`
<div class=item>
  <span class=key>${key}</span>
  <span class=flex></span>
  <checkbox-sk ?checked=${ele._cols.indexOf(key) >= 0}
               @click=${(e) => ele._toggleCol(e, key)}>
  </checkbox-sk>
</div>`;

const col_selector = (ele) => {
  if (!ele._showColSelector) {
    return '';
  }
  return html`
<!-- Stop clicks from traveling outside the popup.-->
<div class=col_selector @click=${e => e.stopPropagation()}>
  <input id=column_search class=search type=text
         placeholder='Search columns to show'
         @input=${e => ele._refilterPossibleColumns(e)}
         <!-- Looking at the change event, but that had the behavior of firing
              any time the user clicked away, with seemingly no differentiation.
              Instead, we watch keyup and wait for the 'Enter' key. -->
         @keyup=${e => ele._columnSearch(e)}>
  </input>
  ${ele._filteredPossibleColumns.map((key) => columnOption(key, ele))}
</div>`;
}

const col_options = (ele, firstCol) => html`
<!-- Put the click action here to make it bigger, especially for mobile.-->
<th class=col_options @click=${ele._toggleColSelector}>
  <span class=show_widget>
    <more-vert-icon-sk></more-vert-icon-sk>
  </span>
  <span>${getColHeader(firstCol)}</span>
  <sort-toggle @click=${e => (e.stopPropagation() && e.preventDefault())}
               key=id .currentKey=${ele._sort} .direction=${ele._dir}>
  </sort-toggle>
  ${col_selector(ele)}
</th>`;

const primaryOption = (key, ele) => html`
<div class=item ?selected=${ele._primaryKey === key}>
  <span class=key>${key}</span>
</div>`;

const secondaryOptions = (ele) => {
  if (!ele._primaryKey) {
    return '';
  }
  let values = ele._primaryMap[ele._primaryKey];
  if (!values) {
    return html`
<div class=information_only>
  Hmm... no preloaded values. Maybe try typing your filter like ${ele._primaryKey}:foo-bar in the
  above box and hitting enter.
</div>`;
  }
  values = filterPossibleValues(values, ele._primaryKey, ele._filterQuery);
  values.sort(naturalSort);
  return values.map((value) =>
    html`
<div class=item>
  <span class=value>${applyAlias(value, ele._primaryKey)}</span>
  <span class=flex></span>
  <add-circle-icon-sk ?hidden=${ele._filters.indexOf(makeFilter(ele._primaryKey, value)) >= 0}
                      @click=${() => ele._addFilter(makeFilter(ele._primaryKey, value))}>
  </add-circle-icon-sk>
</div>`);
}

const filterChip = (filter, ele) => html`
<span class=chip>
  <span>${filter}</span>
  <cancel-icon-sk @click=${() => ele._removeFilter(filter)}></cancel-icon-sk>
</span>`;

// can't use <select> and <option> because <option> strips out non-text
// (e.g. checkboxes)
const filters = (ele) => html`
<!-- primary key selector-->
<select-sk class="selector keys"
           @selection-changed=${(e) => ele._primaryKeyChanged(e)}>
  ${ele._filteredPrimaryArr.map((key) => primaryOption(key, ele))}
</select-sk>
<!-- secondary value selector-->
<select-sk class="selector values" disabled>
  ${secondaryOptions(ele)}
</select-sk>`;

const options = (ele) => html`
<div class=options>
  <div class=verbose>
    <checkbox-sk ?checked=${ele._verbose}
                 @click=${ele._toggleVerbose}>
    </checkbox-sk>
    <span>Verbose Entries</span>
  </div>
  <div>TODO datepicker</div>
  <a href=${ele._matchingBotsLink()}>View Matching Bots</a>
  <button
      ?disabled=${!ele.permissions.cancel_task}
      @click=${(e) => alert('use the dialog on the old tasklist UI for now.')}>
    CANCEL ALL TASKS
  </button>
</div>`;

const summaryQueryRow = (ele, count) => html`
<tr>
  <td><a href=${ifDefined(ele._makeSummaryURL(count, true))}>${count.label}</a>:</td>
  <td>${count.value}</td>
</tr>`;

// TODO(kjlubick): show only displayed, total, Success, Failure, Pending, Running
// (deduped?) and hide the rest by default
const summary = (ele) => html`
<div class=summary>
  <div class=title>Selected Tasks</div>
  <table id=query_counts>
    ${summaryQueryRow(ele, {label: 'Displayed', value: ele._tasks.length})}
    ${ele._queryCounts.map((count) => summaryQueryRow(ele, count))}
  </table>
</div>`;

const header = (ele) => html`
<div class=header>
  <div class=filter_box ?hidden=${!ele.loggedInAndAuthorized}>
    <search-icon-sk></search-icon-sk>
    <input id=filter_search class=search type=text
           placeholder='Search filters or supply a filter
                        and press enter'>
    </input>
    <!-- The following div has display:block and divides the above and
         below inline-block groups-->
    <div></div>
    ${filters(ele)}

    ${options(ele)}
  </div>

    ${summary(ele)}
  </div>
</div>
<div class=chip_container>
  ${ele._filters.map((filter) => filterChip(filter, ele))}
</div>`;

const template = (ele) => html`
<swarming-app id=swapp
              client_id=${ele.client_id}
              ?testing_offline=${ele.testing_offline}>
  <header>
    <div class=title>Swarming Task List</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/oldui/tasklist>Old Task List</a>
        <a href=/tasklist>Task List</a>
      </aside>
  </header>
  <!-- Allow clicking anywhere to dismiss the column selector-->
  <main @click=${e => ele._showColSelector && ele._toggleColSelector(e)}>
    <h2 class=message ?hidden=${ele.loggedInAndAuthorized}>${ele._message}</h2>

    ${ele.loggedInAndAuthorized ? header(ele): ''}

    <table class=task-table ?hidden=${!ele.loggedInAndAuthorized}>
      <thead>
        <tr>
          <tr>
          ${col_options(ele, ele._cols[0])}
          <!-- Slice off the first column so we can
               have a custom first box (including the widget to select columns).
            -->
          ${ele._cols.slice(1).map((col) => colHead(col, ele))}
        </tr>
        </tr>
      </thead>
      <tbody>${ele._tasks.map((task) => taskRow(task, ele))}</tbody>
    </table>

  </main>
  <footer></footer>
</swarming-app>`;

// How many items to load on the first load of tasks
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

    this._cols = ['name', 'state', 'bot', 'created_ts', 'pending_time',
                  'duration', 'pool-tag', 'purpose-tag', 'costs_usd']; // purpose has multiple values in the test data

    this._filters = ['alpha:beta', 'gamma:reallyreallyreallyreallylongvalue'];

    this._limit = 0;
    this._showAll = true;

    this._queryCounts = [
      {label: 'Total', value: 90000},
       {label: 'Total', value: 90000},
        {label: 'Total', value: 90000},
         {label: 'Total', value: 90000},
          {label: 'Completed (Failure)', value: 90000},
           {label: 'Completed (Success)', value: 90000},
      {label: 'Total', value: 90000},
       {label: 'Total', value: 90000},
        {label: 'Total', value: 90000},
         {label: 'Total', value: 90000},
          {label: 'Completed (Failure)', value: 90000},
    ];

    this._stateChanged = () => console.log('TODO state changed');

    this._filteredPrimaryArr = ['bedknobs', 'broomsticks'];

    this._possibleColumns = {};

    this._allTags = {};

    this._message = 'You must sign in to see anything useful.';
    this._fetchController = null;
    this._verbose = false;
  }

  _columnSearch(e) {
    if (e.key !== 'Enter') {
      return;
    }
    let input = $$('#column_search', this);
    let newCol = input.value.trim();
    if (!this._possibleColumns[newCol]) {
      errorMessage(`Column "${newCol}" is not valid.`, 5000);
      return;
    }
    input.value = '';
    this._columnQuery = '';
    if (this._cols.indexOf(newCol) !== -1) {
      this._refilterPossibleColumns();
      errorMessage(`Column "${newCol}" already displayed.`, 5000);
      return;
    }
    this._cols.push(newCol);
    this._stateChanged();
    this._refilterPossibleColumns();
  }

  connectedCallback() {
    super.connectedCallback();

    this._loginEvent = (e) => {
      this._fetch();
      this.render();
    };
    this.addEventListener('log-in', this._loginEvent);
  }

  disconnectedCallback() {
    super.disconnectedCallback();

    this.removeEventListener('log-in', this._loginEvent);
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
    // Fetch the tasks
    this.app.addBusyTasks(1);
    let queryParams = `?limit=${INITIAL_LOAD}`; // TODO
    fetch(`/_ah/api/swarming/v1/tasks/list?${queryParams}`, extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._tasks = [];
        const maybeLoadMore = (json) => {
          this._tasks = this._tasks.concat(processTasks(json.items, this._allTags));
          appendPossibleColumns(this._possibleColumns, this._allTags);
          this._filteredPossibleColumns = Object.keys(this._possibleColumns);
          this.render();
          // Special case: Don't load all the tasks when filters is empty to avoid
          // loading many many tasks unintentionally. A user can over-ride this
          // with the showAll button.
          if ((this._filters.length || this._showAll) && json.cursor) {
            this._limit = BATCH_LOAD;
            queryParams = `?limit=${BATCH_LOAD}&json.cursor`; // TODO
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

    // fetch dimensions so we can fill out the filters.
    // We only need to do this once, because we don't expect it to
    // change (much) after the page has been loaded.
    if (!this._fetchedDimensions) {
      this._fetchedDimensions = true;
      this.app.addBusyTasks(1);
      extra = {
        headers: {'authorization': this.auth_header},
        // No signal here because we shouldn't need to abort it.
        // This request does not depend on the filters.
      };
      fetch('/_ah/api/swarming/v1/bots/dimensions', extra)
      .then(jsonOrThrow)
      .then((json) => {
        //this._primaryMap = processPrimaryMap(json.bots_dimensions);
        appendPossibleColumns(this._possibleColumns, json.bots_dimensions);
        this._filteredPossibleColumns = Object.keys(this._possibleColumns);
        //this._primaryArr = Object.keys(this._primaryMap);
        //this._primaryArr.sort();
        //this._filteredPrimaryArr = this._primaryArr.slice();
        this.render();
        this.app.finishedTask();
      })
      .catch((e) => this.fetchError(e, 'bots/dimensions'));
    }
  }

  _makeSummaryURL() {
    return undefined;
  }

  _matchingBotsLink() {
    return 'example.com/botlist';
  }

  _refilterPossibleColumns(e) {
    let input = $$('#column_search', this);
    // If the column selector box is hidden, input will be null
    this._columnQuery = (input && input.value) || '';
    this._filteredPossibleColumns = filterPossibleColumns(Object.keys(this._possibleColumns), this._columnQuery);
    sortPossibleColumns(this._filteredPossibleColumns, this._cols);
    this.render();
  }

  render() {
    // Incorporate any data changes before rendering.
    sortColumns(this._cols);
    super.render();
  }

  _toggleCol(e, col) {
    // This prevents a double event from happening (because of the
    // default 'click' event);
    e.preventDefault();
    // this prevents the click from bubbling up and being seen by the
    // <select-sk>
    e.stopPropagation();
    let idx = this._cols.indexOf(col);
    if (idx >= 0) {
      this._cols.splice(idx, 1);
    } else {
      this._cols.push(col);
    }
    this._refilterPossibleColumns();
    this._stateChanged();
    this.render();
  }

  _toggleColSelector(e) {
    e.preventDefault();
    // Prevent double click event from happening with the
    // click listener on <main>.
    e.stopPropagation();
    this._showColSelector = !this._showColSelector;
    this._refilterPossibleColumns(); // also renders
  }

  _toggleVerbose(e) {
    // This prevents a double event from happening.
    e.preventDefault();
    this._verbose = !this._verbose;
    this._stateChanged();
    this.render();
  }

});
