import { html, render } from 'lit-html/lib/lit-extended'
import { upgradeProperty } from 'elements-sk/upgradeProperty'


const button_template = document.createElement('template');
button_template.innerHTML =`
<button class=toggle-button>
  <icon-menu-sk>
  </icon-menu-sk>
</button>
`

const login_template = (ele) => html`
<oauth-login client_id=${ele.client_id} testing_offline=${ele.testing_offline}></oauth-login>
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
  set testing_offline(val) {
    // If testing_offline gets passed through multiple layers, it ends up the
    // string 'false'
    if (val && val !== 'false') {
      this.setAttribute('testing_offline', true);
    } else {
      this.removeAttribute('testing_offline');
    }
  }

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

    let spacer = document.createElement('span');
    spacer.classList.add('grow');
    header.appendChild(spacer);

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
