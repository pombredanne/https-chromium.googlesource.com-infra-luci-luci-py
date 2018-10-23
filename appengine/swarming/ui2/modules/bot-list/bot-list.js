// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

/** @module swarming-ui/modules/bot-list
 * @description <h2><code>bot-list</code></h2>
 *
 * <p>
 *  Bot List shows a filterable list of all bots in the fleet.
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
import { jsonOrThrow } from 'common-sk/modules/jsonOrThrow'
import naturalSort from 'javascript-natural-sort/naturalSort'
import { stateReflector } from 'common-sk/modules/stateReflector'

import 'elements-sk/checkbox-sk'
import 'elements-sk/error-toast-sk'
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

import { stableSort } from '../util'
import { aggregateTemps, attribute, botLink, column, colHeaderMap,
         devices, extraKeys, filterBots, filterPossibleColumns, filterPossibleKeys, filterPossibleValues, fromDimension, fromState, initCounts,
         listQueryParams, longestOrAll, makeFilter, processBots, processCounts,
         processDimensions, processPrimaryMap, sortColumns, sortPossibleColumns,
         specialSortMap, taskLink } from './bot-list-helpers'
import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'

const colHead = (col, ele) => html`
<th>${colHeaderMap[col] || col}
  <sort-toggle .key=${col} .currentKey=${ele._sort} .direction=${ele._dir}>
  </sort-toggle>
</th>`;

const botCol = (col, bot, ele) => html`
<td>${column(col, bot, ele)}</td>`;

const botRow = (bot, ele) => html`
<tr class="bot-row ${ele._botClass(bot)}">
  <td class=no_outline></td>
  ${ele._cols.map((col) => botCol(col,bot,ele))}
</tr>`;

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
  return values.map((value) =>
    html`
<div class=item>
  <span class=value>${value}</span>
  <span class=flex></span>
  <add-circle-icon-sk ?hidden=${ele._filters.indexOf(makeFilter(ele._primaryKey, value)) >= 0}
                      @click=${() => ele._addFilter(ele._primaryKey, value)}>
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
           @selection-changed=${(e) => ele._primayKeyChanged(e)}>
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
                 @click=${(e) => ele._toggleVerbose(e)}>
    </checkbox-sk>
    <span>Verbose Entries</span>
  </div>
  <!-- TODO(kjlubick): have something like sk-input -->
  <input placeholder="limit"></input>
  <a href="https://example.com">View Matching Tasks</a>
  <!-- TODO(kjlubick): Only make this button appear for admins -->
  <button @click=${(e) => alert('not implemented yet')}>
    DELETE ALL DEAD BOTS
  </button>
</div>`;

const summaryFleetRow = (count) => html`
<tr>
  <td><a href="/TODO">${count.label}</a>:</td>
  <td>${count.value}</td>
</tr>`;

const summaryQueryRow = (count) => html`
<tr>
  <td><a href="/TODO">${count.label}</a>:</td>
  <td>${count.value}</td>
</tr>`;

// TODO(kjlubick): This could maybe be a generic helper function.
const fleetCountsToggle = (ele) => {
  let toggle = (e) => {
    e.preventDefault();
    e.stopPropagation();
    ele._showFleetCounts = !ele._showFleetCounts;
    ele.render();
  }
  if (ele._showFleetCounts) {
    return html`<expand-less-icon-sk @click=${toggle}></expand-less-icon-sk>`;
  } else {
    return html`<expand-more-icon-sk @click=${toggle}></expand-more-icon-sk>`;
  }
};

const summary = (ele) => html`
<div id=fleet_header class=title>
  <span>Fleet</span>
  ${fleetCountsToggle(ele)}
</div>
<table id=fleet_counts ?hidden=${!ele._showFleetCounts}>
  ${ele._fleetCounts.map((count) => summaryFleetRow(count))}
</table>
<div class=title>Selected</div>
<table id=query_counts>
  ${ele._queryCounts.map((count) => summaryQueryRow(count))}
</table>`;

const header = (ele) => html`
<div class=header>
  <div class=filter_box ?hidden=${!ele.loggedInAndAuthorized}>
    <!-- TODO(kjlubick): have something like sk-input -->
    <search-icon-sk></search-icon-sk>
    <input id=filter_search class=search type=text
           placeholder='Search filters or supply a filter
                        and press enter'
           @input=${e => ele._refilterPrimaryKeys(e)}
           @keyup=${e => ele._filterSearch(e)}>
    </input>
    <!-- The following div has display:block and divides the above and
         below inline-block groups-->
    <div></div>
    ${filters(ele)}

    ${options(ele)}
  </div>

  <div class=summary>
    ${summary(ele)}
  </div>
</div>
<div class=chip_container>
  ${ele._filters.map((filter) => filterChip(filter, ele))}
</div>`;

const columnOption = (key, ele) => html`
<div class=item>
  <span class=key>${key}</span>
  <span class=flex></span>
  <checkbox-sk ?checked=${ele._cols.indexOf(key) >= 0}
               ?disabled=${ele._forcedColumns.indexOf(key) >= 0}
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
         @keyup=${e => ele._columnSearch(e)}>>
  </input>
  ${ele._filteredPossibleColumns.map((key) => columnOption(key, ele))}
</div>`;
}

const col_options = (ele) => html`
<!-- Put the click action here to make it bigger, especially for mobile.-->
<th class=col_options @click=${e => ele._toggleColSelector(e)}>
  <more-vert-icon-sk></more-vert-icon-sk>
  ${col_selector(ele)}
</th>`;

const template = (ele) => html`
<swarming-app id=swapp
              client_id=${ele.client_id}
              ?testing_offline=${ele.testing_offline}>
  <header>
    <div class=title>Swarming Bot List</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/tasklist>Task List</a>
      </aside>
  </header>
  <!-- Allow clicking anywhere to dismiss the column selector-->
  <main @click=${e => ele._showColSelector && ele._toggleColSelector(e)}>
    <h2 class=message ?hidden=${ele.loggedInAndAuthorized}>${ele._message}</h2>

    ${ele.loggedInAndAuthorized ? header(ele): ''}

    <table class=bot-table ?hidden=${!ele.loggedInAndAuthorized}>
      <thead>
        <tr>
          ${col_options(ele)}
          ${ele._cols.map((col) => colHead(col,ele))}
        </tr>
      </thead>
      <tbody>${ele._sortBots().map((bot) => botRow(bot,ele))}</tbody>
    </table>
  </main>
  <footer><error-toast-sk></error-toast-sk></footer>
</swarming-app>`;

window.customElements.define('bot-list', class extends SwarmingAppBoilerplate {

  constructor() {
    super(template);
    this._bots = [];
    this._forcedColumns = ['id'];
    // Set empty values to allow empty rendering while we wait for
    // stateReflector (which triggers on DomReady). Additionlly, these values
    // help stateReflector with types.
    this._cols = [];
    this._dir = '';
    this._filters = [];
    this._limit = 0; // _limit 0 is a sentinel value for _fetch()
                     // We won't actually make a request if _limit is 0.
    this._sort = '';
    this._primaryKey = '';
    this._verbose = false;
    this._showFleetCounts = false;

    this._fleetCounts = initCounts();
    this._queryCounts = initCounts();

    this._stateChanged = stateReflector(
      /*getState*/() => {
        return {
          // provide empty values
          'c': this._cols,
          'd': this._dir,
          'f': this._filters,
          'k': this._primaryKey,
          'l': this._limit,
          's': this._sort,
          'v': this._verbose,
          'e': this._showFleetCounts, // 'e' because 'f', 'l', are taken
        }
    }, /*setState*/(newState) => {
      // default values if not specified.
      this._cols = newState.c;
      if (!newState.c.length) {
        this._cols = ['id', 'task', 'os', 'status'];
      }
      this._dir = newState.d || 'asc';
      this._filters = newState.f; // default to []
      this._primaryKey = newState.k; // default to ''
      this._limit = newState.l || 100; // TODO(kjlubick): add limit UI element
      this._sort = newState.s || 'id';
      this._verbose = newState.v;         // default to false
      this._showFleetCounts = newState.e; // default to false
      this._fetch();
      this.render();
    });

    /** _primaryArr: Array<String>, the display order of the primaryKeys, that is,
        anything that can be searched/filtered by. */
    this._primaryArr = [];
    this._filteredPrimaryArr = [];
    this._possibleColumns = [];
    this._filteredPossibleColumns = [];
    /** _primaryMap: Object, a mapping of primary keys to secondary items.
        The primary keys are things that can be columns or sorted by.  The
        primary values (aka the secondary items) are things that can be filtered
        on. Primary consists of dimensions and state.  Secondary contains the
        values primary things can be.*/
    this._primaryMap = {};
    this._dimensions = [];
    this._message = 'You must sign in to see anything useful.';
    this._showColSelector = false;
    this._columnQuery = '';
    this._filterQuery = '';
  }

  connectedCallback() {
    super.connectedCallback();

    this.addEventListener('log-in', (e) => {
      this._fetch();
      this.render();
    });

    this.addEventListener('sort-change', (e) => {
      this._sort = e.detail.key;
      this._dir = e.detail.direction;
      this.render();
    });
  }

  _addFilter(key, value) {
    let filter = makeFilter(key, value);
    if (this._filters.indexOf(filter) >= 0) {
      return;
    }
    this._filters.push(filter);
    // pre-filter what we have
    this._bots = filterBots(this._filters, this._bots);
    // go fetch for all the bots that match the new filters.
    this._fetch();
    // render what we have now.  When _fetch() resolves it will
    // re-render.
    this.render();
  }

  _botClass(bot) {
    let classes = '';
    if (bot.is_dead) {
      classes += 'dead ';
    }
    if (bot.quarantined) {
      classes += 'quarantined ';
    }
    if (bot.maintenance_msg) {
      classes += 'maintenance ';
    }
    if (bot.version !== this.server_details.server_version) {
      classes += 'old_version';
    }
    return classes;
  }

  _columnSearch(e) {
    if (e.key !== 'Enter') {
      return;
    }
    let input = $$('#column_search', this);
    let newCol = input.value.trim();
    if (this._possibleColumns.indexOf(newCol) === -1) {
      errorMessage(`Column "${newCol}" is not valid.`, 5000);
      return;
    }
    input.value = '';
    this._columnQuery = '';
    if (this._cols.indexOf(newCol) !== -1) {
      this.render();
      errorMessage(`Column "${newCol}" already displayed.`, 5000);
      return;
    }
    this._cols.push(newCol);
    this.render();
  }

  _fetch() {
    // limit of 0 is a sentinel value. See constructor for more details.
    if (!this.loggedInAndAuthorized || !this._limit) {
      return;
    }
    let extra = {
      headers: {'authorization': this.auth_header}
    };
    // Fetch the bots
    this.app.addBusyTasks(1);
    // TODO(kjlubick): support paging
    let queryParams = listQueryParams(this._filters, this._limit);
    fetch('/_ah/api/swarming/v1/bots/list?' + queryParams, extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._bots = processBots(json.items);
        this.render();
        this.app.finishedTask();
      })
      .catch((e) => this.fetchError(e, 'bots/list'));

    this.app.addBusyTasks(1);
    // We can re-use the query params from listQueryParams because
    // the backend will ignore those it doesn't understand (e.g limit
    // and is_dead, etc).
    fetch('/_ah/api/swarming/v1/bots/count?' + queryParams, extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._queryCounts = processCounts(this._queryCounts, json);
        this.render();
        this.app.finishedTask();
      })
      .catch((e) => this.fetchError(e, 'bots/count (query)'));

    // We only need to do this once, because we don't expect it to
    // change (much) after the page has been loaded.
    if (!this._fleetCounts._queried) {
      this._fleetCounts._queried = true;
      this.app.addBusyTasks(1);
      fetch('/_ah/api/swarming/v1/bots/count', extra)
        .then(jsonOrThrow)
        .then((json) => {
          this._fleetCounts = processCounts(this._fleetCounts, json);
          this.render();
          this.app.finishedTask();
        })
        .catch((e) => this.fetchError(e, 'bots/count (fleet)'));
    }

    // Fetch _dimensions so we can fill out the filters.
    // We only need to do this once, because we don't expect it to
    // change (much) after the page has been loaded.
    if (!this._dimensions.length) {
      this.app.addBusyTasks(1);
      // Only need to fetch this once.
      fetch('/_ah/api/swarming/v1/bots/dimensions', extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._dimensions = processDimensions(json.bots_dimensions);
        this._primaryMap = processPrimaryMap(json.bots_dimensions);
        this._possibleColumns = this._dimensions.concat(extraKeys);
        this._filteredPossibleColumns = this._possibleColumns.slice();
        this._primaryArr = Object.keys(this._primaryMap);
        this._primaryArr.sort();
        this._filteredPrimaryArr = this._primaryArr.slice();
        this.render();
        this.app.finishedTask();
      })
      .catch((e) => this.fetchError(e, 'bots/dimensions'));
    }
  }

  _filterSearch(e) {
    if (e.key !== 'Enter') {
      return;
    }
    let input = $$('#filter_search', this);
    let newFilter = input.value.trim();
    if (newFilter.indexOf(':') === -1) {
      errorMessage('Invalid filter.  Should be like "foo:bar"', 5000);
      return;
    }
    input.value = '';
    this._filterQuery = '';
    this._primaryKey = '';
    if (this._filters.indexOf(newFilter) !== -1) {
      this._refilterPrimaryKeys();
      errorMessage(`Filter "${newFilter}" is already active`, 5000);
      return;
    }
    this._filters.push(newFilter);
    this._refilterPrimaryKeys();
  }

  _primayKeyChanged(e) {
    this._primaryKey = this._filteredPrimaryArr[e.detail.selection];
    this.render();
  }

  _refilterPossibleColumns(e) {
    let input = $$('#column_search', this);
    // If the column selector box is hidden, input will be null
    this._columnQuery = (input && input.value) || '';
    this._filteredPossibleColumns = filterPossibleColumns(this._possibleColumns, this._columnQuery);
    sortPossibleColumns(this._filteredPossibleColumns, this._cols);
    this.render();
  }

  _refilterPrimaryKeys(e) {
    this._filterQuery = $$('#filter_search', this).value;

    this._filteredPrimaryArr = filterPossibleKeys(this._primaryArr, this._primaryMap, this._filterQuery);
    // Update the selected to be the current one (if it is still with being
    // shown) or the first match.  This saves the user from having to click
    // the first result before seeing results.
    if (this._filterQuery && this._filteredPrimaryArr.length > 0 &&
        this._filteredPrimaryArr.indexOf(this._primaryKey) === -1) {
      this._primaryKey = this._filteredPrimaryArr[0];
    }

    this.render();
  }

  _removeFilter(filter) {
    let idx = this._filters.indexOf(filter);
    if (idx === -1) {
      return;
    }
    this._filters.splice(idx, 1);
    this._fetch();
    this.render();
  }

  render() {
    // Incorporate any data changes before rendering.
    sortColumns(this._cols);
    this._stateChanged();
    super.render();
  }

  /* sort the internal set of bots based on the sort-toggle and direction
   * and returns it (for use in templating) */
  _sortBots() {
    stableSort(this._bots, (botA, botB) => {
      let sortOn = this._sort;
      if (!sortOn) {
        return 0;
      }
      let dir = 1;
      if (this._dir === 'desc') {
        dir = -1;
      }
      let sorter = specialSortMap[sortOn];
      if (sorter) {
        return sorter(dir, botA, botB);
      }
      // Default to a natural compare of the columns.
      let aCol = column(sortOn, botA, this);
      if (aCol === 'none'){
        // put "none" at the bottom of the sort order
        aCol = 'ZZZ';
      }
      let bCol = column(sortOn, botB, this);
      if (bCol === 'none'){
        // put "none" at the bottom of the sort order
        bCol = 'ZZZ';
      }
      return dir * naturalSort(aCol, bCol);
    });
    return this._bots;
  }

  _toggleCol(e, col) {
    if (this._forcedColumns.indexOf(col) >= 0) {
      return;
    }
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
    this.render();
  }

});
