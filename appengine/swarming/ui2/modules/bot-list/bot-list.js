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
 *
 */

import { html, render } from 'lit-html'
import { jsonOrThrow } from 'common-sk/modules/jsonOrThrow'
import naturalSort from 'javascript-natural-sort/naturalSort'
import { stateReflector } from 'common-sk/modules/stateReflector'

import 'common-sk/modules/select-sk'
import 'elements-sk/checkbox-sk'
import 'elements-sk/icon/arrow-forward-icon-sk'
import 'elements-sk/icon/remove-circle-outline-icon-sk'

import { stableSort } from '../util'
import { aggregateTemps, attribute, botLink, column, colHeaderMap,
         devices, extraKeys, fromDimension, fromState, listQueryParams,
         longestOrAll, makeFilter, processBots, processDimensions,
         processPrimaryMap, sortColumns, sortKeys, specialSortMap, taskLink } from './bot-list-helpers'
import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'

const colHead = (col, ele) => html`
<th>${colHeaderMap[col] || col}
  <sort-toggle .key=${col} .current=${ele._sort} .direction=${ele._dir}></sort-toggle>
</th>
`;

const botCol = (col, bot, ele) => html`
<td>${column(col, bot, ele)}</td>
`;

const botRow = (bot, ele) => html`
<tr class="bot-row ${ele._botClass(bot)}">${ele._cols.map((col) => botCol(col,bot,ele))}</tr>
`;

const primaryOption = (key, ele) => html`
<div class=item ?selected=${ele._primaryKey === key}>
  <span class=key>${key}</span>
  <span class=flex></span>
  <checkbox-sk ?checked=${ele._cols.indexOf(key) >= 0}
               ?disabled=${ele._forcedColumns.indexOf(key) >= 0}
               @click=${(e) => ele._toggleCol(e, key)}>
  </checkbox-sk>
</div>
`

const secondaryOptions = (ele) => {
  if (!ele._primaryKey) {
    return '';
  }
  let values = ele._primaryMap[ele._primaryKey];
  if (!values) {
    return html`<div class="information_only">Only dimensions can be used for filtering.
<i>${ele._primaryKey}</i> is a part of the bot's state and is informational only.</div>`
  }
  return values.map((value) =>
  html`<div class=item>
  <span class=value>${value}</span>
  <span class=flex></span>
  <arrow-forward-icon-sk ?hidden=${ele._filters.indexOf(makeFilter(ele._primaryKey, value)) >= 0}
                         @click=${() => ele._addFilter(ele._primaryKey, value)}>
  </arrow-forward-icon-sk>
</div>`)
}


const filterOption = (filter, ele) => html`
<div class=item>
  <span class=filter>${filter}</span>
  <span class=flex></span>
  <remove-circle-outline-icon-sk @click=${() => ele._removeFilter(filter)}>
  </remove-circle-outline-icon-sk>
</div>
`

// can't use <select> and <option> because <option> strips out non-text (e.g. checkboxes)
const filters = (ele) => html`
<!-- primary key selector-->
<select-sk class="selector keys" @selection-changed=${(e) => ele._primayKeyChanged(e)}>
  ${ele._primaryArr.map((key) => primaryOption(key, ele))}
</select-sk>
<!-- secondary value selector-->
<select-sk class="selector values" disabled>
  ${secondaryOptions(ele)}
</select-sk>
<!-- filters selector-->
<select-sk class="selector filters" disabled>
  ${ele._filters.map((filter) => filterOption(filter, ele))}
</select-sk>
`

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
  <main>
    <h2 class=message ?hidden=${ele.loggedInAndAuthorized}>${ele._message}</h2>

    ${ele.loggedInAndAuthorized ? filters(ele): ''}

    <table class=bot-table ?hidden=${!ele.loggedInAndAuthorized}>
      <thead><tr>${ele._cols.map((col) => colHead(col,ele))}</tr></thead>
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
    // We make _stateChanged a no-op until after the first
    // setState is called (which happens after DomReady)
    // Otherwise, we overwrite the url params with the default values on the
    // first call to render().
    this._stateChanged = () => false;
    let stateChanged = stateReflector(
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
      this._verbose = newState.v; // default to false TODO(kjlubick): add verbose UI element
      this._fetch();
      // Now that the values have been read from the URL, allow
      // enable this._stateChanged to write the state to the URL.
      this._stateChanged = stateChanged;
      this.render();
    });


    /** _primaryArr: Array<String>, the display order of the primary keys.
        This is dimensions, then bot properties, then elements from bot.state. */
    this._primaryArr = [];
    /** _primaryMap: Object, a mapping of primary keys to secondary items.
        The primary keys are things that can be columns or sorted by.  The
        primary values (aka the secondary items) are things that can be filtered
        on. Primary consists of dimensions and state.  Secondary contains the
        values primary things can be.*/
    this._primaryMap = {};
    this._dimensions = [];
    this._message = 'You must sign in to see anything useful.';
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

    this.render();
  }

  _addFilter(key, value) {
    let filter = makeFilter(key, value);
    if (this._filters.indexOf(filter) >= 0) {
      return;
    }
    this._filters.push(filter);
    this._fetch();
    // TODO(kjlubick): Filter the bots we have until the ones
    // arrive from the server.
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

  _fetch() {
    // limit of 0 is a sentinel value. See constructor for more details.
    if (!this.loggedInAndAuthorized || !this._limit) {
      return;
    }
    let extra = {
      headers: {'authorization': this.auth_header}
    };
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
    if (!this._dimensions.length) {
      this.app.addBusyTasks(1);
      // Only need to fetch this once.
      fetch('/_ah/api/swarming/v1/bots/dimensions', extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._dimensions = processDimensions(json.bots_dimensions);
        this._primaryMap = processPrimaryMap(json.bots_dimensions);
        this._primaryArr = this._dimensions.concat(extraKeys);
        this.render();
        this.app.finishedTask();
      })
      .catch((e) => this.fetchError(e, 'bots/dimensions'));
    }
  }

  _primayKeyChanged(e) {
    this._primaryKey = this._primaryArr[e.detail.selection];
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
    sortKeys(this._primaryArr, this._cols);
    sortColumns(this._cols);
    this._stateChanged();
    super.render();
  }

  /* sort the internal set of bots based on the sort-toggle and direction
   * and returns it (for use in templating) */
  _sortBots() {
    //console.time('_sortBots');
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
      var bCol = column(sortOn, botB, this);
      if (bCol === 'none'){
        // put "none" at the bottom of the sort order
        bCol = 'ZZZ';
      }
      return dir * naturalSort(aCol, bCol);
    });
    //console.timeEnd('_sortBots');
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

});
