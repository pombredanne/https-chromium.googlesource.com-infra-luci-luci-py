function upgradeProperty(ele, prop) {
  if (ele.hasOwnProperty(prop)) {
    let value = ele[prop];
    delete ele[prop];
    ele[prop] = value;
  }
}

//==========================================================

import { html, render } from 'lit-html/lib/lit-extended'

const template = (ele) => {
  if (ele.access_token) {
    return html`
<div>
  <img class=center id=avatar src="${ele.profile.imageURL}" width="30" height="30">
  <span class=center>${ele.profile.email}</span>
  <span class=center>|</span>
  <a class="center" on-click=${()=>ele._logOut()} href="#">Sign out</a>
</div>`
  } else {
    return html`
<div>
  <a on-click=${()=>ele._logIn()} href="#">Sign in</a>
</div>`
  }

}

window.customElements.define('oauth-login', class extends HTMLElement {

  connectedCallback() {
    upgradeProperty(this, 'client_id');
    upgradeProperty(this, 'testing_offline');
    if (this.testing_offline) {
      this.access_token = '';//'12345678910-boomshakalaka';
      this.profile = {
        email: 'missing@chromium.org',
        imageURL: 'http://storage.googleapis.com/gd-wagtail-prod-assets/original_images/logo_google_fonts_color_2x_web_64dp.png',
      }
    } else {
      // idk yet
    }
    this._render();
  }

  static get observedAttributes() {
    return ['client_id', 'testing_offline'];
  }

  get client_id() { return this.getAttribute('client_id')}
  set client_id(val) { return this.setAttribute('client_id', val)}

  get testing_offline() { return this.getAttribute('testing_offline')}
  set testing_offline(val) { return this.setAttribute('testing_offline', val)}

  _logIn() {
    if (this.testing_offline) {
        this.access_token = '12345678910-boomshakalaka';
        this.dispatchEvent(new CustomEvent('log-in', {'access_token': this.access_token}));
        this._render();
      } else {
        // idk
      }
  }

  _logOut() {
    if (this.testing_offline) {
      this.access_token = '';
      this._render();
    } else {
      // idk
    }
  }

  _render() {
    render(template(this), this);
  }

  attributeChangedCallback(attrName, oldVal, newVal) {
    this._render();
  }

});
