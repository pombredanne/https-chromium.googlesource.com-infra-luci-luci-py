!function(e){var t={};function s(n){if(t[n])return t[n].exports;var i=t[n]={i:n,l:!1,exports:{}};return e[n].call(i.exports,i,i.exports,s),i.l=!0,i.exports}s.m=e,s.c=t,s.d=function(e,t,n){s.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},s.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},s.t=function(e,t){if(1&t&&(e=s(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(s.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var i in e)s.d(n,i,function(t){return e[t]}.bind(null,i));return n},s.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return s.d(t,"a",t),t},s.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},s.p="/newres/",s(s.s=12)}([function(e,t,s){"use strict";function n(e,t){if(e.hasOwnProperty(t)){let s=e[t];delete e[t],e[t]=s}}s.d(t,"a",function(){return n})},function(e,t,s){"use strict";const n=new Map;class i{constructor(e,t,s,n=y){this.strings=e,this.values=t,this.type=s,this.partCallback=n}getHTML(){const e=this.strings.length-1;let t="",s=!0;for(let n=0;n<e;n++){const e=this.strings[n];t+=e;const i=u(e);t+=(s=i>-1?i<e.length:s)?a:o}return t+this.strings[e]}getTemplateElement(){const e=document.createElement("template");return e.innerHTML=this.getHTML(),e}}function r(e,t,s=function(e){let t=n.get(e.type);void 0===t&&(t=new Map,n.set(e.type,t));let s=t.get(e.strings);return void 0===s&&(s=new _(e,e.getTemplateElement()),t.set(e.strings,s)),s}){const i=s(e);let r=t.__templateInstance;if(void 0!==r&&r.template===i&&r._partCallback===e.partCallback)return void r.update(e.values);r=new x(i,e.partCallback,s),t.__templateInstance=r;const o=r._clone();r.update(e.values),w(t,t.firstChild),t.appendChild(o)}const o=`{{lit-${String(Math.random()).slice(2)}}}`,a=`\x3c!--${o}--\x3e`,l=new RegExp(`${o}|${a}`),h=/[ \x09\x0a\x0c\x0d]([^\0-\x1F\x7F-\x9F \x09\x0a\x0c\x0d"'>=/]+)[ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*)$/;function u(e){const t=e.lastIndexOf(">");return e.indexOf("<",t+1)>-1?e.length:t}class c{constructor(e,t,s,n,i){this.type=e,this.index=t,this.name=s,this.rawName=n,this.strings=i}}const d=e=>-1!==e.index;class _{constructor(e,t){this.parts=[],this.element=t;const s=this.element.content,n=document.createTreeWalker(s,133,null,!1);let i=-1,r=0;const a=[];let u,d;for(;n.nextNode();){i++,u=d;const t=d=n.currentNode;if(1===t.nodeType){if(!t.hasAttributes())continue;const s=t.attributes;let n=0;for(let e=0;e<s.length;e++)s[e].value.indexOf(o)>=0&&n++;for(;n-- >0;){const n=e.strings[r],o=h.exec(n)[1],a=s.getNamedItem(o),u=a.value.split(l);this.parts.push(new c("attribute",i,a.name,o,u)),t.removeAttribute(a.name),r+=u.length-1}}else if(3===t.nodeType){const e=t.nodeValue;if(e.indexOf(o)<0)continue;const s=t.parentNode,n=e.split(l),h=n.length-1;r+=h;for(let e=0;e<h;e++)s.insertBefore(""===n[e]?document.createComment(""):document.createTextNode(n[e]),t),this.parts.push(new c("node",i++));s.insertBefore(""===n[h]?document.createComment(""):document.createTextNode(n[h]),t),a.push(t)}else if(8===t.nodeType&&t.nodeValue===o){const e=t.parentNode,s=t.previousSibling;null===s||s!==u||s.nodeType!==Node.TEXT_NODE?e.insertBefore(document.createComment(""),t):i--,this.parts.push(new c("node",i++)),a.push(t),null===t.nextSibling?e.insertBefore(document.createComment(""),t):i--,d=u,r++}}for(const e of a)e.parentNode.removeChild(e)}}const f=(e,t)=>p(t)?(t=t(e),g):null===t?void 0:t,p=e=>"function"==typeof e&&!0===e.__litDirective,g={},m=e=>null===e||!("object"==typeof e||"function"==typeof e);class v{constructor(e,t,s,n){this.instance=e,this.element=t,this.name=s,this.strings=n,this.size=n.length-1,this._previousValues=[]}_interpolate(e,t){const s=this.strings,n=s.length-1;let i="";for(let r=0;r<n;r++){i+=s[r];const n=f(this,e[t+r]);if(n&&n!==g&&(Array.isArray(n)||"string"!=typeof n&&n[Symbol.iterator]))for(const e of n)i+=e;else i+=n}return i+s[n]}_equalToPreviousValues(e,t){for(let s=t;s<t+this.size;s++)if(this._previousValues[s]!==e[s]||!m(e[s]))return!1;return!0}setValue(e,t){if(this._equalToPreviousValues(e,t))return;const s=this.strings;let n;2===s.length&&""===s[0]&&""===s[1]?(n=f(this,e[t]),Array.isArray(n)&&(n=n.join(""))):n=this._interpolate(e,t),n!==g&&this.element.setAttribute(this.name,n),this._previousValues=e}}class b{constructor(e,t,s){this.instance=e,this.startNode=t,this.endNode=s,this._previousValue=void 0}setValue(e){if((e=f(this,e))!==g)if(m(e)){if(e===this._previousValue)return;this._setText(e)}else e instanceof i?this._setTemplateResult(e):Array.isArray(e)||e[Symbol.iterator]?this._setIterable(e):e instanceof Node?this._setNode(e):void 0!==e.then?this._setPromise(e):this._setText(e)}_insert(e){this.endNode.parentNode.insertBefore(e,this.endNode)}_setNode(e){this._previousValue!==e&&(this.clear(),this._insert(e),this._previousValue=e)}_setText(e){const t=this.startNode.nextSibling;e=void 0===e?"":e,t===this.endNode.previousSibling&&t.nodeType===Node.TEXT_NODE?t.textContent=e:this._setNode(document.createTextNode(e)),this._previousValue=e}_setTemplateResult(e){const t=this.instance._getTemplate(e);let s;this._previousValue&&this._previousValue.template===t?s=this._previousValue:(s=new x(t,this.instance._partCallback,this.instance._getTemplate),this._setNode(s._clone()),this._previousValue=s),s.update(e.values)}_setIterable(e){Array.isArray(this._previousValue)||(this.clear(),this._previousValue=[]);const t=this._previousValue;let s=0;for(const n of e){let e=t[s];if(void 0===e){let n=this.startNode;s>0&&(n=t[s-1].endNode=document.createTextNode(""),this._insert(n)),e=new b(this.instance,n,this.endNode),t.push(e)}e.setValue(n),s++}if(0===s)this.clear(),this._previousValue=void 0;else if(s<t.length){const e=t[s-1];t.length=s,this.clear(e.endNode.previousSibling),e.endNode=this.endNode}}_setPromise(e){this._previousValue=e,e.then(t=>{this._previousValue===e&&this.setValue(t)})}clear(e=this.startNode){w(this.startNode.parentNode,e.nextSibling,this.endNode)}}const y=(e,t,s)=>{if("attribute"===t.type)return new v(e,s,t.name,t.strings);if("node"===t.type)return new b(e,s,s.nextSibling);throw new Error(`Unknown part type ${t.type}`)};class x{constructor(e,t,s){this._parts=[],this.template=e,this._partCallback=t,this._getTemplate=s}update(e){let t=0;for(const s of this._parts)s?void 0===s.size?(s.setValue(e[t]),t++):(s.setValue(e,t),t+=s.size):t++}_clone(){const e=this.template.element.content.cloneNode(!0),t=this.template.parts;if(t.length>0){const s=document.createTreeWalker(e,133,null,!1);let n=-1;for(let e=0;e<t.length;e++){const i=t[e],r=d(i);if(r)for(;n<i.index;)n++,s.nextNode();this._parts.push(r?this._partCallback(this,i,s.currentNode):void 0)}}return e}}const w=(e,t,s=null)=>{let n=t;for(;n!==s;){const t=n.nextSibling;e.removeChild(n),n=t}};s.d(t,"a",function(){return E}),s.d(t,"b",function(){return r});const E=(e,...t)=>new i(e,t,"html",T),T=(e,t,s)=>{if("attribute"===t.type){if("on-"===t.rawName.substr(0,3)){return new class{constructor(e,t,s){this.instance=e,this.element=t,this.eventName=s}setValue(e){const t=f(this,e);t!==this._listener&&(null==t?this.element.removeEventListener(this.eventName,this):null==this._listener&&this.element.addEventListener(this.eventName,this),this._listener=t)}handleEvent(e){"function"==typeof this._listener?this._listener.call(this.element,e):"function"==typeof this._listener.handleEvent&&this._listener.handleEvent(e)}}(e,s,t.rawName.slice(3))}const n=t.name.substr(t.name.length-1);if("$"===n){const n=t.name.slice(0,-1);return new v(e,s,n,t.strings)}if("?"===n){return new class extends v{setValue(e,t){const s=this.strings;if(2!==s.length||""!==s[0]||""!==s[1])throw new Error("boolean attributes can only contain a single expression");{const s=f(this,e[t]);if(s===g)return;s?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name)}}}(e,s,t.name.slice(0,-1),t.strings)}return new class extends v{setValue(e,t){const s=this.strings;let n;this._equalToPreviousValues(e,t)||((n=2===s.length&&""===s[0]&&""===s[1]?f(this,e[t]):this._interpolate(e,t))!==g&&(this.element[this.name]=n),this._previousValues=e)}}(e,s,t.rawName,t.strings)}return y(e,t,s)}},function(e,t,s){"use strict";function n(e,t=1e4){"object"==typeof e&&(e=e.message||JSON.stringify(e));var s={message:e,duration:t};document.dispatchEvent(new CustomEvent("error-sk",{detail:s,bubbles:!0}))}s.d(t,"a",function(){return n})},function(e,t,s){"use strict";function n(e){if(e.ok)return e.json();throw{message:`Bad network response: ${e.statusText}`,resp:e,status:e.status}}s.d(t,"a",function(){return n})},function(e,t,s){"use strict";s.d(t,"a",function(){return i});const n=document.createElement("template");class i extends HTMLElement{constructor(){super(),n.innerHTML=`<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">${this.constructor._svg}</svg>`}connectedCallback(){let e=n.content.cloneNode(!0);this.appendChild(e)}}},function(e,t,s){"use strict";var n=s(1),i=s(0),r=s(3),o=s(2),a=(s(24),s(4));window.customElements.define("menu-icon-sk",class extends a.a{static get _svg(){return'<path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/>'}}),window.customElements.define("spinner-sk",class extends HTMLElement{connectedCallback(){Object(i.a)(this,"active")}get active(){return this.hasAttribute("active")}set active(e){e?this.setAttribute("active",""):this.removeAttribute("active")}});s(22),s(21);window.customElements.define("oauth-login",class extends HTMLElement{connectedCallback(){Object(i.a)(this,"client_id"),Object(i.a)(this,"testing_offline"),this._auth_header="",this.testing_offline?this._profile={email:"missing@chromium.org",imageURL:"http://storage.googleapis.com/gd-wagtail-prod-assets/original_images/logo_google_fonts_color_2x_web_64dp.png"}:(this._profile=null,document.addEventListener("oauth-lib-loaded",()=>{gapi.auth2.init({client_id:this.client_id}).then(()=>{this._maybeFireLoginEvent(),this._render()},e=>{console.error(e),Object(o.a)(`Error initializing oauth: ${JSON.stringify(e)}`,1e4)})})),this._render()}static get observedAttributes(){return["client_id","testing_offline"]}get auth_header(){return this._auth_header}get client_id(){return this.getAttribute("client_id")}set client_id(e){return this.setAttribute("client_id",e)}get testing_offline(){return this.getAttribute("testing_offline")}set testing_offline(e){e&&"false"!==e?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}_maybeFireLoginEvent(){let e=gapi.auth2.getAuthInstance().currentUser.get();if(e.isSignedIn()){let t=e.getBasicProfile();this._profile={email:t.getEmail(),imageURL:t.getImageUrl()};let s=e.getAuthResponse(!0),n=`${s.token_type} ${s.access_token}`;return this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:n},bubbles:!0})),this._auth_header=n,!0}return this._profile=null,this._auth_header="",!1}_logIn(){if(this.testing_offline)this._auth_header="Bearer 12345678910-boomshakalaka",this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:this._auth_header},bubbles:!0})),this._render();else{let e=gapi.auth2.getAuthInstance();e&&e.signIn({scope:"email",prompt:"select_account"}).then(()=>{this._maybeFireLoginEvent()||console.warn("login was not successful; maybe user canceled"),this._render()})}}_logOut(){if(this.testing_offline)this._auth_header="",this._render(),window.location.reload();else{let e=gapi.auth2.getAuthInstance();e&&e.signOut().then(()=>{this._auth_header="",this._profile=null,window.location.reload()})}}_render(){Object(n.b)((e=>e.auth_header?n["a"]` <div> <img class=center id=avatar src="${e._profile.imageURL}" width=30 height=30> <span class=center>${e._profile.email}</span> <span class=center>|</span> <a class=center on-click=${()=>e._logOut()} href="#">Sign out</a> </div>`:n["a"]` <div> <a on-click=${()=>e._logIn()} href="#">Sign in</a> </div>`)(this),this)}attributeChangedCallback(e,t,s){this._render()}});const l=document.createElement("template");l.innerHTML="\n<button class=toggle-button>\n  <menu-icon-sk>\n  </menu-icon-sk>\n</button>\n";const h=document.createElement("template");h.innerHTML="\n<div class=spinner-spacer>\n  <spinner-sk></spinner-sk>\n</div>\n";window.customElements.define("swarming-app",class extends HTMLElement{constructor(){super(),this._busyTaskCount=0,this._spinner=null,this._dynamicEle=null,this._auth_header="",this._server_details={server_version:"You must log in to see more details",bot_version:""},this._permissions={}}connectedCallback(){Object(i.a)(this,"client_id"),Object(i.a)(this,"testing_offline"),this._addHTML(),this.addEventListener("log-in",e=>{this._auth_header=e.detail.auth_header,this._fetch()}),this._render()}static get observedAttributes(){return["client_id","testing_offline"]}get busy(){return!!this._busyTaskCount}get permissions(){return this._permissions}get server_details(){return this._server_details}get client_id(){return this.getAttribute("client_id")}set client_id(e){return this.setAttribute("client_id",e)}get testing_offline(){return this.getAttribute("testing_offline")}set testing_offline(e){e&&"false"!==e?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}addBusyTasks(e){this._busyTaskCount+=e,this._spinner&&this._busyTaskCount>0&&(this._spinner.active=!0)}finishedTask(){this._busyTaskCount--,this._busyTaskCount<=0&&(this._busyTaskCount=0,this._spinner&&(this._spinner.active=!1),this.dispatchEvent(new CustomEvent("busy-end",{bubbles:!0})))}_addHTML(){let e=this.querySelector("header"),t=e&&e.querySelector("aside");if(!(e&&t&&t.classList.contains("hideable")))return;let s=l.content.cloneNode(!0);e.insertBefore(s,e.firstElementChild),(s=e.firstElementChild).addEventListener("click",e=>this._toggleMenu(e,t));let n=h.content.cloneNode(!0);e.insertBefore(n,t),this._spinner=e.querySelector("spinner-sk");let i=document.createElement("span");i.classList.add("grow"),e.appendChild(i),this._dynamicEle=document.createElement("div"),this._dynamicEle.classList.add("right"),e.appendChild(this._dynamicEle)}_toggleMenu(e,t){t.classList.toggle("shown")}_fetch(){if(!this._auth_header)return;this._server_details={server_version:"<loading>",bot_version:"<loading>"};let e={headers:{authorization:this._auth_header}};this.addBusyTasks(2),fetch("/_ah/api/swarming/v1/server/details",e).then(r.a).then(e=>{this._server_details=e,this._render(),this.dispatchEvent(new CustomEvent("server-details-loaded",{bubbles:!0})),this.finishedTask()}).catch(e=>{403===e.status?(this._server_details={server_version:"User unauthorized - try logging in with a different account",bot_version:""},this._render(),this.dispatchEvent(new CustomEvent("server-details-loaded",{bubbles:!0}))):(console.error(e),Object(o.a)(`Unexpected error loading details: ${e.message}`,5e3)),this.finishedTask()}),fetch("/_ah/api/swarming/v1/server/permissions",e).then(r.a).then(e=>{this._permissions=e,this._render(),this.dispatchEvent(new CustomEvent("permissions-loaded",{bubbles:!0})),this.finishedTask()}).catch(e=>{403!==e.status&&(console.error(e),Object(o.a)(`Unexpected error loading permissions: ${e.message}`,5e3)),this.finishedTask()})}_render(){this._dynamicEle&&Object(n.b)((e=>n["a"]` <div class=server-version> Server: <a href$=${function(e){if(e&&e.server_version){var t=e.server_version.split("-");if(2===t.length)return`https://chromium.googlesource.com/infra/luci/luci-py/+/${t[1]}`}}(e._server_details)}> ${e._server_details.server_version} </a> </div> <oauth-login client_id=${e.client_id} testing_offline=${e.testing_offline}></oauth-login> `)(this),this._dynamicEle)}attributeChangedCallback(e,t,s){this._render()}});s(20)},,,,,,,function(e,t,s){"use strict";s.r(t);s(5)},,,,,,,,function(e,t){},function(e,t){},function(e,t){},,function(e,t){}]);