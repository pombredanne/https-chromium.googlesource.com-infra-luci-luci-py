
// TODO(kjlubick): move this to common
function upgradeProperty(ele, prop) {
  if (ele.hasOwnProperty(prop)) {
    let value = ele[prop];
    delete ele[prop];
    ele[prop] = value;
  }
}

const iconSkTemplate = document.createElement('template');
iconSkTemplate.innerHTML = `<svg class="icon-sk-svg" viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false">
  <g><path d=""></path></g>
</svg>`;

class IconSk extends HTMLElement {
  connectedCallback() {
    let icon = iconSkTemplate.content.cloneNode(true);
    icon.querySelector('path').setAttribute('d', this.constructor._path);
    this.appendChild(icon);
  }
}

// TODO(kjlubick): move this to common or import it from Skia
window.customElements.define('icon-menu-sk', class extends IconSk {
  static get _path() { return "M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"; }
});

//==========================================================

import { html, render } from 'lit-html/lib/lit-extended'


const button_template = document.createElement('template');
button_template.innerHTML =`
<button class=toggle-button>
  <icon-menu-sk>
  </icon-menu-sk>
</button>
`

const login_template = (ele) => html`
<div>${ele.client_id} login, is offline: ${ele.testing_offline}</div>
`

window.customElements.define('swarming-app', class extends HTMLElement {
  connectedCallback() {
    upgradeProperty(this, 'client_id');
    upgradeProperty(this, 'testing_offline');
    this._addHTML();
    this._render();
  }

  static get observedAttributes() {
    return ['client_id', 'testing_offline'];
  }

  get client_id() { return this.getAttribute('client_id')}
  set client_id(val) { return this.setAttribute('client_id', val)}

  get testing_offline() { return this.getAttribute('testing_offline')}
  set testing_offline(val) { return this.setAttribute('testing_offline', val)}

  _addHTML() {
    let header = this.querySelector('header');
    let sidebar = header && header.querySelector('aside');
    if (!(header && sidebar && sidebar.classList.contains('hideable'))) {
      return;
    }
    // Add the collapse button to the header as the first item.
    let btn = button_template.content.cloneNode(true);
    // btn is a document-fragment, so we need to insert it into the
    // DOM to make it "expand" into a real button.
    header.insertBefore(btn, header.firstElementChild);
    btn = header.firstElementChild
    btn.addEventListener('click', (e) => this._toggleMenu(e, sidebar));

    this._loginEle = document.createElement('div');
    header.appendChild(this._loginEle);
  }

  _toggleMenu(e, sidebar) {
    sidebar.classList.toggle('shown');
  }

  _render() {
    if (this._loginEle) {
      render(login_template(this), this._loginEle);
    }
  }

  attributeChangedCallback(attrName, oldVal, newVal) {
    this._render();
  }

});
