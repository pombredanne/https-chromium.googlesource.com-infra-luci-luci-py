// Copyright 2018 The LUCI Authors. All rights reserved.
// Use of this source code is governed under the Apache License, Version 2.0
// that can be found in the LICENSE file.

import { html, render } from 'lit-html/lib/lit-extended'
import { upgradeProperty } from 'elements-sk/upgradeProperty'

import 'elements-sk/icon/arrow-drop-down-icon-sk'
import 'elements-sk/icon/arrow-drop-up-icon-sk'

// Looks to properties set, then attributes to initialize ele[prop]
// using the proper setters.  Optionally removes the attr to avoid stale data.
function initPropertyFromAttrOrProperty(ele, prop, removeAttr=true) {
  upgradeProperty(ele, prop);
  if (ele[prop] === undefined && ele.hasAttribute(prop)) {
    ele[prop] = ele.getAttribute(prop);
    if (removeAttr) {
      ele.removeAttribute(prop);
    }
  }
}

const template = (ele) => html`
<arrow-drop-down-icon-sk hidden?=${ele.key === ele.current && ele.direction === 'asc'}></arrow-drop-down-icon-sk>
<arrow-drop-up-icon-sk hidden?=${ele.key === ele.current && ele.direction === 'desc'}></arrow-drop-up-icon-sk>
`

window.customElements.define('sort-toggle', class extends HTMLElement {

  constructor() {
    super()
    // _current, _name, _direction are private members
  }

  connectedCallback() {
    initPropertyFromAttrOrProperty(this, 'current');
    initPropertyFromAttrOrProperty(this, 'key');
    initPropertyFromAttrOrProperty(this, 'direction');

    this.addEventListener('click', () => {
      this.toggle();
    });
  }

  get current() { return this._current; }
  set current(val) { this._current = val; this.render();}

  get key() { return this._key; }
  set key(val) { this._key = val; this.render();}

  get direction() { return this._direction; }
  set direction(val) { this._direction = val; this.render();}

  toggle() {
    if (this.direction === 'asc') {
      this.direction = 'desc';
    } else {
      this.direction = 'asc';
    }
    this.dispatchEvent(new CustomEvent('sort-change', {
      detail: {
        'direction': this.direction,
        'key': this.key,
      },
      bubbles: true,
    }));
  }

  render() {
    render(template(this), this);
  }

});