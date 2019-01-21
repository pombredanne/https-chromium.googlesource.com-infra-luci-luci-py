// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { html, render } from 'lit-html'

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

const template = (ele) => html`
<div>hello world</div>
`;

window.customElements.define('task-page', class extends SwarmingAppBoilerplate {

  constructor() {
    super(template);
  }

  connectedCallback() {
    this.render();
  }

  render() {
    super.render();
  }

});