!function(t){var e={};function s(i){if(e[i])return e[i].exports;var n=e[i]={i:i,l:!1,exports:{}};return t[i].call(n.exports,n,n.exports,s),n.l=!0,n.exports}s.m=t,s.c=e,s.d=function(t,e,i){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:i})},s.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var i=Object.create(null);if(s.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var n in t)s.d(i,n,function(e){return t[e]}.bind(null,n));return i},s.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="/newres/",s(s.s=24)}([function(t,e,s){"use strict";const i=new WeakMap,n=t=>(...e)=>{const s=t(...e);return i.set(s,!0),s},r=t=>"function"==typeof t&&i.has(t),o=void 0!==window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,a=(t,e,s=null,i=null)=>{let n=e;for(;n!==s;){const e=n.nextSibling;t.insertBefore(n,i),n=e}},l=(t,e,s=null)=>{let i=e;for(;i!==s;){const e=i.nextSibling;t.removeChild(i),i=e}},h={},c={},d=`{{lit-${String(Math.random()).slice(2)}}}`,u=`\x3c!--${d}--\x3e`,p=new RegExp(`${d}|${u}`),_="$lit$";class m{constructor(t,e){this.parts=[],this.element=e;let s=-1,i=0;const n=[],r=e=>{const o=e.content,a=document.createTreeWalker(o,133,null,!1);let l=0;for(;a.nextNode();){s++;const e=a.currentNode;if(1===e.nodeType){if(e.hasAttributes()){const n=e.attributes;let r=0;for(let t=0;t<n.length;t++)n[t].value.indexOf(d)>=0&&r++;for(;r-- >0;){const n=t.strings[i],r=v.exec(n)[2],o=r.toLowerCase()+_,a=e.getAttribute(o).split(p);this.parts.push({type:"attribute",index:s,name:r,strings:a}),e.removeAttribute(o),i+=a.length-1}}"TEMPLATE"===e.tagName&&r(e)}else if(3===e.nodeType){const t=e.data;if(t.indexOf(d)>=0){const r=e.parentNode,o=t.split(p),a=o.length-1;for(let t=0;t<a;t++)r.insertBefore(""===o[t]?f():document.createTextNode(o[t]),e),this.parts.push({type:"node",index:++s});""===o[a]?(r.insertBefore(f(),e),n.push(e)):e.data=o[a],i+=a}}else if(8===e.nodeType)if(e.data===d){const t=e.parentNode;null!==e.previousSibling&&s!==l||(s++,t.insertBefore(f(),e)),l=s,this.parts.push({type:"node",index:s}),null===e.nextSibling?e.data="":(n.push(e),s--),i++}else{let t=-1;for(;-1!==(t=e.data.indexOf(d,t+1));)this.parts.push({type:"node",index:-1})}}};r(e);for(const t of n)t.parentNode.removeChild(t)}}const g=t=>-1!==t.index,f=()=>document.createComment(""),v=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F \x09\x0a\x0c\x0d"'>=/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/;class b{constructor(t,e,s){this._parts=[],this.template=t,this.processor=e,this.options=s}update(t){let e=0;for(const s of this._parts)void 0!==s&&s.setValue(t[e]),e++;for(const t of this._parts)void 0!==t&&t.commit()}_clone(){const t=o?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),e=this.template.parts;let s=0,i=0;const n=t=>{const r=document.createTreeWalker(t,133,null,!1);let o=r.nextNode();for(;s<e.length&&null!==o;){const t=e[s];if(g(t))if(i===t.index){if("node"===t.type){const t=this.processor.handleTextExpression(this.options);t.insertAfterNode(o.previousSibling),this._parts.push(t)}else this._parts.push(...this.processor.handleAttributeExpressions(o,t.name,t.strings,this.options));s++}else i++,"TEMPLATE"===o.nodeName&&n(o.content),o=r.nextNode();else this._parts.push(void 0),s++}};return n(t),o&&(document.adoptNode(t),customElements.upgrade(t)),t}}class w{constructor(t,e,s,i){this.strings=t,this.values=e,this.type=s,this.processor=i}getHTML(){const t=this.strings.length-1;let e="";for(let s=0;s<t;s++){const t=this.strings[s],i=v.exec(t);e+=i?t.substr(0,i.index)+i[1]+i[2]+_+i[3]+d:t+u}return e+this.strings[t]}getTemplateElement(){const t=document.createElement("template");return t.innerHTML=this.getHTML(),t}}class E extends w{getHTML(){return`<svg>${super.getHTML()}</svg>`}getTemplateElement(){const t=super.getTemplateElement(),e=t.content,s=e.firstChild;return e.removeChild(s),a(e,s.firstChild),t}}const y=t=>null===t||!("object"==typeof t||"function"==typeof t);class x{constructor(t,e,s){this.dirty=!0,this.element=t,this.name=e,this.strings=s,this.parts=[];for(let t=0;t<s.length-1;t++)this.parts[t]=this._createPart()}_createPart(){return new k(this)}_getValue(){const t=this.strings,e=t.length-1;let s="";for(let i=0;i<e;i++){s+=t[i];const e=this.parts[i];if(void 0!==e){const t=e.value;if(null!=t&&(Array.isArray(t)||"string"!=typeof t&&t[Symbol.iterator]))for(const e of t)s+="string"==typeof e?e:String(e);else s+="string"==typeof t?t:String(t)}}return s+t[e]}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class k{constructor(t){this.value=void 0,this.committer=t}setValue(t){t===h||y(t)&&t===this.value||(this.value=t,r(t)||(this.committer.dirty=!0))}commit(){for(;r(this.value);){const t=this.value;this.value=h,t(this)}this.value!==h&&this.committer.commit()}}class T{constructor(t){this.value=void 0,this._pendingValue=void 0,this.options=t}appendInto(t){this.startNode=t.appendChild(f()),this.endNode=t.appendChild(f())}insertAfterNode(t){this.startNode=t,this.endNode=t.nextSibling}appendIntoPart(t){t._insert(this.startNode=f()),t._insert(this.endNode=f())}insertAfterPart(t){t._insert(this.startNode=f()),this.endNode=t.endNode,t.endNode=this.startNode}setValue(t){this._pendingValue=t}commit(){for(;r(this._pendingValue);){const t=this._pendingValue;this._pendingValue=h,t(this)}const t=this._pendingValue;t!==h&&(y(t)?t!==this.value&&this._commitText(t):t instanceof w?this._commitTemplateResult(t):t instanceof Node?this._commitNode(t):Array.isArray(t)||t[Symbol.iterator]?this._commitIterable(t):t===c?(this.value=c,this.clear()):this._commitText(t))}_insert(t){this.endNode.parentNode.insertBefore(t,this.endNode)}_commitNode(t){this.value!==t&&(this.clear(),this._insert(t),this.value=t)}_commitText(t){const e=this.startNode.nextSibling;t=null==t?"":t,e===this.endNode.previousSibling&&3===e.nodeType?e.data=t:this._commitNode(document.createTextNode("string"==typeof t?t:String(t))),this.value=t}_commitTemplateResult(t){const e=this.options.templateFactory(t);if(this.value&&this.value.template===e)this.value.update(t.values);else{const s=new b(e,t.processor,this.options),i=s._clone();s.update(t.values),this._commitNode(i),this.value=s}}_commitIterable(t){Array.isArray(this.value)||(this.value=[],this.clear());const e=this.value;let s,i=0;for(const n of t)void 0===(s=e[i])&&(s=new T(this.options),e.push(s),0===i?s.appendIntoPart(this):s.insertAfterPart(e[i-1])),s.setValue(n),s.commit(),i++;i<e.length&&(e.length=i,this.clear(s&&s.endNode))}clear(t=this.startNode){l(this.startNode.parentNode,t.nextSibling,this.endNode)}}class C{constructor(t,e,s){if(this.value=void 0,this._pendingValue=void 0,2!==s.length||""!==s[0]||""!==s[1])throw new Error("Boolean attributes can only contain a single expression");this.element=t,this.name=e,this.strings=s}setValue(t){this._pendingValue=t}commit(){for(;r(this._pendingValue);){const t=this._pendingValue;this._pendingValue=h,t(this)}if(this._pendingValue===h)return;const t=!!this._pendingValue;this.value!==t&&(t?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name)),this.value=t,this._pendingValue=h}}class A extends x{constructor(t,e,s){super(t,e,s),this.single=2===s.length&&""===s[0]&&""===s[1]}_createPart(){return new L(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class L extends k{}let N=!1;try{const t={get capture(){return N=!0,!1}};window.addEventListener("test",t,t),window.removeEventListener("test",t,t)}catch(t){}class V{constructor(t,e,s){this.value=void 0,this._pendingValue=void 0,this.element=t,this.eventName=e,this.eventContext=s,this._boundHandleEvent=(t=>this.handleEvent(t))}setValue(t){this._pendingValue=t}commit(){for(;r(this._pendingValue);){const t=this._pendingValue;this._pendingValue=h,t(this)}if(this._pendingValue===h)return;const t=this._pendingValue,e=this.value,s=null==t||null!=e&&(t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive),i=null!=t&&(null==e||s);s&&this.element.removeEventListener(this.eventName,this._boundHandleEvent,this._options),i&&(this._options=$(t),this.element.addEventListener(this.eventName,this._boundHandleEvent,this._options)),this.value=t,this._pendingValue=h}handleEvent(t){"function"==typeof this.value?this.value.call(this.eventContext||this.element,t):this.value.handleEvent(t)}}const $=t=>t&&(N?{capture:t.capture,passive:t.passive,once:t.once}:t.capture);class S{handleAttributeExpressions(t,e,s,i){const n=e[0];return"."===n?new A(t,e.slice(1),s).parts:"@"===n?[new V(t,e.slice(1),i.eventContext)]:"?"===n?[new C(t,e.slice(1),s)]:new x(t,e,s).parts}handleTextExpression(t){return new T(t)}}const M=new S;function j(t){let e=O.get(t.type);void 0===e&&(e={stringsArray:new WeakMap,keyString:new Map},O.set(t.type,e));let s=e.stringsArray.get(t.strings);if(void 0!==s)return s;const i=t.strings.join(d);return void 0===(s=e.keyString.get(i))&&(s=new m(t,t.getTemplateElement()),e.keyString.set(i,s)),e.stringsArray.set(t.strings,s),s}const O=new Map,H=new WeakMap,B=(t,e,s)=>{let i=H.get(e);void 0===i&&(l(e,e.firstChild),H.set(e,i=new T(Object.assign({templateFactory:j},s))),i.appendInto(e)),i.setValue(t),i.commit()};s.d(e,"c",function(){return P}),s.d(e,!1,function(){return S}),s.d(e,!1,function(){return M}),s.d(e,"b",function(){return n}),s.d(e,!1,function(){return r}),s.d(e,!1,function(){return l}),s.d(e,!1,function(){return a}),s.d(e,!1,function(){return h}),s.d(e,!1,function(){return c}),s.d(e,!1,function(){return x}),s.d(e,"a",function(){return k}),s.d(e,!1,function(){return C}),s.d(e,!1,function(){return V}),s.d(e,!1,function(){return y}),s.d(e,!1,function(){return T}),s.d(e,!1,function(){return A}),s.d(e,!1,function(){return L}),s.d(e,!1,function(){return H}),s.d(e,"d",function(){return B}),s.d(e,!1,function(){return O}),s.d(e,!1,function(){return j}),s.d(e,!1,function(){return b}),s.d(e,!1,function(){return E}),s.d(e,!1,function(){return w}),s.d(e,!1,function(){return f}),s.d(e,!1,function(){return g}),s.d(e,!1,function(){return m});const P=(t,...e)=>new w(t,e,"html",M)},function(t,e,s){"use strict";function i(t,e){if(t.hasOwnProperty(e)){let s=t[e];delete t[e],t[e]=s}}s.d(e,"a",function(){return i})},function(t,e,s){"use strict";function i(t,e=1e4){"object"==typeof t&&(t=t.message||JSON.stringify(t));var s={message:t,duration:e};document.dispatchEvent(new CustomEvent("error-sk",{detail:s,bubbles:!0}))}s.d(e,"a",function(){return i})},function(t,e,s){"use strict";function i(t){if(t.ok)return t.json();throw{message:`Bad network response: ${t.statusText}`,resp:t,status:t.status}}s.d(e,"a",function(){return i})},,function(t,e,s){"use strict";s.d(e,"a",function(){return n});var i=s(0);const n=Object(i.b)(t=>e=>{if(void 0===t&&e instanceof i.a){if(t!==e.value){const t=e.committer.name;e.committer.element.removeAttribute(t)}}else e.setValue(t)})},,,,,,,function(t,e,s){"use strict";var i=s(2),n=s(0),r=s(5),o=s(3),a=s(1);window.customElements.define("toast-sk",class extends HTMLElement{constructor(){super(),this._timer=null}connectedCallback(){this.hasAttribute("duration")||(this.duration=5e3),Object(a.a)(this,"duration")}get duration(){return+this.getAttribute("duration")}set duration(t){this.setAttribute("duration",t)}show(){this.setAttribute("shown",""),this.duration>0&&!this._timer&&(this._timer=window.setTimeout(()=>{this._timer=null,this.hide()},this.duration))}hide(){this.removeAttribute("shown"),this._timer&&(window.clearTimeout(this._timer),this._timer=null)}});s(42);window.customElements.define("error-toast-sk",class extends HTMLElement{connectedCallback(){this.innerHTML="<toast-sk></toast-sk>",this._toast=this.firstElementChild,document.addEventListener("error-sk",this)}disconnectedCallback(){document.removeEventListener("error-sk",this)}handleEvent(t){t.detail.duration&&(this._toast.duration=t.detail.duration),this._toast.textContent=t.detail.message,this._toast.show()}});s(40);const l=document.createElement("template");l.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M20 8h-2.81c-.45-.78-1.07-1.45-1.82-1.96L17 4.41 15.59 3l-2.17 2.17C12.96 5.06 12.49 5 12 5c-.49 0-.96.06-1.41.17L8.41 3 7 4.41l1.62 1.63C7.88 6.55 7.26 7.22 6.81 8H4v2h2.09c-.05.33-.09.66-.09 1v1H4v2h2v1c0 .34.04.67.09 1H4v2h2.81c1.04 1.79 2.97 3 5.19 3s4.15-1.21 5.19-3H20v-2h-2.09c.05-.33.09-.66.09-1v-1h2v-2h-2v-1c0-.34-.04-.67-.09-1H20V8zm-6 8h-4v-2h4v2zm0-4h-4v-2h4v2z"/></svg>',window.customElements.define("bug-report-icon-sk",class extends HTMLElement{connectedCallback(){let t=l.content.cloneNode(!0);this.appendChild(t)}});const h=document.createElement("template");h.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>',window.customElements.define("menu-icon-sk",class extends HTMLElement{connectedCallback(){let t=h.content.cloneNode(!0);this.appendChild(t)}}),window.customElements.define("spinner-sk",class extends HTMLElement{connectedCallback(){Object(a.a)(this,"active")}get active(){return this.hasAttribute("active")}set active(t){t?this.setAttribute("active",""):this.removeAttribute("active")}});s(39),s(38);window.customElements.define("oauth-login",class extends HTMLElement{connectedCallback(){Object(a.a)(this,"client_id"),Object(a.a)(this,"testing_offline"),this._auth_header="",this.testing_offline?this._profile={email:"missing@chromium.org",imageURL:"http://storage.googleapis.com/gd-wagtail-prod-assets/original_images/logo_google_fonts_color_2x_web_64dp.png"}:(this._profile=null,document.addEventListener("oauth-lib-loaded",()=>{gapi.auth2.init({client_id:this.client_id}).then(()=>{this._maybeFireLoginEvent(),this._render()},t=>{console.error(t),Object(i.a)(`Error initializing oauth: ${JSON.stringify(t)}`,1e4)})})),this._render()}static get observedAttributes(){return["client_id","testing_offline"]}get auth_header(){return this._auth_header}get client_id(){return this.getAttribute("client_id")}set client_id(t){return this.setAttribute("client_id",t)}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(t){t?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}_maybeFireLoginEvent(){let t=gapi.auth2.getAuthInstance().currentUser.get();if(t.isSignedIn()){let e=t.getBasicProfile();this._profile={email:e.getEmail(),imageURL:e.getImageUrl()};let s=t.getAuthResponse(!0),i=`${s.token_type} ${s.access_token}`;return this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:i},bubbles:!0})),this._auth_header=i,!0}return this._profile=null,this._auth_header="",!1}_logIn(){if(this.testing_offline)this._auth_header="Bearer 12345678910-boomshakalaka",this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:this._auth_header},bubbles:!0})),this._render();else{let t=gapi.auth2.getAuthInstance();t&&t.signIn({scope:"email",prompt:"select_account"}).then(()=>{this._maybeFireLoginEvent()||console.warn("login was not successful; maybe user canceled"),this._render()})}}_logOut(){if(this.testing_offline)this._auth_header="",this._render(),window.location.reload();else{let t=gapi.auth2.getAuthInstance();t&&t.signOut().then(()=>{this._auth_header="",this._profile=null,window.location.reload()})}}_render(){Object(n.d)((t=>t.auth_header?n["c"]` <div> <img class=center id=avatar src="${t._profile.imageURL}" width=30 height=30> <span class=center>${t._profile.email}</span> <span class=center>|</span> <a class=center @click=${()=>t._logOut()} href="#">Sign out</a> </div>`:n["c"]` <div> <a @click=${()=>t._logIn()} href="#">Sign in</a> </div>`)(this),this)}attributeChangedCallback(t,e,s){this._render()}});const c=document.createElement("template");c.innerHTML="\n<button class=toggle-button>\n  <menu-icon-sk>\n  </menu-icon-sk>\n</button>\n";const d=document.createElement("template");d.innerHTML="\n<div class=spinner-spacer>\n  <spinner-sk></spinner-sk>\n</div>\n";const u=document.createElement("template");u.innerHTML='\n<a target=_blank rel=noopener\n   href="https://bugs.chromium.org/p/chromium/issues/entry?components=Infra%3EPlatform%3ESwarming%3EWebUI&owner=kjlubick@chromium.org&status=Assigned">\n  <bug-report-icon-sk class=fab></bug-report-icon-sk>\n</a>',window.customElements.define("swarming-app",class extends HTMLElement{constructor(){super(),this._busyTaskCount=0,this._spinner=null,this._dynamicEle=null,this._auth_header="",this._server_details={server_version:"You must log in to see more details",bot_version:""},this._permissions={}}connectedCallback(){Object(a.a)(this,"client_id"),Object(a.a)(this,"testing_offline"),this._addHTML(),this.addEventListener("log-in",t=>{this._auth_header=t.detail.auth_header,this._fetch()}),this._render()}static get observedAttributes(){return["client_id","testing_offline"]}get busy(){return!!this._busyTaskCount}get permissions(){return this._permissions}get server_details(){return this._server_details}get client_id(){return this.getAttribute("client_id")}set client_id(t){return this.setAttribute("client_id",t)}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(t){t?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}addBusyTasks(t){this._busyTaskCount+=t,this._spinner&&this._busyTaskCount>0&&(this._spinner.active=!0)}finishedTask(){this._busyTaskCount--,this._busyTaskCount<=0&&(this._busyTaskCount=0,this._spinner&&(this._spinner.active=!1),this.dispatchEvent(new CustomEvent("busy-end",{bubbles:!0})))}_addHTML(){let t=this.querySelector("header"),e=t&&t.querySelector("aside"),s=this.querySelector("footer");if(!(t&&e&&e.classList.contains("hideable")))return;let i=c.content.cloneNode(!0);t.insertBefore(i,t.firstElementChild),(i=t.firstElementChild).addEventListener("click",t=>this._toggleMenu(t,e));let n=d.content.cloneNode(!0);t.insertBefore(n,e),this._spinner=t.querySelector("spinner-sk");let r=document.createElement("span");r.classList.add("grow"),t.appendChild(r),this._dynamicEle=document.createElement("div"),this._dynamicEle.classList.add("right"),t.appendChild(this._dynamicEle);let o=document.createElement("error-toast-sk");s.append(o);let a=u.content.cloneNode(!0);s.append(a)}_toggleMenu(t,e){e.classList.toggle("shown")}_fetch(){if(!this._auth_header)return;this._server_details={server_version:"<loading>",bot_version:"<loading>"};let t={headers:{authorization:this._auth_header}};this.addBusyTasks(2),fetch("/_ah/api/swarming/v1/server/details",t).then(o.a).then(t=>{this._server_details=t,this._render(),this.dispatchEvent(new CustomEvent("server-details-loaded",{bubbles:!0})),this.finishedTask()}).catch(t=>{403===t.status?(this._server_details={server_version:"User unauthorized - try logging in with a different account",bot_version:""},this._render()):(console.error(t),Object(i.a)(`Unexpected error loading details: ${t.message}`,5e3)),this.finishedTask()}),fetch("/_ah/api/swarming/v1/server/permissions",t).then(o.a).then(t=>{this._permissions=t,this._render(),this.dispatchEvent(new CustomEvent("permissions-loaded",{bubbles:!0})),this.finishedTask()}).catch(t=>{403!==t.status&&(console.error(t),Object(i.a)(`Unexpected error loading permissions: ${t.message}`,5e3)),this.finishedTask()})}_render(){this._dynamicEle&&Object(n.d)((t=>n["c"]` <div class=server-version> Server: <a href=${Object(r.a)(function(t){if(t&&t.server_version){var e=t.server_version.split("-");if(2===e.length)return`https://chromium.googlesource.com/infra/luci/luci-py/+/${e[1]}`}}(t._server_details))}> ${t._server_details.server_version} </a> </div> <oauth-login client_id=${t.client_id} ?testing_offline=${t.testing_offline}> </oauth-login>`)(this),this._dynamicEle)}attributeChangedCallback(t,e,s){this._render()}});s(37)},function(t,e,s){"use strict";s.d(e,"a",function(){return o});var i=s(2),n=s(0),r=s(1);class o extends HTMLElement{constructor(t){super(),this._template=t,this._app=null,this._auth_header="",this._notAuthorized=!1}connectedCallback(){Object(r.a)(this,"client_id"),Object(r.a)(this,"testing_offline"),this._authHeaderEvent=(t=>{this._auth_header=t.detail.auth_header}),this.addEventListener("log-in",this._authHeaderEvent)}disconnectedCallback(){this.removeEventListener("log-in",this._authHeaderEvent)}static get observedAttributes(){return["client_id","testing_offline"]}get app(){return this._app}get auth_header(){return this._auth_header}get loggedInAndAuthorized(){return!!this._auth_header&&!this._notAuthorized}get permissions(){return this._app&&this._app.permissions||{}}get server_details(){return this._app&&this._app.server_details||{}}get client_id(){return this.getAttribute("client_id")}set client_id(t){return this.setAttribute("client_id",t)}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(t){t?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}fetchError(t,e){403===t.status?(this._message="User unauthorized - try logging in with a different account",this._notAuthorized=!0,this.render()):"AbortError"!==t.name&&(console.error(t),Object(i.a)(`Unexpected error loading ${e}: ${t.message}`,5e3)),this._app.finishedTask()}render(){Object(n.d)(this._template(this),this,{eventContext:this}),this._app||(this._app=this.firstElementChild,Object(n.d)(this._template(this),this,{eventContext:this}))}attributeChangedCallback(t,e,s){this.render()}}},,,,,,,,,,,function(t,e,s){"use strict";s.r(e);var i=s(0),n=(s(1),s(3)),r=(s(2),s(13));s(12);const o=t=>i["c"]` <swarming-app id=swapp client_id="${t.client_id}" ?testing_offline="${t.testing_offline}"> <header> <div class=title>Swarming</div> <aside class=hideable> <a href=/>Home</a> <a href=/botlist>Bot List</a> <a href=/tasklist>Task List</a> </aside> </header> <main> <h2>Service Status</h2> <div>Server Version: <span class=server_version> ${t.server_details.server_version}</span> </div> <div>Bot Version: ${t.server_details.bot_version} </div> <ul> <li>  <a href=/stats>Usage statistics</a> </li> <li> <a href=/restricted/mapreduce/status>Map Reduce Jobs</a> </li> <li> <a href=${(t=>"https://console.cloud.google.com/appengine/instances"+`project=${t._project_id}&versionId=${t.server_details.server_version}`)(t)}>View version's instances on Cloud Console</a> </li> <li> <a><a href=${(t=>`https://console.cloud.google.com/errors?project=${t}`)(t._project_id)}>View server errors on Cloud Console</a></a> </li> <li> <a><a href=${(t=>`https://console.cloud.google.com/logs/viewer?filters=status:500..599&project=${t}`)(t._project_id)}>View logs for HTTP 5xx on Cloud Console</a></a> </li> </ul> <h2>Configuration</h2> <ul>  <li> <a href="/restricted/config">View server config</a> </li> <li> <a href="/restricted/upload/bootstrap">View/upload bootstrap.py</a> </li> <li> <a href="/restricted/upload/bot_config">View/upload bot_config.py</a> </li> <li> <a href="/auth/groups">View/edit user groups</a> </li> </ul> ${t.permissions.get_bootstrap_token?(t=>i["c"]` <div> <h2>Bootstrapping a bot</h2> To bootstrap a bot, run one of these (all links are valid for 1 hour): <ol> <li> <strong> TL;DR; </strong> <pre class=command>python -c "import urllib; exec urllib.urlopen('${t._host_url}/bootstrap?tok=${t._bootstrap_token}').read()"</pre> </li> <li> Escaped version to pass as a ssh argument: <pre class=command>'python -c "import urllib; exec urllib.urlopen('"'${t._host_url}/bootstrap?tok=${t._bootstrap_token}'"').read()"'</pre> </li> <li> Manually: <pre class=command>mkdir bot; cd bot
rm -f swarming_bot.zip; curl -sSLOJ ${t._host_url}/bot_code?tok=${t._bootstrap_token}
python swarming_bot.zip</pre> </li> </ol> </div> `)(t):""} </main> <footer></footer> </swarming-app>`;window.customElements.define("swarming-index",class extends r.a{constructor(){super(o),this._bootstrap_token="...";let t=location.hostname.indexOf(".appspot.com");this._project_id=location.hostname.substring(0,t)||"not_found",this._host_url=location.origin}connectedCallback(){super.connectedCallback(),this.addEventListener("permissions-loaded",t=>{this.permissions.get_bootstrap_token&&this._fetchToken(),this.render()}),this.addEventListener("server-details-loaded",t=>{this.render()}),this.render()}_fetchToken(){let t={headers:{authorization:this.auth_header},method:"POST"};this.app.addBusyTasks(1),fetch("/_ah/api/swarming/v1/server/token",t).then(n.a).then(t=>{this._bootstrap_token=t.bootstrap_token,this.render(),this.app.finishedTask()}).catch(t=>this.fetchError(t,"token"))}});s(31)},,,,,,,function(t,e){},,,,,,function(t,e){},function(t,e){},function(t,e){},function(t,e){},,function(t,e){}]);