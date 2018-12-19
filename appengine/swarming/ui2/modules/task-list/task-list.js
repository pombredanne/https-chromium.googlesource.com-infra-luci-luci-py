import { $, $$ } from 'common-sk/modules/dom'
import { errorMessage } from 'elements-sk/errorMessage'
import { html, render } from 'lit-html'
import { ifDefined } from 'lit-html/directives/if-defined';
import { jsonOrThrow } from 'common-sk/modules/jsonOrThrow'
import naturalSort from 'javascript-natural-sort/naturalSort'
import * as query from 'common-sk/modules/query'
import { stateReflector } from 'common-sk/modules/stateReflector'

import '../swarming-app'

import SwarmingAppBoilerplate from '../SwarmingAppBoilerplate'

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

    Yo
  </main>
  <footer></footer>
</swarming-app>`;


window.customElements.define('task-list', class extends SwarmingAppBoilerplate {

  constructor() {
    super(template);
  }

  connectedCallback() {
    super.connectedCallback();

    this.addEventListener('log-in', (e) => {
      this.render();
    });
  }

  render() {
    // Incorporate any data changes before rendering.
    super.render();
  }

});
