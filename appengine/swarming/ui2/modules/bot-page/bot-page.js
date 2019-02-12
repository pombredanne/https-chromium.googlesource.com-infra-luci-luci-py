// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { $, $$ } from 'common-sk/modules/dom'
import { html, render } from 'lit-html'

import '../swarming-app'

import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'

/**
 * @module swarming-ui/modules/bot-page
 * @description <h2><code>bot-page<code></h2>
 *
 * <p>
 *   TODO
 * </p>
 *
 * <p>This is a top-level element.</p>
 *
 * @attr client_id - The Client ID for authenticating via OAuth.
 * @attr testing_offline - If true, the real OAuth flow won't be used.
 *    Instead, dummy data will be used. Ideal for local testing.
 */

const template = (ele) => html`
<swarming-app id=swapp
              client_id=${ele.client_id}
              ?testing_offline=${ele.testing_offline}>
  <header>
    <div class=title>Swarming Task Page</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/tasklist>Task List</a>
        <a href="/oldui/bot?id=${ele._botId}">Old Bot Page</a>
        <a href=/task>Task Page</a>
      </aside>
  </header>
  <main class="horizontal layout wrap">
    <h2 class=message ?hidden=${ele.loggedInAndAuthorized}>${ele._message}</h2>

    <div class=id_buttons>
      <input id=id_input placeholder="Bot ID" @change=${ele._updateID}></input>
      <span class=message>Enter a Bot ID to get started.</span>
    </div>
    <div>hello world</div>
  </main>
  <footer></footer>
</swarming-app>
`;

window.customElements.define('bot-page', class extends SwarmingAppBoilerplate {

  constructor() {
    super(template);

    // Set empty values to allow empty rendering while we wait for
    // stateReflector (which triggers on DomReady). Additionally, these values
    // help stateReflector with types.
    this._botId = '';

    this._stateChanged = () => console.log('TODO');

    this._message = 'You must sign in to see anything useful.';
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
    if (!this.loggedInAndAuthorized || !this._urlParamsLoaded || !this._botId) {
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
      headers: {'authorization': this.auth_header},
      signal: this._fetchController.signal,
    };
    //this.app.addBusyTasks(1);
    // TODO
  }

  render() {
    super.render();
    const idInput = $$('#id_input', this);
    idInput.value = this._botId;
  }

  _updateID(e) {
    const idInput = $$('#id_input', this);
    this._taskId = idInput.value;
    this._stateChanged();
    this._fetch();
    this.render();
  }
});
