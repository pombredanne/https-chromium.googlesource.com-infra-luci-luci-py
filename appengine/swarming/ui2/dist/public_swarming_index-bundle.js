(()=>{"use strict";var e={445:function(e,t){var s=this&&this.__awaiter||function(e,t,s,i){return new(s||(s=Promise))((function(n,r){function o(e){try{l(i.next(e))}catch(e){r(e)}}function a(e){try{l(i.throw(e))}catch(e){r(e)}}function l(e){var t;e.done?n(e.value):(t=e.value,t instanceof s?t:new s((function(e){e(t)}))).then(o,a)}l((i=i.apply(e,t||[])).next())}))};Object.defineProperty(t,"__esModule",{value:!0}),t.RpcCode=Object.freeze({OK:0,CANCELED:1,UNKNOWN:2,INVALID_ARGUMENT:3,DEADLINE_EXCEEDED:4,NOT_FOUND:5,ALREADY_EXISTS:6,PERMISSION_DENIED:7,RESOURCE_EXHAUSTED:8,FAILED_PRECONDITION:9,ABORTED:10,OUT_OF_RANGE:11,UNIMPLEMENTED:12,INTERNAL:13,UNAVAILABLE:14,DATA_LOSS:15,UNAUTHENTICATED:16});const i={};for(const e in t.RpcCode)i[t.RpcCode[e]]=e;function n(e){return i[e]}t.rpcCodeToCodeName=n,t.PrpcClient=class{constructor(e=null){e=e||{},this.host=e.host||document.location.host,this.accessToken=e.accessToken||null,this.insecure=e.hasOwnProperty("insecure")&&Boolean(e.insecure),this.fetchImpl=e.fetchImpl||window.fetch.bind(window)}call(e,i,n,a){return s(this,void 0,void 0,(function*(){if(!e)throw new TypeError("missing required argument: service");if(!i)throw new TypeError("missing required argument: method");if(!n)throw new TypeError("missing required argument: message");if(!(n instanceof Object))throw new TypeError("argument `message` must be a protobuf object");const s=`${!0===this.insecure?"http:":"https:"}//${this.host}/prpc/${e}/${i}`,l=this._requestOptions(n,a),h=yield this.fetchImpl(s,l);if(!h.headers.has("X-Prpc-Grpc-Code"))throw new o(h.status,"Invalid response: no X-Prpc-Grpc-Code response header");const c=Number.parseInt(h.headers.get("X-Prpc-Grpc-Code"),10);if(Number.isNaN(c))throw new o(h.status,"Invalid X-Prpc-Grpc-Code response header");const d=yield h.text();if(c!==t.RpcCode.OK)throw new r(c,d);if(!d.startsWith(")]}'"))throw new o(h.status,"Response body does not start with XSSI prefix: )]}'");return JSON.parse(d.substr(")]}'".length))}))}_requestOptions(e,t){const s={accept:"application/json","content-type":"application/json"};return t&&Object.assign(s,t),this.accessToken&&(s.authorization=`Bearer ${this.accessToken}`),{credentials:"omit",method:"POST",headers:s,body:JSON.stringify(e)}}};class r extends Error{constructor(e,t){if(super(),this.code=e,this.description=t,null===e)throw new Error("missing required argument: code");this.codeName=n(e)}get message(){return`code: ${this.code} (${this.codeName}) desc: ${this.description}`}}t.GrpcError=r;class o extends Error{constructor(e,t){if(super(),this.httpStatus=e,this.description=t,null===e)throw new Error("missing required argument: httpStatus")}get message(){return`status: ${this.httpStatus} desc: ${this.description}`}}t.ProtocolError=o}},t={};function s(i){var n=t[i];if(void 0!==n)return n.exports;var r=t[i]={exports:{}};return e[i].call(r.exports,r,r.exports,s),r.exports}(()=>{const e=new WeakMap,t=t=>"function"==typeof t&&e.has(t),i=void 0!==window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,n=(e,t,s=null)=>{let i=t;for(;i!==s;){const t=i.nextSibling;e.removeChild(i),i=t}},r={},o={},a=`{{lit-${String(Math.random()).slice(2)}}}`,l=`\x3c!--${a}--\x3e`,h=new RegExp(`${a}|${l}`),c="$lit$";class d{constructor(e,t){this.parts=[],this.element=t;let s=-1,i=0;const n=[],r=t=>{const o=t.content,l=document.createTreeWalker(o,133,null,!1);let d=0;for(;l.nextNode();){s++;const t=l.currentNode;if(1===t.nodeType){if(t.hasAttributes()){const n=t.attributes;let r=0;for(let e=0;e<n.length;e++)n[e].value.indexOf(a)>=0&&r++;for(;r-- >0;){const n=e.strings[i],r=_.exec(n)[2],o=r.toLowerCase()+c,a=t.getAttribute(o).split(h);this.parts.push({type:"attribute",index:s,name:r,strings:a}),t.removeAttribute(o),i+=a.length-1}}"TEMPLATE"===t.tagName&&r(t)}else if(3===t.nodeType){const e=t.data;if(e.indexOf(a)>=0){const r=t.parentNode,o=e.split(h),a=o.length-1;for(let e=0;e<a;e++)r.insertBefore(""===o[e]?p():document.createTextNode(o[e]),t),this.parts.push({type:"node",index:++s});""===o[a]?(r.insertBefore(p(),t),n.push(t)):t.data=o[a],i+=a}}else if(8===t.nodeType)if(t.data===a){const e=t.parentNode;null!==t.previousSibling&&s!==d||(s++,e.insertBefore(p(),t)),d=s,this.parts.push({type:"node",index:s}),null===t.nextSibling?t.data="":(n.push(t),s--),i++}else{let e=-1;for(;-1!==(e=t.data.indexOf(a,e+1));)this.parts.push({type:"node",index:-1})}}};r(t);for(const e of n)e.parentNode.removeChild(e)}}const u=e=>-1!==e.index,p=()=>document.createComment(""),_=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F \x09\x0a\x0c\x0d"'>=/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/;class m{constructor(e,t,s){this._parts=[],this.template=e,this.processor=t,this.options=s}update(e){let t=0;for(const s of this._parts)void 0!==s&&s.setValue(e[t]),t++;for(const e of this._parts)void 0!==e&&e.commit()}_clone(){const e=i?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),t=this.template.parts;let s=0,n=0;const r=e=>{const i=document.createTreeWalker(e,133,null,!1);let o=i.nextNode();for(;s<t.length&&null!==o;){const e=t[s];if(u(e))if(n===e.index){if("node"===e.type){const e=this.processor.handleTextExpression(this.options);e.insertAfterNode(o.previousSibling),this._parts.push(e)}else this._parts.push(...this.processor.handleAttributeExpressions(o,e.name,e.strings,this.options));s++}else n++,"TEMPLATE"===o.nodeName&&r(o.content),o=i.nextNode();else this._parts.push(void 0),s++}};return r(e),i&&(document.adoptNode(e),customElements.upgrade(e)),e}}class g{constructor(e,t,s,i){this.strings=e,this.values=t,this.type=s,this.processor=i}getHTML(){const e=this.strings.length-1;let t="";for(let s=0;s<e;s++){const e=this.strings[s],i=_.exec(e);t+=i?e.substr(0,i.index)+i[1]+i[2]+c+i[3]+a:e+l}return t+this.strings[e]}getTemplateElement(){const e=document.createElement("template");return e.innerHTML=this.getHTML(),e}}const f=e=>null===e||!("object"==typeof e||"function"==typeof e);class v{constructor(e,t,s){this.dirty=!0,this.element=e,this.name=t,this.strings=s,this.parts=[];for(let e=0;e<s.length-1;e++)this.parts[e]=this._createPart()}_createPart(){return new b(this)}_getValue(){const e=this.strings,t=e.length-1;let s="";for(let i=0;i<t;i++){s+=e[i];const t=this.parts[i];if(void 0!==t){const e=t.value;if(null!=e&&(Array.isArray(e)||"string"!=typeof e&&e[Symbol.iterator]))for(const t of e)s+="string"==typeof t?t:String(t);else s+="string"==typeof e?e:String(e)}}return s+e[t]}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class b{constructor(e){this.value=void 0,this.committer=e}setValue(e){e===r||f(e)&&e===this.value||(this.value=e,t(e)||(this.committer.dirty=!0))}commit(){for(;t(this.value);){const e=this.value;this.value=r,e(this)}this.value!==r&&this.committer.commit()}}class w{constructor(e){this.value=void 0,this._pendingValue=void 0,this.options=e}appendInto(e){this.startNode=e.appendChild(p()),this.endNode=e.appendChild(p())}insertAfterNode(e){this.startNode=e,this.endNode=e.nextSibling}appendIntoPart(e){e._insert(this.startNode=p()),e._insert(this.endNode=p())}insertAfterPart(e){e._insert(this.startNode=p()),this.endNode=e.endNode,e.endNode=this.startNode}setValue(e){this._pendingValue=e}commit(){for(;t(this._pendingValue);){const e=this._pendingValue;this._pendingValue=r,e(this)}const e=this._pendingValue;e!==r&&(f(e)?e!==this.value&&this._commitText(e):e instanceof g?this._commitTemplateResult(e):e instanceof Node?this._commitNode(e):Array.isArray(e)||e[Symbol.iterator]?this._commitIterable(e):e===o?(this.value=o,this.clear()):this._commitText(e))}_insert(e){this.endNode.parentNode.insertBefore(e,this.endNode)}_commitNode(e){this.value!==e&&(this.clear(),this._insert(e),this.value=e)}_commitText(e){const t=this.startNode.nextSibling;e=null==e?"":e,t===this.endNode.previousSibling&&3===t.nodeType?t.data=e:this._commitNode(document.createTextNode("string"==typeof e?e:String(e))),this.value=e}_commitTemplateResult(e){const t=this.options.templateFactory(e);if(this.value instanceof m&&this.value.template===t)this.value.update(e.values);else{const s=new m(t,e.processor,this.options),i=s._clone();s.update(e.values),this._commitNode(i),this.value=s}}_commitIterable(e){Array.isArray(this.value)||(this.value=[],this.clear());const t=this.value;let s,i=0;for(const n of e)void 0===(s=t[i])&&(s=new w(this.options),t.push(s),0===i?s.appendIntoPart(this):s.insertAfterPart(t[i-1])),s.setValue(n),s.commit(),i++;i<t.length&&(t.length=i,this.clear(s&&s.endNode))}clear(e=this.startNode){n(this.startNode.parentNode,e.nextSibling,this.endNode)}}class E{constructor(e,t,s){if(this.value=void 0,this._pendingValue=void 0,2!==s.length||""!==s[0]||""!==s[1])throw new Error("Boolean attributes can only contain a single expression");this.element=e,this.name=t,this.strings=s}setValue(e){this._pendingValue=e}commit(){for(;t(this._pendingValue);){const e=this._pendingValue;this._pendingValue=r,e(this)}if(this._pendingValue===r)return;const e=!!this._pendingValue;this.value!==e&&(e?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name)),this.value=e,this._pendingValue=r}}class k extends v{constructor(e,t,s){super(e,t,s),this.single=2===s.length&&""===s[0]&&""===s[1]}_createPart(){return new T(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class T extends b{}let y=!1;try{const e={get capture(){return y=!0,!1}};window.addEventListener("test",e,e),window.removeEventListener("test",e,e)}catch(e){}class x{constructor(e,t,s){this.value=void 0,this._pendingValue=void 0,this.element=e,this.eventName=t,this.eventContext=s,this._boundHandleEvent=e=>this.handleEvent(e)}setValue(e){this._pendingValue=e}commit(){for(;t(this._pendingValue);){const e=this._pendingValue;this._pendingValue=r,e(this)}if(this._pendingValue===r)return;const e=this._pendingValue,s=this.value,i=null==e||null!=s&&(e.capture!==s.capture||e.once!==s.once||e.passive!==s.passive),n=null!=e&&(null==s||i);i&&this.element.removeEventListener(this.eventName,this._boundHandleEvent,this._options),n&&(this._options=C(e),this.element.addEventListener(this.eventName,this._boundHandleEvent,this._options)),this.value=e,this._pendingValue=r}handleEvent(e){"function"==typeof this.value?this.value.call(this.eventContext||this.element,e):this.value.handleEvent(e)}}const C=e=>e&&(y?{capture:e.capture,passive:e.passive,once:e.once}:e.capture),N=new class{handleAttributeExpressions(e,t,s,i){const n=t[0];return"."===n?new k(e,t.slice(1),s).parts:"@"===n?[new x(e,t.slice(1),i.eventContext)]:"?"===n?[new E(e,t.slice(1),s)]:new v(e,t,s).parts}handleTextExpression(e){return new w(e)}};function A(e){let t=L.get(e.type);void 0===t&&(t={stringsArray:new WeakMap,keyString:new Map},L.set(e.type,t));let s=t.stringsArray.get(e.strings);if(void 0!==s)return s;const i=e.strings.join(a);return void 0===(s=t.keyString.get(i))&&(s=new d(e,e.getTemplateElement()),t.keyString.set(i,s)),t.stringsArray.set(e.strings,s),s}const L=new Map,$=new WeakMap,S=(e,t,s)=>{let i=$.get(t);void 0===i&&(n(t,t.firstChild),$.set(t,i=new w(Object.assign({templateFactory:A},s))),i.appendInto(t)),i.setValue(e),i.commit()};(window.litHtmlVersions||(window.litHtmlVersions=[])).push("1.0.0");const V=(e,...t)=>new g(e,t,"html",N);function H(e){if(e.ok)return e.json();throw{message:`Bad network response: ${e.statusText}`,resp:e,status:e.status}}function I(e,t=1e4){"object"==typeof e&&(e=e.message||JSON.stringify(e));var s={message:e,duration:t};document.dispatchEvent(new CustomEvent("error-sk",{detail:s,bubbles:!0}))}function M(e,t){if(e.hasOwnProperty(t)){let s=e[t];delete e[t],e[t]=s}}var O=s(445);class B{constructor(e,t=null,s={}){const i={...s,accessToken:void 0};if(window.LIVE_DEMO&&(i.insecure=!0),this._token=e,t){const e=(e,s)=>(s.signal=t,fetch(e,s));i.fetchImpl=e}this._client=new O.PrpcClient(i)}get service(){throw new Error("Subclasses must define service")}_call(e,t){const s={authorization:this._token};return this._client.call(this.service,e,t,s)}}class D extends B{get service(){return"swarming.v2.Tasks"}cancel(e,t){return this._call("CancelTask",{task_id:e,kill_running:t})}stdout(e,t,s){return this._call("GetStdout",{task_id:e,offset:t,length:s})}request(e){return this._call("GetRequest",{task_id:e})}result(e,t){return this._call("GetResult",{task_id:e,include_performance_stats:t})}new(e){return this._call("NewTask",e)}count(e){return this._call("CountTasks",e)}list(e){return e.state||(e={...e,state:"QUERY_ALL"}),this._call("ListTasks",e)}massCancel(e){return this._call("CancelTasks",e)}}class P extends B{get service(){return"swarming.v2.Bots"}getBot(e){return this._call("GetBot",{bot_id:e})}getTasks(e,t){const s={sort:4,state:10,bot_id:e,cursor:t,limit:30,include_performance_stats:!0};return this._call("ListBotTasks",s)}terminate(e){const t={bot_id:e};return this._call("TerminateBot",t)}events(e,t){const s={limit:50,bot_id:e,cursor:t};return this._call("ListBotEvents",s)}delete(e){return this._call("DeleteBot",{bot_id:e})}count(e){return this._call("CountBots",{dimensions:e})}dimensions(e){return this._call("GetBotDimensions",{pool:e})}list(e){return this._call("ListBots",e)}}class R extends HTMLElement{constructor(e){super(),this._template=e,this._app=null,this._auth_header="",this._profile=null,this._notAuthorized=!1}connectedCallback(){M(this,"testing_offline"),this._authHeaderEvent=e=>{this._auth_header=e.detail.authHeader},this.addEventListener("log-in",this._authHeaderEvent)}disconnectedCallback(){this.removeEventListener("log-in",this._authHeaderEvent)}static get observedAttributes(){return["testing_offline"]}get app(){return this._app}get authHeader(){return this._auth_header}get loggedInAndAuthorized(){return!!this._auth_header&&!this._notAuthorized}get permissions(){return this._app&&this._app.permissions||{}}get profile(){return this._app&&this._app.profile||{}}get serverDetails(){return this._app&&this._app.serverDetails||{}}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(e){e?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}prpcError(e,t,s){"PERMISSION_DENIED"!==e.codeName||s?"AbortError"!==e.name&&(console.error(e),I(`Unexpected error loading ${t}: ${e.message}`,5e3)):(this._message="User unauthorized - try logging in with a different account",this._notAuthorized=!0,this.render()),this._app.finishedTask()}fetchError(e,t,s){403!==e.status||s?"AbortError"!==e.name&&(console.error(e),I(`Unexpected error loading ${t}: ${e.message}`,5e3)):(this._message="User unauthorized - try logging in with a different account",this._notAuthorized=!0,this.render()),this._app.finishedTask()}render(){S(this._template(this),this,{eventContext:this}),this._app||(this._app=this.firstElementChild,S(this._template(this),this,{eventContext:this}))}attributeChangedCallback(e,t,s){this.render()}_createTasksService(){return new D(this.authHeader,this._fetchController.signal)}_createBotService(){return new P(this.authHeader,this._fetchController.signal)}}window.customElements.define("toast-sk",class extends HTMLElement{constructor(){super(),this._timer=null}connectedCallback(){this.hasAttribute("duration")||(this.duration=5e3),M(this,"duration")}get duration(){return+this.getAttribute("duration")}set duration(e){this.setAttribute("duration",e)}show(){this.setAttribute("shown",""),this.duration>0&&!this._timer&&(this._timer=window.setTimeout((()=>{this._timer=null,this.hide()}),this.duration))}hide(){this.removeAttribute("shown"),this._timer&&(window.clearTimeout(this._timer),this._timer=null)}}),window.customElements.define("error-toast-sk",class extends HTMLElement{connectedCallback(){this.innerHTML="<toast-sk></toast-sk>",this._toast=this.firstElementChild,document.addEventListener("error-sk",this)}disconnectedCallback(){document.removeEventListener("error-sk",this)}handleEvent(e){e.detail.duration&&(this._toast.duration=e.detail.duration),this._toast.textContent=e.detail.message,this._toast.show()}});const U=document.createElement("template");U.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M20 8h-2.81c-.45-.78-1.07-1.45-1.82-1.96L17 4.41 15.59 3l-2.17 2.17C12.96 5.06 12.49 5 12 5c-.49 0-.96.06-1.41.17L8.41 3 7 4.41l1.62 1.63C7.88 6.55 7.26 7.22 6.81 8H4v2h2.09c-.05.33-.09.66-.09 1v1H4v2h2v1c0 .34.04.67.09 1H4v2h2.81c1.04 1.79 2.97 3 5.19 3s4.15-1.21 5.19-3H20v-2h-2.09c.05-.33.09-.66.09-1v-1h2v-2h-2v-1c0-.34-.04-.67-.09-1H20V8zm-6 8h-4v-2h4v2zm0-4h-4v-2h4v2z"/></svg>',window.customElements.define("bug-report-icon-sk",class extends HTMLElement{connectedCallback(){let e=U.content.cloneNode(!0);this.appendChild(e)}});const j=document.createElement("template");function z(e){var t=[];return Object.keys(e).sort().forEach((function(s){Array.isArray(e[s])?e[s].forEach((function(e){t.push(encodeURIComponent(s)+"="+encodeURIComponent(e))})):"object"==typeof e[s]?t.push(encodeURIComponent(s)+"="+encodeURIComponent(z(e[s]))):t.push(encodeURIComponent(s)+"="+encodeURIComponent(e[s]))})),t.join("&")}j.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>',window.customElements.define("menu-icon-sk",class extends HTMLElement{connectedCallback(){let e=j.content.cloneNode(!0);this.appendChild(e)}}),window.customElements.define("spinner-sk",class extends HTMLElement{connectedCallback(){M(this,"active")}get active(){return this.hasAttribute("active")}set active(e){e?this.setAttribute("active",""):this.removeAttribute("active")}}),window.customElements.define("oauth-login",class extends HTMLElement{connectedCallback(){M(this,"testing_offline"),this._auth_header="",this._profile=null,this.testing_offline||this._fetchAuthState().then((e=>{"anonymous:anonymous"!=e.identity&&(this._fireLoginEvent(e),this.render())}),(e=>{console.error(e),I(`Error getting auth state: ${JSON.stringify(e)}`,1e4)})),this.render()}static get observedAttributes(){return["testing_offline"]}get authHeader(){return this._auth_header}get profile(){return this._profile}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(e){e?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}_fireLoginEvent(e){this._profile={email:e.email,imageURL:e.picture},this._auth_header=`Bearer ${e.accessToken}`,this.dispatchEvent(new CustomEvent("log-in",{detail:{authHeader:this._auth_header,profile:this._profile},bubbles:!0}))}_logIn(){this.testing_offline?(this._fireLoginEvent({email:"missing@chromium.org",picture:"http://storage.googleapis.com/gd-wagtail-prod-assets/original_images/logo_google_fonts_color_2x_web_64dp.png",accessToken:"12345678910-boomshakalaka"}),this.render()):this._nagivateTo("login")}_logOut(){this.testing_offline?window.location.reload():this._nagivateTo("logout")}_nagivateTo(e){const t=window.location.pathname+window.location.search;window.location=t&&"/"!=t?`/auth/openid/${e}?r=${encodeURIComponent(t)}`:`/auth/openid/${e}`}_fetchAuthState(){return fetch("/auth/openid/state",{mode:"same-origin",credentials:"same-origin",cache:"no-store"}).then(H)}render(){var e;S((e=this).authHeader?V` <div> <img class="center" id="avatar" src="${e._profile.imageURL}" width="30" height="30" /> <span class="center">${e._profile.email}</span> <span class="center">|</span> <a class="center" @click=${e._logOut} href="#">Sign out</a> </div>`:V` <div> <a @click=${e._logIn} href="#">Sign in</a> </div>`,this,{eventContext:this})}attributeChangedCallback(e,t,s){this.render()}});const q=document.createElement("template");q.innerHTML="\n<button class=toggle-button>\n  <menu-icon-sk>\n  </menu-icon-sk>\n</button>\n";const G=document.createElement("template");G.innerHTML="\n<div class=spinner-spacer>\n  <spinner-sk></spinner-sk>\n</div>\n";const F="You must log in to see more details",W=document.createElement("template");W.innerHTML='\n<a target=_blank rel=noopener\n   href="https://bugs.chromium.org/p/chromium/issues/entry?components=Infra%3ELUCI%3ETaskDistribution%3EUI&owner=kjlubick@chromium.org&status=Assigned">\n  <bug-report-icon-sk class=fab></bug-report-icon-sk>\n</a>',window.customElements.define("swarming-app",class extends HTMLElement{constructor(){super(),this._busyTaskCount=0,this._spinner=null,this._dynamicEle=null,this._auth_header="",this._profile={},this._server_details={server_version:F,bot_version:"",cas_viewer_server:""};const e=location.hostname.indexOf(".appspot.com");this._project_id=location.hostname.substring(0,e),this._permissions={}}connectedCallback(){M(this,"testing_offline"),this._addHTML(),this.addEventListener("log-in",(e=>{this._auth_header=e.detail.authHeader,this._profile=e.detail.profile,this._fetch()})),this.render()}static get observedAttributes(){return["testing_offline"]}get busy(){return!!this._busyTaskCount}get permissions(){return this._permissions}get profile(){return this._profile}get serverDetails(){return this._server_details}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(e){e?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}addBusyTasks(e){this._busyTaskCount+=e,this._spinner&&this._busyTaskCount>0&&(this._spinner.active=!0)}finishedTask(){this._busyTaskCount--,this._busyTaskCount<=0&&(this._busyTaskCount=0,this._spinner&&(this._spinner.active=!1),this.dispatchEvent(new CustomEvent("busy-end",{bubbles:!0})))}_addHTML(){const e=this.querySelector("header"),t=e&&e.querySelector("aside"),s=this.querySelector("footer");if(!(e&&t&&t.classList.contains("hideable")))return;let i=q.content.cloneNode(!0);e.insertBefore(i,e.firstElementChild),(i=e.firstElementChild).addEventListener("click",(e=>this._toggleMenu(e,t)));const n=G.content.cloneNode(!0);e.insertBefore(n,t),this._spinner=e.querySelector("spinner-sk");const r=document.createElement("span");r.classList.add("grow"),e.appendChild(r),this._dynamicEle=document.createElement("div"),this._dynamicEle.classList.add("right"),e.appendChild(this._dynamicEle);const o=document.createElement("error-toast-sk");s.append(o);const a=W.content.cloneNode(!0);s.append(a)}_toggleMenu(e,t){t.classList.toggle("shown")}_fetch(){if(!this._auth_header)return;this._server_details={server_version:"<loading>",bot_version:"<loading>"};const e={headers:{authorization:this._auth_header}};this.addBusyTasks(1),fetch("/_ah/api/swarming/v1/server/details",e).then(H).then((e=>{this._server_details=e,this.render(),this.dispatchEvent(new CustomEvent("server-details-loaded",{bubbles:!0})),this.finishedTask()})).catch((e=>{403===e.status?(this._server_details={server_version:"User unauthorized - try logging in with a different account",bot_version:""},this.render()):(console.error(e),I(`Unexpected error loading details: ${e.message}`,5e3)),this.finishedTask()})),this._fetchPermissions(e)}_fetchPermissions(e,t){this.addBusyTasks(1);let s="/_ah/api/swarming/v1/server/permissions";return t&&(s+=`?${z(t)}`),fetch(s,e).then(H).then((e=>{this._permissions=e,this.render(),this.dispatchEvent(new CustomEvent("permissions-loaded",{bubbles:!0})),this.finishedTask()})).catch((e=>{403!==e.status&&(console.error(e),I(`Unexpected error loading permissions: ${e.message}`,5e3)),this.finishedTask()}))}render(){var e;this._dynamicEle&&S(V` <div class="server-version"> AppEngine version: ${function(e,t){return t&&t.server_version?V`<a href=${"https://console.cloud.google.com/appengine/versions?project=".concat(e,"&serviceId=default&pageState=(%22versionsTable%22:(%22f%22:%22%255B%257B_22k_22_3A_22Version_22_2C_22t_22_3A10_2C_22v_22_3A_22_5C_22",t.server_version,"_5C_22_22_2C_22s_22_3Atrue_2C_22i_22_3A_22id_22%257D%255D%22))")} > ${t.server_version}</a >`:F}((e=this)._project_id,e._server_details)} Git version:${function(e){if(!e||!e.server_version)return"";const t=e.server_version.split("-");if(t.length>=3)return console.error(`Invalid Git version. version=${e.server_version}`),"";const s=2==t.length?t[1]:t[0];return V`<a href=https://chromium.googlesource.com/infra/luci/luci-py/+/${s}>${s}</a>`}(e._server_details)} </div> <oauth-login ?testing_offline=${e.testing_offline}> </oauth-login>`,this._dynamicEle)}attributeChangedCallback(e,t,s){this.render()}});const X=e=>V` <swarming-app id=swapp ?testing_offline="${e.testing_offline}"> <header> <div class=title>Swarming</div> <aside class=hideable> <a href=/>Home</a> <a href=/botlist>Bot List</a> <a href=/tasklist>Task List</a> <a href=/bot>Bot Page</a> <a href=/task>Task Page</a> </aside> </header> <main> <h2>Service Status</h2> <div>Server Version: <span class=server_version> ${e.serverDetails.server_version}</span> </div> <div>Bot Version: ${e.serverDetails.bot_version} </div> <ul> <li> <a href=${(e=>`https://console.cloud.google.com/appengine/instances?project=${e._project_id}&versionId=${e.serverDetails.server_version}`)(e)}>View version's instances on Cloud Console</a> </li> <li> <a href=${(e=>`https://console.cloud.google.com/errors?project=${e}`)(e._project_id)}>View server errors on Cloud Console</a> </li> <li> <a href=${(e=>`https://console.cloud.google.com/logs/viewer?filters=status:500..599&project=${e}`)(e._project_id)}>View logs for HTTP 5xx on Cloud Console</a> </li> <li> <a href="/restricted/ereporter2/report">View ereporter2 report</a> </li> </ul> <h2>Configuration</h2> <ul>  <li> <a href="/restricted/config">View server config</a> </li> <li> <a href="/restricted/upload/bootstrap">View/upload bootstrap.py</a> </li> <li> <a href="/restricted/upload/bot_config">View/upload bot_config.py</a> </li> <li> <a href="/auth/groups">View/edit user groups</a> </li> </ul> ${e.permissions.get_bootstrap_token?(e=>V`
  <div>
    <h2>Bootstrapping a bot</h2>
    <div>
      To bootstrap a bot, run one of these (all links are valid for 1 hour):
    </div>
    <ol>
      <li>
        <strong> TL;DR; </strong>
        <pre class="command">
python3 -c "import urllib.request; exec(urllib.request.urlopen('${e._host_url}/bootstrap?tok=${e._bootstrap_token}').read())"</pre
        >
      </li>
      <li>
        Escaped version to pass as a ssh argument:
        <pre class="command">
'python3 -c "import urllib.request; exec(urllib.request.urlopen('"'${e._host_url}/bootstrap?tok=${e._bootstrap_token}'"').read())"'</pre
        >
      </li>
      <li>
        Manually:
        <pre class="command">
mkdir bot; cd bot
rm -f swarming_bot.zip; curl -sSLOJ ${e._host_url}/bot_code?tok=${e._bootstrap_token}
python3 swarming_bot.zip</pre
        >
      </li>
    </ol>
    <div>Windows bot requires pywin32, Mac bot requires pyobjc</div>
  </div>
`)(e):""} </main> <footer></footer> </swarming-app>`;window.customElements.define("swarming-index",class extends R{constructor(){super(X),this._bootstrap_token="...";const e=location.hostname.indexOf(".appspot.com");this._project_id=location.hostname.substring(0,e)||"not_found",this._host_url=location.origin}connectedCallback(){super.connectedCallback(),this.addEventListener("permissions-loaded",(e=>{this.permissions.get_bootstrap_token&&this._fetchToken(),this.render()})),this.addEventListener("server-details-loaded",(e=>{this.render()})),this.render()}_fetchToken(){const e={headers:{authorization:this.authHeader},method:"POST"};this.app.addBusyTasks(1),fetch("/_ah/api/swarming/v1/server/token",e).then(H).then((e=>{this._bootstrap_token=e.bootstrap_token,this.render(),this.app.finishedTask()})).catch((e=>this.fetchError(e,"token")))}})})()})();