// Copyright 2019 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { html, render } from 'lit-html'

/**
 * @module swarming-ui/modules/stacked-time-chart
 * @description <h2><code>stacked-time-chart<code></h2>
 *
 * <p>
 *   TODO
 * </p>
 *
 */

const template = (ele) => html`
<div> hello world </div>
`;

window.customElements.define('stacked-time-chart', class extends HTMLElement {

  constructor() {
    super();
  }

  connectedCallback() {
    this.render();
  }

  render() {
    render(template(this), this, {eventContext: this});
  }

});
