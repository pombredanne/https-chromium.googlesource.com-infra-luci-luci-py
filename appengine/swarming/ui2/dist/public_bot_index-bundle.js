!function(e){var t={};function n(s){if(t[s])return t[s].exports;var i=t[s]={i:s,l:!1,exports:{}};return e[s].call(i.exports,i,i.exports,n),i.l=!0,i.exports}n.m=e,n.c=t,n.d=function(e,t,s){n.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:s})},n.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},n.t=function(e,t){if(1&t&&(e=n(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var s=Object.create(null);if(n.r(s),Object.defineProperty(s,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var i in e)n.d(s,i,function(t){return e[t]}.bind(null,i));return s},n.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return n.d(t,"a",t),t},n.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},n.p="/newres/",n(n.s=9)}([function(e,t,n){"use strict";function s(e,t){if(e.hasOwnProperty(t)){let n=e[t];delete e[t],e[t]=n}}n.d(t,"a",function(){return s})},function(e,t,n){"use strict";const s=new Map;class i{constructor(e,t,n,s=b){this.strings=e,this.values=t,this.type=n,this.partCallback=s}getHTML(){const e=this.strings.length-1;let t="",n=!0;for(let s=0;s<e;s++){const e=this.strings[s];t+=e;const i=u(e);t+=(n=i>-1?i<e.length:n)?a:o}return t+this.strings[e]}getTemplateElement(){const e=document.createElement("template");return e.innerHTML=this.getHTML(),e}}function r(e,t,n=function(e){let t=s.get(e.type);void 0===t&&(t=new Map,s.set(e.type,t));let n=t.get(e.strings);return void 0===n&&(n=new d(e,e.getTemplateElement()),t.set(e.strings,n)),n}){const i=n(e);let r=t.__templateInstance;if(void 0!==r&&r.template===i&&r._partCallback===e.partCallback)return void r.update(e.values);r=new x(i,e.partCallback,n),t.__templateInstance=r;const o=r._clone();r.update(e.values),w(t,t.firstChild),t.appendChild(o)}const o=`{{lit-${String(Math.random()).slice(2)}}}`,a=`\x3c!--${o}--\x3e`,l=new RegExp(`${o}|${a}`),c=/[ \x09\x0a\x0c\x0d]([^\0-\x1F\x7F-\x9F \x09\x0a\x0c\x0d"'>=/]+)[ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*)$/;function u(e){const t=e.lastIndexOf(">");return e.indexOf("<",t+1)>-1?e.length:t}class h{constructor(e,t,n,s,i){this.type=e,this.index=t,this.name=n,this.rawName=s,this.strings=i}}class d{constructor(e,t){this.parts=[],this.element=t;const n=this.element.content,s=document.createTreeWalker(n,133,null,!1);let i=-1,r=0;const a=[];let u,d;for(;s.nextNode();){i++,u=d;const t=d=s.currentNode;if(1===t.nodeType){if(!t.hasAttributes())continue;const n=t.attributes;let s=0;for(let e=0;e<n.length;e++)n[e].value.indexOf(o)>=0&&s++;for(;s-- >0;){const s=e.strings[r],o=c.exec(s)[1],a=n.getNamedItem(o),u=a.value.split(l);this.parts.push(new h("attribute",i,a.name,o,u)),t.removeAttribute(a.name),r+=u.length-1}}else if(3===t.nodeType){const e=t.nodeValue;if(e.indexOf(o)<0)continue;const n=t.parentNode,s=e.split(l),a=s.length-1;r+=a,t.textContent=s[a];for(let e=0;e<a;e++)n.insertBefore(document.createTextNode(s[e]),t),this.parts.push(new h("node",i++))}else if(8===t.nodeType&&t.nodeValue===o){const e=t.parentNode,n=t.previousSibling;null===n||n!==u||n.nodeType!==Node.TEXT_NODE?e.insertBefore(document.createTextNode(""),t):i--,this.parts.push(new h("node",i++)),a.push(t),null===t.nextSibling?e.insertBefore(document.createTextNode(""),t):i--,d=u,r++}}for(const e of a)e.parentNode.removeChild(e)}}const _=(e,t)=>p(t)?(t=t(e),f):null===t?void 0:t,p=e=>"function"==typeof e&&!0===e.__litDirective,f={},g=e=>null===e||!("object"==typeof e||"function"==typeof e);class m{constructor(e,t,n,s){this.instance=e,this.element=t,this.name=n,this.strings=s,this.size=s.length-1,this._previousValues=[]}_interpolate(e,t){const n=this.strings,s=n.length-1;let i="";for(let r=0;r<s;r++){i+=n[r];const s=_(this,e[t+r]);if(s&&s!==f&&(Array.isArray(s)||"string"!=typeof s&&s[Symbol.iterator]))for(const e of s)i+=e;else i+=s}return i+n[s]}_equalToPreviousValues(e,t){for(let n=t;n<t+this.size;n++)if(this._previousValues[n]!==e[n]||!g(e[n]))return!1;return!0}setValue(e,t){if(this._equalToPreviousValues(e,t))return;const n=this.strings;let s;2===n.length&&""===n[0]&&""===n[1]?(s=_(this,e[t]),Array.isArray(s)&&(s=s.join(""))):s=this._interpolate(e,t),s!==f&&this.element.setAttribute(this.name,s),this._previousValues=e}}class v{constructor(e,t,n){this.instance=e,this.startNode=t,this.endNode=n,this._previousValue=void 0}setValue(e){if((e=_(this,e))!==f)if(g(e)){if(e===this._previousValue)return;this._setText(e)}else e instanceof i?this._setTemplateResult(e):Array.isArray(e)||e[Symbol.iterator]?this._setIterable(e):e instanceof Node?this._setNode(e):void 0!==e.then?this._setPromise(e):this._setText(e)}_insert(e){this.endNode.parentNode.insertBefore(e,this.endNode)}_setNode(e){this._previousValue!==e&&(this.clear(),this._insert(e),this._previousValue=e)}_setText(e){const t=this.startNode.nextSibling;e=void 0===e?"":e,t===this.endNode.previousSibling&&t.nodeType===Node.TEXT_NODE?t.textContent=e:this._setNode(document.createTextNode(e)),this._previousValue=e}_setTemplateResult(e){const t=this.instance._getTemplate(e);let n;this._previousValue&&this._previousValue.template===t?n=this._previousValue:(n=new x(t,this.instance._partCallback,this.instance._getTemplate),this._setNode(n._clone()),this._previousValue=n),n.update(e.values)}_setIterable(e){Array.isArray(this._previousValue)||(this.clear(),this._previousValue=[]);const t=this._previousValue;let n=0;for(const s of e){let e=t[n];if(void 0===e){let s=this.startNode;n>0&&(s=t[n-1].endNode=document.createTextNode(""),this._insert(s)),e=new v(this.instance,s,this.endNode),t.push(e)}e.setValue(s),n++}if(0===n)this.clear(),this._previousValue=void 0;else if(n<t.length){const e=t[n-1];t.length=n,this.clear(e.endNode.previousSibling),e.endNode=this.endNode}}_setPromise(e){this._previousValue=e,e.then(t=>{this._previousValue===e&&this.setValue(t)})}clear(e=this.startNode){w(this.startNode.parentNode,e.nextSibling,this.endNode)}}const b=(e,t,n)=>{if("attribute"===t.type)return new m(e,n,t.name,t.strings);if("node"===t.type)return new v(e,n,n.nextSibling);throw new Error(`Unknown part type ${t.type}`)};class x{constructor(e,t,n){this._parts=[],this.template=e,this._partCallback=t,this._getTemplate=n}update(e){let t=0;for(const n of this._parts)void 0===n.size?(n.setValue(e[t]),t++):(n.setValue(e,t),t+=n.size)}_clone(){const e=document.importNode(this.template.element.content,!0),t=this.template.parts;if(t.length>0){const n=document.createTreeWalker(e,133,null,!1);let s=-1;for(let e=0;e<t.length;e++){const i=t[e];for(;s<i.index;)s++,n.nextNode();this._parts.push(this._partCallback(this,i,n.currentNode))}}return e}}const w=(e,t,n=null)=>{let s=t;for(;s!==n;){const t=s.nextSibling;e.removeChild(s),s=t}};n.d(t,"a",function(){return y}),n.d(t,"b",function(){return r});const y=(e,...t)=>new i(e,t,"html",E),E=(e,t,n)=>{if("attribute"===t.type){if(t.rawName.startsWith("on-")){return new class{constructor(e,t,n){this.instance=e,this.element=t,this.eventName=n}setValue(e){const t=_(this,e),n=this._listener;t!==n&&(this._listener=t,null!=n&&this.element.removeEventListener(this.eventName,n),null!=t&&this.element.addEventListener(this.eventName,t))}}(e,n,t.rawName.slice(3))}if(t.name.endsWith("$")){const s=t.name.slice(0,-1);return new m(e,n,s,t.strings)}if(t.name.endsWith("?")){return new class extends m{setValue(e,t){const n=this.strings;if(2!==n.length||""!==n[0]||""!==n[1])throw new Error("boolean attributes can only contain a single expression");{const n=_(this,e[t]);if(n===f)return;n?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name)}}}(e,n,t.name.slice(0,-1),t.strings)}return new class extends m{setValue(e,t){const n=this.strings;let s;this._equalToPreviousValues(e,t)||((s=2===n.length&&""===n[0]&&""===n[1]?_(this,e[t]):this._interpolate(e,t))!==f&&(this.element[this.name]=s),this._previousValues=e)}}(e,n,t.rawName,t.strings)}return b(e,t,n)}},function(e,t,n){"use strict";function s(e,t=1e4){"object"==typeof e&&(e=e.message||JSON.stringify(e));var n={message:e,duration:t};document.dispatchEvent(new CustomEvent("error-sk",{detail:n,bubbles:!0}))}n.d(t,"a",function(){return s})},function(e,t,n){"use strict";n(4),n(16);var s=n(0);window.customElements.define("spinner-sk",class extends HTMLElement{connectedCallback(){Object(s.a)(this,"active")}get active(){return this.hasAttribute("active")}set active(e){e?this.setAttribute("active",""):this.removeAttribute("active")}});n(14),n(13);var i=n(1),r=n(2);window.customElements.define("oauth-login",class extends HTMLElement{connectedCallback(){Object(s.a)(this,"client_id"),Object(s.a)(this,"testing_offline"),this._auth_header="",this.testing_offline?this._profile={email:"missing@chromium.org",imageURL:"http://storage.googleapis.com/gd-wagtail-prod-assets/original_images/logo_google_fonts_color_2x_web_64dp.png"}:(this._profile=null,document.addEventListener("oauth-lib-loaded",()=>{gapi.auth2.init({client_id:this.client_id}).then(()=>{this._maybeFireLoginEvent(),this._render()},e=>{console.error(e),Object(r.a)(`Error initializing oauth: ${JSON.stringify(e)}`,1e4)})})),this._render()}static get observedAttributes(){return["client_id","testing_offline"]}get auth_header(){return this._auth_header}get client_id(){return this.getAttribute("client_id")}set client_id(e){return this.setAttribute("client_id",e)}get testing_offline(){return this.getAttribute("testing_offline")}set testing_offline(e){e&&"false"!==e?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}_maybeFireLoginEvent(){let e=gapi.auth2.getAuthInstance().currentUser.get();if(e.isSignedIn()){let t=e.getBasicProfile();this._profile={email:t.getEmail(),imageURL:t.getImageUrl()};let n=e.getAuthResponse(!0),s=`${n.token_type} ${n.access_token}`;return this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:s},bubbles:!0})),this._auth_header=s,!0}return this._profile=null,this._auth_header="",!1}_logIn(){if(this.testing_offline)this._auth_header="Bearer 12345678910-boomshakalaka",this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:this._auth_header},bubbles:!0})),this._render();else{let e=gapi.auth2.getAuthInstance();e&&e.signIn({scope:"email",prompt:"select_account"}).then(()=>{this._maybeFireLoginEvent()||console.warn("login was not successful; maybe user canceled"),this._render()})}}_logOut(){if(this.testing_offline)this._auth_header="",this._render(),window.location.reload();else{let e=gapi.auth2.getAuthInstance();e&&e.signOut().then(()=>{this._auth_header="",this._profile=null,window.location.reload()})}}_render(){Object(i.b)((e=>e.auth_header?i["a"]` <div> <img class=center id=avatar src="${e._profile.imageURL}" width=30 height=30> <span class=center>${e._profile.email}</span> <span class=center>|</span> <a class=center on-click=${()=>e._logOut()} href="#">Sign out</a> </div>`:i["a"]` <div> <a on-click=${()=>e._logIn()} href="#">Sign in</a> </div>`)(this),this)}attributeChangedCallback(e,t,n){this._render()}});const o=document.createElement("template");o.innerHTML="\n<button class=toggle-button>\n  <icon-menu-sk>\n  </icon-menu-sk>\n</button>\n";const a=document.createElement("template");a.innerHTML="\n<div class=spinner-spacer>\n  <spinner-sk></spinner-sk>\n</div>\n";window.customElements.define("swarming-app",class extends HTMLElement{connectedCallback(){Object(s.a)(this,"client_id"),Object(s.a)(this,"testing_offline"),this._busyTaskCount=0,this._spinner=null,this._loginEle=null,this._addHTML(),this._render()}static get observedAttributes(){return["client_id","testing_offline"]}get busy(){return!!this._busyTaskCount}get client_id(){return this.getAttribute("client_id")}set client_id(e){return this.setAttribute("client_id",e)}get testing_offline(){return this.getAttribute("testing_offline")}set testing_offline(e){e&&"false"!==e?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}addBusyTasks(e){this._busyTaskCount+=e,this._spinner&&this._busyTaskCount>0&&(this._spinner.active=!0)}finishedTask(){this._busyTaskCount--,this._busyTaskCount<=0&&(this._busyTaskCount=0,this._spinner&&(this._spinner.active=!1),this.dispatchEvent(new CustomEvent("busy-end",{bubbles:!0})))}_addHTML(){let e=this.querySelector("header"),t=e&&e.querySelector("aside");if(!(e&&t&&t.classList.contains("hideable")))return;let n=o.content.cloneNode(!0);e.insertBefore(n,e.firstElementChild),(n=e.firstElementChild).addEventListener("click",e=>this._toggleMenu(e,t));let s=a.content.cloneNode(!0);e.insertBefore(s,t),this._spinner=e.querySelector("spinner-sk");let i=document.createElement("span");i.classList.add("grow"),e.appendChild(i),this._loginEle=document.createElement("div"),e.appendChild(this._loginEle)}_toggleMenu(e,t){t.classList.toggle("shown")}_render(){this._loginEle&&Object(i.b)((e=>i["a"]` <oauth-login client_id=${e.client_id} testing_offline=${e.testing_offline}></oauth-login> `)(this),this._loginEle)}attributeChangedCallback(e,t,n){this._render()}});n(12)},function(e,t){const n=document.createElement("template");n.innerHTML='<svg class="icon-sk-svg" viewBox="0 0 24 24" preserveAspectRatio="xMidYMid meet" focusable="false">\n  <g><path d=""></path></g>\n</svg>';class s extends HTMLElement{connectedCallback(){let e=n.content.cloneNode(!0);e.querySelector("path").setAttribute("d",this.constructor._path),this.appendChild(e)}}window.customElements.define("icon-menu-sk",class extends s{static get _path(){return"M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"}}),window.customElements.define("icon-link-sk",class extends s{static get _path(){return"M3.9 12c0-1.71 1.39-3.1 3.1-3.1h4V7H7c-2.76 0-5 2.24-5 5s2.24 5 5 5h4v-1.9H7c-1.71 0-3.1-1.39-3.1-3.1zM8 13h8v-2H8v2zm9-6h-4v1.9h4c1.71 0 3.1 1.39 3.1 3.1s-1.39 3.1-3.1 3.1h-4V17h4c2.76 0 5-2.24 5-5s-2.24-5-5-5z"}}),window.customElements.define("icon-check-sk",class extends s{static get _path(){return"M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"}}),window.customElements.define("icon-warning-sk",class extends s{static get _path(){return"M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"}}),window.customElements.define("icon-create-sk",class extends s{static get _path(){return"M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"}}),window.customElements.define("icon-alarm-sk",class extends s{static get _path(){return"M22 5.72l-4.6-3.86-1.29 1.53 4.6 3.86L22 5.72zM7.88 3.39L6.6 1.86 2 5.71l1.29 1.53 4.59-3.85zM12.5 8H11v6l4.75 2.85.75-1.23-4-2.37V8zM12 4c-4.97 0-9 4.03-9 9s4.02 9 9 9c4.97 0 9-4.03 9-9s-4.03-9-9-9zm0 16c-3.87 0-7-3.13-7-7s3.13-7 7-7 7 3.13 7 7-3.13 7-7 7z"}})},,,,,function(e,t,n){"use strict";n.r(t);n(3)},,,function(e,t){},function(e,t){},function(e,t){},,function(e,t){}]);