import { html, render } from 'lit-html/lib/lit-extended'
import { upgradeProperty } from 'elements-sk/upgradeProperty'

export default class SwarmingAppBoilerplate extends HTMLElement {

  constructor(template) {
    super();
    this._template = template;
  }

  connectedCallback() {
    upgradeProperty(this, 'client_id');
    upgradeProperty(this, 'testing_offline');
  }

  static get observedAttributes() {
    return ['client_id', 'testing_offline'];
  }

  /** @prop {string} client_id Mirrors the attribute 'client_id'. */
  get client_id() { return this.getAttribute('client_id');}
  set client_id(val) {return this.setAttribute('client_id', val);}

  /** @prop {bool} testing_offline Mirrors the attribute 'testing_offline'. */
  get testing_offline() { return this.getAttribute('testing_offline')}
  set testing_offline(val) {
    // handle testing_offline=false "correctly"
    if (val && val !== 'false') {
      this.setAttribute('testing_offline', true);
    } else {
      this.removeAttribute('testing_offline');
    }
  }

  render() {
    console.time('render');
    render(this._template(this), this);
    console.timeEnd('render');
  }

  attributeChangedCallback(attrName, oldVal, newVal) {
    this.render();
  }
}