!function(t){var e={};function s(i){if(e[i])return e[i].exports;var n=e[i]={i:i,l:!1,exports:{}};return t[i].call(n.exports,n,n.exports,s),n.l=!0,n.exports}s.m=t,s.c=e,s.d=function(t,e,i){s.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:i})},s.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},s.t=function(t,e){if(1&e&&(t=s(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var i=Object.create(null);if(s.r(i),Object.defineProperty(i,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var n in t)s.d(i,n,function(e){return t[e]}.bind(null,n));return i},s.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return s.d(e,"a",e),e},s.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},s.p="/newres/",s(s.s=57)}([function(t,e,s){"use strict";s.d(e,"b",(function(){return a.a})),s.d(e,"a",(function(){return i.b})),s.d(e,"d",(function(){return h})),s.d(e,"c",(function(){return p}));var i=s(3);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const n=new class{handleAttributeExpressions(t,e,s,n){const r=e[0];if("."===r){return new i.f(t,e.slice(1),s).parts}return"@"===r?[new i.d(t,e.slice(1),n.eventContext)]:"?"===r?[new i.c(t,e.slice(1),s)]:new i.a(t,e,s).parts}handleTextExpression(t){return new i.e(t)}};var r=s(12),a=s(11),o=s(9),d=(s(5),s(2));
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
function c(t){let e=l.get(t.type);void 0===e&&(e={stringsArray:new WeakMap,keyString:new Map},l.set(t.type,e));let s=e.stringsArray.get(t.strings);if(void 0!==s)return s;const i=t.strings.join(d.f);return s=e.keyString.get(i),void 0===s&&(s=new d.a(t,t.getTemplateElement()),e.keyString.set(i,s)),e.stringsArray.set(t.strings,s),s}const l=new Map,u=new WeakMap,h=(t,e,s)=>{let n=u.get(e);void 0===n&&(Object(o.b)(e,e.firstChild),u.set(e,n=new i.e(Object.assign({templateFactory:c},s))),n.appendInto(e)),n.setValue(t),n.commit()};
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */s(16);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */(window.litHtmlVersions||(window.litHtmlVersions=[])).push("1.0.0");const p=(t,...e)=>new r.b(t,e,"html",n)},function(t,e,s){"use strict";function i(t,e){if(t.hasOwnProperty(e)){let s=t[e];delete t[e],t[e]=s}}s.d(e,"a",(function(){return i}))},function(t,e,s){"use strict";s.d(e,"f",(function(){return i})),s.d(e,"g",(function(){return n})),s.d(e,"b",(function(){return a})),s.d(e,"a",(function(){return o})),s.d(e,"d",(function(){return d})),s.d(e,"c",(function(){return c})),s.d(e,"e",(function(){return l}));
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const i=`{{lit-${String(Math.random()).slice(2)}}}`,n=`\x3c!--${i}--\x3e`,r=new RegExp(`${i}|${n}`),a="$lit$";class o{constructor(t,e){this.parts=[],this.element=e;let s=-1,n=0;const o=[],d=e=>{const u=e.content,h=document.createTreeWalker(u,133,null,!1);let p=0;for(;h.nextNode();){s++;const e=h.currentNode;if(1===e.nodeType){if(e.hasAttributes()){const o=e.attributes;let d=0;for(let t=0;t<o.length;t++)o[t].value.indexOf(i)>=0&&d++;for(;d-- >0;){const i=t.strings[n],o=l.exec(i)[2],d=o.toLowerCase()+a,c=e.getAttribute(d).split(r);this.parts.push({type:"attribute",index:s,name:o,strings:c}),e.removeAttribute(d),n+=c.length-1}}"TEMPLATE"===e.tagName&&d(e)}else if(3===e.nodeType){const t=e.data;if(t.indexOf(i)>=0){const i=e.parentNode,a=t.split(r),d=a.length-1;for(let t=0;t<d;t++)i.insertBefore(""===a[t]?c():document.createTextNode(a[t]),e),this.parts.push({type:"node",index:++s});""===a[d]?(i.insertBefore(c(),e),o.push(e)):e.data=a[d],n+=d}}else if(8===e.nodeType)if(e.data===i){const t=e.parentNode;null!==e.previousSibling&&s!==p||(s++,t.insertBefore(c(),e)),p=s,this.parts.push({type:"node",index:s}),null===e.nextSibling?e.data="":(o.push(e),s--),n++}else{let t=-1;for(;-1!==(t=e.data.indexOf(i,t+1));)this.parts.push({type:"node",index:-1})}}};d(e);for(const t of o)t.parentNode.removeChild(t)}}const d=t=>-1!==t.index,c=()=>document.createComment(""),l=/([ \x09\x0a\x0c\x0d])([^\0-\x1F\x7F-\x9F \x09\x0a\x0c\x0d"'>=/]+)([ \x09\x0a\x0c\x0d]*=[ \x09\x0a\x0c\x0d]*(?:[^ \x09\x0a\x0c\x0d"'`<>=]*|"[^"]*|'[^']*))$/},function(t,e,s){"use strict";s.d(e,"g",(function(){return c})),s.d(e,"a",(function(){return l})),s.d(e,"b",(function(){return u})),s.d(e,"e",(function(){return h})),s.d(e,"c",(function(){return p})),s.d(e,"f",(function(){return _})),s.d(e,"d",(function(){return g}));var i=s(11),n=s(9),r=s(5),a=s(16),o=s(12),d=s(2);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const c=t=>null===t||!("object"==typeof t||"function"==typeof t);class l{constructor(t,e,s){this.dirty=!0,this.element=t,this.name=e,this.strings=s,this.parts=[];for(let t=0;t<s.length-1;t++)this.parts[t]=this._createPart()}_createPart(){return new u(this)}_getValue(){const t=this.strings,e=t.length-1;let s="";for(let i=0;i<e;i++){s+=t[i];const e=this.parts[i];if(void 0!==e){const t=e.value;if(null!=t&&(Array.isArray(t)||"string"!=typeof t&&t[Symbol.iterator]))for(const e of t)s+="string"==typeof e?e:String(e);else s+="string"==typeof t?t:String(t)}}return s+=t[e],s}commit(){this.dirty&&(this.dirty=!1,this.element.setAttribute(this.name,this._getValue()))}}class u{constructor(t){this.value=void 0,this.committer=t}setValue(t){t===r.a||c(t)&&t===this.value||(this.value=t,Object(i.b)(t)||(this.committer.dirty=!0))}commit(){for(;Object(i.b)(this.value);){const t=this.value;this.value=r.a,t(this)}this.value!==r.a&&this.committer.commit()}}class h{constructor(t){this.value=void 0,this._pendingValue=void 0,this.options=t}appendInto(t){this.startNode=t.appendChild(Object(d.c)()),this.endNode=t.appendChild(Object(d.c)())}insertAfterNode(t){this.startNode=t,this.endNode=t.nextSibling}appendIntoPart(t){t._insert(this.startNode=Object(d.c)()),t._insert(this.endNode=Object(d.c)())}insertAfterPart(t){t._insert(this.startNode=Object(d.c)()),this.endNode=t.endNode,t.endNode=this.startNode}setValue(t){this._pendingValue=t}commit(){for(;Object(i.b)(this._pendingValue);){const t=this._pendingValue;this._pendingValue=r.a,t(this)}const t=this._pendingValue;t!==r.a&&(c(t)?t!==this.value&&this._commitText(t):t instanceof o.b?this._commitTemplateResult(t):t instanceof Node?this._commitNode(t):Array.isArray(t)||t[Symbol.iterator]?this._commitIterable(t):t===r.b?(this.value=r.b,this.clear()):this._commitText(t))}_insert(t){this.endNode.parentNode.insertBefore(t,this.endNode)}_commitNode(t){this.value!==t&&(this.clear(),this._insert(t),this.value=t)}_commitText(t){const e=this.startNode.nextSibling;t=null==t?"":t,e===this.endNode.previousSibling&&3===e.nodeType?e.data=t:this._commitNode(document.createTextNode("string"==typeof t?t:String(t))),this.value=t}_commitTemplateResult(t){const e=this.options.templateFactory(t);if(this.value instanceof a.a&&this.value.template===e)this.value.update(t.values);else{const s=new a.a(e,t.processor,this.options),i=s._clone();s.update(t.values),this._commitNode(i),this.value=s}}_commitIterable(t){Array.isArray(this.value)||(this.value=[],this.clear());const e=this.value;let s,i=0;for(const n of t)s=e[i],void 0===s&&(s=new h(this.options),e.push(s),0===i?s.appendIntoPart(this):s.insertAfterPart(e[i-1])),s.setValue(n),s.commit(),i++;i<e.length&&(e.length=i,this.clear(s&&s.endNode))}clear(t=this.startNode){Object(n.b)(this.startNode.parentNode,t.nextSibling,this.endNode)}}class p{constructor(t,e,s){if(this.value=void 0,this._pendingValue=void 0,2!==s.length||""!==s[0]||""!==s[1])throw new Error("Boolean attributes can only contain a single expression");this.element=t,this.name=e,this.strings=s}setValue(t){this._pendingValue=t}commit(){for(;Object(i.b)(this._pendingValue);){const t=this._pendingValue;this._pendingValue=r.a,t(this)}if(this._pendingValue===r.a)return;const t=!!this._pendingValue;this.value!==t&&(t?this.element.setAttribute(this.name,""):this.element.removeAttribute(this.name)),this.value=t,this._pendingValue=r.a}}class _ extends l{constructor(t,e,s){super(t,e,s),this.single=2===s.length&&""===s[0]&&""===s[1]}_createPart(){return new f(this)}_getValue(){return this.single?this.parts[0].value:super._getValue()}commit(){this.dirty&&(this.dirty=!1,this.element[this.name]=this._getValue())}}class f extends u{}let m=!1;try{const t={get capture(){return m=!0,!1}};window.addEventListener("test",t,t),window.removeEventListener("test",t,t)}catch(t){}class g{constructor(t,e,s){this.value=void 0,this._pendingValue=void 0,this.element=t,this.eventName=e,this.eventContext=s,this._boundHandleEvent=t=>this.handleEvent(t)}setValue(t){this._pendingValue=t}commit(){for(;Object(i.b)(this._pendingValue);){const t=this._pendingValue;this._pendingValue=r.a,t(this)}if(this._pendingValue===r.a)return;const t=this._pendingValue,e=this.value,s=null==t||null!=e&&(t.capture!==e.capture||t.once!==e.once||t.passive!==e.passive),n=null!=t&&(null==e||s);s&&this.element.removeEventListener(this.eventName,this._boundHandleEvent,this._options),n&&(this._options=b(t),this.element.addEventListener(this.eventName,this._boundHandleEvent,this._options)),this.value=t,this._pendingValue=r.a}handleEvent(t){"function"==typeof this.value?this.value.call(this.eventContext||this.element,t):this.value.handleEvent(t)}}const b=t=>t&&(m?{capture:t.capture,passive:t.passive,once:t.once}:t.capture)},function(t,e,s){"use strict";s.d(e,"b",(function(){return a})),s.d(e,"a",(function(){return o})),s.d(e,"c",(function(){return d})),s.d(e,"d",(function(){return c})),s.d(e,"e",(function(){return l})),s.d(e,"f",(function(){return u})),s.d(e,"g",(function(){return h})),s.d(e,"h",(function(){return p})),s.d(e,"i",(function(){return _})),s.d(e,"j",(function(){return f})),s.d(e,"k",(function(){return m})),s.d(e,"l",(function(){return g}));var i=s(13),n=s(7),r=s(1);function a(t){if(t)return"/bot?id="+t}function o(t=[],e=[]){const s=[];for(const e of t)if(e.key&&e.value)if(Array.isArray(e.value))for(const t of e.value)s.push(e.key+":"+t);else s.push(e.key+":"+e.value);else s.push(e);const i={f:s,c:e};return"/botlist?"+n.b(i)}function d(t){return t||(t=[]),function(e,s){let i=t.indexOf(e);-1===i&&(i=t.length+1);let n=t.indexOf(s);return-1===n&&(n=t.length+1),i===n?e.localeCompare(s):i-n}}function c(t){if(0===t||"0"===t)return"0s";if(!t)return"--";const e=parseFloat(t);return e?e>60?i.e(e):e.toFixed(2)+"s":t+" seconds"}function l(t,e,s=!0){Object(r.a)(t,e),void 0===t[e]&&t.hasAttribute(e)&&(t[e]=t.getAttribute(e),s&&t.removeAttribute(e))}function u(){return window.innerWidth<600||window.innerHeight<600}function h(t){let e=t.slice(0,-1);if(!/[1-9][0-9]*/.test(e))return null;switch(e=parseInt(e),t.slice(-1)){case"h":e*=60;case"m":e*=60;case"s":break;default:return null}return e}function p(t,e){if(t["human_"+e]="--",t[e]){t[e].endsWith&&!t[e].endsWith("Z")&&(t[e]+="Z"),t[e]=new Date(t[e]);const s=t[e].toString(),i=s.substring(s.indexOf("("));t["human_"+e]=t[e].toLocaleString()+" "+i}}function _(t=[],e=[]){const s=[];for(const e of t)if(e.key&&e.value)if(Array.isArray(e.value))for(const t of e.value)s.push(e.key+":"+t);else s.push(e.key+":"+e.value);else s.push(e);for(let t=2;t<arguments.length;t++)s.push(arguments[t]);const i={f:s,c:e};return"/tasklist?"+n.b(i)}function f(t,e){if(t)return e||(t=t.substring(0,t.length-1)+"0"),`/task?id=${t}`}function m(t){return t?i.c(t.getTime())||"0s":"eons"}function g(t,e){return t?(e||(e=new Date),i.e((e.getTime()-t.getTime())/1e3)||"0s"):"eons"}},function(t,e,s){"use strict";s.d(e,"a",(function(){return i})),s.d(e,"b",(function(){return n}));
/**
 * @license
 * Copyright (c) 2018 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const i={},n={}},function(t,e,s){"use strict";s.d(e,"c",(function(){return i})),s.d(e,"a",(function(){return n})),s.d(e,"b",(function(){return r}));const i=new Promise((function(t,e){"loading"!==document.readyState?t():document.addEventListener("DOMContentLoaded",t)})),n=(t,e=document)=>Array.prototype.slice.call(e.querySelectorAll(t)),r=(t,e=document)=>e.querySelector(t)},function(t,e,s){"use strict";function i(t){if(!t)return"";var e=[];return Object.keys(t).sort().forEach((function(s){t[s].forEach((function(t){e.push(encodeURIComponent(s)+"="+encodeURIComponent(t))}))})),e.join("&")}function n(t){var e=[];return Object.keys(t).sort().forEach((function(s){Array.isArray(t[s])?t[s].forEach((function(t){e.push(encodeURIComponent(s)+"="+encodeURIComponent(t))})):"object"==typeof t[s]?e.push(encodeURIComponent(s)+"="+encodeURIComponent(n(t[s]))):e.push(encodeURIComponent(s)+"="+encodeURIComponent(t[s]))})),e.join("&")}function r(t,e){e=e||{};for(var s={},i=t.split("&"),n=0;n<i.length;n++){var a=i[n].split("=",2);if(2==a.length){var o=decodeURIComponent(a[0]),d=decodeURIComponent(a[1]);if(e.hasOwnProperty(o))switch(typeof e[o]){case"boolean":s[o]="true"==d;break;case"number":s[o]=Number(d);break;case"object":if(Array.isArray(e[o])){var c=s[o]||[];c.push(d),s[o]=c}else s[o]=r(d,e[o]);break;case"string":s[o]=d;break;default:s[o]=d}else s[o]=d}}return s}s.d(e,"b",(function(){return i})),s.d(e,"a",(function(){return n})),s.d(e,"c",(function(){return r}))},function(t,e,s){"use strict";function i(t,e=1e4){"object"==typeof t&&(t=t.message||JSON.stringify(t));var s={message:t,duration:e};document.dispatchEvent(new CustomEvent("error-sk",{detail:s,bubbles:!0}))}s.d(e,"a",(function(){return i}))},function(t,e,s){"use strict";s.d(e,"a",(function(){return i})),s.d(e,"c",(function(){return n})),s.d(e,"b",(function(){return r}));
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const i=void 0!==window.customElements&&void 0!==window.customElements.polyfillWrapFlushCallback,n=(t,e,s=null,i=null)=>{let n=e;for(;n!==s;){const e=n.nextSibling;t.insertBefore(n,i),n=e}},r=(t,e,s=null)=>{let i=e;for(;i!==s;){const e=i.nextSibling;t.removeChild(i),i=e}}},function(t,e,s){"use strict";function i(t){if(t.ok)return t.json();throw{message:`Bad network response: ${t.statusText}`,resp:t,status:t.status}}s.d(e,"a",(function(){return i}))},function(t,e,s){"use strict";s.d(e,"a",(function(){return n})),s.d(e,"b",(function(){return r}));
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const i=new WeakMap,n=t=>(...e)=>{const s=t(...e);return i.set(s,!0),s},r=t=>"function"==typeof t&&i.has(t)},function(t,e,s){"use strict";s.d(e,"b",(function(){return r})),s.d(e,"a",(function(){return a}));var i=s(9),n=s(2);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
class r{constructor(t,e,s,i){this.strings=t,this.values=e,this.type=s,this.processor=i}getHTML(){const t=this.strings.length-1;let e="";for(let s=0;s<t;s++){const t=this.strings[s],i=n.e.exec(t);e+=i?t.substr(0,i.index)+i[1]+i[2]+n.b+i[3]+n.f:t+n.g}return e+this.strings[t]}getTemplateElement(){const t=document.createElement("template");return t.innerHTML=this.getHTML(),t}}class a extends r{getHTML(){return`<svg>${super.getHTML()}</svg>`}getTemplateElement(){const t=super.getTemplateElement(),e=t.content,s=e.firstChild;return e.removeChild(s),Object(i.c)(e,s.firstChild),t}}},function(t,e,s){"use strict";s.d(e,"a",(function(){return n})),s.d(e,"e",(function(){return d})),s.d(e,"c",(function(){return c})),s.d(e,"b",(function(){return l})),s.d(e,"d",(function(){return u}));const i=[{units:"w",delta:604800},{units:"d",delta:86400},{units:"h",delta:3600},{units:"m",delta:60},{units:"s",delta:1}],n=1048576,r=1024*n,a=1024*r,o=[{units:" PB",delta:1024*a},{units:" TB",delta:a},{units:" GB",delta:r},{units:" MB",delta:n},{units:" KB",delta:1024},{units:" B",delta:1}];function d(t){if(t<0&&(t=-t),0===t)return"  0s";let e="";for(let s=0;s<i.length;s++)if(i[s].delta<=t){let n=Math.floor(t/i[s].delta)+i[s].units;for(;n.length<4;)n=" "+n;e+=n,t%=i[s].delta}return e}function c(t){let e=(("number"==typeof t?t:Date.parse(t))-Date.now())/1e3;return e<0&&(e*=-1),h(e,i)}function l(t,e=1){return Number.isInteger(e)&&(t*=e),h(t,o)}function u(t){let e=t.toString(),s=e.substring(e.indexOf("("));return t.toLocaleString()+" "+s}function h(t,e){for(let s=0;s<e.length-1;s++){if(Math.round(t/e[s+1].delta)*e[s+1].delta/e[s].delta>=1)return Math.round(t/e[s].delta)+e[s].units}let s=e.length-1;return Math.round(t/e[s].delta)+e[s].units}},function(t,e,s){},function(t,e,s){"use strict";s.d(e,"a",(function(){return a})),s.d(e,"b",(function(){return o})),s.d(e,"c",(function(){return d})),s.d(e,"d",(function(){return c})),s.d(e,"e",(function(){return l})),s.d(e,"f",(function(){return u})),s.d(e,"g",(function(){return h})),s.d(e,"h",(function(){return p})),s.d(e,"i",(function(){return _})),s.d(e,"j",(function(){return f})),s.d(e,"k",(function(){return m})),s.d(e,"l",(function(){return g})),s.d(e,"m",(function(){return b})),s.d(e,"o",(function(){return v})),s.d(e,"n",(function(){return k})),s.d(e,"p",(function(){return y})),s.d(e,"q",(function(){return w}));var i=s(13),n=s(4),r=s(20);function a(t){return t&&t.properties&&t.properties.idempotent}function o(t,e){if(!t||!e)return;const s=t.split(":");return 2===s.length?`${e}/p/${s[0]}/+/${s[1]}`:void 0}function d(t){let e=0,s=0;return t.performance_stats&&(s=t.performance_stats.isolated_upload&&t.performance_stats.isolated_upload.duration||0,e=t.performance_stats.bot_overhead-s),[t.pending,e,t.duration,s].map((function(t){return t?Math.round(10*t)/10:0}))}function c(t,e){const s=t.filter((function(t){return t.key===e}));if(!s.length)return null;const i=s[0].value;return i.length?i[0]:null}function l(t){if(!t||!t._request||!t._request.tagMap)return!1;const e=t._request.tagMap;return e.allow_milo||e.luci_project}function u(t,e){if(!t||!t.state)return"";if(void 0!==e&&t.current_task_slice!==e)return"THIS SLICE DID NOT RUN. Select another slice above.";const s=t.state;return"COMPLETED"===s?t.failure?"COMPLETED (FAILURE)":y(t)?"COMPLETED (DEDUPED)":"COMPLETED (SUCCESS)":s}function h(t){return t.isolatedserver+"/browse?namespace="+t.namespace+"&hash="+t.isolated}function p(t){if(!t)return{};t.tagMap={},t.tags=t.tags||[];for(const e of t.tags){const s=e.split(":",1)[0],i=e.substring(s.length+1);t.tagMap[s]=i}return $.forEach(e=>{Object(n.h)(t,e)}),t}function _(t){if(!t)return{};$.forEach(e=>{Object(n.h)(t,e)}),t.try_number&&(t.try_number=+t.try_number);const e=new Date;!t.duration&&"RUNNING"===t.state&&t.started_ts?t.duration=(e-t.started_ts)/1e3:!t.duration&&"BOT_DIED"===t.state&&t.started_ts&&t.abandoned_ts&&(t.duration=(t.abandoned_ts-t.started_ts)/1e3),t.human_duration=Object(n.d)(t.duration),"RUNNING"===t.state?t.human_duration+="*":"BOT_DIED"===t.state&&(t.human_duration+=" -- died");const s=t.started_ts||t.abandoned_ts||new Date;return t.created_ts?s<=t.created_ts?(t.pending=0,t.human_pending="0s"):(t.pending=(s-t.created_ts)/1e3,t.human_pending=Object(n.l)(t.created_ts,s)):(t.pending=0,t.human_pending=""),t.current_task_slice=parseInt(t.current_task_slice)||0,t}function f(t){if(!t||!t._request||!t._request.tagMap)return;const e=t._request.tagMap,s=e.milo_host;let i=e.log_location;if(i&&s){if(i=i.replace("logdog://",""),-1!==i.indexOf("${SWARMING_TASK_ID}")){if(!t._result||!t._result.run_id)return;i=i.replace("${SWARMING_TASK_ID}",t._result.run_id)}return s.replace("%s",i)}const n=t.server_details.display_server_url_template;return n&&t._taskId?n.replace("%s",t._taskId):void 0}function m(t,e){if(!e.created_ts)return"";const s=1e3*t.expiration_secs;return i.d(new Date(e.created_ts.getTime()+s))}function g(t){if(!t||!t.state)return"";const e=t.state;return r.b.has(e)?"exception":"BOT_DIED"===e?"bot_died":r.d.has(e)?"pending_task":"COMPLETED"===e&&t.failure?"failed_task":""}function b(t){return t&&t.costs_usd&&t.costs_usd.length?t.costs_usd[0].toFixed(4):0}function v(t){if(!t.created_ts)return"";const e=1e3*t.expiration_secs;return i.d(new Date(t.created_ts.getTime()+e))}function k(t,e){return t&&e&&-1!==t._currentSliceIdx&&t._currentSliceIdx!==e.current_task_slice?"inactive":""}function y(t){return 0===t.try_number}function w(t){return t&&"PENDING"!==t.state&&"NO_RESOURCE"!==t.state&&"CANCELED"!==t.state&&"EXPIRED"!==t.state}const $=["abandoned_ts","completed_ts","created_ts","modified_ts","started_ts"]},function(t,e,s){"use strict";s.d(e,"a",(function(){return r}));var i=s(9),n=s(2);
/**
 * @license
 * Copyright (c) 2017 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
class r{constructor(t,e,s){this._parts=[],this.template=t,this.processor=e,this.options=s}update(t){let e=0;for(const s of this._parts)void 0!==s&&s.setValue(t[e]),e++;for(const t of this._parts)void 0!==t&&t.commit()}_clone(){const t=i.a?this.template.element.content.cloneNode(!0):document.importNode(this.template.element.content,!0),e=this.template.parts;let s=0,r=0;const a=t=>{const i=document.createTreeWalker(t,133,null,!1);let o=i.nextNode();for(;s<e.length&&null!==o;){const t=e[s];if(Object(n.d)(t))if(r===t.index){if("node"===t.type){const t=this.processor.handleTextExpression(this.options);t.insertAfterNode(o.previousSibling),this._parts.push(t)}else this._parts.push(...this.processor.handleAttributeExpressions(o,t.name,t.strings,this.options));s++}else r++,"TEMPLATE"===o.nodeName&&a(o.content),o=i.nextNode();else this._parts.push(void 0),s++}};return a(t),i.a&&(document.adoptNode(t),customElements.upgrade(t)),t}}},function(t,e,s){"use strict";s.d(e,"a",(function(){return n}));var i=s(0);
/**
 * @license
 * Copyright (c) 2018 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */const n=Object(i.b)(t=>e=>{if(void 0===t&&e instanceof i.a){if(t!==e.value){const t=e.committer.name;e.committer.element.removeAttribute(t)}}else e.setValue(t)})},function(t,e,s){"use strict";function i(t,e){if(!n[e]||"none"===t||!t)return t;let s=n[e][t];if("gpu"===e){const i=t.split("-")[0];s=n[e][i]}else if("os"===e){const i=t.split(".")[0];s=n[e][i]}return s?`${s} (${t})`:t}s.d(e,"a",(function(){return i})),s.d(e,"b",(function(){return a})),s.d(e,"c",(function(){return o}));const n={device:{"iPad4,1":"iPad Air","iPad5,1":"iPad mini 4","iPad6,3":"iPad Pro [9.7 in]","iPhone7,2":"iPhone 6","iPhone9,1":"iPhone 7"},device_type:{angler:"Nexus 6p",athene:"Moto G4",blueline:"Pixel 3",bullhead:"Nexus 5X",crosshatch:"Pixel 3 XL",darcy:"NVIDIA Shield [2017]",dragon:"Pixel C",flame:"Pixel 4",flo:"Nexus 7 [2013]",flounder:"Nexus 9",foster:"NVIDIA Shield [2015]",fugu:"Nexus Player",gce_x86:"Android on GCE",goyawifi:"Galaxy Tab 3",grouper:"Nexus 7 [2012]",hammerhead:"Nexus 5",herolte:"Galaxy S7 [Global]",heroqlteatt:"Galaxy S7 [AT&T]","iPad4,1":"iPad Air","iPad5,1":"iPad mini 4","iPad6,3":"iPad Pro [9.7 in]","iPhone7,2":"iPhone 6","iPhone9,1":"iPhone 7","iPhone10,1":"iPhone 8",j5xnlte:"Galaxy J5",m0:"Galaxy S3",mako:"Nexus 4",manta:"Nexus 10",marlin:"Pixel XL",sailfish:"Pixel",sargo:"Pixel 3a",shamu:"Nexus 6",sprout:"Android One",starlte:"Galaxy S9",taimen:"Pixel 2 XL","TECNO-KB8":"TECNO Spark 3 Pro",walleye:"Pixel 2",zerofltetmo:"Galaxy S6"},gpu:{1002:"AMD","1002:6613":"AMD Radeon R7 240","1002:6646":"AMD Radeon R9 M280X","1002:6779":"AMD Radeon HD 6450/7450/8450","1002:679e":"AMD Radeon HD 7800","1002:6821":"AMD Radeon HD 8870M","1002:683d":"AMD Radeon HD 7770/8760","1002:9830":"AMD Radeon HD 8400","1002:9874":"AMD Carrizo","1a03":"ASPEED","1a03:2000":"ASPEED Graphics Family","102b":"Matrox","102b:0522":"Matrox MGA G200e","102b:0532":"Matrox MGA G200eW","102b:0534":"Matrox G200eR2","10de":"NVIDIA","10de:08a4":"NVIDIA GeForce 320M","10de:08aa":"NVIDIA GeForce 320M","10de:0a65":"NVIDIA GeForce 210","10de:0fe9":"NVIDIA GeForce GT 750M Mac Edition","10de:0ffa":"NVIDIA Quadro K600","10de:104a":"NVIDIA GeForce GT 610","10de:11c0":"NVIDIA GeForce GTX 660","10de:1244":"NVIDIA GeForce GTX 550 Ti","10de:1401":"NVIDIA GeForce GTX 960","10de:1ba1":"NVIDIA GeForce GTX 1070","10de:1cb3":"NVIDIA Quadro P400","10de:2184":"NVIDIA GeForce GTX 1660",8086:"Intel","8086:0046":"Intel Ironlake HD Graphics","8086:0102":"Intel Sandy Bridge HD Graphics 2000","8086:0116":"Intel Sandy Bridge HD Graphics 3000","8086:0166":"Intel Ivy Bridge HD Graphics 4000","8086:0412":"Intel Haswell HD Graphics 4600","8086:041a":"Intel Haswell HD Graphics","8086:0a16":"Intel Haswell HD Graphics 4400","8086:0a26":"Intel Haswell HD Graphics 5000","8086:0a2e":"Intel Haswell Iris Graphics 5100","8086:0d26":"Intel Haswell Iris Pro Graphics 5200","8086:0f31":"Intel Bay Trail HD Graphics","8086:1616":"Intel Broadwell HD Graphics 5500","8086:161e":"Intel Broadwell HD Graphics 5300","8086:1626":"Intel Broadwell HD Graphics 6000","8086:162b":"Intel Broadwell Iris Graphics 6100","8086:1912":"Intel Skylake HD Graphics 530","8086:191e":"Intel Skylake HD Graphics 515","8086:1926":"Intel Skylake Iris 540/550","8086:193b":"Intel Skylake Iris Pro 580","8086:22b1":"Intel Braswell HD Graphics","8086:3e92":"Intel Coffee Lake UHD Graphics 630","8086:3ea5":"Intel Coffee Lake Iris Plus Graphics 655","8086:5912":"Intel Kaby Lake HD Graphics 630","8086:591e":"Intel Kaby Lake HD Graphics 615","8086:5926":"Intel Kaby Lake Iris Plus Graphics 640"},os:{"Windows-10-10240":"Windows 10 version 1507","Windows-10-10586":"Windows 10 version 1511","Windows-10-14393":"Windows 10 version 1607","Windows-10-15063":"Windows 10 version 1703","Windows-10-16299":"Windows 10 version 1709","Windows-10-17134":"Windows 10 version 1803","Windows-10-17763":"Windows 10 version 1809","Windows-10-18362":"Windows 10 version 1903","Windows-10-18363":"Windows 10 version 1909","Windows-Server-14393":"Windows Server 2016","Windows-Server-17134":"Windows Server version 1803","Windows-Server-17763":"Windows Server 2019 or version 1809","Windows-Server-18362":"Windows Server version 1903","Windows-Server-18363":"Windows Server version 1909"}},r=/.+\((.+)\)/;function a(t){return t?t.map(t=>{const e=t.split(":")[0];if(n[e]){const s=t.match(r);return s?e+":"+s[1]:t}return t}):[]}function o(t){const e=t.indexOf(":");if(e<0)return t;const s=t.substring(0,e),n=t.substring(e+1),r=s.split("-tag")[0];return`${s}:${i(n,r)}`}},,function(t,e,s){"use strict";s.d(e,"d",(function(){return i})),s.d(e,"b",(function(){return n})),s.d(e,"a",(function(){return r})),s.d(e,"c",(function(){return a}));const i=new Set(["PENDING","RUNNING"]),n=new Set(["TIMED_OUT","EXPIRED","NO_RESOURCE","CANCELED","KILLED"]),r=[{label:"Total",value:"..."},{label:"Success",value:"...",filter:"COMPLETED_SUCCESS"},{label:"Failure",value:"...",filter:"COMPLETED_FAILURE"},{label:"Pending",value:"...",filter:"PENDING"},{label:"Running",value:"...",filter:"RUNNING"},{label:"Timed Out",value:"...",filter:"TIMED_OUT"},{label:"Bot Died",value:"...",filter:"BOT_DIED"},{label:"Deduplicated",value:"...",filter:"DEDUPED"},{label:"Expired",value:"...",filter:"EXPIRED"},{label:"No Resource",value:"...",filter:"NO_RESOURCE"},{label:"Canceled",value:"...",filter:"CANCELED"},{label:"Killed",value:"...",filter:"KILLED"}],a=["ALL","COMPLETED","COMPLETED_SUCCESS","COMPLETED_FAILURE","RUNNING","PENDING","PENDING_RUNNING","BOT_DIED","DEDUPED","TIMED_OUT","EXPIRED","NO_RESOURCE","CANCELED","KILLED"]},function(t,e,s){"use strict";s.d(e,"a",(function(){return a}));var i=s(8),n=s(0),r=s(1);class a extends HTMLElement{constructor(t){super(),this._template=t,this._app=null,this._auth_header="",this._profile=null,this._notAuthorized=!1}connectedCallback(){Object(r.a)(this,"client_id"),Object(r.a)(this,"testing_offline"),this._authHeaderEvent=t=>{this._auth_header=t.detail.auth_header},this.addEventListener("log-in",this._authHeaderEvent)}disconnectedCallback(){this.removeEventListener("log-in",this._authHeaderEvent)}static get observedAttributes(){return["client_id","testing_offline"]}get app(){return this._app}get auth_header(){return this._auth_header}get loggedInAndAuthorized(){return!!this._auth_header&&!this._notAuthorized}get permissions(){return this._app&&this._app.permissions||{}}get profile(){return this._app&&this._app.profile||{}}get server_details(){return this._app&&this._app.server_details||{}}get client_id(){return this.getAttribute("client_id")}set client_id(t){return this.setAttribute("client_id",t)}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(t){t?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}fetchError(t,e,s){403!==t.status||s?"AbortError"!==t.name&&(console.error(t),Object(i.a)(`Unexpected error loading ${e}: ${t.message}`,5e3)):(this._message="User unauthorized - try logging in with a different account",this._notAuthorized=!0,this.render()),this._app.finishedTask()}render(){Object(n.d)(this._template(this),this,{eventContext:this}),this._app||(this._app=this.firstElementChild,Object(n.d)(this._template(this),this,{eventContext:this}))}attributeChangedCallback(t,e,s){this.render()}}},,function(t,e,s){"use strict";s.d(e,"a",(function(){return o}));var i=s(7);const n=t=>JSON.parse(JSON.stringify(t));function r(t,e){let s={};return Object.keys(t).forEach((function(n){(function(t,e){if(typeof t!=typeof e)return!1;let s=typeof t;return"string"===s||"boolean"===s||"number"===s?t===e:"object"===s?Array.isArray(s)?JSON.stringify(t)===JSON.stringify(e):Object(i.a)(t)===Object(i.a)(e):void 0})(t[n],e[n])||(s[n]=t[n])})),s}var a=s(6);function o(t,e){let s=n(t()),o=!1;const d=()=>{o=!0;let t=i.c(window.location.search.slice(1),s);e(function(t,e){let s={};return Object.keys(e).forEach((function(i){t.hasOwnProperty(i)?s[i]=n(t[i]):s[i]=n(e[i])})),s}(t,s))};return a.c.then(d),window.addEventListener("popstate",d),()=>{if(!o)return;let e=i.a(r(t(),s));history.pushState(null,"",window.location.origin+window.location.pathname+"?"+e)}}},function(t,e,s){"use strict";s(32)},function(t,e,s){},function(t,e,s){},function(t,e,s){},function(t,e,s){},function(t,e,s){"use strict";var i=s(1);window.customElements.define("toast-sk",class extends HTMLElement{constructor(){super(),this._timer=null}connectedCallback(){this.hasAttribute("duration")||(this.duration=5e3),Object(i.a)(this,"duration")}get duration(){return+this.getAttribute("duration")}set duration(t){this.setAttribute("duration",t)}show(){this.setAttribute("shown",""),this.duration>0&&!this._timer&&(this._timer=window.setTimeout(()=>{this._timer=null,this.hide()},this.duration))}hide(){this.removeAttribute("shown"),this._timer&&(window.clearTimeout(this._timer),this._timer=null)}});s(25);window.customElements.define("error-toast-sk",class extends HTMLElement{connectedCallback(){this.innerHTML="<toast-sk></toast-sk>",this._toast=this.firstElementChild,document.addEventListener("error-sk",this)}disconnectedCallback(){document.removeEventListener("error-sk",this)}handleEvent(t){t.detail.duration&&(this._toast.duration=t.detail.duration),this._toast.textContent=t.detail.message,this._toast.show()}});s(14);const n=document.createElement("template");n.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M20 8h-2.81c-.45-.78-1.07-1.45-1.82-1.96L17 4.41 15.59 3l-2.17 2.17C12.96 5.06 12.49 5 12 5c-.49 0-.96.06-1.41.17L8.41 3 7 4.41l1.62 1.63C7.88 6.55 7.26 7.22 6.81 8H4v2h2.09c-.05.33-.09.66-.09 1v1H4v2h2v1c0 .34.04.67.09 1H4v2h2.81c1.04 1.79 2.97 3 5.19 3s4.15-1.21 5.19-3H20v-2h-2.09c.05-.33.09-.66.09-1v-1h2v-2h-2v-1c0-.34-.04-.67-.09-1H20V8zm-6 8h-4v-2h4v2zm0-4h-4v-2h4v2z"/></svg>',window.customElements.define("bug-report-icon-sk",class extends HTMLElement{connectedCallback(){let t=n.content.cloneNode(!0);this.appendChild(t)}});const r=document.createElement("template");r.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M3 18h18v-2H3v2zm0-5h18v-2H3v2zm0-7v2h18V6H3z"/></svg>',window.customElements.define("menu-icon-sk",class extends HTMLElement{connectedCallback(){let t=r.content.cloneNode(!0);this.appendChild(t)}}),window.customElements.define("spinner-sk",class extends HTMLElement{connectedCallback(){Object(i.a)(this,"active")}get active(){return this.hasAttribute("active")}set active(t){t?this.setAttribute("active",""):this.removeAttribute("active")}});s(26),s(27);var a=s(0),o=s(8);const d=new Promise((t,e)=>{const s=()=>{void 0!==window.gapi?t():setTimeout(s,10)};setTimeout(s,10)});window.customElements.define("oauth-login",class extends HTMLElement{connectedCallback(){Object(i.a)(this,"client_id"),Object(i.a)(this,"testing_offline"),this._auth_header="",this.testing_offline?this._profile={email:"missing@chromium.org",imageURL:"http://storage.googleapis.com/gd-wagtail-prod-assets/original_images/logo_google_fonts_color_2x_web_64dp.png"}:(this._profile=null,d.then(()=>{gapi.load("auth2",()=>{gapi.auth2.init({client_id:this.client_id}).then(()=>{this._maybeFireLoginEvent(),this.render()},t=>{console.error(t),Object(o.a)(`Error initializing oauth: ${JSON.stringify(t)}`,1e4)})})})),this.render()}static get observedAttributes(){return["client_id","testing_offline"]}get auth_header(){return this._auth_header}get client_id(){return this.getAttribute("client_id")}set client_id(t){return this.setAttribute("client_id",t)}get profile(){return this._profile}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(t){t?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}_maybeFireLoginEvent(){const t=gapi.auth2.getAuthInstance().currentUser.get();if(t.isSignedIn()){const e=t.getBasicProfile();this._profile={email:e.getEmail(),imageURL:e.getImageUrl()};const s=t.getAuthResponse(!0),i=`${s.token_type} ${s.access_token}`;return this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:i,profile:this._profile},bubbles:!0})),this._auth_header=i,!0}return this._profile=null,this._auth_header="",!1}_logIn(){if(this.testing_offline)this._auth_header="Bearer 12345678910-boomshakalaka",this.dispatchEvent(new CustomEvent("log-in",{detail:{auth_header:this._auth_header,profile:this._profile},bubbles:!0})),this.render();else{const t=gapi.auth2.getAuthInstance();t&&t.signIn({scope:"email",prompt:"select_account"}).then(()=>{this._maybeFireLoginEvent()||console.warn("login was not successful; maybe user canceled"),this.render()})}}_logOut(){if(this.testing_offline)this._auth_header="",this.render(),window.location.reload();else{const t=gapi.auth2.getAuthInstance();t&&t.signOut().then(()=>{this._auth_header="",this._profile=null,window.location.reload()})}}render(){var t;Object(a.d)((t=this).auth_header?a.c`
<div>
  <img class=center id=avatar src="${t._profile.imageURL}" width=30 height=30>
  <span class=center>${t._profile.email}</span>
  <span class=center>|</span>
  <a class=center @click=${t._logOut} href="#">Sign out</a>
</div>`:a.c`
<div>
  <a @click=${t._logIn} href="#">Sign in</a>
</div>`,this,{eventContext:this})}attributeChangedCallback(t,e,s){this.render()}});var c=s(10),l=s(7),u=s(17);const h=document.createElement("template");h.innerHTML="\n<button class=toggle-button>\n  <menu-icon-sk>\n  </menu-icon-sk>\n</button>\n";const p=document.createElement("template");p.innerHTML="\n<div class=spinner-spacer>\n  <spinner-sk></spinner-sk>\n</div>\n";const _=document.createElement("template");_.innerHTML='\n<a target=_blank rel=noopener\n   href="https://bugs.chromium.org/p/chromium/issues/entry?components=Infra%3EPlatform%3ESwarming%3EWebUI&owner=kjlubick@chromium.org&status=Assigned">\n  <bug-report-icon-sk class=fab></bug-report-icon-sk>\n</a>',window.customElements.define("swarming-app",class extends HTMLElement{constructor(){super(),this._busyTaskCount=0,this._spinner=null,this._dynamicEle=null,this._auth_header="",this._profile={},this._server_details={server_version:"You must log in to see more details",bot_version:""},this._permissions={}}connectedCallback(){Object(i.a)(this,"client_id"),Object(i.a)(this,"testing_offline"),this._addHTML(),this.addEventListener("log-in",t=>{this._auth_header=t.detail.auth_header,this._profile=t.detail.profile,this._fetch()}),this.render()}static get observedAttributes(){return["client_id","testing_offline"]}get busy(){return!!this._busyTaskCount}get permissions(){return this._permissions}get profile(){return this._profile}get server_details(){return this._server_details}get client_id(){return this.getAttribute("client_id")}set client_id(t){return this.setAttribute("client_id",t)}get testing_offline(){return this.hasAttribute("testing_offline")}set testing_offline(t){t?this.setAttribute("testing_offline",!0):this.removeAttribute("testing_offline")}addBusyTasks(t){this._busyTaskCount+=t,this._spinner&&this._busyTaskCount>0&&(this._spinner.active=!0)}finishedTask(){this._busyTaskCount--,this._busyTaskCount<=0&&(this._busyTaskCount=0,this._spinner&&(this._spinner.active=!1),this.dispatchEvent(new CustomEvent("busy-end",{bubbles:!0})))}_addHTML(){const t=this.querySelector("header"),e=t&&t.querySelector("aside"),s=this.querySelector("footer");if(!(t&&e&&e.classList.contains("hideable")))return;let i=h.content.cloneNode(!0);t.insertBefore(i,t.firstElementChild),i=t.firstElementChild,i.addEventListener("click",t=>this._toggleMenu(t,e));const n=p.content.cloneNode(!0);t.insertBefore(n,e),this._spinner=t.querySelector("spinner-sk");const r=document.createElement("span");r.classList.add("grow"),t.appendChild(r),this._dynamicEle=document.createElement("div"),this._dynamicEle.classList.add("right"),t.appendChild(this._dynamicEle);const a=document.createElement("error-toast-sk");s.append(a);const o=_.content.cloneNode(!0);s.append(o)}_toggleMenu(t,e){e.classList.toggle("shown")}_fetch(){if(!this._auth_header)return;this._server_details={server_version:"<loading>",bot_version:"<loading>"};const t={headers:{authorization:this._auth_header}};this.addBusyTasks(1),fetch("/_ah/api/swarming/v1/server/details",t).then(c.a).then(t=>{this._server_details=t,this.render(),this.dispatchEvent(new CustomEvent("server-details-loaded",{bubbles:!0})),this.finishedTask()}).catch(t=>{403===t.status?(this._server_details={server_version:"User unauthorized - try logging in with a different account",bot_version:""},this.render()):(console.error(t),Object(o.a)(`Unexpected error loading details: ${t.message}`,5e3)),this.finishedTask()}),this._fetchPermissions(t)}_fetchPermissions(t,e){this.addBusyTasks(1);let s="/_ah/api/swarming/v1/server/permissions";return e&&(s+=`?${l.a(e)}`),fetch(s,t).then(c.a).then(t=>{this._permissions=t,this.render(),this.dispatchEvent(new CustomEvent("permissions-loaded",{bubbles:!0})),this.finishedTask()}).catch(t=>{403!==t.status&&(console.error(t),Object(o.a)(`Unexpected error loading permissions: ${t.message}`,5e3)),this.finishedTask()})}render(){var t;this._dynamicEle&&Object(a.d)((t=this,a.c`
<div class=server-version>
  Server:
  <a href=${Object(u.a)(function(t){if(!t||!t.server_version)return;const e=t.server_version.split("-");return 2===e.length?`https://chromium.googlesource.com/infra/luci/luci-py/+/${e[1]}`:void 0}(t._server_details))}>
    ${t._server_details.server_version}
  </a>
</div>
<oauth-login client_id=${t.client_id}
             ?testing_offline=${t.testing_offline}>
</oauth-login>`),this._dynamicEle)}attributeChangedCallback(t,e,s){this.render()}});s(28)},function(t,e,s){"use strict";var i=s(1);class n extends HTMLElement{get _role(){return"checkbox"}static get observedAttributes(){return["checked","disabled","name","label"]}connectedCallback(){this.innerHTML=`<label><input type=${this._role}></input><span class=box></span><span class=label></span></label>`,this._label=this.querySelector(".label"),this._input=this.querySelector("input"),Object(i.a)(this,"checked"),Object(i.a)(this,"disabled"),Object(i.a)(this,"name"),Object(i.a)(this,"label"),this._input.checked=this.checked,this._input.disabled=this.disabled,this._input.setAttribute("name",this.getAttribute("name")),this._label.textContent=this.getAttribute("label")}get checked(){return this.hasAttribute("checked")}set checked(t){let e=!!t;this._input.checked=e,t?this.setAttribute("checked",""):this.removeAttribute("checked")}get disabled(){return this.hasAttribute("disabled")}set disabled(t){let e=!!t;this._input.disabled=e,e?this.setAttribute("disabled",""):this.removeAttribute("disabled")}get name(){return this._input.getAttribute("name")}set name(t){this.setAttribute("name",t),this._input.setAttribute("name",t)}get label(){return this._input.getAttribute("label")}set label(t){this.setAttribute("label",t),this._input.setAttribute("label",t)}attributeChangedCallback(t,e,s){if(!this._input)return;let i=null!=s;switch(t){case"checked":this._input.checked=i;break;case"disabled":this._input.disabled=i;break;case"name":this._input.name=s;break;case"label":this._label.textContent=s}}}window.customElements.define("checkbox-sk",n);s(31)},function(t,e,s){},function(t,e,s){},function(t,e,s){},function(t,e,s){"use strict";var i=s(6);const n=document.createElement("template");n.innerHTML="<div class=backdrop></div>",window.customElements.define("dialog-pop-over",class extends HTMLElement{constructor(){super(),this._backdrop=null,this._content=null}connectedCallback(){const t=n.content.cloneNode(!0);if(this.appendChild(t),this._backdrop=Object(i.b)(".backdrop",this),this._content=Object(i.b)(".content",this),!this._content)throw"You must have an element with class content to show."}hide(){this._backdrop.classList.remove("opened"),this._content.classList.remove("opened")}show(){const t=window.innerWidth,e=window.innerHeight,s=Math.min(this._content.offsetWidth,t-50),i=Math.min(this._content.offsetHeight,e-50);this._content.style.width=s,this._content.style.left=(t-s)/2,this._content.style.top=(e-i)/2,this._backdrop.classList.add("opened"),this._content.classList.add("opened")}});s(33)},,,,,function(t,e,s){"use strict";s(14);const i=document.createElement("template");i.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M13 7h-2v4H7v2h4v4h2v-4h4v-2h-4V7zm-1-5C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>',window.customElements.define("add-circle-outline-icon-sk",class extends HTMLElement{connectedCallback(){let t=i.content.cloneNode(!0);this.appendChild(t)}})},function(t,e,s){"use strict";s(14);const i=document.createElement("template");i.innerHTML='<svg class="icon-sk-svg" xmlns="http://www.w3.org/2000/svg" width=24 height=24 viewBox="0 0 24 24"><path d="M7 11v2h10v-2H7zm5-9C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>',window.customElements.define("remove-circle-outline-icon-sk",class extends HTMLElement{connectedCallback(){let t=i.content.cloneNode(!0);this.appendChild(t)}})},,,,,,,,,,,,,function(t,e,s){},,,,function(t,e,s){"use strict";s.r(e);var i=s(6),n=s(8),r=s(0);
/**
 * @license
 * Copyright (c) 2018 The Polymer Project Authors. All rights reserved.
 * This code may only be used under the BSD style license found at
 * http://polymer.github.io/LICENSE.txt
 * The complete set of authors may be found at
 * http://polymer.github.io/AUTHORS.txt
 * The complete set of contributors may be found at
 * http://polymer.github.io/CONTRIBUTORS.txt
 * Code distributed by Google as part of the polymer project is also
 * subject to an additional IP rights grant found at
 * http://polymer.github.io/PATENTS.txt
 */
const a=new WeakMap;Object(r.b)((t,e)=>s=>{const i=a.get(s);if(Array.isArray(t)){if(Array.isArray(i)&&i.length===t.length&&t.every((t,e)=>t===i[e]))return}else if(i===t&&(void 0!==t||a.has(s)))return;s.setValue(e()),a.set(s,Array.isArray(t)?Array.from(t):t)});var o=s(17),d=s(10),c=s(23);s(30),s(39),s(40),s(24),s(34);const l=Symbol("loadScript"),u=Symbol("instance");let h;class p{get[u](){return h}set[u](t){h=t}constructor(){if(this[u])return this[u];this[u]=this}reset(){h=null}[l](){return this.scriptPromise||(this.scriptPromise=new Promise(t=>{const e=document.getElementsByTagName("body")[0],s=document.createElement("script");s.type="text/javascript",s.onload=function(){_.api=window.google,_.api.charts.load("current",{packages:["corechart","table"]}),_.api.charts.setOnLoadCallback(()=>{t()})},s.src="https://www.gstatic.com/charts/loader.js",e.appendChild(s)})),this.scriptPromise}load(t,e){return this[l]().then(()=>{if(e){let s={};s=e instanceof Object?e:Array.isArray(e)?{packages:e}:{packages:[e]},this.api.charts.load("current",s),this.api.charts.setOnLoadCallback(t)}else{if("function"!=typeof t)throw"callback must be a function";t()}})}}const _=new p;var f=s(4);const m=new Promise((t,e)=>{try{_.load(t)}catch(t){e(t)}});function g(t){return"string"==typeof t?JSON.parse(t):t}window.customElements.define("stacked-time-chart",class extends HTMLElement{constructor(){super(),this._loaded=!1,this._error=""}connectedCallback(){Object(f.e)(this,"colors"),Object(f.e)(this,"labels"),Object(f.e)(this,"values"),this._colors=g(this._colors),this._labels=g(this._labels),this._values=g(this._values),m.then(()=>{this._loaded=!0,this.render()}).catch(t=>{console.error(t),this._error="Could not load Google Charts JS from Internet",this.render()}),this.render()}get colors(){return this._colors}set colors(t){this._colors=t,this.render()}get labels(){return this._labels}set labels(t){this._labels=t,this.render()}get values(){return this._values}set values(t){this._values=t,this.render()}drawChart(){const t=_.api.visualization.arrayToDataTable([["Type"].concat(this._labels),[""].concat(this._values)]);let e=0;for(const t of this._values)e+=+t;const s=[{v:0,f:""}];let i=0;if(e<120){for(let t=10;t<e;t+=10)s.push({v:t,f:t+"s"});i=5}else if(e<1500){for(let t=60;t<e;t+=60)s.push({v:t,f:t/60+"m"});i=e<300?5:e<900?1:0}else if(e<1e6){for(let t=600;t<e;t+=600)s.push({v:t,f:t/60+"m"});i=e<6e3?10:e<12e3?5:1}const n={width:400,height:250,isStacked:!0,chartArea:{width:"100%",height:"65%"},legend:{position:"top",maxLines:1,alignment:"center",textStyle:{fontSize:12}},colors:this._colors,hAxis:{title:"Time",ticks:s,minorGridlines:{count:i}}};new _.api.visualization.BarChart(this.firstElementChild).draw(t,n)}render(){var t;Object(r.d)((t=this,r.c`<div id=chart>${t._error}</div>`),this,{eventContext:this}),this._loaded&&this.drawChart()}});s(29);var b=s(13),v=s(7),k=s(18),y=s(15),w=s(21);const $='resource.type="gae_app"\n'+['protoPayload.resource>="/internal/"','protoPayload.resource>="/swarming/api/v1/bot/"','protoPayload.method!="GET"'].join(" OR ")+"\n",E=(t,e,s)=>{let i="https://console.cloud.google.com/logs/viewer";if(i+=`?project=${t._project_id}`,i+="&resource=gae_app",e.created_ts){const t=new Date(e.created_ts.getTime()-6e4),n=s.completed_ts||s.abandoned_ts,r=n?new Date(n.getTime()+6e4):new Date;i+="&interval=CUSTOM",i+=`&dateRangeStart=${t.toISOString()}`,i+=`&dateRangeEnd=${r.toISOString()}`}return i},I=(t,e)=>{if(!t.task_id)return r.c`<tr><td>&lt;loading&gt;</td><td></td><td></td></tr>`;let s=t.task_id.substring(0,t.task_id.length-1);return s+=e+1,r.c`
<tr>
  <td>
    <a href=${Object(o.a)(Object(f.j)(s,!0))} target=_blank>
      ${s}
    </a>
  </td>
  <td>
    <a href=${Object(o.a)(Object(f.b)(t.bot_id))} target=_blank>
      ${t.bot_id}
    </a>
  </td>
  <td class=${Object(y.l)(t)}>${Object(y.f)(t)}</td>
</tr>
`},O=(t,e)=>r.c`
  <div class=tab ?selected=${t._currentSliceIdx===e}
                 @click=${()=>t._setSlice(e)}>Task Slice ${e+1}</div>
`,T=(t,e,s)=>r.c`
<tr>
  <td>State</td>
  <td class=${Object(y.l)(s)}>${Object(y.f)(s,t._currentSliceIdx)}</td>
</tr>
${x(s,t._capacityCounts[t._currentSliceIdx],t._pendingCounts[t._currentSliceIdx],t._runningCounts[t._currentSliceIdx],t._currentSlice.properties||{})}
<tr ?hidden=${!s.deduped_from} class=highlighted>
  <td><b>Deduped From</b></td>
  <td>
    <a href=${Object(f.j)(s.deduped_from)} target=_blank>
      ${s.deduped_from}
    </a>
  </td>
</tr>
<tr ?hidden=${!s.deduped_from}>
  <td>Deduped On</td>
  <td title=${e.created_ts}>
    ${e.human_created_ts}
  </td>
</tr>
`,x=(t,e,s,i,n)=>r.c`
<tr ?hidden=${!e}>
  <td class=${"PENDING"===t.state?"bold":""}>
    ${"PENDING"===t.state?"Why Pending?":"Fleet Capacity"}
  </td>
  <td>
    ${C(e,"count")}
    <a href=${Object(f.a)(n.dimensions)}>bots</a>
    could possibly run this task
    (${C(e,"busy")} busy,
    ${C(e,"dead")} dead,
    ${C(e,"quarantined")} quarantined,
    ${C(e,"maintenance")} maintenance)
  </td>
</tr>
<tr ?hidden=${!s||!i}>
  <td>Similar Load</td>
  <td>
      ${C(s)}
      <a href=${Object(f.i)(n.dimensions,[],"state:PENDING")}>
        similar pending tasks</a>,
      ${C(i)}
      <a href=${Object(f.i)(n.dimensions,[],"state:RUNNING")}>
        similar running tasks</a>
  </td>
</tr>
`,C=(t,e)=>!t||e&&void 0===t[e]?r.c`<span class=italic>&lt;counting&gt</span>`:e?t[e]:t,D=(t,e,s)=>r.c`
<tr>
  <td>Priority</td>
  <td>${t.priority}</td>
</tr>
<tr>
  <td>Wait for Capacity</td>
  <td>${!!s.wait_for_capacity}</td>
</tr>
<tr>
  <td>Slice Scheduling Deadline</td>
  <td>${Object(y.k)(s,t)}</td>
</tr>
<tr>
  <td>User</td>
  <td>${t.user||"--"}</td>
</tr>
<tr>
  <td>Authenticated</td>
  <td>${t.authenticated}</td>
</tr>
<tr ?hidden=${!t.service_account}>
  <td>Service Account</td>
  <td>${t.service_account}</td>
</tr>
<tr ?hidden=${!t.realm}>
  <td>Realm</td>
  <td>${t.realm}</td>
</tr>
<tr ?hidden=${!s.properties.secret_bytes}>
  <td>Has Secret Bytes</td>
  <td title="The secret bytes are present on the machine, but not in the UI/API">true</td>
</tr>
<tr ?hidden=${!t.parent_task_id}>
  <td>Parent Task</td>
  <td>
    <a href=${Object(f.j)(t.parent_task_id)}>
      ${t.parent_task_id}
    </a>
  </td>
</tr>
`,S=t=>r.c`
<tr>
  <td rowspan=${t.length+1}>
    Dimensions <br/>
    <a  title="The list of bots that matches the list of dimensions"
        href=${Object(f.a)(t)}>Bots</a>
    <a  title="The list of tasks that matches the list of dimensions"
        href=${Object(f.i)(t)}>Tasks</a>
  </td>
</tr>
${t.map(N)}
`,N=t=>r.c`
<tr>
  <td class=break-all><b class=dim_key>${t.key}:</b>${Object(k.a)(t.value,t.key)}</td>
</tr>
`,A=(t,e)=>e.isolated?r.c`
<tr>
  <td>${t}</td>
  <td>
    <a href=${Object(y.g)(e)}>
      ${e.isolated}
    </a>
  </td>
</tr>`:"",j=(t,e,s)=>t&&t.length?r.c`
<tr>
  <td rowspan=${t.length+1}>${e}</td>
</tr>
${t.map(P(s))}`:r.c`
<tr>
  <td>${e}</td>
  <td>--</td>
</tr>`,P=t=>e=>r.c`
<tr>
  <td class=break-all>${t(e)}</td>
</tr>
`,L=t=>t&&t.source_revision?r.c`
<tr>
  <td>Associated Commit</td>
  <td>
    <a href=${t.source_repo.replace("%s",t.source_revision)}>
      ${t.source_revision.substring(0,12)}
    </a>
  </td>
</tr>
`:"",M=(t,e,s)=>r.c`
<tr>
  <td>Extra Args</td>
  <td class="code break-all">${(t.extra_args||[]).join(" ")||"--"}</td>
</tr>
<tr>
  <td>Command</td>
  <td class="code break-all">${(t.command||[]).join(" ")||"--"}</td>
</tr>
<tr>
  <td>Relative Cwd</td>
  <td class="code break-all">${t.relative_cwd||"--"}</td>
</tr>
${j(e,"Environment Vars",t=>t.key+"="+t.value)}
${j(s,"Environment Prefixes",t=>t.key+"="+t.value.join(":"))}
<tr>
  <td>Idempotent</td>
  <td>${!!t.idempotent}</td>
</tr>
`,H=(t,e)=>{if(!t)return r.c`
<tr>
  <td>Uses CIPD</td>
  <td>false</td>
</tr>`;const s=t.packages||[],i=e.cipd_pins&&e.cipd_pins.packages||[];for(let t=0;t<s.length;t++){const e=s[t];e.requested=`${e.package_name}:${e.version}`,i[t]&&(e.actual=`${i[t].package_name}:${i[t].version}`)}let n="(available when task is run)";e.cipd_pins&&e.cipd_pins.client_package&&(n=e.cipd_pins.client_package.package_name);let a=s.length;return i.length?a*=3:a*=2,a+=1,r.c`
<tr>
  <td>CIPD server</td>
  <td>
    <a href=${t.server}>${t.server}</a>
  </td>
</tr>
<tr>
  <td>CIPD version</td>
  <td class=break-all>${t.client_package&&t.client_package.version}</td>
</tr>
<tr>
  <td>CIPD package name</td>
  <td>${n}</td>
</tr>
<tr>
  <td rowspan=${a}>CIPD packages</td>
</tr>
${s.map(e=>G(e,t,!!i.length))}
`},G=(t,e,s)=>r.c`
<tr>
  <td>${t.path}/</td>
</tr>
<tr>
  <td class=break-all>
    <span class=cipd-header>Requested: </span>${t.requested}
  </td>
</tr>
<tr ?hidden=${!s}>
  <td class=break-all>
    <span class=cipd-header>Actual: </span>
    <a href=${Object(y.b)(t.actual,e.server)}
       target=_blank rel=noopener>
      ${t.actual}
    </a>
  </td>
</tr>
`,R=(t,e,s)=>{if(!t._taskId||t._notFound)return"";let i=null,n=null;if(s&&s.bot_dimensions)for(const t of s.bot_dimensions)"gcp"==t.key&&(i=t.value[0]),"os"==t.key&&(n=t.value[0]);const a=i&&"Linux"==n;return r.c`
<div class=title>Logs Information</div>
<div class="horizontal layout wrap">
  <table class="task-info left">
    <tbody>
      <tr>
        <td>Task related server Logs</td>
        <td>
          <a href=${((t,e,s)=>{let i=E(t,e,s),n=$;return n+=`${t._taskId.slice(0,-1)}`,i+=`&advancedFilter=${n}`,encodeURI(i)})(t,e,s)} target="_blank">
            View on Cloud Console
          </a>
        </td>
      </tr>
      <tr>
        <td>Bot related server Logs</td>
        <td>
          <a href=${((t,e,s)=>{let i=E(t,e,s),n=$;return n+=`${s.bot_id}`,i+=`&advancedFilter=${n}`,encodeURI(i)})(t,e,s)} target="_blank"
             ?hidden=${!s.bot_id}>
            View on Cloud Console
          </a>
          <p ?hidden=${s.bot_id}>--</p>
        </td>
      </tr>
      <tr>
        <td>Bot Logs</td>
        <td>
          <a href=${((t,e,s,i)=>{let n="https://console.cloud.google.com/logs/viewer";if(n+=`?project=${i}`,s.started_ts){const t=new Date(s.started_ts.getTime()-6e4),e=s.completed_ts||s.abandoned_ts,i=e?new Date(e.getTime()+6e4):new Date;n+="&interval=CUSTOM",n+=`&dateRangeStart=${t.toISOString()}`,n+=`&dateRangeEnd=${i.toISOString()}`}let r=`labels."compute.googleapis.com/resource_name"="${s.bot_id}"\n`;return r+=[`logName:"projects/${i}/logs/swarming"`,`logName:"projects/${i}/logs/chromebuild"`].join(" OR "),n+=`&advancedFilter=${r}`,encodeURI(n)})(0,0,s,i)} target="_blank" ?hidden=${!a}>
            View on Cloud Console
          </a>
          <p ?hidden=${a}>--</p>
        </td>
      </tr>
    </tbody>
  </table>
</div>
`},B=(t,e)=>r.c`
<tr>
  <td class=${t.highlight?"highlight":""}>
    <b class=dim_key>${t.key}:</b>${t.values.map(U)}
  </td>
</tr>
`,U=t=>r.c`<span class="break-all dim ${t.bold?"bold":""}">${t.name}</span>`,V=t=>r.c`<div>${t}</div>`,F=t=>r.c`
<tr>
  <td><input value=${t.key}></input></td>
  <td><input value=${t.value}></input></td>
</tr>
`,q=t=>r.c`
<swarming-app id=swapp
              client_id=${t.client_id}
              ?testing_offline=${t.testing_offline}>
  <header>
    <div class=title>Swarming Task Page</div>
      <aside class=hideable>
        <a href=/>Home</a>
        <a href=/botlist>Bot List</a>
        <a href=/tasklist>Task List</a>
        <a href=/bot>Bot Page</a>
      </aside>
  </header>
  <main class="horizontal layout wrap">
    <h2 class=message ?hidden=${t.loggedInAndAuthorized}>${t._message}</h2>

    <div class="left grow" ?hidden=${!t.loggedInAndAuthorized}>
    ${(t=>!t._taskId||t._notFound?r.c`
<div class=id_buttons>
  <input id=id_input placeholder="Task ID" @change=${t._updateID}></input>
  <span class=message>Enter a Task ID to get started.</span>
</div>`:r.c`
<div class=id_buttons>
  <input id=id_input placeholder="Task ID" @change=${t._updateID}></input>
  <button title="Retry the task"
          @click=${t._promptRetry} class=retry
          ?hidden=${!Object(y.a)(t._request)}>retry</button>
  <button title="Re-queue the task, but don't run it automatically"
          @click=${t._promptDebug} class=debug>debug</button>
  <button title="Cancel a pending task, so it does not start"
          ?hidden=${"PENDING"!==t._result.state}
          ?disabled=${!t.permissions.cancel_task}
          @click=${t._promptCancel} class=cancel>cancel</button>
  <button title="Kill a running task, so it stops as soon as possible"
          ?hidden=${"RUNNING"!==t._result.state}
          ?disabled=${!t.permissions.cancel_task}
          @click=${t._promptCancel} class=kill>kill</button>
</div>`)(t)}

    <h2 class=not_found ?hidden=${!t._notFound||!t._taskId}>
      Task not found
    </h2>

    ${((t,e)=>t._taskId&&!t._notFound&&t._taskId.endsWith("0")&&1!==e.try_number&&e.try_number?r.c`
<h2>Displaying a summary for a task with multiple tries</h2>
<table class=task-disambiguation>
  <thead>
    <tr>
      <th>Try ID</th>
      <th>Bot ID</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    ${t._extraTries.map(I)}
  </tbody>
</table>`:"")(t,t._result)}

    ${(t=>!t._taskId||t._notFound?"":t._request.task_slices&&t._request.task_slices.length>1?r.c`
<div class=slice-picker>
  ${t._request.task_slices.map((e,s)=>O(t,s))}
</div>`:"")(t)}

    ${((t,e,s,i)=>!t._taskId||t._notFound?"":(i.properties||(i.properties={}),r.c`
<table class="task-info request-info ${Object(y.n)(t,s)}">
<tbody>
  <tr>
    <td>Name</td>
    <td>${e.name}</td>
  </tr>
  ${T(t,e,s)}
  ${D(e,s,i)}
  ${S(i.properties.dimensions||[])}
  ${A("Isolated Inputs",i.properties.inputs_ref||{})}
  ${j(i.properties.outputs,"Expected outputs",t=>t)}
  ${L(e.tagMap)}

  <tr class=details>
    <td>More Details</td>
    <td>
      <button @click=${t._toggleDetails} ?hidden=${t._showDetails}>
        <add-circle-outline-icon-sk></add-circle-outline-icon-sk>
      </button>
      <button @click=${t._toggleDetails} ?hidden=${!t._showDetails}>
        <remove-circle-outline-icon-sk></remove-circle-outline-icon-sk>
      </button>
    </td>
  </tr>
</tbody>
<tbody ?hidden=${!t._showDetails}>
  ${M(i.properties,i.properties.env||[],i.properties.env_prefixes||[])}

  ${j(e.tags,"Tags",t=>t)}
  <tr>
    <td>Execution timeout</td>
    <td>${Object(f.d)(i.properties.execution_timeout_secs)}</td>
  </tr>
  <tr>
    <td>I/O timeout</td>
    <td>${Object(f.d)(i.properties.io_timeout_secs)}</td>
  </tr>
  <tr>
    <td>Grace period</td>
    <td>${Object(f.d)(i.properties.grace_period_secs)}</td>
  </tr>

  ${H(i.properties.cipd_input,s)}
  ${j(i.properties.caches,"Named Caches",t=>t.name+":"+t.path)}
</tbody>
</table>
`))(t,t._request,t._result,t._currentSlice)}

    ${((t,e,s)=>{if(!t._taskId||t._notFound||Object(y.p)(s))return"";const i=s.performance_stats||{};return r.c`
<div class=title>Task Timing Information</div>
<div class="horizontal layout wrap">
  <table class="task-info task-timing left">
    <tbody>
      <tr>
        <td>Created</td>
        <td title=${e.created_ts}>${e.human_created_ts}</td>
      </tr>
      <tr ?hidden=${!Object(y.q)(s)}>
        <td>Started</td>
        <td title=${s.started_ts}>${s.human_started_ts}</td>
      </tr>
      <tr>
        <td>Scheduling Deadline</td>
        <td>${Object(y.o)(e)}</td>
      </tr>
      <tr ?hidden=${!s.completed_ts}>
        <td>Completed</td>
        <td title=${s.completed_ts}>${s.human_completed_ts}</td>
      </tr>
      <tr ?hidden=${!s.abandoned_ts}>
        <td>Abandoned</td>
        <td title=${s.abandoned_ts}>${s.human_abandoned_ts}</td>
      </tr>
      <tr>
        <td>Last updated</td>
        <td title=${s.modified_ts}>${s.human_modified_ts}</td>
      </tr>
      <tr>
        <td>Pending Time</td>
        <td class=pending>${s.human_pending}</td>
      </tr>
      <tr>
        <td>Total Overhead</td>
        <td class=overhead>${Object(f.d)(i.bot_overhead)}</td>
      </tr>
      <tr>
        <td>Running Time</td>
        <td class=running title="An asterisk indicates the task is still running and thus the time is dynamic.">
          ${s.human_duration}
        </td>
      </tr>
    </tbody>
  </table>
  <div class=right>
    <stacked-time-chart
      labels='["Pending", "Overhead", "Running", "Overhead"]'
      colors='["#E69F00", "#D55E00", "#0072B2", "#D55E00"]'
      .values=${Object(y.c)(s)}>
    </stacked-time-chart>
  </div>
</div>
`})(t,t._request,t._result)}

    ${R(t,t._request,t._result)}

    ${((t,e,s,i)=>{if(!t._taskId||t._notFound)return"";if(!s||!Object(y.q)(s))return r.c`
<div class=title>Task Execution</div>
<div class=task-execution>This space left blank until a bot is assigned to the task.</div>
`;if(Object(y.p)(s))return r.c`
<div class=title>Task was Deduplicated</div>

<p class=deduplicated>
  This task was deduplicated from task
  <a href=${Object(f.j)(s.deduped_from)}>${s.deduped_from}</a>.
  For more information on deduplication, see
  <a href="https://chromium.googlesource.com/infra/luci/luci-py/+/master/appengine/swarming/doc/Detailed-Design.md#task-deduplication">
  the docs</a>.
</p>`;i.properties||(i.properties={});const n=s.bot_dimensions||[],a=i.properties.dimensions||[];for(const t of n){for(const e of a)e.key===t.key&&(t.highlight=!0);if(t.values=[],t.value)for(const e of t.value){const s={name:Object(k.a)(e,t.key)};for(const i of a)i.key===t.key&&i.value===e&&(s.bold=!0);t.values.push(s)}}return r.c`
<div class=title>Task Execution</div>
<table class=task-execution>
  <tr>
    <td>Bot assigned to task</td>
    <td><a href=${Object(f.b)(s.bot_id)}>${s.bot_id}</td>
  </tr>
  <tr>
    <td rowspan=${n.length+1}>
      Dimensions
    </td>
  </tr>
  ${n.map(t=>B(t,a))}
  <tr>
    <td>Exit Code</td>
    <td>${s.exit_code}</td>
  </tr>
  <tr>
    <td>Try Number</td>
    <td>${s.try_number}</td>
  </tr>
  <tr>
    <td>Failure</td>
    <td class=${s.failure?"failed_task":""}>${!!s.failure}</td>
  </tr>
  <tr>
    <td>Internal Failure</td>
    <td class=${s.internal_failure?"exception":""}>${s.internal_failure}</td>
  </tr>
  <tr>
    <td>Cost (USD)</td>
    <td>$${Object(y.m)(s)}</td>
  </tr>
  ${A("Isolated Outputs",s.outputs_ref||{})}
  <tr>
    <td>Bot Version</td>
    <td>${s.bot_version}</td>
  </tr>
  <tr>
    <td>Server Version</td>
    <td>${s.server_versions}</td>
  </tr>
</table>`})(t,t._request,t._result,t._currentSlice)}

    ${((t,e)=>t._taskId&&!t._notFound&&e?r.c`
<div class=title>Performance Stats</div>
<table class=performance-stats>
  <tr>
    <td title="This includes time taken to download inputs, isolate outputs, and setup CIPD">Total Overhead</td>
    <td>${Object(f.d)(e.bot_overhead)}</td>
  </tr>
  <tr>
    <td>Downloading Inputs From Isolate</td>
    <td>${Object(f.d)(e.isolated_download.duration)}</td>
  </tr>
  <tr>
    <td>Uploading Outputs To Isolate</td>
    <td>${Object(f.d)(e.isolated_upload.duration)}</td>
  </tr>
  <tr>
    <td>Initial bot cache</td>
    <td>${e.isolated_download.initial_number_items||0} items;
    ${b.b(e.isolated_download.initial_size||0)}</td>
  </tr>
  <tr>
    <td>Downloaded Cold Items</td>
    <td>${e.isolated_download.num_items_cold||0} items;
     ${b.b(e.isolated_download.total_bytes_items_cold||0)}</td>
  </tr>
  <tr>
    <td>Downloaded Hot Items</td>
    <td>${e.isolated_download.num_items_hot||0} items;
     ${b.b(e.isolated_download.total_bytes_items_hot||0)}</td>
  </tr>
  <tr>
    <td>Uploaded Cold Items</td>
    <td>${e.isolated_upload.num_items_cold||0} items;
     ${b.b(e.isolated_upload.total_bytes_items_cold||0)}</td>
  </tr>
  <tr>
    <td>Uploaded Hot Items</td>
    <td>${e.isolated_upload.num_items_hot||0} items;
     ${b.b(e.isolated_upload.total_bytes_items_hot||0)}</td>
  </tr>
</table>`:"")(t,t._result.performance_stats)}

    ${((t,e)=>{if(!t._taskId||t._notFound)return"";const s=e.properties&&e.properties.inputs_ref||{},i=!!s.isolated,n=window.location.hostname;return r.c`
<div class=title>Reproducing the task locally</div>
<div class=reproduce>
  <div ?hidden=${!i}>Download inputs files into directory <i>foo</i>:</div>
  <div class="code bottom_space" ?hidden=${!i}>
    # (if needed) cipd install 'infra/tools/luci/isolated/\${platform}' -root bar<br>
    ./bar/isolated download -I ${s.isolatedserver} --namespace ${s.namespace}
    -isolated ${s.isolated} -output-dir foo
  </div>

  <div>Run this task locally:</div>
  <div class="code bottom_space">
    # (if needed) git clone https://chromium.googlesource.com/infra/luci/client-py<br>
    python ./client-py/swarming.py reproduce -S ${n} ${t._taskId}
  </div>

  <div>Download output results into directory <i>foo</i>:</div>
  <div class="code bottom_space">
    # (if needed) git clone https://chromium.googlesource.com/infra/luci/client-py<br>
    python ./client-py/swarming.py collect -S ${n} --task-output-dir=foo ${t._taskId}
  </div>
</div>
`})(t,t._currentSlice)}
    </div>
    <div class="right grow" ?hidden=${!t.loggedInAndAuthorized}>
    ${(t=>!t._taskId||t._notFound?"":r.c`
<div class="horizontal layout">
  <div class=output-picker>
    <div class=tab selected>
      Raw Output
    </div>
    <div class=tab ?hidden=${!Object(y.e)(t)}>
      <a rel=noopener target=_blank href=${Object(o.a)(Object(y.j)(t))}>
        Rich Output
      </a>
    </div>
    <checkbox-sk
      id=wide_logs ?checked=${t._wideLogs} @click=${t._toggleWidth}>
    </checkbox-sk>
    <span>Full Width Logs</span>
  </div>
</div>
<div class="code stdout tabbed ${t._wideLogs?"wide":"break-all"}">
  ${t._stdout.map(V)}
</div>`)(t)}
    </div>
  </main>
  <footer></footer>
  <dialog-pop-over id=retry>
    <div class='retry-dialog content'>
      ${((t,e)=>{const s=e.dimensions||[];return r.c`
<div class=prompt>
  <h2>
    Are you sure you want to ${t._isPromptDebug?"debug":"retry"}
    task ${t._taskId}?
  </h2>
  <div>
    <div class=ib ?hidden=${!t._isPromptDebug}>
      <span>Lease Duration</span>
      <input id=lease_duration value=4h></input>
    </div>
    <div class=ib>
      <checkbox-sk class=same-bot
          ?disabled=${!Object(y.q)(t._result)}
          ?checked=${t._useSameBot}
          @click=${t._toggleSameBot}>
      </checkbox-sk>
      <span>Run task on the same bot</span>
    </div>
    <br>
  </div>
  <div>If you want to modify any dimensions (e.g. specify a bot's id), do so now.</div>
  <table ?hidden=${t._useSameBot}>
    <thead>
      <tr>
        <th>Key</th>
        <th>Value</th>
      </tr>
    </thead>
    <tbody id=retry_inputs>
      ${s.map(F)}
      ${F({key:"",value:""})}
    </tbody>
  </table>
</div>`})(t,t._currentSlice.properties||{})}
      <div class="horizontal layout end">
        <button @click=${t._closePopups} class=cancel tabindex=0>Cancel</button>
        <button @click=${t._promptCallback} class=ok tabindex=0>OK</button>
      </div>
    </div>
  </dialog-pop-over>
  <dialog-pop-over id=cancel>
    <div class='cancel-dialog content'>
      Are you sure you want to ${t._prompt} task ${t._taskId}?
      <div class="horizontal layout end">
        <button @click=${t._closePopups} class=cancel tabindex=0>NO</button>
        <button @click=${t._promptCallback} class=ok tabindex=0>YES</button>
      </div>
    </div>
  </dialog-pop-over>
</swarming-app>
`;window.customElements.define("task-page",class extends w.a{constructor(){super(q),this._taskId="",this._showDetails=!1,this._wideLogs=!1,this._urlParamsLoaded=!1;const t=location.hostname.indexOf(".appspot.com");this._project_id=location.hostname.substring(0,t),this._stateChanged=Object(c.a)(()=>({id:this._taskId,d:this._showDetails,w:this._wideLogs}),t=>{this._taskId=t.id||this._taskId,this._showDetails=t.d,this._wideLogs=t.w,this._urlParamsLoaded=!0,this._fetch(),this.render()}),this._request={},this._result={},this._stdout=[],this._stdoutOffset=0,this._currentSlice={},this._currentSliceIdx=-1,this._notFound=!1,this._extraTries=[],this._capacityCounts=[],this._pendingCounts=[],this._runningCounts=[],this._message="You must sign in to see anything useful.",this._fetchController=null,this._promptCallback=()=>{},this._isPromptDebug=!1,this._useSameBot=!1,this._logFetchPeriod=1e4}connectedCallback(){super.connectedCallback(),this._loginEvent=t=>{this._fetch(),this.render()},this.addEventListener("log-in",this._loginEvent),this.render()}disconnectedCallback(){super.disconnectedCallback(),this.removeEventListener("log-in",this._loginEvent)}_cancelTask(){const t={};"RUNNING"===this._result.state&&(t.kill_running=!0),this.app.addBusyTasks(1),fetch(`/_ah/api/swarming/v1/task/${this._taskId}/cancel`,{method:"POST",headers:{authorization:this.auth_header,"content-type":"application/json; charset=UTF-8"},body:JSON.stringify(t)}).then(d.a).then(t=>{this._closePopups(),Object(n.a)("Request sent",4e3),this.render(),this.app.finishedTask()}).catch(t=>this.fetchError(t,"task/cancel"))}_closePopups(){this._promptCallback=()=>{},Object(i.a)("dialog-pop-over",this).map(t=>t.hide())}_collectDimensions(){const t=[];if(this._useSameBot)t.push({key:"id",value:Object(y.d)(this._result.bot_dimensions,"id")},{key:"pool",value:Object(y.d)(this._result.bot_dimensions,"pool")});else{const e=Object(i.a)("#retry_inputs tr",this);for(const s of e){const e=s.children[0].firstElementChild.value,i=s.children[1].firstElementChild.value;e&&i&&t.push({key:e,value:i})}if(!t.length)return Object(n.a)("You must specify some dimensions (pool is required)",6e3),null;if(!Object(y.d)(t,"pool"))return Object(n.a)("The pool dimension is required"),null}return t}_debugTask(){const t={expiration_secs:this._request.expiration_secs,name:`leased to ${this.profile.email} for debugging`,pool_task_template:3,priority:20,properties:this._currentSlice.properties,service_account:this._request.service_account,tags:["debug_task:1"],user:this.profile.email},e=Object(i.b)("#lease_duration").value,s=Object(f.g)(e);t.properties.command=["python","-c",`import os, sys, time\nprint('Mapping task: ${location.origin}/task?id=${this._taskId}')\nprint('Files are mapped into: ' + os.getcwd())\nprint('')\nprint('Bot id: ' + os.environ['SWARMING_BOT_ID'])\nprint('Bot leased for: ${s} seconds')\nprint('How to access this bot: http://go/swarming-ssh')\nprint('When done, reboot the host')\nprint('')\nprint('Some tests may fail without the following env vars set:')\nprint('PATH=' + os.environ['PATH'])\nprint('LUCI_CONTEXT=' + os.environ['LUCI_CONTEXT'])\nsys.stdout.flush()\ntime.sleep(${s})`],delete t.properties.extra_args,t.properties.execution_timeout_secs=s,t.properties.io_timeout_secs=s;const n=this._collectDimensions();n&&(t.properties.dimensions=n,this._newTask(t),this._closePopups())}_fetch(){if(!this.loggedInAndAuthorized||!this._urlParamsLoaded||!this._taskId)return;this._fetchController&&this._fetchController.abort(),this._fetchController=new AbortController;const t={headers:{authorization:this.auth_header},signal:this._fetchController.signal};this.app._fetchPermissions(t,{task_id:this._taskId}),this._fetchTaskInfo(t),this._fetchStdOut(t)}_fetchTaskInfo(t){this.app.addBusyTasks(2);let e=-1;fetch(`/_ah/api/swarming/v1/task/${this._taskId}/request`,t).then(d.a).then(s=>{this._notFound=!1,this._request=Object(y.h)(s),this._fetchCounts(this._request,t),e>=0?this._setSlice(e):this.render(),this.app.finishedTask()}).catch(t=>{404===t.status&&(this._request={},this._notFound=!0,this.render()),this.fetchError(t,"task/request")}),this._extraTries=[],fetch(`/_ah/api/swarming/v1/task/${this._taskId}/result?include_performance_stats=true`,t).then(d.a).then(s=>{this._result=Object(y.i)(s),this._result.try_number>1&&(this._extraTries[this._result.try_number-1]=this._result,this._extraTries.fill({},0,this._result.try_number-1),this._fetchExtraTries(this._taskId,this._result.try_number-1,t)),e=+this._result.current_task_slice,this._setSlice(e),this.app.finishedTask()}).catch(t=>this.fetchError(t,"task/result"))}_fetchStdOut(t){this.app.addBusyTasks(1);let e="";const s=()=>{fetch(`/_ah/api/swarming/v1/task/${this._taskId}/stdout?offset=${this._stdoutOffset}&`+"length=102400",t).then(d.a).then(i=>{e||(e=i.state);const n=i.output||"";this._stdoutOffset+=n.length;const r=n.replace(/\r\n/g,"\n"),a=r.lastIndexOf("\n");let o=r,d="";-1!==a&&(o=r.substring(0,a+1),d=r.substring(a+1)),this._stdout.length&&!this._stdout[this._stdout.length-1].endsWith("\n")?(this._stdout[this._stdout.length-1]+=o,d&&this._stdout.push(d)):(this._stdout.push(o),d&&this._stdout.push(d)),this.render(),i.state!==e&&this._fetchTaskInfo(t),"RUNNING"===i.state||"PENDING"===i.state?n.length<102400?setTimeout(s,this._logFetchPeriod):s():n.length<102400?this.app.finishedTask():s(),e=i.state}).catch(t=>this.fetchError(t,"task/request"))};s()}_fetchCounts(t,e){const s=t.task_slices.length;this.app.addBusyTasks(3*s),this._capacityCounts=[],this._pendingCounts=[],this._runningCounts=[];for(let i=0;i<s;i++){const s={dimensions:[]};for(const e of t.task_slices[i].properties.dimensions)s.dimensions.push(`${e.key}:${e.value}`);fetch(`/_ah/api/swarming/v1/bots/count?${v.a(s)}`,e).then(d.a).then(t=>{this._capacityCounts[i]=t,this.render(),this.app.finishedTask()}).catch(t=>this.fetchError(t,"bots/count slice "+i,!0));let n=new Date;n.setSeconds(0),n=""+(n.getTime()-864e5),n=n.substring(0,n.length-3);const r={start:[n],state:["RUNNING"],tags:s.dimensions};fetch(`/_ah/api/swarming/v1/tasks/count?${v.a(r)}`,e).then(d.a).then(t=>{this._runningCounts[i]=t.count,this.render(),this.app.finishedTask()}).catch(t=>this.fetchError(t,"tasks/running slice "+i,!0)),r.state=["PENDING"],fetch(`/_ah/api/swarming/v1/tasks/count?${v.a(r)}`,e).then(d.a).then(t=>{this._pendingCounts[i]=t.count,this.render(),this.app.finishedTask()}).catch(t=>this.fetchError(t,"tasks/pending slice "+i,!0))}}_fetchExtraTries(t,e,s){this.app.addBusyTasks(e);t.substring(0,t.length-1);for(let i=0;i<e;i++)fetch(`/_ah/api/swarming/v1/task/${t+(i+1)}/result`,s).then(d.a).then(t=>{const e=Object(y.i)(t);this._extraTries[i]=e,this.render(),this.app.finishedTask()}).catch(t=>this.fetchError(t,"task/result"))}_newTask(t){t.properties.idempotent=!1,this.app.addBusyTasks(1),fetch("/_ah/api/swarming/v1/tasks/new",{method:"POST",headers:{authorization:this.auth_header,"content-type":"application/json; charset=UTF-8"},body:JSON.stringify(t)}).then(d.a).then(t=>{t&&t.task_id&&(this._taskId=t.task_id,this._stateChanged(),this._fetch(),this.render(),this.app.finishedTask())}).catch(t=>this.fetchError(t,"newtask"))}_promptCancel(){this._prompt="cancel","RUNNING"===this._result.state&&(this._prompt="kill"),this._promptCallback=this._cancelTask,this.render(),Object(i.b)("dialog-pop-over#cancel",this).show(),Object(i.b)("dialog-pop-over#cancel button.cancel",this).focus()}_promptDebug(){this._request?(this._isPromptDebug=!0,this._useSameBot=!1,this._promptCallback=this._debugTask,this.render(),Object(i.b)("dialog-pop-over#retry",this).show(),Object(i.b)("dialog-pop-over#retry button.cancel",this).focus()):Object(n.a)("Task not yet loaded",3e3)}_promptRetry(){this._request?(this._isPromptDebug=!1,this._useSameBot=!1,this._promptCallback=this._retryTask,this.render(),Object(i.b)("dialog-pop-over#retry",this).show(),Object(i.b)("dialog-pop-over#retry button.cancel",this).focus()):Object(n.a)("Task not yet loaded",3e3)}render(){super.render(),Object(i.b)("#id_input",this).value=this._taskId}_retryTask(){const t={expiration_secs:this._request.expiration_secs,name:this._request.name+" (retry)",pool_task_template:3,priority:this._request.priority,properties:this._currentSlice.properties,service_account:this._request.service_account,tags:this._request.tags,user:this.profile.email};t.tags.push("retry:1");const e=this._collectDimensions();e&&(t.properties.dimensions=e,this._newTask(t),this._closePopups())}_setSlice(t){this._currentSliceIdx=t,this._request.task_slices&&(this._currentSlice=this._request.task_slices[t],this.render())}_toggleDetails(t){this._showDetails=!this._showDetails,this._stateChanged(),this.render()}_toggleSameBot(t){t.preventDefault(),Object(y.q)(this._result)&&(this._useSameBot=!this._useSameBot,this.render())}_toggleWidth(t){t.preventDefault(),this._wideLogs=!this._wideLogs,this._stateChanged(),this.render()}_updateID(t){const e=Object(i.b)("#id_input",this);this._taskId=e.value,this._stdout=[],this._stdoutOffset=0,this._stateChanged(),this._fetch(),this.render()}});s(53)}]);