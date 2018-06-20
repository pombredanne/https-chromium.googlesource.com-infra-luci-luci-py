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


import { errorMessage } from 'common-sk/modules/errorMessage'
import { html, render } from 'lit-html/lib/lit-extended'
import { jsonOrThrow } from 'common-sk/modules/jsonOrThrow'
import naturalSort from 'javascript-natural-sort/naturalSort'

import { stableSort } from '../util'
import { aggregateTemps, attribute, botLink, column, colHeaderMap,
         devices, fromDimension, fromState, longestOrAll, processBots,
         specialSortMap, taskLink } from './bot-list-helpers'
import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'

const colHead = (col, ele) => html`
<th>${colHeaderMap[col] || col}
  <sort-toggle key=${col} current=${ele._sort} direction=${ele._dir}></sort-toggle>
</th>
`;

const botCol = (col, bot, ele) => html`
<td>${column(col, bot, ele)}</td>
`;

const botRow = (bot, ele) => html`
<tr class$="bot-row ${ele._botClass(bot)}">${ele._cols.map((col) => botCol(col,bot,ele))}</tr>
`;

const template = (ele) => html`
<swarming-app id=swapp
              client_id=${ele.client_id}
              testing_offline=${ele.testing_offline}>
  <header>
    <div class=title>Swarming Server</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/tasklist>Task List</a>
      </aside>
  </header>
  <main>
    <h1> Hello Botlist</h1>

    <table class=bot-table>
    <!-- TODO(kjlubick) maybe use repeat instead of map here, at least for the body-->
    <!-- https://github.com/Polymer/lit-html#repeatitems-keyfn-template-->
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
    // TODO(kjlubick): pull these from url params
    this._cols = ['id', 'task', 'os', 'status'];
    this._limit = 100;
    this._sort = 'id';
    this._dir = 'asc';
    this._verbose = false;
  }

  connectedCallback() {
    super.connectedCallback();

    this.addEventListener('log-in', (e) => {
      this._auth_header = e.detail.auth_header;
      this._update();
    });

    this.addEventListener('sort-change', (e) => {
      console.log('saw sort-change', e.detail);
      this._sort = e.detail.key;
      this._dir = e.detail.direction;
      this.render();
    });

    // TODO(kjlubick): pipe this in via swarming-app
    this._serverVersion = "888035583d659dbf017e4ddcda0054a8d5cec814";

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
    if (bot.version !== this._serverVersion) {
      classes += 'old_version';
    }
    return classes;
  }

  /* sort the internal set of bots based on the sort-toggle and direction
   * and returns it (for use in templating) */
  _sortBots() {
    console.time('_sortBots');
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
    console.timeEnd('_sortBots');
    return this._bots;
  }

  _update() {
    if (!this._auth_header) {
      return;
    }
    let extra = {
      headers: {'authorization': this._auth_header}
    };
    let app = this.firstElementChild;
    app.addBusyTasks(1);
    // TODO(kjlubick): need query params
    fetch('/_ah/api/swarming/v1/bots/list', extra)
      .then(jsonOrThrow)
      .then((json) => {
        this._bots = processBots(json.items);
        this.render();
        app.finishedTask();
      })
      .catch((e) => {
        console.error(e);
        errorMessage(e);
        app.finishedTask();
      })
  }

});