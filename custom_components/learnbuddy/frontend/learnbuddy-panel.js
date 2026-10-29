var gt=Object.defineProperty;var _t=Object.getOwnPropertyDescriptor;var b=(u,a,e,t)=>{for(var i=t>1?void 0:t?_t(a,e):a,n=u.length-1,s;n>=0;n--)(s=u[n])&&(i=(t?s(a,e,i):s(i))||i);return t&&i&&gt(a,e,i),i};var pe=globalThis,me=pe.ShadowRoot&&(pe.ShadyCSS===void 0||pe.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,xe=Symbol(),Ne=new WeakMap,se=class{constructor(a,e,t){if(this._$cssResult$=!0,t!==xe)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=a,this.t=e}get styleSheet(){let a=this.o,e=this.t;if(me&&a===void 0){let t=e!==void 0&&e.length===1;t&&(a=Ne.get(e)),a===void 0&&((this.o=a=new CSSStyleSheet).replaceSync(this.cssText),t&&Ne.set(e,a))}return a}toString(){return this.cssText}},Pe=u=>new se(typeof u=="string"?u:u+"",void 0,xe),C=(u,...a)=>{let e=u.length===1?u[0]:a.reduce((t,i,n)=>t+(s=>{if(s._$cssResult$===!0)return s.cssText;if(typeof s=="number")return s;throw Error("Value passed to 'css' function must be a 'css' function result: "+s+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+u[n+1],u[0]);return new se(e,u,xe)},Me=(u,a)=>{if(me)u.adoptedStyleSheets=a.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of a){let t=document.createElement("style"),i=pe.litNonce;i!==void 0&&t.setAttribute("nonce",i),t.textContent=e.cssText,u.appendChild(t)}},ye=me?u=>u:u=>u instanceof CSSStyleSheet?(a=>{let e="";for(let t of a.cssRules)e+=t.cssText;return Pe(e)})(u):u;var{is:ft,defineProperty:bt,getOwnPropertyDescriptor:pt,getOwnPropertyNames:mt,getOwnPropertySymbols:vt,getPrototypeOf:kt}=Object,ve=globalThis,je=ve.trustedTypes,$t=je?je.emptyScript:"",wt=ve.reactiveElementPolyfillSupport,ae=(u,a)=>u,re={toAttribute(u,a){switch(a){case Boolean:u=u?$t:null;break;case Object:case Array:u=u==null?u:JSON.stringify(u)}return u},fromAttribute(u,a){let e=u;switch(a){case Boolean:e=u!==null;break;case Number:e=u===null?null:Number(u);break;case Object:case Array:try{e=JSON.parse(u)}catch{e=null}}return e}},ke=(u,a)=>!ft(u,a),qe={attribute:!0,type:String,converter:re,reflect:!1,useDefault:!1,hasChanged:ke};Symbol.metadata??=Symbol("metadata"),ve.litPropertyMetadata??=new WeakMap;var M=class extends HTMLElement{static addInitializer(a){this._$Ei(),(this.l??=[]).push(a)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(a,e=qe){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(a)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(a,e),!e.noAccessor){let t=Symbol(),i=this.getPropertyDescriptor(a,t,e);i!==void 0&&bt(this.prototype,a,i)}}static getPropertyDescriptor(a,e,t){let{get:i,set:n}=pt(this.prototype,a)??{get(){return this[e]},set(s){this[e]=s}};return{get:i,set(s){let l=i?.call(this);n?.call(this,s),this.requestUpdate(a,l,t)},configurable:!0,enumerable:!0}}static getPropertyOptions(a){return this.elementProperties.get(a)??qe}static _$Ei(){if(this.hasOwnProperty(ae("elementProperties")))return;let a=kt(this);a.finalize(),a.l!==void 0&&(this.l=[...a.l]),this.elementProperties=new Map(a.elementProperties)}static finalize(){if(this.hasOwnProperty(ae("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(ae("properties"))){let e=this.properties,t=[...mt(e),...vt(e)];for(let i of t)this.createProperty(i,e[i])}let a=this[Symbol.metadata];if(a!==null){let e=litPropertyMetadata.get(a);if(e!==void 0)for(let[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(let[e,t]of this.elementProperties){let i=this._$Eu(e,t);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(a){let e=[];if(Array.isArray(a)){let t=new Set(a.flat(1/0).reverse());for(let i of t)e.unshift(ye(i))}else a!==void 0&&e.push(ye(a));return e}static _$Eu(a,e){let t=e.attribute;return t===!1?void 0:typeof t=="string"?t:typeof a=="string"?a.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(a=>this.enableUpdating=a),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(a=>a(this))}addController(a){(this._$EO??=new Set).add(a),this.renderRoot!==void 0&&this.isConnected&&a.hostConnected?.()}removeController(a){this._$EO?.delete(a)}_$E_(){let a=new Map,e=this.constructor.elementProperties;for(let t of e.keys())this.hasOwnProperty(t)&&(a.set(t,this[t]),delete this[t]);a.size>0&&(this._$Ep=a)}createRenderRoot(){let a=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return Me(a,this.constructor.elementStyles),a}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(a=>a.hostConnected?.())}enableUpdating(a){}disconnectedCallback(){this._$EO?.forEach(a=>a.hostDisconnected?.())}attributeChangedCallback(a,e,t){this._$AK(a,t)}_$ET(a,e){let t=this.constructor.elementProperties.get(a),i=this.constructor._$Eu(a,t);if(i!==void 0&&t.reflect===!0){let n=(t.converter?.toAttribute!==void 0?t.converter:re).toAttribute(e,t.type);this._$Em=a,n==null?this.removeAttribute(i):this.setAttribute(i,n),this._$Em=null}}_$AK(a,e){let t=this.constructor,i=t._$Eh.get(a);if(i!==void 0&&this._$Em!==i){let n=t.getPropertyOptions(i),s=typeof n.converter=="function"?{fromAttribute:n.converter}:n.converter?.fromAttribute!==void 0?n.converter:re;this._$Em=i;let l=s.fromAttribute(e,n.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(a,e,t,i=!1,n){if(a!==void 0){let s=this.constructor;if(i===!1&&(n=this[a]),t??=s.getPropertyOptions(a),!((t.hasChanged??ke)(n,e)||t.useDefault&&t.reflect&&n===this._$Ej?.get(a)&&!this.hasAttribute(s._$Eu(a,t))))return;this.C(a,e,t)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(a,e,{useDefault:t,reflect:i,wrapped:n},s){t&&!(this._$Ej??=new Map).has(a)&&(this._$Ej.set(a,s??e??this[a]),n!==!0||s!==void 0)||(this._$AL.has(a)||(this.hasUpdated||t||(e=void 0),this._$AL.set(a,e)),i===!0&&this._$Em!==a&&(this._$Eq??=new Set).add(a))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let a=this.scheduleUpdate();return a!=null&&await a,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,n]of this._$Ep)this[i]=n;this._$Ep=void 0}let t=this.constructor.elementProperties;if(t.size>0)for(let[i,n]of t){let{wrapped:s}=n,l=this[i];s!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,n,l)}}let a=!1,e=this._$AL;try{a=this.shouldUpdate(e),a?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(t){throw a=!1,this._$EM(),t}a&&this._$AE(e)}willUpdate(a){}_$AE(a){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(a)),this.updated(a)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(a){return!0}update(a){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(a){}firstUpdated(a){}};M.elementStyles=[],M.shadowRootOptions={mode:"open"},M[ae("elementProperties")]=new Map,M[ae("finalized")]=new Map,wt?.({ReactiveElement:M}),(ve.reactiveElementVersions??=[]).push("2.1.2");var Ie=globalThis,Ue=u=>u,$e=Ie.trustedTypes,Ke=$e?$e.createPolicy("lit-html",{createHTML:u=>u}):void 0,Ge="$lit$",U=`lit$${Math.random().toFixed(9).slice(2)}$`,We="?"+U,xt=`<${We}>`,Z=document,he=()=>Z.createComment(""),oe=u=>u===null||typeof u!="object"&&typeof u!="function",De=Array.isArray,yt=u=>De(u)||typeof u?.[Symbol.iterator]=="function",ze=`[ 	
\f\r]`,le=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,He=/-->/g,Ce=/>/g,V=RegExp(`>|${ze}(?:([^\\s"'>=/]+)(${ze}*=${ze}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Ve=/'/g,Oe=/"/g,Je=/^(?:script|style|textarea|title)$/i,Be=u=>(a,...e)=>({_$litType$:u,strings:a,values:e}),r=Be(1),N=Be(2),Jt=Be(3),G=Symbol.for("lit-noChange"),c=Symbol.for("lit-nothing"),Ze=new WeakMap,O=Z.createTreeWalker(Z,129);function Xe(u,a){if(!De(u)||!u.hasOwnProperty("raw"))throw Error("invalid template strings array");return Ke!==void 0?Ke.createHTML(a):a}var zt=(u,a)=>{let e=u.length-1,t=[],i,n=a===2?"<svg>":a===3?"<math>":"",s=le;for(let l=0;l<e;l++){let h=u[l],d,g,o=-1,_=0;for(;_<h.length&&(s.lastIndex=_,g=s.exec(h),g!==null);)_=s.lastIndex,s===le?g[1]==="!--"?s=He:g[1]!==void 0?s=Ce:g[2]!==void 0?(Je.test(g[2])&&(i=RegExp("</"+g[2],"g")),s=V):g[3]!==void 0&&(s=V):s===V?g[0]===">"?(s=i??le,o=-1):g[1]===void 0?o=-2:(o=s.lastIndex-g[2].length,d=g[1],s=g[3]===void 0?V:g[3]==='"'?Oe:Ve):s===Oe||s===Ve?s=V:s===He||s===Ce?s=le:(s=V,i=void 0);let f=s===V&&u[l+1].startsWith("/>")?" ":"";n+=s===le?h+xt:o>=0?(t.push(d),h.slice(0,o)+Ge+h.slice(o)+U+f):h+U+(o===-2?l:f)}return[Xe(u,n+(u[e]||"<?>")+(a===2?"</svg>":a===3?"</math>":"")),t]},ce=class u{constructor({strings:a,_$litType$:e},t){let i;this.parts=[];let n=0,s=0,l=a.length-1,h=this.parts,[d,g]=zt(a,e);if(this.el=u.createElement(d,t),O.currentNode=this.el.content,e===2||e===3){let o=this.el.content.firstChild;o.replaceWith(...o.childNodes)}for(;(i=O.nextNode())!==null&&h.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(let o of i.getAttributeNames())if(o.endsWith(Ge)){let _=g[s++],f=i.getAttribute(o).split(U),k=/([.?@])?(.*)/.exec(_);h.push({type:1,index:n,name:k[2],strings:f,ctor:k[1]==="."?Ee:k[1]==="?"?Se:k[1]==="@"?Te:X}),i.removeAttribute(o)}else o.startsWith(U)&&(h.push({type:6,index:n}),i.removeAttribute(o));if(Je.test(i.tagName)){let o=i.textContent.split(U),_=o.length-1;if(_>0){i.textContent=$e?$e.emptyScript:"";for(let f=0;f<_;f++)i.append(o[f],he()),O.nextNode(),h.push({type:2,index:++n});i.append(o[_],he())}}}else if(i.nodeType===8)if(i.data===We)h.push({type:2,index:n});else{let o=-1;for(;(o=i.data.indexOf(U,o+1))!==-1;)h.push({type:7,index:n}),o+=U.length-1}n++}}static createElement(a,e){let t=Z.createElement("template");return t.innerHTML=a,t}};function J(u,a,e=u,t){if(a===G)return a;let i=t!==void 0?e._$Co?.[t]:e._$Cl,n=oe(a)?void 0:a._$litDirective$;return i?.constructor!==n&&(i?._$AO?.(!1),n===void 0?i=void 0:(i=new n(u),i._$AT(u,e,t)),t!==void 0?(e._$Co??=[])[t]=i:e._$Cl=i),i!==void 0&&(a=J(u,i._$AS(u,a.values),i,t)),a}var Ae=class{constructor(a,e){this._$AV=[],this._$AN=void 0,this._$AD=a,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(a){let{el:{content:e},parts:t}=this._$AD,i=(a?.creationScope??Z).importNode(e,!0);O.currentNode=i;let n=O.nextNode(),s=0,l=0,h=t[0];for(;h!==void 0;){if(s===h.index){let d;h.type===2?d=new ue(n,n.nextSibling,this,a):h.type===1?d=new h.ctor(n,h.name,h.strings,this,a):h.type===6&&(d=new Fe(n,this,a)),this._$AV.push(d),h=t[++l]}s!==h?.index&&(n=O.nextNode(),s++)}return O.currentNode=Z,i}p(a){let e=0;for(let t of this._$AV)t!==void 0&&(t.strings!==void 0?(t._$AI(a,t,e),e+=t.strings.length-2):t._$AI(a[e])),e++}},ue=class u{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(a,e,t,i){this.type=2,this._$AH=c,this._$AN=void 0,this._$AA=a,this._$AB=e,this._$AM=t,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let a=this._$AA.parentNode,e=this._$AM;return e!==void 0&&a?.nodeType===11&&(a=e.parentNode),a}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(a,e=this){a=J(this,a,e),oe(a)?a===c||a==null||a===""?(this._$AH!==c&&this._$AR(),this._$AH=c):a!==this._$AH&&a!==G&&this._(a):a._$litType$!==void 0?this.$(a):a.nodeType!==void 0?this.T(a):yt(a)?this.k(a):this._(a)}O(a){return this._$AA.parentNode.insertBefore(a,this._$AB)}T(a){this._$AH!==a&&(this._$AR(),this._$AH=this.O(a))}_(a){this._$AH!==c&&oe(this._$AH)?this._$AA.nextSibling.data=a:this.T(Z.createTextNode(a)),this._$AH=a}$(a){let{values:e,_$litType$:t}=a,i=typeof t=="number"?this._$AC(a):(t.el===void 0&&(t.el=ce.createElement(Xe(t.h,t.h[0]),this.options)),t);if(this._$AH?._$AD===i)this._$AH.p(e);else{let n=new Ae(i,this),s=n.u(this.options);n.p(e),this.T(s),this._$AH=n}}_$AC(a){let e=Ze.get(a.strings);return e===void 0&&Ze.set(a.strings,e=new ce(a)),e}k(a){De(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,t,i=0;for(let n of a)i===e.length?e.push(t=new u(this.O(he()),this.O(he()),this,this.options)):t=e[i],t._$AI(n),i++;i<e.length&&(this._$AR(t&&t._$AB.nextSibling,i),e.length=i)}_$AR(a=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);a!==this._$AB;){let t=Ue(a).nextSibling;Ue(a).remove(),a=t}}setConnected(a){this._$AM===void 0&&(this._$Cv=a,this._$AP?.(a))}},X=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(a,e,t,i,n){this.type=1,this._$AH=c,this._$AN=void 0,this.element=a,this.name=e,this._$AM=i,this.options=n,t.length>2||t[0]!==""||t[1]!==""?(this._$AH=Array(t.length-1).fill(new String),this.strings=t):this._$AH=c}_$AI(a,e=this,t,i){let n=this.strings,s=!1;if(n===void 0)a=J(this,a,e,0),s=!oe(a)||a!==this._$AH&&a!==G,s&&(this._$AH=a);else{let l=a,h,d;for(a=n[0],h=0;h<n.length-1;h++)d=J(this,l[t+h],e,h),d===G&&(d=this._$AH[h]),s||=!oe(d)||d!==this._$AH[h],d===c?a=c:a!==c&&(a+=(d??"")+n[h+1]),this._$AH[h]=d}s&&!i&&this.j(a)}j(a){a===c?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,a??"")}},Ee=class extends X{constructor(){super(...arguments),this.type=3}j(a){this.element[this.name]=a===c?void 0:a}},Se=class extends X{constructor(){super(...arguments),this.type=4}j(a){this.element.toggleAttribute(this.name,!!a&&a!==c)}},Te=class extends X{constructor(a,e,t,i,n){super(a,e,t,i,n),this.type=5}_$AI(a,e=this){if((a=J(this,a,e,0)??c)===G)return;let t=this._$AH,i=a===c&&t!==c||a.capture!==t.capture||a.once!==t.once||a.passive!==t.passive,n=a!==c&&(t===c||i);i&&this.element.removeEventListener(this.name,this,t),n&&this.element.addEventListener(this.name,this,a),this._$AH=a}handleEvent(a){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,a):this._$AH.handleEvent(a)}},Fe=class{constructor(a,e,t){this.element=a,this.type=6,this._$AN=void 0,this._$AM=e,this.options=t}get _$AU(){return this._$AM._$AU}_$AI(a){J(this,a)}};var At=Ie.litHtmlPolyfillSupport;At?.(ce,ue),(Ie.litHtmlVersions??=[]).push("3.3.3");var Qe=(u,a,e)=>{let t=e?.renderBefore??a,i=t._$litPart$;if(i===void 0){let n=e?.renderBefore??null;t._$litPart$=i=new ue(a.insertBefore(he(),n),n,void 0,e??{})}return i._$AI(u),i};var Re=globalThis,R=class extends M{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let a=super.createRenderRoot();return this.renderOptions.renderBefore??=a.firstChild,a}update(a){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(a),this._$Do=Qe(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return G}};R._$litElement$=!0,R.finalized=!0,Re.litElementHydrateSupport?.({LitElement:R});var Et=Re.litElementPolyfillSupport;Et?.({LitElement:R});(Re.litElementVersions??=[]).push("4.2.2");var St={attribute:!0,type:String,converter:re,reflect:!1,hasChanged:ke},Tt=(u=St,a,e)=>{let{kind:t,metadata:i}=e,n=globalThis.litPropertyMetadata.get(i);if(n===void 0&&globalThis.litPropertyMetadata.set(i,n=new Map),t==="setter"&&((u=Object.create(u)).wrapped=!0),n.set(e.name,u),t==="accessor"){let{name:s}=e;return{set(l){let h=a.get.call(this);a.set.call(this,l),this.requestUpdate(s,h,u,!0,l)},init(l){return l!==void 0&&this.C(s,void 0,u,l),l}}}if(t==="setter"){let{name:s}=e;return function(l){let h=this[s];a.call(this,l),this.requestUpdate(s,h,u,!0,l)}}throw Error("Unsupported decorator location: "+t)};function F(u){return(a,e)=>typeof e=="object"?Tt(u,a,e):((t,i,n)=>{let s=i.hasOwnProperty(n);return i.constructor.createProperty(n,t),s?Object.getOwnPropertyDescriptor(i,n):void 0})(u,a,e)}function m(u){return F({...u,state:!0,attribute:!1})}var K=class{constructor(a){this.hass=a}call(a,e={}){return this.hass.callWS({type:`learnbuddy/${a}`,...e})}uebersicht(){return this.call("overview")}dashboard(a){return this.call("dashboard",{kind_id:a})}frageStellen(a,e,t={},i=1){return this.call("ask",{kind_id:a,fach_id:e,...t,anzahl:i})}async abfrageUmfang(a,e,t){return(await this.call("ask_count",{kind_id:a,fach_id:e,...t})).aufgaben}async frageAbbrechen(a){return(await this.call("cancel_question",{kind_id:a})).abgebrochen}setzeAktiv(a,e){return this.call("set_active",{kind_id:a,aktiv:e})}fortschritt(a,e){return this.call("progress",{kind_id:a,tage:e})}wochenreport(a,e){return this.call("weekly_report",{kind_id:a,versatz:e})}async kalenderPruefen(a){return(await this.call("calendar/refresh",{kind_id:a})).gelesen}kalenderIgnorieren(a,e){return this.call("calendar/ignore",{kind_id:a,uid:e})}kalenderWiederherstellen(a){return this.call("calendar/restore",{kind_id:a})}async fachAnlegen(a,e,t,i){return(await this.call("subjects/create",{kind_id:a,typ:e,name:t||null,sprache:i})).fach_id}absenderZuordnen(a,e){return this.call("sender/assign",{kind_id:a,kennung:e})}absenderVerwerfen(a){return this.call("sender/dismiss",{kennung:a})}async aufgaben(a){return(await this.call("tasks/list",{fach_id:a})).aufgaben}aufgabeAnlegen(a,e){return this.call("tasks/create",{fach_id:a,aufgabe:e})}aufgabeAendern(a,e,t){return this.call("tasks/update",{fach_id:a,aufgabe_id:e,aenderungen:t})}aufgabenLoeschen(a,e,t){return this.call("tasks/delete",{fach_id:a,aufgabe_ids:e,bestaetigt:t})}async lektionHinzufuegen(a,e){return(await this.call("lessons/add",{fach_id:a,name:e})).lektionen}async lektionLoeschen(a,e){return(await this.call("lessons/delete",{fach_id:a,name:e})).lektionen}async bereichHinzufuegen(a,e,t=null){return(await this.call("sections/add",{fach_id:a,name:e,art:t})).bereiche}async bereichUmbenennen(a,e,t){return(await this.call("sections/rename",{fach_id:a,bereich:e,name:t})).bereiche}async bereichLoeschen(a,e){return(await this.call("sections/delete",{fach_id:a,bereich:e})).bereiche}importVorschau(a,e,t){return this.call("tasks/import_text",{fach_id:a,inhalt:e,trennzeichen:t,vorschau:!0})}importText(a,e,t,i,n,s=null){return this.call("tasks/import_text",{fach_id:a,inhalt:e,lektion:t,trennzeichen:i,geprueft:n,bereich:s})}generieren(a,e){return this.call("tasks/generate",{fach_id:a,...e})}satzaufgabenErzeugen(a,e){return this.call("tasks/generate_sentences",{fach_id:a,...e})}fragenAusSeiten(a,e){return this.call("tasks/generate_from_pages",{fach_id:a,...e})}fotoAuslesen(a,e){return this.call("tasks/photo_extract",{fach_id:a,seiten:e})}fotoUebernehmen(a,e,t,i=null){return this.call("tasks/photo_accept",{fach_id:a,zeilen:e,lektion:t,bereich:i})}beschriftungenFinden(a,e){return this.call("tasks/label_detect",{fach_id:a,bild:e})}beschriftungVorschau(a,e,t,i){return this.call("tasks/label_preview",{fach_id:a,bild:e,felder:t,vorherige:i})}beschriftungLesen(a,e){return this.call("tasks/label_get",{fach_id:a,bild:e})}beschriftungSpeichern(a,e,t,i,n,s){return this.call("tasks/label_save",{fach_id:a,bild:e,felder:t,lektion:i,bereich:n,vorschau:s})}nachrechnen(a,e){return this.call("tasks/verify",{fach_id:a,aufgabe_ids:e})}rechenwegeErzeugen(a,e){return this.call("tasks/generate_steps",{fach_id:a,aufgabe_ids:e})}async bildHochladen(a,e=!1){let t=new FormData;t.append("file",a);let i=`/api/learnbuddy/bilder${e?"?zweck=seite":""}`,n=await this.hass.fetchWithAuth(i,{method:"POST",body:t}),s=await n.json().catch(()=>({}));if(!n.ok||!s.bild)throw{code:String(n.status),message:s.message??"bild_ungueltig"};return s.bild}async bildAdresse(a){return(await this.hass.callWS({type:"auth/sign_path",path:`/api/learnbuddy/bilder/${a}`,expires:3600})).path}async vorschlagUebernehmen(a,e){return(await this.call("tasks/accept_suggestion",{fach_id:a,aufgabe_ids:e})).uebernommen}async alsGeprueftMarkieren(a,e){return(await this.call("tasks/mark_verified",{fach_id:a,aufgabe_ids:e})).markiert}export(a,e){return this.call("tasks/export",{fach_id:a,mit_statistik:e})}importJson(a,e,t,i,n=null){return this.call("tasks/import_json",{fach_id:a,daten:e,mit_statistik:t,lektion:i,bereich:n})}async arbeitSpeichern(a,e){return(await this.call("exams/save",{arbeit_id:a,arbeit:e})).arbeit_id}simulieren(a,e,t){return this.call("exams/simulate",{arbeit_id:a,anzahl:e,weg:t})}async simulationAbbrechen(a){return(await this.call("exams/simulate_stop",{kind_id:a})).abgebrochen}arbeitLoeschen(a){return this.call("exams/delete",{arbeit_id:a})}};var Ye={titel:"LearnBuddy",kind:"Kind",fach:"Fach",keine_kinder:"Es ist noch kein Kind angelegt. Lege unter Einstellungen \u2192 Ger\xE4te & Dienste \u2192 LearnBuddy zuerst ein Kind und ein Fach an.",keine_faecher:"F\xFCr dieses Kind gibt es noch kein Fach.",tab_uebersicht:"\xDCbersicht",status_aktiv:"Abfragen aktiv",status_pausiert:"Abfragen pausiert",status_pausiert_bis:"Pausiert bis {zeit}",status_nichts_geplant:"Keine Abfrage geplant",pausieren:"Pausieren",fortsetzen:"Fortsetzen",offene_frage:"Offene Frage",offene_frage_text:"{fach}, gestellt um {von}, l\xE4uft bis {bis}",offene_frage_ohne_frist:"{fach}, gestellt um {von}, ohne Zeitlimit",offene_frage_angehalten:"{fach}, gestellt um {von}, Zeit angehalten (pausiert)",keine_offene_frage:"Keine offene Frage",naechste_abfrage:"N\xE4chste Abfrage",keine_geplant:"Keine geplant",nach_offener_frage:"Nach der offenen Frage",letzte_frage:"Letzte Frage",noch_nie:"Noch nie",jetzt_fragen_kurz:"Jetzt abfragen",egal_welches:"Egal welches Fach",frage_gesendet:"Die Frage wurde gesendet.",fragen_gesendet:"Die Abfrage wurde gestartet.",abfrage_titel:"Jetzt abfragen",abfrage_fach:"Fach",abfrage_lektionen:"Lektion",abfrage_aufgaben:"Welche Aufgaben",abfrage_themen:"{n} Themen",abfrage_einzeln:"{n} Einzelaufgaben",abfrage_seite_kurz:"S.",abfrage_ohne_lektion:"{n} Aufgaben ohne Lektion sind nur dabei, wenn alles angehakt ist.",abfrage_laeuft:"Laufende Abfrage",abfrage_laeuft_text:"{ort} \xB7 noch {n} weitere",abfrage_seiten:"S. {von}\u2013{bis}",abfrage_ab_seite:"ab S. {n}",abfrage_bis_seite:"bis S. {n}",abfrage_ab_fehlerquote:"Fehlerquote ab {n} %",abfrage_seite_von:"Buchseite von",abfrage_seite_bis:"Buchseite bis",abfrage_fehlerquote:"Fehlerquote mindestens (%)",abfrage_filter_hinweis:"Ohne Auswahl wird das ganze Fach abgefragt. Mit Fehlerquote z\xE4hlen nur schon beantwortete Aufgaben. Ungepr\xFCfte Aufgaben werden nie abgefragt.",abfrage_anzahl:"Anzahl der Aufgaben (1 bis 100)",abfrage_frist:"Ablaufzeit je Frage (Minuten)",abfrage_frist_hinweis:"Leer = allgemeine Einstellung, 0 = l\xE4uft nie ab. Gilt nur f\xFCr diese Abfrage.",abfrage_umfang:"Zur Auswahl stehen {n} Aufgaben. Sie kommen nacheinander, die n\xE4chste nach jeder Antwort.",abfrage_umfang_laedt:"Die Auswahl wird gez\xE4hlt \u2026",err_seiten_verdreht:"Die erste Buchseite liegt hinter der letzten.",abfrage_senden:"Abfrage starten",kz_gefragt:"Gestellte Fragen",kz_richtig:"Richtig",kz_falsch:"Falsch",kz_unbeantwortet:"Unbeantwortet",ki_keine:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt.",ki_nicht_verfuegbar:"Die gew\xE4hlte KI-Entit\xE4t ist gerade nicht verf\xFCgbar.",ki_ohne_bilder:"Die gew\xE4hlte KI-Entit\xE4t kann keine Bilder lesen.",ki_hinweis_keine:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt. Aufgaben erzeugen, Rechenwege schreiben und der Import aus Fotos sind deshalb ausgeschaltet; Antworten werden nur lokal bewertet. Einrichten unter Einstellungen \u2192 Ger\xE4te & Dienste \u2192 LearnBuddy \u2192 Zahnrad.",ki_hinweis_ohne_bilder:"Die gew\xE4hlte KI-Entit\xE4t kann keine Bilder lesen. Funktionen mit Fotos sind deshalb ausgeschaltet.",ki_hinweis_nicht_verfuegbar:"Die gew\xE4hlte KI-Entit\xE4t ist gerade nicht verf\xFCgbar. Die KI-Funktionen sind ausgeschaltet und Antworten werden nur lokal bewertet. Pr\xFCfe die KI-Integration in Home Assistant.",ki_hinweis_sach_zusatz:" Kurzantworten werden so lange nicht gestellt, nur Auswahlfragen.",err_ki_nicht_verfuegbar:"Die gew\xE4hlte KI-Entit\xE4t ist gerade nicht verf\xFCgbar.",err_ki_nicht_erreichbar:"Die KI war nicht erreichbar oder hat den Auftrag abgelehnt (Verbindung, Konto, Guthaben). Bitte sp\xE4ter erneut versuchen.",neue_version:"LearnBuddy wurde aktualisiert. Diese Seite zeigt noch die alte Version; lade sie neu, damit alle Funktionen sichtbar sind.",neu_laden:"Seite neu laden",absender_unbekannt:"Eine Nachricht von einem unbekannten Absender ist eingegangen: {kennung} ({quelle}). Sie konnte keinem Kind zugeordnet werden.",absender_uebernehmen:"Als Absenderkennung f\xFCr {name} \xFCbernehmen",absender_verwerfen:"Verwerfen",absender_uebernommen:"Absenderkennung \xFCbernommen. Die n\xE4chste Antwort wird zugeordnet.",quelle_telegram:"Telegram",quelle_whatsapp:"WhatsApp",quelle_event:"eigenes Ereignis",err_absender_leer:"Die Absenderkennung ist leer.",err_absender_vergeben:"Diese Absenderkennung geh\xF6rt schon zu einem anderen Kind.",absender_fehlt:"Bei diesem Kind fehlt die Absenderkennung (Chat-ID oder Telefonnummer). Fragen gehen raus, aber Antworten k\xF6nnen nicht zugeordnet werden. Eintragen unter Einstellungen \u2192 Ger\xE4te & Dienste \u2192 LearnBuddy \u2192 Kind bearbeiten.",sim_plan:"Simulation einplanen (optional)",sim_plan_aktiv:"Zu einem festen Zeitpunkt automatisch eine Simulation schicken",sim_plan_hilfe:"Zum gew\xE4hlten Zeitpunkt bekommt das Kind automatisch eine Simulation dieser Arbeit per Messenger: das Aufgabenblatt als Bild, dann die Aufgaben nacheinander, am Ende die Auswertung. Ist das Kind dann pausiert oder l\xE4uft schon eine Simulation, entf\xE4llt sie.",sim_plan_um:"Datum und Uhrzeit",sim_plan_offen:"Simulation geplant f\xFCr {zeit} ({n} Aufgaben)",sim_plan_erledigt:"Geplante Simulation vom {zeit} ist erledigt",err_simulation_um_vergangen:"Der Zeitpunkt der Simulation liegt in der Vergangenheit.",err_simulation_um_ungueltig:"Bitte Datum und Uhrzeit der Simulation pr\xFCfen.",sim_knopf_arbeit:"Klassenarbeit simulieren",sim_knopf_hue:"H\xDC simulieren",sim_hilfe:"Aus den freigegebenen Aufgaben dieser Arbeit wird zuf\xE4llig ein Aufgabenblatt zusammengestellt. Die Lernstatistik bleibt davon unber\xFChrt.",sim_weg_ausdruck:"Per Ausdruck",sim_weg_ausdruck_hilfe:"Das Aufgabenblatt entsteht als Bild zum Herunterladen und Drucken. Es wird nichts verschickt.",sim_weg_messenger:"Per Messenger",sim_weg_messenger_hilfe:"{name} bekommt das Blatt als Bild und danach die Aufgaben nacheinander. R\xFCckmeldung gibt es erst am Ende: Punkte, Prozent und die L\xF6sungen zu den Fehlern.",sim_anzahl:"Anzahl der Aufgaben",sim_verfuegbar:"Auf diesem Weg verf\xFCgbar: {n}",sim_keine_aufgaben:"F\xFCr diese Arbeit gibt es keine freigegebenen Aufgaben.",sim_start_ausdruck:"Blatt erzeugen",sim_start_messenger:"Simulation starten",sim_gestartet:"Die Simulation mit {n} Aufgaben l\xE4uft. Die Auswertung geht am Ende ans Kind.",sim_blatt_hilfe:"Das Blatt mit {n} Aufgaben ist fertig. Die Bilder werden nach 24 Stunden gel\xF6scht; lade sie herunter, wenn du sie behalten willst.",sim_herunterladen:"Seite {n} herunterladen",sim_drucken:"Drucken",sim_druck_blockiert:"Der Browser hat das Druckfenster blockiert. Lade die Seiten herunter und drucke sie von dort.",sim_laeuft:"Simulation",sim_laeuft_text:"l\xE4uft: Aufgabe {nr} von {n}",sim_abbrechen:"Simulation abbrechen",frage_abbrechen:"Frage abbrechen",frage_abbrechen_frage:"Die offene Frage zur\xFCckziehen? Sie wird nicht gez\xE4hlt, und das Kind bekommt eine kurze Nachricht.",sim_abbrechen_frage:"Die laufende Simulation ohne Auswertung beenden?",err_simulation_laeuft:"F\xFCr dieses Kind l\xE4uft gerade eine Simulation.",err_weg_ungueltig:"Unbekannter Weg f\xFCr die Simulation.",foto_import:"Aus Foto importieren",foto_titel:"Aufgaben aus Fotos auslesen",beschriftung_neu:"Beschriftungsbild",beschriftung_titel:"Beschriftungen abfragen",beschriftung_hilfe:"Lade ein Bild mit Beschriftungen hoch (z. B. ein Mikroskop). LearnBuddy ersetzt die Beschriftungen durch Nummern und fragt das Kind je Nummer, was dort steht.",beschriftung_bild:"Bild mit Beschriftungen",beschriftung_suchen:"Beschriftungen von der KI suchen lassen",beschriftung_von_hand:"Von Hand markieren",beschriftung_nichts_gefunden:"Die KI hat keine Beschriftungen gefunden. Du kannst sie von Hand markieren.",beschriftung_editor_hilfe:"Ziehe einen Rahmen um jede Beschriftung, damit sie verdeckt wird. Rahmen lassen sich verschieben, am Punkt unten rechts vergr\xF6\xDFern und unten in der Liste l\xF6schen. Trage rechts den richtigen Text ein.",beschriftung_text:"Text zu Nummer {nr}",beschriftung_alternativen:"Weitere richtige Schreibweisen (mit | trennen) zu Nummer {nr}",beschriftung_text_fehlt:"Zu jeder Nummer fehlt noch der richtige Text.",beschriftung_pruefen:"Vorschau ansehen",beschriftung_vorschau:"So sieht das Kind das Bild",beschriftung_vorschau_hilfe:"Die Beschriftungen sind durch Nummern ersetzt. Passt alles, dann speichere die Aufgaben, sonst gehe zur\xFCck und korrigiere die Rahmen.",beschriftung_speichern:"{n} Aufgaben anlegen",beschriftung_aktualisieren:"\xC4nderungen speichern",beschriftung_bearbeiten:"Beschriftungen bearbeiten",beschriftung_fertig:"Beschriftungen gespeichert: {neu} neu, {geaendert} ge\xE4ndert, {entfernt} entfernt.",zurueck:"Zur\xFCck",form_beschriftung:"Beschriftung",err_beschriftung_nur_sachfach:"Beschriftungsbilder gibt es nur f\xFCr Sachf\xE4cher.",err_beschriftung_felder_ungueltig:"Die Rahmen sind ung\xFCltig. Jede Nummer braucht einen Rahmen mit sichtbarer Gr\xF6\xDFe.",foto_hilfe:"Fotografiere die Vokabelseiten m\xF6glichst gerade und gut lesbar. Die KI liest Wort, \xDCbersetzung, Seitenzahl und den Verweis auf die Unit-Seite aus. Beispiels\xE4tze und Lautschrift l\xE4sst sie weg. Danach pr\xFCfst du die Vorschau. Die Fotos gehen an den KI-Dienst und werden anschlie\xDFend gel\xF6scht.",foto_hilfe_mathe:"Fotografiere Buchseite oder Arbeitsblatt m\xF6glichst gerade und gut lesbar. Die KI liest die Aufgaben aus und l\xF6st sie; die L\xF6sungen werden nachgerechnet. Danach pr\xFCfst du die Vorschau. Die Fotos gehen an den KI-Dienst und werden anschlie\xDFend gel\xF6scht.",foto_auslesen:"Auslesen",foto_leer:"Auf den Fotos wurde nichts Verwertbares gefunden.",foto_vorschau_titel:"Vorschau pr\xFCfen",foto_vorschau_hilfe:"Vergleiche die Zeilen mit dem Buch, korrigiere sie bei Bedarf und entferne das H\xE4kchen bei allem, was nicht \xFCbernommen werden soll. Gespeichert wird erst mit \u201E\xDCbernehmen\u201C.",foto_vorhanden:"schon vorhanden",foto_braucht_bild:"braucht eine Abbildung \u2013 als \u201EAufgabe mit Bild\u201C anlegen",foto_unbestaetigt:"L\xF6sung nicht best\xE4tigt",foto_uebernehmen:"{n} \xFCbernehmen",foto_fertig:"{n} \xFCbernommen, {doppelt} schon vorhanden, {fehler} fehlerhaft.",foto_fehler:"{n} Zeilen sind fehlerhaft (leere oder zu lange Felder). Bitte korrigieren.",err_foto_sachfach:"F\xFCr Sachf\xE4cher gibt es \u201EFragen aus Buchseite\u201C.",kz_teilweise:"Teilweise richtig",neue_frage:"Neue Frage",spalte_frage:"Frage",spalte_musterantwort:"Musterantwort",spalte_satz:"Satz",spalte_satz_loesung:"L\xF6sung",richtige_antwort:"Richtige Antwort",form:"Frageform",form_kurz:"Kurzantwort",form_auswahl:"Auswahl",form_gemischt:"Gemischt",form_luecke:"L\xFCckentext",hilfe_label:"\xDCbersetzung als Hilfe ({sprache})",hilfe_senden:"\xDCbersetzung mitsenden",hilfe_senden_kurz:"\xDCbersetzung mitsenden",hilfe_alle_an:"\xDCbersetzung mitsenden",hilfe_alle_aus:"Ohne \xDCbersetzung senden",hilfe_gesetzt:"{n} Aufgaben ge\xE4ndert.",err_hilfe_senden_ungueltig:"Ung\xFCltige Angabe.",err_hilfe_ungueltig:"Die \xDCbersetzung ist zu lang.",form_uebersetzung:"\xDCbersetzung",saetze_erzeugen:"S\xE4tze erzeugen",saetze_hilfe:"Die KI schreibt kurze S\xE4tze f\xFCr das Thema. Beschreibe, was ge\xFCbt werden soll, und/oder lade Fotos von Buchseiten hoch (die KI \xFCbernimmt die \xDCbungen oder erfindet \xE4hnliche). Die Aufgaben warten danach auf deine Freigabe.",saetze_fotos:"Fotos von Buchseiten (optional, bis zu {n})",saetze_beschreibung:"Beschreibung und W\xFCnsche",saetze_beschreibung_hilfe:"z. B. Personalpronomen in kurzen S\xE4tzen",saetze_uebernehmen:"\xDCbungen von der Seite \xFCbernehmen",saetze_aehnliche:"\xC4hnliche neue Aufgaben erfinden",saetze_laeuft:"Die KI schreibt die S\xE4tze. Das kann eine Minute dauern \u2026",saetze_start:"Erzeugen",saetze_fertig:"{erzeugt} Aufgaben erzeugt, {verworfen} unbrauchbar, {doppelt} doppelt. Sie warten auf deine Freigabe.",err_saetze_nur_satzbereich:"Das geht nur in einem Thema f\xFCr S\xE4tze.",bereich_art:"Art der Aufgaben",bereich_art_vokabel:"Vokabeln (Wortpaare)",bereich_art_satz:"S\xE4tze (L\xFCckentext, Auswahl, Kurzantwort)",err_import_satz:"In ein Satz-Thema l\xE4sst sich nur per JSON-Import oder von Hand eintragen.",err_foto_satz:"Das Foto-Import kennt nur Vokabeln.",kernpunkte:"Kernpunkte (einer je Zeile, optional): was eine vollst\xE4ndige Antwort enth\xE4lt",falsche_optionen:"Falsche Antworten (eine je Zeile, 2 bis 3)",belegstelle:"Belegstelle",quellseite_anzeigen:"Buchseite anzeigen",sach_ohne_ki:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt. Deshalb werden nur Auswahlfragen gestellt; Kurzantworten kann nur die KI bewerten.",seiten:"Fragen aus Buchseite",seiten_titel:"Fragen aus Buchseiten erzeugen",seiten_hilfe:"Fotografiere die Seiten m\xF6glichst gerade und gut lesbar. Die KI liest sie und schl\xE4gt Fragen mit Musterantwort vor. Die Fragen warten danach auf deine Freigabe. Die Fotos gehen an den KI-Dienst.",seiten_waehlen:"Fotos der Seiten (bis zu {n})",seiten_zu_viele:"Es werden nur die ersten {n} Fotos verwendet.",seiten_anzahl:"Anzahl Fragen",seiten_schwerpunkt:"Schwerpunkt (optional)",seiten_schwerpunkt_hilfe:"z. B. nur der Abschnitt \xFCber die Zellatmung",seiten_start:"Fragen erzeugen",seiten_laeuft:"Die KI liest die Seiten. Das kann eine Minute dauern \u2026",seiten_fertig:"{erzeugt} Fragen erzeugt, {verworfen} unbrauchbar, {doppelt} doppelt. Bitte pr\xFCfen und freigeben.",err_sach_frage_ungueltig:"Bitte eine Frage eingeben (h\xF6chstens 500 Zeichen).",err_sach_antwort_ungueltig:"Bitte eine Antwort eingeben (h\xF6chstens 500 Zeichen).",err_form_ungueltig:"Unbekannte Frageform.",err_kernpunkte_ungueltig:"H\xF6chstens 6 Kernpunkte mit je 200 Zeichen.",err_falsche_optionen_ungueltig:"Eine Auswahlfrage braucht 2 bis 3 falsche Antworten, die sich untereinander und von der richtigen unterscheiden.",err_stelle_ungueltig:"Die Belegstelle darf h\xF6chstens 300 Zeichen lang sein.",err_import_sachfach:"In Sachf\xE4cher lassen sich keine Listen importieren.",err_seiten_nur_sachfach:"Fragen aus Buchseiten gibt es nur f\xFCr Sachf\xE4cher.",err_seiten_ungueltig:"Bitte 1 bis 4 Fotos w\xE4hlen.",err_ki_ohne_bilder:"Die gew\xE4hlte KI-Entit\xE4t kann keine Bilder lesen.",kz_trefferquote:"Trefferquote",kz_aufgaben:"Aufgaben",fortschritt:"Fortschritt",fortschritt_zeitraum:"Zeitraum",fortschritt_tage:"{n} Tage",fortschritt_seit:"Der Verlauf wird seit dem {datum} aufgezeichnet.",fortschritt_leer:"Noch nichts aufgezeichnet. Sobald Fragen gestellt und beantwortet werden, erscheint hier der Verlauf.",fortschritt_antworten:"Antworten je Tag",fortschritt_quote:"Trefferquote",fortschritt_quote_hilfe:"\xDCber die jeweils letzten 7 Tage gerechnet.",fortschritt_lernstand:"Lernstand je Fach",fortschritt_lernstand_hilfe:"Anteil der Karten ab Box 3.",fortschritt_schwach:"Schwachstellen",fortschritt_lektionen:"Lektionen mit den meisten Fehlern",fortschritt_aufgaben:"Aufgaben mit den meisten Fehlern",fortschritt_keine_schwach:"Keine auff\xE4lligen Lektionen oder Aufgaben im Zeitraum.",fortschritt_simulationen:"Simulationen",fortschritt_keine_sim:"Keine Simulation im Zeitraum.",fortschritt_tabelle:"Als Tabelle",fortschritt_diagramm:"Als Diagramm",fortschritt_keine_daten:"Keine Antworten im Zeitraum.",reihe_tag:"Tag",reihe_gefragt:"Gestellt",reihe_richtig:"Richtig",reihe_teilweise:"Teilweise",reihe_falsch:"Falsch",reihe_unbeantwortet:"Unbeantwortet",fehler_n:"{n}\xD7 falsch",fehlerquote_n:"{n} % falsch ({f} von {g})",sim_punkte:"{p} von {m} Punkten ({proz} %)",sim_unvollstaendig:"Zeit abgelaufen",wochenreport:"Wochenreport",report_woche:"Woche vom {von} bis {bis}",report_laufend:"laufende Woche",report_frueher:"Vorige Woche",report_spaeter:"N\xE4chste Woche",report_kennzahlen:"Kennzahlen der Woche",report_tage_aktiv:"Tage mit Antworten",report_vergleich:"Vergleich zur Vorwoche",report_antworten:"Antworten",report_vorwoche:"Vorwoche: {wert}",report_lernstand:"Lernstand {fach}",report_keine_vorwoche:"keine Daten",report_schwach:"Schwachstellen",report_anstehend:"Anstehende Arbeiten (n\xE4chste 14 Tage)",report_keine_arbeiten:"Keine Arbeit in den n\xE4chsten 14 Tagen.",report_in_tagen:"in {n} Tagen",report_heute:"heute",report_morgen:"morgen",report_sicher:"{n} % sicher",report_vorschlaege:"Noch nicht eingetragen (aus dem Kalender)",report_simulationen:"Simulationen",report_loesung:"L\xF6sung: {loesung}",report_drucken:"Drucken",report_kopieren:"Als Text kopieren",report_kopiert:"In die Zwischenablage kopiert.",report_kopieren_fehler:"Kopieren wurde vom Browser nicht erlaubt.",report_druck_blockiert:"Der Browser hat das Druckfenster blockiert.",err_verlauf_aus:"Der Verlauf ist in den Optionen ausgeschaltet.",err_wochenreport_aus:"Der Wochenreport ist in den Optionen ausgeschaltet.",err_zeitraum_ungueltig:"Dieser Zeitraum ist nicht m\xF6glich.",anstehend:"Anstehende Arbeiten und H\xDCs",vorschlaege:"Vorschl\xE4ge aus dem Kalender",vorschlag_eintragen:"Eintragen",vorschlag_ignorieren:"Ignorieren",vorschlag_gleicher_tag:"Am selben Tag gibt es schon: {arbeiten}",keine_vorschlaege:"Keine neuen Termine im Kalender.",kalender_pruefen:"Jetzt pr\xFCfen",kalender_geprueft:"Zuletzt gepr\xFCft: {zeit}",kalender_nie:"Der Kalender wurde noch nicht gelesen.",kalender_fehler:"Der Kalender konnte zuletzt nicht gelesen werden. Angezeigt wird der Stand davor.",kalender_ignorierte:"{n} ignorierte wieder anzeigen",arbeit_fach:"Fach",arbeit_fach_waehlen:"\u2013 bitte w\xE4hlen \u2013",arbeit_fehlt_fach:"Zum Speichern fehlt noch das Fach.",fach_neu:"Neues Fach",fach_neu_titel:"Neues Fach anlegen",fach_neu_art:"Art des Fachs",fach_neu_sprache:"Sprache",fach_neu_name:"Name",fach_neu_name_optional:"Name (leer: wie die Sprache bzw. \u201EMathe\u201C)",fach_neu_anlegen:"Fach anlegen",fach_neu_fehlt:"F\xFCr dieses Kind gibt es noch kein Fach. Lege zuerst eines an.",fachart_fremdsprache:"Fremdsprache",err_kalender_aus:"F\xFCr dieses Kind ist kein Pr\xFCfungskalender eingeschaltet.",err_termin_unbekannt:"Der Termin steht nicht mehr im Kalender.",err_sprache_ungueltig:"Bitte eine Fremdsprache w\xE4hlen, die nicht die Muttersprache ist.",err_fachart_ungueltig:"Bitte die Art des Fachs w\xE4hlen.",err_fach_vorhanden:"Ein Fach mit diesem Namen gibt es schon.",err_name_leer:"Bitte einen Namen eingeben.",keine_anstehend:"Keine Arbeit oder H\xDC geplant.",heute:"heute",morgen:"morgen",in_tagen:"in {n} Tagen",heute_abfragen:"heute {n} Abfragen",sicher:"{n} % sicher",sicher_hinweis:"Anteil der Karten in Box 3 bis 5",faecher_titel:"F\xE4cher",fach_aufgaben:"{n} Aufgaben in {l} Lektionen",ungeprueft:"{n} ungepr\xFCft",aufgaben_oeffnen:"Aufgaben",lernstand:"Lernstand",lernstand_hinweis:"Karten je Leitner-Box: Box 1 ist neu oder zuletzt falsch, Box 5 sitzt sicher.",box:"Box {n}",karten:"{n} Karten",keine_karten:"Noch keine Aufgaben vorhanden.",schwierig:"Schwierigste Vokabeln",keine_schwierig:"Noch keine falschen Antworten.",fehler_mal:"{n} \xD7 falsch",arbeiten_oeffnen:"Arbeiten verwalten",tab_aufgaben:"Aufgaben",tab_arbeiten:"Arbeiten",laden:"Lade \u2026",neue_aufgabe:"Neue Aufgabe",importieren:"Importieren",lektion_hinzufuegen:"Lektion hinzuf\xFCgen",lektion_titel:"Lektionen",lektion_hilfe:"Lektionen werden hier angelegt und stehen danach beim Anlegen, Importieren und in Arbeiten zur Auswahl.",lektion_name:"Name der Lektion",lektion_keine:"Noch keine Lektion angelegt.",lektion_anzahl:"{n} Aufgaben",lektion_loeschen_hinweis:"Nur leere Lektionen lassen sich l\xF6schen",lektion_angelegt:"\u201E{name}\u201C angelegt.",keine_lektion:"\u2013 keine \u2013",export_json:"JSON exportieren",import_json:"JSON importieren",ausgewaehlt:"{n} ausgew\xE4hlt",loeschen:"L\xF6schen",arbeit_aus_auswahl:"Arbeit aus Auswahl",filter_suche:"Suche",filter_lektion:"Lektion",filter_quelle:"Quelle",filter_geprueft:"Gepr\xFCft",filter_fehlerquote:"Fehlerquote ab %",filter_von:"Erstellt ab",filter_bis:"Erstellt bis",filter_seite_von:"Buchseite von",filter_seite_bis:"Buchseite bis",filter_zuruecksetzen:"Filter zur\xFCcksetzen",alle:"Alle",ohne_lektion:"Ohne Lektion",ja:"Ja",nein:"Nein",quelle_manuell:"Manuell",quelle_upload:"Upload",quelle_generiert:"Generiert",spalte_alternativen:"Alternativen",spalte_hinweis:"Hinweis",aufgabenart_titel:"Was f\xFCr eine Aufgabe?",aufgabenart_rechnen:"Rechenaufgabe",aufgabenart_rechnen_hilfe:"Nur Text, zum Beispiel 3/4 + 1/8 oder eine Textaufgabe.",aufgabenart_bild:"Aufgabe mit Bild",aufgabenart_bild_hilfe:"Ein Diagramm, eine Kurve oder eine Zeichnung ist die Grundlage. Das Bild wird mit der Aufgabe verschickt.",bildaufgabe_titel:"Aufgabe mit Bild",bild:"Bild",bild_waehlen:"Bild ausw\xE4hlen",bild_hilfe:"PNG, JPEG, WebP oder GIF, h\xF6chstens 10 MB. Das Bild wird verkleinert gespeichert, Zusatzdaten wie der Aufnahmeort werden entfernt.",bild_vorschau:"Vorschau des Bildes",bild_anzeigen:"Bild anzeigen",einleitung:"Einleitung (optional)",einleitung_hilfe:"Steht vor jeder Teilaufgabe, z. B. \u201EIn anderen L\xE4ndern sind die Schulferien \u2026\u201C",teilaufgaben:"Teilaufgaben",teilaufgaben_hilfe:"Jede Zeile wird eine eigene Aufgabe mit demselben Bild und wird einzeln abgefragt.",teilaufgabe:"Teilaufgabe {n}",teilaufgabe_hinzufuegen:"Teilaufgabe hinzuf\xFCgen",teilaufgabe_entfernen:"Teilaufgabe entfernen",bildaufgaben_gespeichert:"Aufgaben mit Bild angelegt: {n}",bild_fehlt:"Bitte ein Bild ausw\xE4hlen.",teil_fehlt:"Bitte mindestens eine Teilaufgabe mit L\xF6sung eintragen.",keine_bilder:"{name} kann im Moment keine Bilder empfangen. Aufgaben mit Bild werden deshalb nicht gestellt. Bilder gehen automatisch \xFCber Telegram; f\xFCr andere Messenger tr\xE4gst du beim Kind eine \u201EAktion f\xFCr Bilder\u201C ein.",export_ohne_bild:"Exportiert. Aufgaben mit Bild sind nicht enthalten: {n}",spalte_aufgabe:"Aufgabe",spalte_loesung:"L\xF6sung",spalte_schwierigkeit:"Stufe",schwierigkeit:"Schwierigkeit",schwierigkeit_hinweis:"1 = leicht, 5 = schwer",schwierigkeit_beliebig:"beliebig",rechenweg:"Rechenweg (ein Schritt je Zeile, optional)",rechenweg_vorhanden:"Rechenweg hinterlegt",verifikation_rechnerisch:"nachgerechnet",verifikation_ki:"von der KI gegengepr\xFCft",verifikation_manuell:"selbst nachgerechnet",selbst_nachgerechnet:"Selbst nachgerechnet",selbst_nachgerechnet_hinweis:"Markiert die L\xF6sungen der Auswahl als von dir gepr\xFCft. Ein abweichender Vorschlag wird verworfen.",selbst_nachgerechnet_fertig:"Als selbst nachgerechnet markiert: {n}",verifikation_abweichung:"L\xF6sung weicht ab",nachrechnen:"Auswahl nachrechnen",nachrechnen_laeuft:"Die Aufgaben werden nachgerechnet \u2026",nachgerechnet:"{bestaetigt} best\xE4tigt, {abweichend} abweichend, {offen} nicht pr\xFCfbar.",nachrechnen_titel:"Ergebnis des Nachrechnens",nachrechnen_zusammenfassung:"{bestaetigt} L\xF6sungen wurden best\xE4tigt, {offen} Aufgaben lie\xDFen sich nicht pr\xFCfen. Bei diesen Aufgaben kommt ein anderes Ergebnis heraus. Ge\xE4ndert wurde nichts. Du kannst den gefundenen Wert je Aufgabe \xFCbernehmen oder die Aufgabe sp\xE4ter in der Tabelle bearbeiten. Ein Ergebnis der KI kann auch selbst falsch sein oder die Aufgabe ist mehrdeutig gestellt.",nachrechnen_eingetragen:"eingetragen",nachrechnen_berechnet:"berechnet",nachrechnen_ki:"die KI kommt auf",nur_abweichende:"Diese Aufgaben anzeigen",rechenweg_erzeugen:"Rechenweg erzeugen",rechenweg_erzeugen_laeuft:"Die KI schreibt die Rechenwege \u2026",rechenwege_erzeugt:"Rechenwege erzeugt: {erzeugt}. Schon vorhanden: {vorhanden}. \xDCbersprungen, weil die L\xF6sung abweicht: {abweichend}. Fehlgeschlagen: {fehlgeschlagen}.",vorschlag:"Vorschlag",vorschlag_ki:"Vorschlag der KI",uebernehmen_loesung:"\xDCbernehmen",uebernehmen_titel:"Ersetzt die eingetragene L\xF6sung durch diesen Wert. Der gespeicherte Rechenweg und die bisherige Statistik der Aufgabe werden dabei gel\xF6scht.",alle_uebernehmen:"Alle \xFCbernehmen",alle_uebernehmen_frage:"{n} L\xF6sungen ersetzen? {ki} davon stammen von der KI und k\xF6nnen selbst falsch sein.",uebernommen:"L\xF6sungen \xFCbernommen: {n}",schliessen:"Schlie\xDFen",fachart_mathe:"Mathematik",fachart_sach:"Sachfach",generieren:"Aufgaben generieren",generieren_titel:"Aufgaben von der KI erzeugen lassen",generieren_hilfe:"Die KI erzeugt Aufgaben, die den vorhandenen \xE4hneln. Gespeichert werden nur Aufgaben, deren L\xF6sung nachgerechnet oder gegengepr\xFCft werden konnte. Sie warten danach auf deine Freigabe. Der Name des Kindes wird nicht \xFCbertragen.",generieren_beispiele_auswahl:"Als Beispiele dienen die {n} markierten Aufgaben.",generieren_beispiele_thema:"Als Beispiele dienen die Aufgaben der gew\xE4hlten Lektion.",generieren_anzahl:"Anzahl (1\u201320)",generieren_beschreibung:"Beschreibung (optional)",generieren_beschreibung_hilfe:"z. B. Br\xFCche mit gleichem Nenner addieren",generieren_start:"Erzeugen",generieren_laeuft:"Die KI arbeitet, das kann bis zu zwei Minuten dauern \u2026",generieren_ohne_ki:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt (Einstellungen der Integration).",generiert:"{erzeugt} erzeugt, {verworfen} verworfen, {doppelt} doppelt.",freigeben:"Auswahl freigeben",freigegeben:"{n} Aufgaben freigegeben.",import_titel_mathe:"Aufgaben importieren",import_hilfe_mathe:"Eine Aufgabe pro Zeile: Aufgabe; L\xF6sung; optionaler Hinweis. Weitere g\xFCltige Schreibweisen der L\xF6sung mit | trennen.",schwierig_aufgaben:"Schwierigste Aufgaben",spalte_seite:"Seite",spalte_lektion:"Lektion",spalte_box:"Box",spalte_fehler:"Fehler",spalte_geprueft:"Gepr\xFCft",spalte_erstellt:"Erstellt",box_hinweis:"Leitner-Box je Abfragerichtung (1 = neu oder falsch, 5 = sicher)",alternativen_hinweis:"Mehrere mit | trennen",keine_aufgaben:"Keine Aufgaben vorhanden.",keine_treffer:"Keine Aufgabe passt zu den Filtern.",anzahl:"{n} von {gesamt} Aufgaben",bearbeiten:"Bearbeiten",speichern:"Speichern",abbrechen:"Abbrechen",alle_auswaehlen:"Alle sichtbaren ausw\xE4hlen",loeschen_frage:"{n} Aufgabe(n) wirklich l\xF6schen?",loeschen_warnung:"{n} der ausgew\xE4hlten Aufgaben geh\xF6ren zu anstehenden Arbeiten: {arbeiten}. Trotzdem l\xF6schen?",geloescht:"{n} Aufgabe(n) gel\xF6scht.",geloescht_arbeit:"Arbeit gel\xF6scht.",gespeichert:"Gespeichert.",import_titel:"Vokabeln importieren",import_hilfe:"Eine Vokabel pro Zeile: {a}; {b}; optionaler Hinweis. Alternativen mit | trennen.",import_inhalt:"Inhalt",import_trennzeichen:"Trennzeichen (leer = automatisch)",import_geprueft:"Als gepr\xFCft \xFCbernehmen",vorschau:"Vorschau",uebernehmen:"\xDCbernehmen",vorschau_neu:"neu",vorschau_vorhanden:"bereits vorhanden",vorschau_fehler:"Nicht lesbare Zeilen: {zeilen}",import_ergebnis:"{n} importiert, {u} \xFCbersprungen.",import_fehler:"{n} fehlerhafte Eintr\xE4ge.",export_titel:"Aufgaben exportieren",mit_statistik:"Lernstatistik einschlie\xDFen",herunterladen:"Herunterladen",import_json_titel:"JSON importieren",import_json_hilfe:"Vorhandene Aufgaben bleiben erhalten, gleiche Vokabeln werden \xFCbersprungen.",datei_ungueltig:"Die Datei enth\xE4lt kein g\xFCltiges JSON.",import_json_lektion:"Lektion der importierten Aufgaben",import_json_aus_datei:"Lektionen aus der Datei \xFCbernehmen",import_json_lektion_hilfe:"Mit einer gew\xE4hlten Lektion landen alle importierten Aufgaben dort, egal was in der Datei steht.",neue_arbeit:"Neue Arbeit / H\xDC",keine_arbeiten:"F\xFCr dieses Fach ist keine Arbeit angelegt.",art:"Art",art_arbeit:"Klassenarbeit",art_hue:"H\xDC",datum:"Datum",thema:"Titel",abfragen_pro_tag:"Abfragen pro Tag",start_tage_vorher:"Beginn (Tage vorher)",intensivierung:"Frequenz zum Termin hin steigern",antwortfrist:"Antwortfrist (Minuten)",antwortfrist_leer:"wie allgemein eingestellt",antwortfrist_hinweis:"Leer: Es gilt die allgemeine Einstellung. Bei mehreren laufenden Arbeiten gilt die k\xFCrzeste Frist.",aufgaben_der_arbeit:"Aufgaben der Arbeit",auswahl_alle:"Alle Aufgaben des Fachs",auswahl_gezielt:"Gezielte Auswahl",schnell_lektionen:"Ganze Lektionen",schnell_bereiche:"Ganze Themen",bereich:"Thema",bereiche_verwalten:"Themen verwalten",faecher_verwalten:"F\xE4cher verwalten",faecher_hilfe:"Hier siehst du die F\xE4cher des Kindes und legst neue an.",faecher_einstellungen:"Name, KI und L\xF6schen eines Fachs in den Einstellungen von Home Assistant",fach_angelegt:"Fach angelegt.",themen_titel:"Themen",aufgabenverwaltung:"Aufgabenverwaltung",import_aus_text:"Aus Text importieren",bereiche_titel:"Themen",bereiche_hilfe:"Themen sind Reiter eines Fachs, z. B. \u201EVokabeln\u201C und \u201EPersonalpronomen\u201C. Neue Aufgaben, Importe und Fotos landen im gew\xE4hlten Thema.",bereich_name:"Name des neuen Themas",bereich_angelegt:"\u201E{name}\u201C angelegt.",bereich_standard_vokabel:"Vokabeln",bereich_standard_mathe:"Aufgaben",bereich_standard_sach:"Fragen",bereich_standard_satz:"S\xE4tze",bereich_standard_hinweis:"Das erste Thema bleibt immer bestehen",bereich_loeschen_hinweis:"Nur leere Themen lassen sich l\xF6schen",verschieben_nach:"Verschieben nach \u2026",verschoben:"{n} Aufgaben verschoben.",umbenennen:"Umbenennen",err_bereich_leer:"Bitte einen Namen eingeben.",err_bereich_ungueltig:"Der Name ist zu lang.",err_bereich_zu_viele:"Mehr Themen sind nicht m\xF6glich.",err_bereich_vorhanden:"Dieses Thema gibt es schon.",err_bereich_art_ungueltig:"Diese Aufgabenart ist hier nicht m\xF6glich.",err_bereich_unbekannt:"Dieses Thema gibt es nicht.",err_bereich_standard:"Das erste Thema l\xE4sst sich nicht l\xF6schen.",err_bereich_verwendet:"Das Thema enth\xE4lt noch Aufgaben.",arbeit_fehlt_beides:"Zum Speichern fehlen noch Titel und Datum.",arbeit_fehlt_thema:"Zum Speichern fehlt noch der Titel.",arbeit_fehlt_datum:"Zum Speichern fehlt noch das Datum.",schnell_seit:"Alle Aufgaben seit",schnell_seiten:"Alle Aufgaben von Buchseite",schnell_seiten_bis:"bis Buchseite",hinzufuegen:"Hinzuf\xFCgen",einzelne_aufgaben:"Einzelne Aufgaben",auswahl_leeren:"Auswahl leeren",arbeit_umfang:"{n} Aufgaben",arbeit_alle:"alle Aufgaben",arbeit_loeschen_frage:"Arbeit \u201E{thema}\u201C wirklich l\xF6schen?",arbeit_titel_neu:"Arbeit / H\xDC anlegen",arbeit_titel_bearbeiten:"Arbeit / H\xDC bearbeiten",vergangen:"vorbei",fehler_allgemein:"Das hat nicht geklappt: {fehler}",err_nicht_geladen:"LearnBuddy ist gerade nicht geladen.",err_fach_unbekannt:"Das Fach wurde nicht gefunden.",err_aufgabe_unbekannt:"Die Aufgabe wurde nicht gefunden.",err_arbeit_unbekannt:"Die Arbeit wurde nicht gefunden.",err_frage_ungueltig:"Bitte beide W\xF6rter ausf\xFCllen (h\xF6chstens 500 Zeichen).",err_alternativen_ungueltig:"Die Alternativen sind ung\xFCltig.",err_hinweis_ungueltig:"Der Hinweis ist zu lang.",err_aufgabe_ungueltig:"Bitte eine Aufgabe eingeben (h\xF6chstens 500 Zeichen).",err_loesung_ungueltig:"Bitte eine L\xF6sung eingeben (h\xF6chstens 100 Zeichen).",err_rechenweg_ungueltig:"Der Rechenweg darf h\xF6chstens 8 Schritte haben.",err_schwierigkeit_ungueltig:"Die Schwierigkeit muss zwischen 1 und 5 liegen.",err_anzahl_ungueltig:"Die Anzahl muss zwischen 1 und 20 liegen.",err_beschreibung_ungueltig:"Die Beschreibung ist zu lang.",err_ki_fehlt:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt.",err_ki_fehler:"Die KI hat keine brauchbaren Aufgaben geliefert. Bitte sp\xE4ter erneut versuchen.",err_generieren_nur_mathe:"Aufgaben lassen sich nur f\xFCr Mathe-F\xE4cher generieren.",err_generieren_ohne_vorgabe:"Bitte eine Lektion oder eine Beschreibung angeben oder zuerst Beispielaufgaben anlegen.",err_export_typ:"Die Datei geh\xF6rt zu einer anderen Art von Fach.",err_bild_ungueltig:"Das ist kein Bild in einem unterst\xFCtzten Format (PNG, JPEG, WebP, GIF).",err_bild_zu_gross:"Das Bild ist gr\xF6\xDFer als 10 MB.",err_bild_unbekannt:"Das Bild wurde nicht gefunden. Bitte erneut hochladen.",err_nachrechnen_nur_mathe:"Nachrechnen gibt es nur f\xFCr Mathe-F\xE4cher.",err_rechenweg_nur_mathe:"Rechenwege gibt es nur f\xFCr Mathe-F\xE4cher.",err_auswahl_ungueltig:"Bitte 1 bis 100 Aufgaben ausw\xE4hlen.",err_seite_ungueltig:"Die Seite muss eine Zahl zwischen 1 und 9999 sein.",err_lektion_ungueltig:"Der Name ist zu lang (h\xF6chstens 100 Zeichen).",err_lektion_leer:"Bitte einen Namen eingeben.",err_lektion_vorhanden:"Diese Lektion gibt es schon.",err_lektion_unbekannt:"Diese Lektion gibt es nicht. Bitte zuerst anlegen.",err_lektion_verwendet:"Die Lektion enth\xE4lt noch Aufgaben.",err_import_leer:"Der Inhalt enth\xE4lt keine g\xFCltige Zeile.",err_export_ungueltig:"Die Datei ist kein LearnBuddy-Export.",err_export_version:"Diese Export-Version wird nicht unterst\xFCtzt.",err_export_sprachen:"Die Sprachen des Exports passen nicht zu diesem Fach.",err_thema_leer:"Bitte einen Titel eingeben.",err_datum_vergangen:"Das Datum liegt in der Vergangenheit.",err_arbeit_ungueltig:"Bitte die Angaben zur Arbeit pr\xFCfen.",err_unauthorized:"Daf\xFCr sind Administratorrechte n\xF6tig.",err_kind_unbekannt:"Das Kind wurde nicht gefunden.",err_keine_aufgaben:"Es gibt keine gepr\xFCften Aufgaben, die abgefragt werden k\xF6nnten.",err_senden_fehlgeschlagen:"Die Nachricht konnte nicht zugestellt werden. Bitte das Messenger-Ziel des Kindes pr\xFCfen."},Ft={titel:"LearnBuddy",kind:"Child",fach:"Subject",keine_kinder:"No child has been added yet. Add a child and a subject under Settings \u2192 Devices & services \u2192 LearnBuddy first.",keine_faecher:"This child has no subject yet.",tab_uebersicht:"Overview",status_aktiv:"Questions enabled",status_pausiert:"Questions paused",status_pausiert_bis:"Paused until {zeit}",status_nichts_geplant:"No question scheduled",pausieren:"Pause",fortsetzen:"Resume",offene_frage:"Open question",offene_frage_text:"{fach}, asked at {von}, expires at {bis}",offene_frage_ohne_frist:"{fach}, asked at {von}, no time limit",offene_frage_angehalten:"{fach}, asked at {von}, clock stopped (paused)",keine_offene_frage:"No open question",naechste_abfrage:"Next question",keine_geplant:"None scheduled",nach_offener_frage:"After the open question",letzte_frage:"Last question",noch_nie:"Never",jetzt_fragen_kurz:"Ask now",egal_welches:"Any subject",frage_gesendet:"The question was sent.",fragen_gesendet:"The questions were started.",abfrage_titel:"Ask now",abfrage_fach:"Subject",abfrage_lektionen:"Lesson",abfrage_aufgaben:"Which tasks",abfrage_themen:"{n} topics",abfrage_einzeln:"{n} single tasks",abfrage_seite_kurz:"p.",abfrage_ohne_lektion:"{n} tasks without a lesson are only included if all lessons are selected.",abfrage_laeuft:"Running questions",abfrage_laeuft_text:"{ort} \xB7 {n} more to come",abfrage_seiten:"p. {von}\u2013{bis}",abfrage_ab_seite:"from p. {n}",abfrage_bis_seite:"up to p. {n}",abfrage_ab_fehlerquote:"error rate from {n} %",abfrage_seite_von:"Book page from",abfrage_seite_bis:"Book page to",abfrage_fehlerquote:"Error rate at least (%)",abfrage_filter_hinweis:"Without a selection the whole subject is asked. With an error rate only tasks that were answered before count. Tasks that wait for approval are never asked.",abfrage_anzahl:"Number of questions (1 to 100)",abfrage_frist:"Time to answer each question (minutes)",abfrage_frist_hinweis:"Empty = general setting, 0 = never expires. Applies to this request only.",abfrage_umfang:"{n} tasks are available. They come one after another, the next one after each answer.",abfrage_umfang_laedt:"Counting the selection \u2026",err_seiten_verdreht:"The first book page is behind the last one.",abfrage_senden:"Start asking",kz_gefragt:"Questions asked",kz_richtig:"Correct",kz_falsch:"Wrong",kz_unbeantwortet:"Unanswered",ki_keine:"No AI entity is selected for this subject.",ki_nicht_verfuegbar:"The selected AI entity is not available right now.",ki_ohne_bilder:"The selected AI entity cannot read images.",ki_hinweis_keine:"No AI entity is selected for this subject. Creating tasks, writing solution steps and the import from photos are switched off; answers are only judged locally. Set it up under Settings \u2192 Devices & services \u2192 LearnBuddy \u2192 gear.",ki_hinweis_ohne_bilder:"The selected AI entity cannot read images. Features that use photos are switched off.",ki_hinweis_nicht_verfuegbar:"The selected AI entity is not available right now. The AI features are switched off and answers are only judged locally. Check the AI integration in Home Assistant.",ki_hinweis_sach_zusatz:" Short answers are not asked meanwhile, only multiple-choice questions.",err_ki_nicht_verfuegbar:"The selected AI entity is not available right now.",err_ki_nicht_erreichbar:"The AI could not be reached or refused the request (connection, account, credit). Please try again later.",neue_version:"LearnBuddy was updated. This page still shows the old version; reload it to see all features.",neu_laden:"Reload the page",absender_unbekannt:"A message from an unknown sender arrived: {kennung} ({quelle}). It could not be assigned to a child.",absender_uebernehmen:"Use as sender ID for {name}",absender_verwerfen:"Dismiss",absender_uebernommen:"Sender ID saved. The next answer will be assigned.",quelle_telegram:"Telegram",quelle_whatsapp:"WhatsApp",quelle_event:"custom event",err_absender_leer:"The sender ID is empty.",err_absender_vergeben:"This sender ID already belongs to another child.",absender_fehlt:"This child has no sender ID (chat ID or phone number). Questions are sent, but answers cannot be assigned. Set it under Settings \u2192 Devices & services \u2192 LearnBuddy \u2192 edit the child.",sim_plan:"Plan a simulation (optional)",sim_plan_aktiv:"Send a simulation automatically at a fixed time",sim_plan_hilfe:"At the chosen time the child automatically gets a simulation of this exam in the messenger: the sheet as an image, then the tasks one after the other, the result at the end. If the child is paused or a simulation is already running then, it is skipped.",sim_plan_um:"Date and time",sim_plan_offen:"Simulation planned for {zeit} ({n} tasks)",sim_plan_erledigt:"The simulation planned for {zeit} is done",err_simulation_um_vergangen:"The time of the simulation is in the past.",err_simulation_um_ungueltig:"Please check date and time of the simulation.",sim_knopf_arbeit:"Simulate the exam",sim_knopf_hue:"Simulate the homework check",sim_hilfe:"A sheet is put together at random from the approved tasks of this exam. The learning statistics stay untouched.",sim_weg_ausdruck:"As a printout",sim_weg_ausdruck_hilfe:"The sheet is made as an image to download and print. Nothing is sent.",sim_weg_messenger:"In the messenger",sim_weg_messenger_hilfe:"{name} gets the sheet as an image and then the tasks one after the other. Feedback only comes at the end: points, percent and the solutions to the mistakes.",sim_anzahl:"Number of tasks",sim_verfuegbar:"Available this way: {n}",sim_keine_aufgaben:"There are no approved tasks for this exam.",sim_start_ausdruck:"Create the sheet",sim_start_messenger:"Start the simulation",sim_gestartet:"The simulation with {n} tasks is running. The child gets the result at the end.",sim_blatt_hilfe:"The sheet with {n} tasks is ready. The images are deleted after 24 hours; download them if you want to keep them.",sim_herunterladen:"Download page {n}",sim_drucken:"Print",sim_druck_blockiert:"The browser blocked the print window. Download the pages and print them from there.",sim_laeuft:"Simulation",sim_laeuft_text:"running: task {nr} of {n}",sim_abbrechen:"Stop the simulation",frage_abbrechen:"Cancel question",frage_abbrechen_frage:"Withdraw the open question? It is not counted, and the child gets a short message.",sim_abbrechen_frage:"Stop the running simulation without a result?",err_simulation_laeuft:"A simulation is running for this child.",err_weg_ungueltig:"Unknown way of simulating.",foto_import:"Import from photo",foto_titel:"Read tasks from photos",beschriftung_neu:"Labelled image",beschriftung_titel:"Ask for labels",beschriftung_hilfe:"Upload an image with labels (for example a microscope). LearnBuddy replaces the labels with numbers and asks the child what each number stands for.",beschriftung_bild:"Image with labels",beschriftung_suchen:"Let the AI find the labels",beschriftung_von_hand:"Mark by hand",beschriftung_nichts_gefunden:"The AI found no labels. You can mark them by hand.",beschriftung_editor_hilfe:"Draw a box around every label to cover it. Boxes can be moved, enlarged at the dot in the lower right corner and deleted in the list below. Enter the correct text next to its number.",beschriftung_text:"Text for number {nr}",beschriftung_alternativen:"Other correct spellings (separate with |) for number {nr}",beschriftung_text_fehlt:"Some numbers still need their correct text.",beschriftung_pruefen:"Show preview",beschriftung_vorschau:"What the child sees",beschriftung_vorschau_hilfe:"The labels are replaced by numbers. If everything fits, save the tasks, otherwise go back and correct the boxes.",beschriftung_speichern:"Create {n} tasks",beschriftung_aktualisieren:"Save changes",beschriftung_bearbeiten:"Edit labels",beschriftung_fertig:"Labels saved: {neu} new, {geaendert} changed, {entfernt} removed.",zurueck:"Back",form_beschriftung:"Label",err_beschriftung_nur_sachfach:"Labelled images only exist for knowledge subjects.",err_beschriftung_felder_ungueltig:"The boxes are invalid. Every number needs a box of visible size.",foto_hilfe:"Take the photos of the vocabulary pages straight and legible. The AI reads word, translation, page number and the reference to the unit page. It leaves out example sentences and phonetic transcriptions. Then you check the preview. The photos are sent to the AI service and deleted afterwards.",foto_hilfe_mathe:"Take the photo of the book page or worksheet straight and legible. The AI reads the tasks and solves them; the results are recalculated. Then you check the preview. The photos are sent to the AI service and deleted afterwards.",foto_auslesen:"Read",foto_leer:"Nothing usable was found on the photos.",foto_vorschau_titel:"Check the preview",foto_vorschau_hilfe:"Compare the lines with the book, correct them if needed and untick everything that should not be imported. Nothing is stored before you click the button.",foto_vorhanden:"already there",foto_braucht_bild:"needs a figure \u2013 create it as a task with an image",foto_unbestaetigt:"result not confirmed",foto_uebernehmen:"Import {n}",foto_fertig:"{n} imported, {doppelt} already there, {fehler} faulty.",foto_fehler:"{n} lines are faulty (empty or too long fields). Please correct them.",err_foto_sachfach:"Knowledge subjects have their own way to create questions from pages.",kz_teilweise:"Partly right",neue_frage:"New question",spalte_frage:"Question",spalte_musterantwort:"Model answer",spalte_satz:"Sentence",spalte_satz_loesung:"Solution",richtige_antwort:"Correct answer",form:"Form",form_kurz:"Short answer",form_auswahl:"Multiple choice",form_gemischt:"Mixed",form_luecke:"Gap text",hilfe_label:"Translation as a hint ({sprache})",hilfe_senden:"Send the translation",hilfe_senden_kurz:"Send the translation",hilfe_alle_an:"Send the translation",hilfe_alle_aus:"Send without translation",hilfe_gesetzt:"{n} tasks changed.",err_hilfe_senden_ungueltig:"Invalid value.",err_hilfe_ungueltig:"The translation is too long.",form_uebersetzung:"Translation",saetze_erzeugen:"Generate sentences",saetze_hilfe:"The AI writes short sentences for the topic. Describe what to practise and/or upload photos of book pages (the AI takes over the exercises or invents similar ones). The tasks then wait for your approval.",saetze_fotos:"Photos of book pages (optional, up to {n})",saetze_beschreibung:"Description and wishes",saetze_beschreibung_hilfe:"e.g. personal pronouns in short sentences",saetze_uebernehmen:"Take over the exercises of the page",saetze_aehnliche:"Invent similar new tasks",saetze_laeuft:"The AI is writing the sentences. This can take a minute \u2026",saetze_start:"Create",saetze_fertig:"{erzeugt} tasks created, {verworfen} unusable, {doppelt} duplicates. They wait for your approval.",err_saetze_nur_satzbereich:"This only works in a topic for sentences.",bereich_art:"Kind of tasks",bereich_art_vokabel:"Vocabulary (word pairs)",bereich_art_satz:"Sentences (gap, choice, short answer)",err_import_satz:"A sentence topic only takes tasks by JSON import or by hand.",err_foto_satz:"The photo import only knows vocabulary.",kernpunkte:"Key points (one per line, optional): what a complete answer contains",falsche_optionen:"Wrong answers (one per line, 2 to 3)",belegstelle:"Source passage",quellseite_anzeigen:"Show the book page",sach_ohne_ki:"No AI entity is selected for this subject. Therefore only multiple-choice questions are asked; short answers can only be judged by the AI.",seiten:"Questions from a book page",seiten_titel:"Create questions from book pages",seiten_hilfe:"Take the photos straight and legible. The AI reads the pages and suggests questions with a model answer. The questions then wait for your approval. The photos are sent to the AI service.",seiten_waehlen:"Photos of the pages (up to {n})",seiten_zu_viele:"Only the first {n} photos are used.",seiten_anzahl:"Number of questions",seiten_schwerpunkt:"Focus (optional)",seiten_schwerpunkt_hilfe:"e.g. only the part about cellular respiration",seiten_start:"Create questions",seiten_laeuft:"The AI is reading the pages. This can take a minute \u2026",seiten_fertig:"{erzeugt} questions created, {verworfen} unusable, {doppelt} duplicates. Please check and approve them.",err_sach_frage_ungueltig:"Please enter a question (at most 500 characters).",err_sach_antwort_ungueltig:"Please enter an answer (at most 500 characters).",err_form_ungueltig:"Unknown form of question.",err_kernpunkte_ungueltig:"At most 6 key points with 200 characters each.",err_falsche_optionen_ungueltig:"A multiple-choice question needs 2 to 3 wrong answers that differ from each other and from the correct one.",err_stelle_ungueltig:"The source passage may be 300 characters long at most.",err_import_sachfach:"Lists cannot be imported into knowledge subjects.",err_seiten_nur_sachfach:"Questions from book pages only exist for knowledge subjects.",err_seiten_ungueltig:"Please choose 1 to 4 photos.",err_ki_ohne_bilder:"The selected AI entity cannot read images.",kz_trefferquote:"Success rate",kz_aufgaben:"Tasks",fortschritt:"Progress",fortschritt_zeitraum:"Period",fortschritt_tage:"{n} days",fortschritt_seit:"The history is recorded since {datum}.",fortschritt_leer:"Nothing recorded yet. As soon as questions are asked and answered, the history shows up here.",fortschritt_antworten:"Answers per day",fortschritt_quote:"Hit rate",fortschritt_quote_hilfe:"Calculated over the last 7 days each.",fortschritt_lernstand:"Level per subject",fortschritt_lernstand_hilfe:"Share of cards in box 3 or higher.",fortschritt_schwach:"Weak spots",fortschritt_lektionen:"Lessons with the most mistakes",fortschritt_aufgaben:"Tasks with the most mistakes",fortschritt_keine_schwach:"No conspicuous lessons or tasks in the period.",fortschritt_simulationen:"Simulations",fortschritt_keine_sim:"No simulation in the period.",fortschritt_tabelle:"As a table",fortschritt_diagramm:"As a chart",fortschritt_keine_daten:"No answers in the period.",reihe_tag:"Day",reihe_gefragt:"Asked",reihe_richtig:"Right",reihe_teilweise:"Partly",reihe_falsch:"Wrong",reihe_unbeantwortet:"Unanswered",fehler_n:"{n}\xD7 wrong",fehlerquote_n:"{n} % wrong ({f} of {g})",sim_punkte:"{p} of {m} points ({proz} %)",sim_unvollstaendig:"time ran out",wochenreport:"Weekly report",report_woche:"Week from {von} to {bis}",report_laufend:"running week",report_frueher:"Previous week",report_spaeter:"Next week",report_kennzahlen:"Figures of the week",report_tage_aktiv:"Days with answers",report_vergleich:"Compared to the week before",report_antworten:"Answers",report_vorwoche:"week before: {wert}",report_lernstand:"Level {fach}",report_keine_vorwoche:"no data",report_schwach:"Weak spots",report_anstehend:"Upcoming exams (next 14 days)",report_keine_arbeiten:"No exam in the next 14 days.",report_in_tagen:"in {n} days",report_heute:"today",report_morgen:"tomorrow",report_sicher:"{n} % safe",report_vorschlaege:"Not entered yet (from the calendar)",report_simulationen:"Simulations",report_loesung:"Solution: {loesung}",report_drucken:"Print",report_kopieren:"Copy as text",report_kopiert:"Copied to the clipboard.",report_kopieren_fehler:"The browser did not allow copying.",report_druck_blockiert:"The browser blocked the print window.",err_verlauf_aus:"The history is switched off in the options.",err_wochenreport_aus:"The weekly report is switched off in the options.",err_zeitraum_ungueltig:"This period is not possible.",anstehend:"Upcoming exams",vorschlaege:"Suggestions from the calendar",vorschlag_eintragen:"Enter",vorschlag_ignorieren:"Ignore",vorschlag_gleicher_tag:"Already on the same day: {arbeiten}",keine_vorschlaege:"No new dates in the calendar.",kalender_pruefen:"Check now",kalender_geprueft:"Last checked: {zeit}",kalender_nie:"The calendar has not been read yet.",kalender_fehler:"The calendar could not be read last time. Shown is what was read before.",kalender_ignorierte:"Show {n} ignored again",arbeit_fach:"Subject",arbeit_fach_waehlen:"\u2013 please choose \u2013",arbeit_fehlt_fach:"Choose the subject before saving.",fach_neu:"New subject",fach_neu_titel:"Add a subject",fach_neu_art:"Kind of subject",fach_neu_sprache:"Language",fach_neu_name:"Name",fach_neu_name_optional:"Name (empty: like the language or \u201CMath\u201D)",fach_neu_anlegen:"Add subject",fach_neu_fehlt:"This child has no subject yet. Add one first.",fachart_fremdsprache:"Foreign language",err_kalender_aus:"No exam calendar is switched on for this child.",err_termin_unbekannt:"The date is no longer in the calendar.",err_sprache_ungueltig:"Please choose a foreign language other than the native language.",err_fachart_ungueltig:"Please choose the kind of subject.",err_fach_vorhanden:"A subject with this name already exists.",err_name_leer:"Please enter a name.",keine_anstehend:"No exam is planned.",heute:"today",morgen:"tomorrow",in_tagen:"in {n} days",heute_abfragen:"{n} questions today",sicher:"{n} % mastered",sicher_hinweis:"Share of cards in boxes 3 to 5",faecher_titel:"Subjects",fach_aufgaben:"{n} tasks in {l} lessons",ungeprueft:"{n} not approved",aufgaben_oeffnen:"Tasks",lernstand:"Progress",lernstand_hinweis:"Cards per Leitner box: box 1 is new or was wrong last time, box 5 is mastered.",box:"Box {n}",karten:"{n} cards",keine_karten:"There are no tasks yet.",schwierig:"Hardest words",keine_schwierig:"No wrong answers yet.",fehler_mal:"{n} \xD7 wrong",arbeiten_oeffnen:"Manage exams",tab_aufgaben:"Tasks",tab_arbeiten:"Exams",laden:"Loading \u2026",neue_aufgabe:"New task",importieren:"Import",lektion_hinzufuegen:"Add lesson",lektion_titel:"Lessons",lektion_hilfe:"Lessons are created here and can then be selected when adding or importing tasks and in exams.",lektion_name:"Name of the lesson",lektion_keine:"No lesson has been created yet.",lektion_anzahl:"{n} tasks",lektion_loeschen_hinweis:"Only empty lessons can be deleted",lektion_angelegt:"\u201C{name}\u201D created.",keine_lektion:"\u2013 none \u2013",export_json:"Export JSON",import_json:"Import JSON",ausgewaehlt:"{n} selected",loeschen:"Delete",arbeit_aus_auswahl:"Exam from selection",filter_suche:"Search",filter_lektion:"Lesson",filter_quelle:"Source",filter_geprueft:"Approved",filter_fehlerquote:"Error rate from %",filter_von:"Created from",filter_bis:"Created until",filter_seite_von:"Book page from",filter_seite_bis:"Book page to",filter_zuruecksetzen:"Reset filters",alle:"All",ohne_lektion:"Without lesson",ja:"Yes",nein:"No",quelle_manuell:"Manual",quelle_upload:"Upload",quelle_generiert:"Generated",spalte_alternativen:"Alternatives",spalte_hinweis:"Hint",aufgabenart_titel:"What kind of task?",aufgabenart_rechnen:"Calculation",aufgabenart_rechnen_hilfe:"Text only, for example 3/4 + 1/8 or a word problem.",aufgabenart_bild:"Task with an image",aufgabenart_bild_hilfe:"A diagram, a graph or a drawing is the basis. The image is sent with the task.",bildaufgabe_titel:"Task with an image",bild:"Image",bild_waehlen:"Choose an image",bild_hilfe:"PNG, JPEG, WebP or GIF, at most 10 MB. The image is stored smaller, extra data such as the location is removed.",bild_vorschau:"Preview of the image",bild_anzeigen:"Show the image",einleitung:"Introduction (optional)",einleitung_hilfe:"Is put in front of every part, e.g. \u201CIn other countries the holidays \u2026\u201D",teilaufgaben:"Parts",teilaufgaben_hilfe:"Every row becomes a task of its own with the same image and is asked separately.",teilaufgabe:"Part {n}",teilaufgabe_hinzufuegen:"Add a part",teilaufgabe_entfernen:"Remove the part",bildaufgaben_gespeichert:"Tasks with an image created: {n}",bild_fehlt:"Please choose an image.",teil_fehlt:"Please enter at least one part with its result.",keine_bilder:"{name} cannot receive images at the moment, so tasks with an image are not asked. Images are sent automatically through Telegram; for other messengers enter an \u201Caction for images\u201D at the child.",export_ohne_bild:"Exported. Tasks with an image are not included: {n}",spalte_aufgabe:"Task",spalte_loesung:"Result",spalte_schwierigkeit:"Level",schwierigkeit:"Difficulty",schwierigkeit_hinweis:"1 = easy, 5 = hard",schwierigkeit_beliebig:"any",rechenweg:"Steps of the solution (one per line, optional)",rechenweg_vorhanden:"Steps of the solution are stored",verifikation_rechnerisch:"recalculated",verifikation_ki:"double-checked by the AI",verifikation_manuell:"checked by yourself",selbst_nachgerechnet:"Checked by myself",selbst_nachgerechnet_hinweis:"Marks the solutions of the selection as checked by you. A differing suggestion is dropped.",selbst_nachgerechnet_fertig:"Marked as checked by yourself: {n}",verifikation_abweichung:"result differs",nachrechnen:"Recalculate selection",nachrechnen_laeuft:"The tasks are being recalculated \u2026",nachgerechnet:"{bestaetigt} confirmed, {abweichend} differing, {offen} not checkable.",nachrechnen_titel:"Result of recalculating",nachrechnen_zusammenfassung:"{bestaetigt} results were confirmed, {offen} tasks could not be checked. These tasks give another result. Nothing was changed. You can apply the value that was found per task or edit the task in the table later. A result of the AI can be wrong itself, or the task is ambiguous.",nachrechnen_eingetragen:"stored",nachrechnen_berechnet:"calculated",nachrechnen_ki:"the AI gets",nur_abweichende:"Show these tasks",rechenweg_erzeugen:"Create solution steps",rechenweg_erzeugen_laeuft:"The AI is writing the solution steps \u2026",rechenwege_erzeugt:"Solution steps created: {erzeugt}. Already there: {vorhanden}. Skipped because the result differs: {abweichend}. Failed: {fehlgeschlagen}.",vorschlag:"Suggestion",vorschlag_ki:"Suggestion of the AI",uebernehmen_loesung:"Apply",uebernehmen_titel:"Replaces the stored result with this value. The stored solution steps and the statistics of the task are deleted.",alle_uebernehmen:"Apply all",alle_uebernehmen_frage:"Replace {n} results? {ki} of them come from the AI and can be wrong themselves.",uebernommen:"Results applied: {n}",schliessen:"Close",fachart_mathe:"Mathematics",fachart_sach:"Knowledge subject",generieren:"Generate tasks",generieren_titel:"Let the AI create tasks",generieren_hilfe:"The AI creates tasks similar to the existing ones. Only tasks whose solution could be recalculated or double-checked are stored. They wait for your approval afterwards. The name of the child is not sent.",generieren_beispiele_auswahl:"The {n} selected tasks serve as examples.",generieren_beispiele_thema:"The tasks of the chosen lesson serve as examples.",generieren_anzahl:"Number (1\u201320)",generieren_beschreibung:"Description (optional)",generieren_beschreibung_hilfe:"e.g. adding fractions with the same denominator",generieren_start:"Create",generieren_laeuft:"The AI is working, this can take up to two minutes \u2026",generieren_ohne_ki:"No AI entity is selected for this subject (settings of the integration).",generiert:"{erzeugt} created, {verworfen} discarded, {doppelt} duplicates.",freigeben:"Approve selection",freigegeben:"{n} tasks approved.",import_titel_mathe:"Import tasks",import_hilfe_mathe:"One task per line: task; result; optional hint. Separate other accepted spellings of the result with |.",schwierig_aufgaben:"Hardest tasks",spalte_seite:"Page",spalte_lektion:"Lesson",spalte_box:"Box",spalte_fehler:"Errors",spalte_geprueft:"Approved",spalte_erstellt:"Created",box_hinweis:"Leitner box per direction (1 = new or wrong, 5 = mastered)",alternativen_hinweis:"Separate several with |",keine_aufgaben:"There are no tasks yet.",keine_treffer:"No task matches the filters.",anzahl:"{n} of {gesamt} tasks",bearbeiten:"Edit",speichern:"Save",abbrechen:"Cancel",alle_auswaehlen:"Select all visible",loeschen_frage:"Really delete {n} task(s)?",loeschen_warnung:"{n} of the selected tasks belong to upcoming exams: {arbeiten}. Delete anyway?",geloescht:"{n} task(s) deleted.",geloescht_arbeit:"Exam deleted.",gespeichert:"Saved.",import_titel:"Import vocabulary",import_hilfe:"One word per line: {a}; {b}; optional hint. Separate alternatives with |.",import_inhalt:"Content",import_trennzeichen:"Separator (empty = automatic)",import_geprueft:"Import as approved",vorschau:"Preview",uebernehmen:"Import",vorschau_neu:"new",vorschau_vorhanden:"already exists",vorschau_fehler:"Unreadable lines: {zeilen}",import_ergebnis:"{n} imported, {u} skipped.",import_fehler:"{n} invalid entries.",export_titel:"Export tasks",mit_statistik:"Include learning statistics",herunterladen:"Download",import_json_titel:"Import JSON",import_json_hilfe:"Existing tasks are kept, identical words are skipped.",datei_ungueltig:"The file does not contain valid JSON.",import_json_lektion:"Lesson of the imported tasks",import_json_aus_datei:"Keep the lessons from the file",import_json_lektion_hilfe:"With a selected lesson all imported tasks go there, whatever the file says.",neue_arbeit:"New exam",keine_arbeiten:"There is no exam for this subject.",art:"Type",art_arbeit:"Exam",art_hue:"Homework check",datum:"Date",thema:"Title",abfragen_pro_tag:"Questions per day",start_tage_vorher:"Start (days before)",intensivierung:"Increase frequency towards the date",antwortfrist:"Time to answer (minutes)",antwortfrist_leer:"as set in general",antwortfrist_hinweis:"Empty: the general setting applies. With several running exams the shortest time wins.",aufgaben_der_arbeit:"Tasks of the exam",auswahl_alle:"All tasks of the subject",auswahl_gezielt:"Specific selection",schnell_lektionen:"Whole lessons",schnell_bereiche:"Whole topics",bereich:"Topic",bereiche_verwalten:"Manage topics",faecher_verwalten:"Manage subjects",faecher_hilfe:"Here you see the subjects of the child and add new ones.",faecher_einstellungen:"Name, AI and deleting a subject in the settings of Home Assistant",fach_angelegt:"Subject added.",themen_titel:"Topics",aufgabenverwaltung:"Task management",import_aus_text:"Import from text",bereiche_titel:"Topics",bereiche_hilfe:"Topics are tabs of a subject, e.g. \u201CVocabulary\u201D and \u201CPersonal pronouns\u201D. New tasks, imports and photos go to the selected topic.",bereich_name:"Name of the new topic",bereich_angelegt:"\u201C{name}\u201D created.",bereich_standard_vokabel:"Vocabulary",bereich_standard_mathe:"Tasks",bereich_standard_sach:"Questions",bereich_standard_satz:"Sentences",bereich_standard_hinweis:"The first topic always stays",bereich_loeschen_hinweis:"Only empty topics can be deleted",verschieben_nach:"Move to \u2026",verschoben:"{n} tasks moved.",umbenennen:"Rename",err_bereich_leer:"Please enter a name.",err_bereich_ungueltig:"The name is too long.",err_bereich_zu_viele:"No more topics are possible.",err_bereich_vorhanden:"This topic already exists.",err_bereich_art_ungueltig:"This kind of task is not possible here.",err_bereich_unbekannt:"This topic does not exist.",err_bereich_standard:"The first topic cannot be deleted.",err_bereich_verwendet:"The topic still contains tasks.",arbeit_fehlt_beides:"Title and date are still missing.",arbeit_fehlt_thema:"The title is still missing.",arbeit_fehlt_datum:"The date is still missing.",schnell_seit:"All tasks since",schnell_seiten:"All tasks from book page",schnell_seiten_bis:"to book page",hinzufuegen:"Add",einzelne_aufgaben:"Single tasks",auswahl_leeren:"Clear selection",arbeit_umfang:"{n} tasks",arbeit_alle:"all tasks",arbeit_loeschen_frage:"Really delete the exam \u201C{thema}\u201D?",arbeit_titel_neu:"Add exam",arbeit_titel_bearbeiten:"Edit exam",vergangen:"past",fehler_allgemein:"That did not work: {fehler}",err_nicht_geladen:"LearnBuddy is not loaded right now.",err_fach_unbekannt:"The subject was not found.",err_aufgabe_unbekannt:"The task was not found.",err_arbeit_unbekannt:"The exam was not found.",err_frage_ungueltig:"Please fill in both words (500 characters at most).",err_alternativen_ungueltig:"The alternatives are invalid.",err_hinweis_ungueltig:"The hint is too long.",err_aufgabe_ungueltig:"Please enter a task (at most 500 characters).",err_loesung_ungueltig:"Please enter a result (at most 100 characters).",err_rechenweg_ungueltig:"The solution may have at most 8 steps.",err_schwierigkeit_ungueltig:"The difficulty must be between 1 and 5.",err_anzahl_ungueltig:"The number must be between 1 and 20.",err_beschreibung_ungueltig:"The description is too long.",err_ki_fehlt:"No AI entity is selected for this subject.",err_ki_fehler:"The AI did not return usable tasks. Please try again later.",err_generieren_nur_mathe:"Tasks can only be generated for math subjects.",err_generieren_ohne_vorgabe:"Enter a lesson or a description, or add example tasks first.",err_export_typ:"The file belongs to another kind of subject.",err_bild_ungueltig:"This is not an image in a supported format (PNG, JPEG, WebP, GIF).",err_bild_zu_gross:"The image is larger than 10 MB.",err_bild_unbekannt:"The image was not found. Please upload it again.",err_nachrechnen_nur_mathe:"Only math subjects can be recalculated.",err_rechenweg_nur_mathe:"Only math subjects have solution steps.",err_auswahl_ungueltig:"Please select 1 to 100 tasks.",err_seite_ungueltig:"The page must be a number between 1 and 9999.",err_lektion_ungueltig:"The name is too long (100 characters at most).",err_lektion_leer:"Please enter a name.",err_lektion_vorhanden:"This lesson already exists.",err_lektion_unbekannt:"This lesson does not exist. Please create it first.",err_lektion_verwendet:"The lesson still contains tasks.",err_import_leer:"The content does not contain any valid line.",err_export_ungueltig:"The file is not a LearnBuddy export.",err_export_version:"This export version is not supported.",err_export_sprachen:"The languages of the export do not match this subject.",err_thema_leer:"Please enter a title.",err_datum_vergangen:"The date is in the past.",err_arbeit_ungueltig:"Please check the details of the exam.",err_unauthorized:"Administrator rights are required.",err_kind_unbekannt:"The child was not found.",err_keine_aufgaben:"There are no approved tasks that could be asked.",err_senden_fehlgeschlagen:"The message could not be delivered. Please check the messenger target of the child."},It={de:{de:"Deutsch",en:"Englisch",fr:"Franz\xF6sisch",es:"Spanisch",it:"Italienisch",la:"Latein"},en:{de:"German",en:"English",fr:"French",es:"Spanish",it:"Italian",la:"Latin"}};function et(u){return u.toLowerCase().startsWith("de")?"de":"en"}function Q(u){let a=et(u)==="de"?Ye:Ft;return(e,t={})=>a[e].replace(/\{(\w+)\}/g,(i,n)=>String(t[n]??""))}function E(u,a){return It[et(u)]?.[a]??a}function x(u,a){let e=a,t=[`err_${e?.message??""}`,`err_${e?.code??""}`];for(let i of t)if(i in Ye)return u(i);return u("fehler_allgemein",{fehler:e?.message??String(a)})}var Y=C`
  :host {
    display: block;
    min-height: 100vh;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
    font-size: 14px;
    --lh-border: var(--divider-color, rgba(128, 128, 128, 0.3));
    --lh-card: var(--card-background-color, #fff);
    --lh-radius: var(--ha-card-border-radius, 12px);
    --lh-muted: var(--secondary-text-color);
    --lh-accent: var(--primary-color);
    --lh-error: var(--error-color, #db4437);
    --lh-ok: var(--success-color, #43a047);
  }
  * {
    box-sizing: border-box;
  }
  header {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 8px 16px;
    min-height: 56px;
    background: var(--app-header-background-color, var(--lh-accent));
    color: var(--app-header-text-color, #fff);
    position: sticky;
    top: 0;
    z-index: 2;
  }
  header h1 {
    font-size: 20px;
    font-weight: 400;
    margin: 0 auto 0 0;
  }
  header label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
  }
  .kinder {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .kinder.fachwahl {
    margin-bottom: 12px;
  }
  button.kindwahl {
    border-radius: 18px;
    padding: 7px 16px;
  }
  header button.kindwahl {
    background: transparent;
    color: inherit;
    border-color: currentColor;
    opacity: 0.75;
  }
  button.kindwahl[aria-pressed="true"] {
    background: var(--lh-accent);
    border-color: var(--lh-accent);
    color: var(--text-primary-color, #fff);
  }
  header button.kindwahl[aria-pressed="true"] {
    /* A tint of the header text colour: readable with every theme, also
       when the theme makes the header background transparent */
    background: color-mix(in srgb, currentColor 24%, transparent);
    border-color: currentColor;
    color: inherit;
    opacity: 1;
    font-weight: 600;
  }
  main {
    padding: 16px;
    max-width: 1400px;
    margin: 0 auto;
  }
  .card {
    background: var(--lh-card);
    border: 1px solid var(--lh-border);
    border-radius: var(--lh-radius);
    padding: 16px;
    margin-bottom: 16px;
  }
  .tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--lh-border);
  }
  .tabs button {
    border: none;
    border-bottom: 3px solid transparent;
    border-radius: 0;
    background: none;
    padding: 10px 16px;
    font-size: 15px;
    color: var(--lh-muted);
  }
  .tabs button[aria-selected="true"] {
    color: var(--lh-accent);
    border-bottom-color: var(--lh-accent);
  }
  .abschnittskopf {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 8px;
  }
  .abschnittskopf.trenner,
  h3.abschnitt.trenner {
    margin-top: 24px;
  }
  h3.abschnitt {
    margin: 0 4px 8px;
    font-size: 1.05em;
    font-weight: 600;
  }
  .abschnittskopf h3.abschnitt {
    margin: 0 4px;
  }
  .werkzeuge {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    margin: -8px 0 8px;
  }
  .leiste {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }
  .leiste .abstand {
    flex: 1;
  }
  .filter {
    margin-top: 20px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px 12px;
    align-items: end;
  }
  .feld {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12px;
    color: var(--lh-muted);
    min-width: 0;
  }
  .lektionswahl {
    border: 1px solid var(--divider-color);
    border-radius: 8px;
    margin: 12px 0;
    padding: 8px 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    max-height: 240px;
    overflow-y: auto;
  }
  .lektionswahl legend {
    font-size: 12px;
    color: var(--lh-muted);
    padding: 0 4px;
  }
  .lektionszeile {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 4px 12px;
  }
  .lektionszeile .seiten {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--lh-muted);
  }
  .lektionszeile .seiten input {
    width: 72px;
  }
  .lektionswahl label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 14px;
  }
  .feld.zeile {
    flex-direction: row;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--primary-text-color);
  }
  input,
  select,
  textarea {
    font: inherit;
    font-size: 14px;
    color: var(--primary-text-color);
    background: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
    border: 1px solid var(--lh-border);
    border-radius: 6px;
    padding: 7px 8px;
    min-width: 0;
    width: 100%;
  }
  input[type="checkbox"],
  input[type="radio"] {
    width: 18px;
    height: 18px;
    flex: none;
    accent-color: var(--lh-accent);
  }
  header select {
    width: auto;
    max-width: 200px;
    color: var(--primary-text-color);
    background: var(--lh-card);
  }
  textarea {
    min-height: 160px;
    resize: vertical;
    font-family: var(--code-font-family, monospace);
  }
  input:focus-visible,
  select:focus-visible,
  textarea:focus-visible,
  button:focus-visible {
    outline: 2px solid var(--lh-accent);
    outline-offset: 1px;
  }
  button {
    font: inherit;
    cursor: pointer;
    border: 1px solid var(--lh-border);
    background: var(--lh-card);
    color: var(--primary-text-color);
    border-radius: 18px;
    padding: 7px 14px;
    white-space: nowrap;
  }
  button:hover:not(:disabled) {
    border-color: var(--lh-accent);
  }
  button:disabled {
    opacity: 0.5;
    cursor: default;
  }
  button.primaer {
    background: var(--lh-accent);
    border-color: var(--lh-accent);
    color: var(--text-primary-color, #fff);
  }
  button.gefahr {
    color: var(--lh-error);
    border-color: var(--lh-error);
  }
  button.icon {
    border: none;
    background: none;
    padding: 6px;
    border-radius: 50%;
    color: var(--lh-muted);
    line-height: 0;
  }
  button.icon:hover:not(:disabled) {
    color: var(--lh-accent);
    background: rgba(128, 128, 128, 0.12);
  }
  header button.icon {
    color: inherit;
  }
  .abschnitt {
    margin: 18px 4px 6px;
    font-size: 1.05em;
    font-weight: 600;
  }
  .tabelle-rahmen {
    overflow-x: auto;
    padding: 0;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th,
  td {
    text-align: left;
    padding: 8px 10px;
    border-bottom: 1px solid var(--lh-border);
    vertical-align: top;
  }
  th {
    font-size: 12px;
    font-weight: 500;
    color: var(--lh-muted);
    white-space: nowrap;
    position: sticky;
    top: 0;
    background: var(--lh-card);
  }
  tr:last-child td {
    border-bottom: none;
  }
  tr.gewaehlt td {
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
  }
  td.schmal,
  th.schmal {
    width: 1%;
    white-space: nowrap;
  }
  .klein {
    font-size: 12px;
    color: var(--lh-muted);
  }
  .marke {
    display: inline-block;
    font-size: 11px;
    padding: 1px 7px;
    border-radius: 9px;
    border: 1px solid var(--lh-border);
    color: var(--lh-muted);
    white-space: nowrap;
  }
  .marke.warn {
    color: var(--lh-error);
    border-color: var(--lh-error);
  }
  .marke.ok {
    color: var(--lh-ok);
    border-color: var(--lh-ok);
  }
  .meldung {
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    background: rgba(67, 160, 71, 0.14);
  }
  .meldung.fehler {
    background: rgba(219, 68, 55, 0.14);
    color: var(--lh-error);
  }
  .meldung span {
    flex: 1 1 220px;
  }
  .leer {
    padding: 28px 16px;
    text-align: center;
    color: var(--lh-muted);
  }
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 24px 12px;
    overflow-y: auto;
    z-index: 10;
  }
  .dialog {
    background: var(--lh-card);
    border-radius: var(--lh-radius);
    width: min(720px, 100%);
    padding: 20px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
  }
  a.knopf {
    display: inline-block;
    padding: 6px 14px;
    border: 1px solid var(--lh-border);
    border-radius: 18px;
    color: var(--primary-text-color);
    text-decoration: none;
    font-size: 14px;
  }
  .dialog.breit {
    width: min(1100px, 100%);
  }
  .label-flaeche {
    position: relative;
    display: block;
    width: fit-content;
    max-width: 100%;
    margin: 0 auto;
    touch-action: none;
    user-select: none;
    cursor: crosshair;
  }
  .label-flaeche img {
    display: block;
    max-width: 100%;
    max-height: 60vh;
    border-radius: 8px;
    background: #fff;
    pointer-events: none;
  }
  .label-box {
    position: absolute;
    box-sizing: border-box;
    border: 2px solid var(--primary-color);
    background: color-mix(in srgb, var(--primary-color) 18%, transparent);
    cursor: move;
  }
  .label-box.gewaehlt {
    border-color: var(--error-color, #db4437);
    background: color-mix(in srgb, var(--error-color, #db4437) 18%, transparent);
  }
  .label-nr {
    position: absolute;
    left: -2px;
    top: -22px;
    min-width: 20px;
    padding: 0 5px;
    border-radius: 10px;
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
    font-size: 12px;
    line-height: 20px;
    text-align: center;
  }
  .label-box.gewaehlt .label-nr {
    background: var(--error-color, #db4437);
  }
  .label-griff {
    position: absolute;
    right: -7px;
    bottom: -7px;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background: var(--primary-color);
    cursor: nwse-resize;
  }
  .label-liste {
    display: grid;
    gap: 6px;
    margin-top: 12px;
  }
  .label-zeile {
    display: grid;
    grid-template-columns: 2em 1fr 1fr auto;
    gap: 8px;
    align-items: center;
    padding: 2px 4px;
    border-radius: 8px;
  }
  .label-zeile.gewaehlt {
    background: color-mix(in srgb, var(--error-color, #db4437) 10%, transparent);
  }
  @media (max-width: 600px) {
    .label-zeile {
      grid-template-columns: 2em 1fr auto;
    }
    .label-zeile input:nth-of-type(2) {
      grid-column: 2 / 4;
    }
  }
  .vorschaubild {
    display: block;
    width: 56px;
    height: 42px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid var(--lh-border);
    background: #fff;
    cursor: zoom-in;
    padding: 0;
  }
  .grossbild {
    display: block;
    max-width: 100%;
    max-height: 70vh;
    margin: 0 auto;
    border-radius: 8px;
    background: #fff;
  }
  .wahl {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
  }
  .wahl button {
    display: block;
    text-align: left;
    padding: 16px;
    height: auto;
    white-space: normal;
    border-radius: var(--lh-radius);
  }
  .wahl button.primaer .klein {
    color: inherit;
    opacity: 0.92;
  }
  .wahl button strong {
    display: block;
    margin-bottom: 4px;
    font-size: 15px;
  }
  .teil {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr auto;
    gap: 8px;
    align-items: end;
    margin-bottom: 8px;
  }
  @media (max-width: 600px) {
    .teil {
      grid-template-columns: 1fr;
    }
  }
  .dialog h2 {
    margin: 0 0 12px;
    font-size: 18px;
    font-weight: 500;
  }
  .dialog .raster {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }
  .dialog .raster + .klein {
    margin-bottom: 14px;
  }
  .dialog .aktionen {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 16px;
  }
  fieldset {
    border: 1px solid var(--lh-border);
    border-radius: 8px;
    padding: 12px;
    margin: 0 0 12px;
    min-width: 0;
  }
  legend {
    padding: 0 6px;
    font-size: 12px;
    color: var(--lh-muted);
  }
  .liste {
    max-height: 240px;
    overflow-y: auto;
    border: 1px solid var(--lh-border);
    border-radius: 6px;
  }
  .liste label,
  .liste .eintrag {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-bottom: 1px solid var(--lh-border);
  }
  .liste label:last-child,
  .liste .eintrag:last-child {
    border-bottom: none;
  }
  .liste .kopf {
    position: sticky;
    top: 0;
    z-index: 1;
    background: var(--lh-card);
    font-size: 12px;
    font-weight: 500;
    color: var(--secondary-text-color);
  }
  .liste .kopf .haken {
    width: 13px;
    flex: none;
  }
  .liste .seite {
    width: 64px;
    flex: none;
    text-align: right;
  }
  .liste .lektion {
    width: 130px;
    flex: none;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 14px;
  }
  .arbeit {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
  .arbeit .info {
    flex: 1;
    min-width: 200px;
  }
  .arbeit .titel {
    font-size: 16px;
  }

  /* Narrow screens: every table row becomes a card */
  :host([narrow]) main {
    padding: 8px;
  }
  :host([narrow]) table,
  :host([narrow]) tbody,
  :host([narrow]) tr,
  :host([narrow]) td {
    display: block;
    width: 100%;
  }
  :host([narrow]) thead {
    display: none;
  }
  :host([narrow]) tr {
    border-bottom: 1px solid var(--lh-border);
    padding: 8px 4px;
  }
  :host([narrow]) td {
    border: none;
    padding: 3px 10px;
  }
  :host([narrow]) td[data-label]:not(:empty)::before {
    content: attr(data-label) ": ";
    font-size: 12px;
    color: var(--lh-muted);
  }
  :host([narrow]) td.schmal {
    white-space: normal;
  }
`;var de=["richtig","teilweise","falsch","unbeantwortet"],Dt={richtig:"#2a78d6",teilweise:"#1baf7a",falsch:"#eb6834",unbeantwortet:"#4a3aa7"},Bt={richtig:"#3987e5",teilweise:"#199e70",falsch:"#d95926",unbeantwortet:"#9085e9"},tt=["#2a78d6","#eb6834","#1baf7a","#eda100","#e87ba4","#008300"],it=["#3987e5","#d95926","#199e70","#c98500","#d55181","#008300"],Rt=[7,30,90],Lt=200,nt=170,I=38,ee=12,te=10,H=24,Nt=24,st=2;function Pt(u){if(u<=4)return 4;let a=10**Math.floor(Math.log10(u));for(let e of[1,2,4,5,10])if(u<=e*a)return e*a;return 10*a}var S=class extends R{constructor(){super(...arguments);this.narrow=!1;this.kindId="";this.wochenreport=!1;this._tage=30;this._fehler="";this._tabelle=!1;this._zeiger=null;this._report=null;this._reportVersatz=-1;this._reportOffen=!1;this._reportHinweis="";this._breiten={}}static{this.styles=[Y,C`
      :host {
        min-height: 0;
        background: none;
        margin-top: 16px;
      }
      .kopf {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-bottom: 12px;
      }
      .kopf h2 {
        flex: 1 1 140px;
        margin: 0;
        font-size: 18px;
        font-weight: 500;
      }
      .wahl {
        display: inline-flex;
        gap: 4px;
      }
      .wahl button[aria-pressed="true"] {
        background: var(--lh-accent);
        border-color: var(--lh-accent);
        color: var(--text-primary-color, #fff);
      }
      .raster {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      .raster > .breit {
        grid-column: 1 / -1;
      }
      :host([narrow]) .raster {
        grid-template-columns: minmax(0, 1fr);
      }
      .card {
        margin: 0;
      }
      .card h3 {
        font-size: 16px;
        font-weight: 500;
        margin: 0 0 2px;
      }
      h4 {
        font-size: 14px;
        font-weight: 500;
        margin: 12px 0 4px;
      }
      .diagramm {
        position: relative;
        margin-top: 8px;
      }
      svg {
        display: block;
        width: 100%;
      }
      svg text {
        font-size: 11px;
        fill: var(--secondary-text-color);
      }
      .gitter {
        stroke: var(--lh-border);
        stroke-width: 1;
      }
      .fadenkreuz {
        stroke: var(--secondary-text-color);
        stroke-width: 1;
        stroke-dasharray: 3 3;
      }
      .tooltip {
        position: absolute;
        top: 0;
        z-index: 1;
        pointer-events: none;
        background: var(--lh-card);
        color: var(--primary-text-color);
        border: 1px solid var(--lh-border);
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 12px;
        white-space: nowrap;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      }
      .tooltip .tag {
        font-weight: 500;
        margin-bottom: 2px;
      }
      .legende {
        display: flex;
        flex-wrap: wrap;
        gap: 4px 14px;
        margin-top: 6px;
        font-size: 12px;
        color: var(--secondary-text-color);
      }
      .punkt {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 2px;
        margin-right: 5px;
        vertical-align: -1px;
      }
      ul {
        margin: 4px 0 0;
        padding-left: 18px;
      }
      li {
        margin: 3px 0;
      }
      .tabelle {
        overflow-x: auto;
      }
      .tabelle table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }
      .tabelle th,
      .tabelle td {
        text-align: right;
        padding: 4px 8px;
        border-bottom: 1px solid var(--lh-border);
        white-space: nowrap;
      }
      .tabelle th:first-child,
      .tabelle td:first-child {
        text-align: left;
      }
      .report h3 {
        font-size: 15px;
        font-weight: 500;
        margin: 16px 0 4px;
      }
      .report .woche {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 4px;
      }
      .report .woche span {
        flex: 1;
        text-align: center;
        font-weight: 500;
      }
    `]}get _t(){return Q(this.hass?.language??"en")}get _api(){return new K(this.hass)}get _dunkel(){return!!this.hass?.themes?.darkMode}willUpdate(e){(e.has("kindId")||e.has("stand"))&&this._lade(),e.has("kindId")&&(this._reportOffen=!1)}_mass(e,t){return{b:Math.max(240,this._breiten[e]??600),h:t}}connectedCallback(){super.connectedCallback(),this._beobachter=new ResizeObserver(e=>{let t={...this._breiten},i=!1;for(let n of e){let s=n.target.dataset.name??"",l=Math.round(n.contentRect.width);s&&l&&t[s]!==l&&(t[s]=l,i=!0)}i&&(this._breiten=t)})}disconnectedCallback(){super.disconnectedCallback(),this._beobachter?.disconnect()}updated(){for(let e of this.renderRoot.querySelectorAll(".diagramm"))this._beobachter?.observe(e)}async _lade(){if(!(!this.hass||!this.kindId))try{this._daten=await this._api.fortschritt(this.kindId,this._tage),this._fehler=""}catch(e){this._fehler=x(this._t,e)}}async _setzeTage(e){this._tage=e,this._zeiger=null,await this._lade()}_datum(e,t=!1){return e?new Date(`${e.slice(0,10)}T00:00:00`).toLocaleDateString(this.hass?.language??"en",t?{weekday:"short",day:"2-digit",month:"2-digit",year:"numeric"}:{day:"2-digit",month:"2-digit"}):""}_prozent(e){return e==null?"\u2013":`${e} %`}_simText(e){let t=this._t,i=[e.fach,e.thema].filter(Boolean).join(": "),n=t("sim_punkte",{p:e.punkte.toLocaleString(this.hass?.language??"en"),m:e.moeglich,proz:e.prozent??0});return`${this._datum(e.tag)}${i?` \xB7 ${i}`:""} \u2013 ${n}${e.vollstaendig?"":` (${t("sim_unvollstaendig")})`}`}_lektionText(e){return`${e.fach} \xB7 ${e.lektion}: ${this._t("fehlerquote_n",{n:e.fehlerquote,f:e.falsch,g:e.richtig+e.falsch})}`}_spalten(e,t,i){let n=(e.b-I-ee)/i,s=this._zeiger?.diagramm===t?this._zeiger.index:-1;return N`
      ${s>=0?N`<line class="fadenkreuz"
              x1=${I+(s+.5)*n} x2=${I+(s+.5)*n}
              y1=${te} y2=${e.h-H}></line>`:c}
      ${Array.from({length:i},(l,h)=>N`<rect
          x=${I+h*n} y=${te}
          width=${n} height=${e.h-te-H}
          fill="transparent"
          @pointerenter=${()=>{this._zeiger={diagramm:t,index:h}}}
        ></rect>`)}
    `}_achsen(e,t,i,n){let s=e.h-te-H,l=(e.b-I-ee)/n.length,h=Math.max(1,Math.ceil(n.length/Math.max(2,(e.b-I)/60)));return N`
      ${[0,.5,1].map(d=>{let g=e.h-H-d*s;return N`
          <line class="gitter" x1=${I} x2=${e.b-ee} y1=${g} y2=${g}></line>
          <text x=${I-6} y=${g+4} text-anchor="end">
            ${Math.round(d*t)}${i}
          </text>`})}
      ${n.map((d,g)=>g%h===0?N`<text x=${I+(g+.5)*l} y=${e.h-6}
              text-anchor="middle">${this._datum(d)}</text>`:c)}
    `}_tooltip(e,t,i,n){let s=this._zeiger;if(!s||s.diagramm!==t)return c;let l=(I+(s.index+.5)*(e.b-I-ee)/i)/e.b,h=l>.5?`right: calc(${(1-l)*100}% + 10px)`:`left: calc(${l*100}% + 10px)`;return r`<div class="tooltip" style=${h}>${n(s.index)}</div>`}_antworten(e){let t=this._t,i=this._mass("antworten",Lt),n=this._dunkel?Bt:Dt,s=e.reihe,l=f=>f.richtig+f.teilweise+f.falsch+f.unbeantwortet,h=Pt(Math.max(...s.map(l))),d=i.h-te-H,g=(i.b-I-ee)/s.length,o=Math.max(2,Math.min(Nt,g-st)),_=s.map((f,k)=>{let z=I+k*g+(g-o)/2,y=i.h-H,w=de.filter(j=>f[j]>0);return w.map((j,p)=>{let A=f[j]/h*d,T=Math.max(1,A-(p>0?st:0));y-=A;let q=p===w.length-1?Math.min(4,o/2,T):0,dt=`M${z},${y+T} V${y+q} q0,${-q} ${q},${-q} H${z+o-q} q${q},0 ${q},${q} V${y+T} Z`;return N`<path d=${dt} fill=${n[j]}></path>`})});return r`
      <h3>${t("fortschritt_antworten")}</h3>
      <div
        class="diagramm"
        data-name="antworten"
        @pointerleave=${()=>{this._zeiger=null}}
      >
        <svg viewBox="0 0 ${i.b} ${i.h}" height=${i.h} role="img" aria-label=${t("fortschritt_antworten")}>
          ${this._achsen(i,h,"",s.map(f=>f.tag))}
          ${_}
          ${this._spalten(i,"antworten",s.length)}
        </svg>
        ${this._tooltip(i,"antworten",s.length,f=>{let k=s[f];return k?r`
            <div class="tag">${this._datum(k.tag,!0)}</div>
            ${de.map(z=>r`<div>
                  <span class="punkt" style="background: ${n[z]}"></span>
                  ${t(`reihe_${z}`)}: ${k[z]}
                </div>`)}
          `:r``})}
      </div>
      <div class="legende">
        ${de.map(f=>r`<span>
              <span class="punkt" style="background: ${n[f]}"></span>
              ${t(`reihe_${f}`)}
            </span>`)}
      </div>
    `}_linie(e,t,i,n){let s=e.h-te-H,l=(e.b-I-ee)/t.length,h=(f,k)=>[I+(k+.5)*l,e.h-H-f/100*s],d="",g=!1,o=[];t.forEach((f,k)=>{if(f===null){g=!1;return}let[z,y]=h(f,k);d+=`${g?"L":"M"}${z},${y} `,!g&&(k===t.length-1||t[k+1]===null)&&o.push([z,y]),g=!0});let _=n>=0?t[n]:null;return N`
      <path d=${d} fill="none" stroke=${i} stroke-width="2"
        stroke-linejoin="round" stroke-linecap="round"></path>
      ${o.map(([f,k])=>N`<circle cx=${f} cy=${k} r="3" fill=${i}></circle>`)}
      ${_!=null?N`<circle cx=${h(_,n)[0]} cy=${h(_,n)[1]}
              r="4" fill=${i} stroke="var(--lh-card)" stroke-width="2"></circle>`:c}
    `}_quote(e){let t=this._t,i=this._mass("quote",nt),n=(this._dunkel?it:tt)[0],s=e.reihe,l=s.map(d=>d.trefferquote),h=this._zeiger?.diagramm==="quote"?this._zeiger.index:-1;return r`
      <h3>${t("fortschritt_quote")}</h3>
      <div class="klein">${t("fortschritt_quote_hilfe")}</div>
      <div
        class="diagramm"
        data-name="quote"
        @pointerleave=${()=>{this._zeiger=null}}
      >
        <svg viewBox="0 0 ${i.b} ${i.h}" height=${i.h} role="img" aria-label=${t("fortschritt_quote")}>
          ${this._achsen(i,100," %",s.map(d=>d.tag))}
          ${this._linie(i,l,n,h)}
          ${this._spalten(i,"quote",s.length)}
        </svg>
        ${this._tooltip(i,"quote",s.length,d=>r`
          <div class="tag">${this._datum(s[d]?.tag,!0)}</div>
          <div>${t("fortschritt_quote")}: ${this._prozent(s[d]?.trefferquote)}</div>
        `)}
      </div>
    `}_lernstand(e){let t=this._t,i=this._mass("lernstand",nt),n=this._dunkel?it:tt,s=e.faecher.slice(0,n.length),l=e.reihe.map(d=>d.tag),h=this._zeiger?.diagramm==="lernstand"?this._zeiger.index:-1;return r`
      <h3>${t("fortschritt_lernstand")}</h3>
      <div class="klein">${t("fortschritt_lernstand_hilfe")}</div>
      <div
        class="diagramm"
        data-name="lernstand"
        @pointerleave=${()=>{this._zeiger=null}}
      >
        <svg
          viewBox="0 0 ${i.b} ${i.h}"
          height=${i.h}
          role="img"
          aria-label=${t("fortschritt_lernstand")}
        >
          ${this._achsen(i,100," %",l)}
          ${s.map((d,g)=>this._linie(i,d.lernstand,n[g],h))}
          ${this._spalten(i,"lernstand",l.length)}
        </svg>
        ${this._tooltip(i,"lernstand",l.length,d=>r`
          <div class="tag">${this._datum(l[d],!0)}</div>
          ${s.map((g,o)=>r`<div>
                <span class="punkt" style="background: ${n[o]}"></span>
                ${g.name}: ${this._prozent(g.lernstand[d])}
              </div>`)}
        `)}
      </div>
      ${s.length>1?r`<div class="legende">
            ${s.map((d,g)=>r`<span>
                  <span class="punkt" style="background: ${n[g]}"></span>
                  ${d.name}
                </span>`)}
          </div>`:c}
    `}_alsTabelle(e){let t=this._t,i=e.reihe.map((n,s)=>({tag:n,index:s})).filter(({tag:n})=>n.gefragt||n.richtig||n.falsch||n.teilweise).reverse();return i.length?r`
      <div class="tabelle">
        <table>
          <thead>
            <tr>
              <th>${t("reihe_tag")}</th>
              <th>${t("reihe_gefragt")}</th>
              ${de.map(n=>r`<th>${t(`reihe_${n}`)}</th>`)}
              <th>${t("fortschritt_quote")}</th>
              ${e.faecher.map(n=>r`<th>${n.name}</th>`)}
            </tr>
          </thead>
          <tbody>
            ${i.map(({tag:n,index:s})=>r`<tr>
                  <td>${this._datum(n.tag,!0)}</td>
                  <td>${n.gefragt}</td>
                  ${de.map(l=>r`<td>${n[l]}</td>`)}
                  <td>${this._prozent(n.trefferquote)}</td>
                  ${e.faecher.map(l=>r`<td>${this._prozent(l.lernstand[s])}</td>`)}
                </tr>`)}
          </tbody>
        </table>
      </div>
    `:r`<div class="leer">${t("fortschritt_keine_daten")}</div>`}_aufgabenListe(e){let t=this._t;return r`<ul>
      ${e.map(i=>r`<li>
            ${i.fach}: ${i.aufgabe} → ${i.loesung}
            <span class="klein">(${t("fehler_n",{n:i.falsch})})</span>
          </li>`)}
    </ul>`}_schwach(e){let t=this._t;return r`
      <h3>${t("fortschritt_schwach")}</h3>
      ${!e.lektionen.length&&!e.aufgaben.length?r`<div class="leer">${t("fortschritt_keine_schwach")}</div>`:c}
      ${e.lektionen.length?r`<h4>${t("fortschritt_lektionen")}</h4>
            <ul>
              ${e.lektionen.map(i=>r`<li>${this._lektionText(i)}</li>`)}
            </ul>`:c}
      ${e.aufgaben.length?r`<h4>${t("fortschritt_aufgaben")}</h4>
            ${this._aufgabenListe(e.aufgaben)}`:c}
    `}_simulationen(e){let t=this._t;return r`
      <h3>${t("fortschritt_simulationen")}</h3>
      ${e.simulationen.length?r`<ul>
            ${e.simulationen.map(i=>r`<li>${this._simText(i)}</li>`)}
          </ul>`:r`<div class="leer">${t("fortschritt_keine_sim")}</div>`}
    `}async _oeffneReport(e=-1){try{this._report=await this._api.wochenreport(this.kindId,e),this._reportVersatz=e,this._reportHinweis="",this._reportOffen=!0,this._fehler=""}catch(t){this._fehler=x(this._t,t)}}_veraenderung(e,t,i){let n=this._t;if(e===null)return"\u2013";if(t===null)return`${e}${i} (${n("report_vorwoche",{wert:n("report_keine_vorwoche")})})`;let s=e>t?"\u2191":e<t?"\u2193":"\u2192";return`${e}${i} ${s} (${n("report_vorwoche",{wert:`${t}${i}`})})`}_abschnitte(e){let t=this._t,i=e.kennzahlen,n=e.vorwoche,s=g=>g.richtig+g.teilweise+g.falsch,l=g=>g===0?t("report_heute"):g===1?t("report_morgen"):t("report_in_tagen",{n:g}),h=[{titel:t("report_kennzahlen"),zeilen:[`${t("reihe_gefragt")}: ${i.gefragt}`,`${t("reihe_richtig")}: ${i.richtig}`,`${t("reihe_teilweise")}: ${i.teilweise}`,`${t("reihe_falsch")}: ${i.falsch}`,`${t("reihe_unbeantwortet")}: ${i.unbeantwortet}`,`${t("fortschritt_quote")}: ${this._prozent(i.trefferquote)}`,`${t("report_tage_aktiv")}: ${i.tage_aktiv}`]},{titel:t("report_vergleich"),zeilen:[`${t("report_antworten")}: ${this._veraenderung(s(i),s(n),"")}`,`${t("fortschritt_quote")}: ${this._veraenderung(i.trefferquote,n.trefferquote," %")}`,...e.faecher.map(g=>`${t("report_lernstand",{fach:g.name})}: ${this._veraenderung(g.lernstand,g.vorher," %")}`)]}],d=[...e.lektionen.map(g=>this._lektionText(g)),...e.aufgaben.map(g=>`${g.fach}: ${g.aufgabe} \u2013 ${t("report_loesung",{loesung:g.loesung})} (${t("fehler_n",{n:g.falsch})})`)];return d.length&&h.push({titel:t("report_schwach"),zeilen:d}),h.push({titel:t("report_anstehend"),zeilen:e.arbeiten.length?e.arbeiten.map(g=>`${this._datum(g.datum)} (${l(g.tage_bis)}) \xB7 ${g.fach}: ${g.thema} [${t(g.art==="hue"?"art_hue":"art_arbeit")}]${g.sicher===null?"":` \u2013 ${t("report_sicher",{n:g.sicher})}`}`):[t("report_keine_arbeiten")]}),e.vorschlaege.length&&h.push({titel:t("report_vorschlaege"),zeilen:e.vorschlaege.map(g=>`${this._datum(g.datum)} \xB7 ${g.text} [${t(g.art==="hue"?"art_hue":"art_arbeit")}]`)}),e.simulationen.length&&h.push({titel:t("report_simulationen"),zeilen:e.simulationen.map(g=>this._simText(g))}),h}_reportTitel(e){let t=this._t;return`${t("report_woche",{von:this._datum(e.von),bis:this._datum(e.bis)})}${e.laufend?` (${t("report_laufend")})`:""}`}_reportText(e){return[`${this._t("wochenreport")} \u2013 ${this._reportTitel(e)}`,...this._abschnitte(e).map(t=>`
${t.titel}
${t.zeilen.map(i=>`- ${i}`).join(`
`)}`)].join(`
`)}async _kopiereReport(){if(this._report)try{await navigator.clipboard.writeText(this._reportText(this._report)),this._reportHinweis=this._t("report_kopiert")}catch{this._reportHinweis=this._t("report_kopieren_fehler")}}_druckeReport(){let e=this._report;if(!e)return;let t=window.open("","_blank");if(!t){this._reportHinweis=this._t("report_druck_blockiert");return}let i=t.document;i.title=this._t("wochenreport");let n=i.createElement("style");n.textContent="body{font-family:sans-serif;margin:24px;color:#000}h1{font-size:20px}h2{font-size:15px;margin:18px 0 4px}li{margin:3px 0}",i.head.append(n);let s=i.createElement("h1");s.textContent=`${this._t("wochenreport")} \u2013 ${this._reportTitel(e)}`,i.body.append(s);for(let l of this._abschnitte(e)){let h=i.createElement("h2");h.textContent=l.titel;let d=i.createElement("ul");for(let g of l.zeilen){let o=i.createElement("li");o.textContent=g,d.append(o)}i.body.append(h,d)}t.focus(),t.print()}_reportDialog(e){let t=this._t;return r`
      <div
        class="overlay"
        @click=${i=>{i.target===i.currentTarget&&(this._reportOffen=!1)}}
      >
        <div class="dialog report" role="dialog" aria-modal="true">
          <h2>${t("wochenreport")}</h2>
          <div class="woche">
            <button
              class="icon"
              title=${t("report_frueher")}
              aria-label=${t("report_frueher")}
              @click=${()=>this._oeffneReport(this._reportVersatz-1)}
            >
              <ha-icon icon="mdi:chevron-left"></ha-icon>
            </button>
            <span>${this._reportTitel(e)}</span>
            <button
              class="icon"
              title=${t("report_spaeter")}
              aria-label=${t("report_spaeter")}
              ?disabled=${this._reportVersatz>=0}
              @click=${()=>this._oeffneReport(this._reportVersatz+1)}
            >
              <ha-icon icon="mdi:chevron-right"></ha-icon>
            </button>
          </div>
          ${e.seit&&e.seit>e.bis?r`<p class="klein">
                ${t("fortschritt_seit",{datum:this._datum(e.seit,!0)})}
              </p>`:c}
          ${this._abschnitte(e).map(i=>r`<h3>${i.titel}</h3>
                <ul>
                  ${i.zeilen.map(n=>r`<li>${n}</li>`)}
                </ul>`)}
          ${this._reportHinweis?r`<div class="meldung" role="status" style="margin-top: 12px">
                <span>${this._reportHinweis}</span>
              </div>`:c}
          <div class="aktionen">
            <button @click=${this._kopiereReport}>${t("report_kopieren")}</button>
            <button @click=${this._druckeReport}>${t("report_drucken")}</button>
            <button
              class="primaer"
              @click=${()=>{this._reportOffen=!1}}
            >
              ${t("schliessen")}
            </button>
          </div>
        </div>
      </div>
    `}render(){let e=this._t,t=this._daten;return r`
      <div class="kopf">
        <h2>${e("fortschritt")}</h2>
        <div class="wahl" role="group" aria-label=${e("fortschritt_zeitraum")}>
          ${Rt.map(i=>r`<button
                aria-pressed=${i===this._tage?"true":"false"}
                @click=${()=>this._setzeTage(i)}
              >
                ${e("fortschritt_tage",{n:i})}
              </button>`)}
        </div>
        <button
          @click=${()=>{this._tabelle=!this._tabelle}}
        >
          ${e(this._tabelle?"fortschritt_diagramm":"fortschritt_tabelle")}
        </button>
        ${this.wochenreport?r`<button class="primaer" @click=${()=>this._oeffneReport()}>
              ${e("wochenreport")}
            </button>`:c}
      </div>
      ${this._fehler?r`<div class="meldung fehler" role="alert"><span>${this._fehler}</span></div>`:c}
      ${t?t.seit?r`
              <div class="klein" style="margin-bottom: 8px">
                ${e("fortschritt_seit",{datum:this._datum(t.seit,!0)})}
              </div>
              <div class="raster">
                ${this._tabelle?r`<div class="card breit">${this._alsTabelle(t)}</div>`:r`
                      <div class="card breit">${this._antworten(t)}</div>
                      <div class="card">${this._quote(t)}</div>
                      <div class="card">${this._lernstand(t)}</div>
                    `}
                <div class="card">${this._schwach(t)}</div>
                <div class="card">${this._simulationen(t)}</div>
              </div>
            `:r`<div class="card leer">${e("fortschritt_leer")}</div>`:c}
      ${this._reportOffen&&this._report?this._reportDialog(this._report):c}
    `}};b([F({attribute:!1})],S.prototype,"hass",2),b([F({type:Boolean,reflect:!0})],S.prototype,"narrow",2),b([F()],S.prototype,"kindId",2),b([F({type:Boolean})],S.prototype,"wochenreport",2),b([F({attribute:!1})],S.prototype,"stand",2),b([m()],S.prototype,"_tage",2),b([m()],S.prototype,"_daten",2),b([m()],S.prototype,"_fehler",2),b([m()],S.prototype,"_tabelle",2),b([m()],S.prototype,"_zeiger",2),b([m()],S.prototype,"_report",2),b([m()],S.prototype,"_reportVersatz",2),b([m()],S.prototype,"_reportOffen",2),b([m()],S.prototype,"_reportHinweis",2),b([m()],S.prototype,"_breiten",2);customElements.get("lh-fortschritt")||customElements.define("lh-fortschritt",S);function ge(u,a,e){let t=a.trim()===""?null:Number(a),i=e.trim()===""?null:Number(e);return t===null&&i===null?!0:u===null?!1:(t===null||u>=t)&&(i===null||u<=i)}function _e(u,a,e){return u.typ==="mathe"?`${u.aufgabe} = ${u.loesung}`:u.typ==="sach"?`${u.frage} \u2013 ${u.antwort}`:`${u.frage[a]??""} \u2013 ${u.frage[e]??""}`}var at=["#86b6ef","#5598e7","#2a78d6","#1c5cab","#104281"],rt=["#184f95","#256abf","#3987e5","#6da7ec","#b7d3f6"],Mt=6e4,lt=100,jt=5,qt=["learnbuddy_question_sent","learnbuddy_answer_evaluated"],L=class extends R{constructor(){super(...arguments);this.narrow=!1;this.kindId="";this._fehler="";this._kalenderLaeuft=!1;this._erfolg="";this._abfrage=null;this._zaehlung=0;this._beschaeftigt=!1;this._abos=[]}static{this.styles=[Y,C`
      :host {
        min-height: 0;
        background: none;
      }
      .raster {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      .raster > .breit {
        grid-column: 1 / -1;
      }
      :host([narrow]) .raster {
        grid-template-columns: minmax(0, 1fr);
      }
      .card {
        margin: 0;
      }
      h2 {
        font-size: 16px;
        font-weight: 500;
        margin: 0 0 12px;
      }
      .status {
        display: flex;
        flex-wrap: wrap;
        gap: 16px 24px;
        align-items: center;
      }
      .status .zustand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 500;
      }
      .status .zustand ha-icon {
        --mdc-icon-size: 28px;
      }
      .status .zustand.gut ha-icon {
        color: #0ca30c;
      }
      .status .zustand.aus ha-icon {
        color: var(--lh-muted);
      }
      .status .fakten {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 8px 20px;
        flex: 1;
        min-width: 240px;
      }
      .fakt .wert {
        font-size: 14px;
      }
      .status .knoepfe {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      .kacheln {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
      }
      .kachel {
        background: var(--lh-card);
        border: 1px solid var(--lh-border);
        border-radius: var(--lh-radius);
        padding: 14px 16px;
      }
      .kachel .zahl {
        font-size: 30px;
        line-height: 1.15;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
      }
      .kachel .name {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: var(--lh-muted);
      }
      .kachel .name ha-icon {
        --mdc-icon-size: 16px;
      }
      .balken {
        display: flex;
        gap: 2px;
        height: 12px;
        border-radius: 4px;
        overflow: hidden;
        background: rgba(128, 128, 128, 0.15);
      }
      .balken.gross {
        height: 22px;
      }
      .balken span {
        min-width: 3px;
      }
      .legende {
        display: flex;
        flex-wrap: wrap;
        gap: 6px 16px;
        margin-top: 10px;
        font-size: 12px;
        color: var(--lh-muted);
      }
      .legende i {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 2px;
        margin-right: 5px;
      }
      .legende b {
        font-weight: 500;
        color: var(--primary-text-color);
      }
      .zeile {
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 10px 0;
        border-top: 1px solid var(--lh-border);
      }
      .zeile:first-of-type {
        border-top: none;
        padding-top: 0;
      }
      /* Ticks in the selection of a request are no list rows */
      .chips .zeile {
        border-top: none;
        padding: 0;
      }
      h2.abstand {
        margin-top: 20px;
      }
      .kalenderfuss {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 10px;
      }
      .kalenderfuss span {
        flex: 1 1 160px;
      }
      .warnung {
        color: var(--lh-error);
        margin-bottom: 6px;
      }
      .zeile .mitte {
        flex: 1;
        min-width: 0;
      }
      .zeile .titel {
        font-size: 15px;
        overflow-wrap: anywhere;
      }
      .countdown {
        flex: none;
        width: 76px;
        text-align: center;
        border: 1px solid var(--lh-border);
        border-radius: 10px;
        padding: 6px 4px;
      }
      .countdown .tage {
        font-size: 15px;
        font-weight: 500;
      }
      .countdown.bald {
        border-color: var(--lh-accent);
      }
      .mini {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 6px;
      }
      .mini .balken {
        flex: 1;
        max-width: 220px;
      }
      .fachknoepfe {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        justify-content: flex-end;
      }
      .auswahl {
        display: grid;
        gap: 8px;
      }
      .auswahl button {
        text-align: left;
        border-radius: 10px;
        padding: 12px 14px;
        white-space: normal;
      }
    `]}get _t(){return Q(this.hass?.language??"en")}get _api(){return new K(this.hass)}connectedCallback(){super.connectedCallback(),this._timer=window.setInterval(()=>void this._lade(),Mt)}_abonniere(){let e=this.hass?.connection;!e||this._abos.length||(this._abos=qt.map(t=>e.subscribeEvents(()=>void this._lade(),t)))}disconnectedCallback(){super.disconnectedCallback(),window.clearInterval(this._timer);for(let e of this._abos)e.then(t=>t()).catch(()=>{});this._abos=[]}willUpdate(e){this._abonniere(),e.has("kindId")&&(this._daten=void 0,this._fehler="",this._erfolg="",this._lade())}async _lade(){if(!this.hass||!this.kindId)return;let e=this.kindId;try{let t=await this._api.dashboard(e);e===this.kindId&&(this._daten=t,this._fehler="")}catch(t){this._fehler=x(this._t,t)}}async _frage(e,t={},i=1){this._abfrage=null,this._beschaeftigt=!0,this._erfolg="";try{await this._api.frageStellen(this.kindId,e,t,i),this._fehler="",this._erfolg=this._t(i>1?"fragen_gesendet":"frage_gesendet")}catch(n){this._fehler=x(this._t,n)}finally{this._beschaeftigt=!1,await this._lade()}}_jetztFragen(e=null){let t=this._daten?.faecher??[],i=t.find(n=>n.id===e)??(t.length===1?t[0]:void 0);this._setzeAbfrage({fachId:i?.id??null,modus:"alle",lektionen:new Set,bereiche:new Set,ids:new Set,seit:"",seiteVon:"",seiteBis:"",aufgaben:[],fehlerquote:"",frist:"",anzahl:jt,umfang:null,fehler:""}),i&&this._ladeAufgaben(i.id)}async _ladeAufgaben(e){try{let t=await this._api.aufgaben(e);this._abfrage?.fachId===e&&(this._abfrage={...this._abfrage,aufgaben:t})}catch(t){this._abfrage?.fachId===e&&(this._abfrage={...this._abfrage,fehler:x(this._t,t)})}}async _brichFrageAb(){if(window.confirm(this._t("frage_abbrechen_frage"))){try{await this._api.frageAbbrechen(this.kindId),this._fehler=""}catch(e){this._fehler=x(this._t,e)}await this._lade()}}async _brichSimulationAb(){if(window.confirm(this._t("sim_abbrechen_frage"))){try{await this._api.simulationAbbrechen(this.kindId),this._fehler=""}catch(e){this._fehler=x(this._t,e)}await this._lade()}}async _setzeAktiv(e){try{await this._api.setzeAktiv(this.kindId,e),this._fehler=""}catch(t){this._fehler=x(this._t,t)}await this._lade()}_oeffne(e,t){this.dispatchEvent(new CustomEvent("lh-oeffnen",{detail:{ziel:e,fachId:t}}))}_zeit(e){if(!e)return"";let t=new Date(e),i=this.hass?.language??"en",n=new Date().toDateString()===t.toDateString();return t.toLocaleString(i,{...n?{}:{weekday:"short",day:"2-digit",month:"2-digit"},hour:"2-digit",minute:"2-digit"})}_uhr(e){return e?new Date(e).toLocaleTimeString(this.hass?.language??"en",{hour:"2-digit",minute:"2-digit"}):""}_datum(e){return new Date(`${e}T00:00:00`).toLocaleDateString(this.hass?.language??"en",{weekday:"short",day:"2-digit",month:"2-digit"})}_tage(e){return e<=0?this._t("heute"):e===1?this._t("morgen"):this._t("in_tagen",{n:e})}_balken(e,t=!1){let i=this.hass?.themes?.darkMode?rt:at,n=e.reduce((h,d)=>h+d,0),s=this._t,l=e.map((h,d)=>`${s("box",{n:d+1})}: ${h}`).join(", ");return r`
      <div class="balken ${t?"gross":""}" role="img" aria-label=${l}>
        ${n===0?c:e.map((h,d)=>h===0?c:r`<span
                    style="flex: ${h}; background: ${i[d]??""}"
                    title="${s("box",{n:d+1})}: ${s("karten",{n:h})}"
                  ></span>`)}
      </div>
    `}_legende(e){let t=this.hass?.themes?.darkMode?rt:at;return r`
      <div class="legende">
        ${e.map((i,n)=>r`
            <span>
              <i style="background: ${t[n]??""}"></i>${this._t("box",{n:n+1})}:
              <b>${i}</b>
            </span>
          `)}
      </div>
    `}render(){let e=this._t,t=this._daten;return r`
      ${this._fehler?r`<div class="meldung fehler" role="alert">
            <span>${this._fehler}</span>
          </div>`:c}
      ${this._erfolg?r`<div class="meldung" role="status">
            <span>${this._erfolg}</span>
            <button
              class="icon"
              aria-label=${e("schliessen")}
              @click=${()=>{this._erfolg=""}}
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>`:c}
      ${t?r`
            <div class="raster">
              <div class="card breit">${this._status(t)}</div>
              <div class="kacheln breit">${this._kacheln(t)}</div>
              <div class="card">${this._arbeiten(t)}</div>
              <div class="card">${this._faecher(t)}</div>
              <div class="card">${this._lernstand(t)}</div>
              <div class="card">${this._schwierig(t)}</div>
            </div>
            ${t.verlauf?r`<lh-fortschritt
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .kindId=${this.kindId}
                  .wochenreport=${t.wochenreport??!1}
                  .stand=${t}
                ></lh-fortschritt>`:c}
          `:this._fehler?c:r`<div class="leer">${e("laden")}</div>`}
      ${this._abfrage&&t?this._abfrageDialog(t,this._abfrage):c}
    `}_status(e){let t=this._t,i=e.zustand,n=i.offene_frage,s=i.pausiert?i.pausiert_bis?t("status_pausiert_bis",{zeit:this._zeit(i.pausiert_bis)}):t("status_pausiert"):n||i.naechste_abfrage||i.simulation?t("status_aktiv"):t("status_nichts_geplant"),l=!i.pausiert&&!n&&!i.naechste_abfrage&&!i.simulation,h=(d,g)=>r`
      <div class="fakt">
        <div class="klein">${d}</div>
        <div class="wert">${g}</div>
      </div>
    `;return r`
      <div class="status">
        <div class="zustand ${i.pausiert||l?"aus":"gut"}">
          <ha-icon
            icon=${i.pausiert?"mdi:pause-circle":l?"mdi:calendar-blank":"mdi:check-circle"}
          ></ha-icon>
          ${s}
        </div>
        <div class="fakten">
          ${i.simulation?h(t("sim_laeuft"),t("sim_laeuft_text",{nr:Math.min(i.simulation.nummer,i.simulation.anzahl),n:i.simulation.anzahl})):c}
          ${h(t("offene_frage"),n?t(n.angehalten?"offene_frage_angehalten":n.timeout_um?"offene_frage_text":"offene_frage_ohne_frist",{fach:n.fach,von:this._uhr(n.gestellt_um),bis:this._uhr(n.timeout_um)}):t("keine_offene_frage"))}
          ${i.abfrage&&n?h(t("abfrage_laeuft"),this._abfrageText(n.fach,i.abfrage)):c}
          ${h(t("naechste_abfrage"),n&&!i.pausiert?t("nach_offener_frage"):i.naechste_abfrage&&!i.pausiert?this._zeit(i.naechste_abfrage):t("keine_geplant"))}
          ${h(t("letzte_frage"),i.letzte_frage_um?this._zeit(i.letzte_frage_um):t("noch_nie"))}
        </div>
        <div class="knoepfe">
          ${l?c:r`<button
                @click=${()=>this._setzeAktiv(!i.aktiv||i.pausiert)}
              >
                ${t(i.pausiert?"fortsetzen":"pausieren")}
              </button>`}
          ${n&&!i.simulation?r`<button class="gefahr" @click=${this._brichFrageAb}>
                ${t("frage_abbrechen")}
              </button>`:c}
          ${i.simulation?r`<button class="gefahr" @click=${this._brichSimulationAb}>
                ${t("sim_abbrechen")}
              </button>`:c}
        </div>
      </div>
    `}_kacheln(e){let t=this._t,i=e.statistik,n=(s,l,h)=>r`
      <div class="kachel">
        <div class="zahl">${l}</div>
        <div class="name"><ha-icon icon=${h}></ha-icon>${s}</div>
      </div>
    `;return r`
      ${n(t("kz_gefragt"),String(i.gefragt),"mdi:chat-question")}
      ${n(t("kz_richtig"),String(i.richtig),"mdi:check")}
      ${n(t("kz_falsch"),String(i.falsch),"mdi:close")}
      ${i.teilweise?n(t("kz_teilweise"),String(i.teilweise),"mdi:circle-half-full"):c}
      ${n(t("kz_unbeantwortet"),String(i.unbeantwortet),"mdi:timer-sand")}
      ${n(t("kz_trefferquote"),i.trefferquote===null?"\u2013":`${Math.round(i.trefferquote)} %`,"mdi:bullseye-arrow")}
      ${n(t("kz_aufgaben"),String(i.aufgaben),"mdi:cards-outline")}
    `}_sicher(e){return e===null?c:r`<span class="klein" title=${this._t("sicher_hinweis")}>
          ${this._t("sicher",{n:e})}
        </span>`}_arbeiten(e){let t=this._t,i=n=>r`
      <div class="zeile">
        <div class="countdown ${n.tage_bis<=2?"bald":""}">
          <div class="tage">${this._tage(n.tage_bis)}</div>
          <div class="klein">${this._datum(n.datum)}</div>
        </div>
        <div class="mitte">
          <div class="titel">
            ${n.fach}: ${n.thema}
            <span class="marke">
              ${t(n.art==="hue"?"art_hue":"art_arbeit")}
            </span>
          </div>
          <div class="klein">
            ${t("arbeit_umfang",{n:n.aufgaben})} ·
            ${t("heute_abfragen",{n:n.abfragen_heute})}
          </div>
          <div class="mini">${this._balken(n.boxen)} ${this._sicher(n.sicher)}</div>
        </div>
        <button
          class="icon"
          title=${t("arbeiten_oeffnen")}
          aria-label=${t("arbeiten_oeffnen")}
          @click=${()=>this._oeffne("arbeiten",n.fach_id)}
        >
          <ha-icon icon="mdi:chevron-right"></ha-icon>
        </button>
      </div>
    `;return r`
      <h2>${t("anstehend")}</h2>
      ${e.arbeiten.length?e.arbeiten.map(i):r`<div class="leer">${t("keine_anstehend")}</div>`}
      ${this._vorschlaege(e)}
    `}_vorschlaege(e){let t=e.kalender;if(!t)return c;let i=this._t,n=e.vorschlaege??[],s=l=>r`
      <div class="zeile">
        <div class="countdown">
          <div class="klein">${this._datum(l.datum)}</div>
        </div>
        <div class="mitte">
          <div class="titel">
            ${l.text}
            <span class="marke">
              ${i(l.art==="hue"?"art_hue":"art_arbeit")}
            </span>
          </div>
          ${l.gleicher_tag.length?r`<div class="klein">
                ${i("vorschlag_gleicher_tag",{arbeiten:l.gleicher_tag.join(", ")})}
              </div>`:c}
        </div>
        <button class="primaer" @click=${()=>this._trageEin(l)}>
          ${i("vorschlag_eintragen")}
        </button>
        <button @click=${()=>this._ignoriere(l)}>
          ${i("vorschlag_ignorieren")}
        </button>
      </div>
    `;return r`
      <h2 class="abstand">${i("vorschlaege")}</h2>
      ${t.fehler?r`<div class="klein warnung" role="status">${i("kalender_fehler")}</div>`:c}
      ${n.length?n.map(s):r`<div class="leer">${i("keine_vorschlaege")}</div>`}
      <div class="kalenderfuss">
        <span class="klein">
          ${t.geprueft_um?i("kalender_geprueft",{zeit:this._zeit(t.geprueft_um)}):i("kalender_nie")}
        </span>
        <button ?disabled=${this._kalenderLaeuft} @click=${this._pruefeKalender}>
          ${i("kalender_pruefen")}
        </button>
        ${t.ignoriert?r`<button @click=${this._zeigeIgnorierte}>
              ${i("kalender_ignorierte",{n:t.ignoriert})}
            </button>`:c}
      </div>
    `}_trageEin(e){this.dispatchEvent(new CustomEvent("lh-vorschlag",{detail:{vorschlag:e}}))}async _ignoriere(e){try{await this._api.kalenderIgnorieren(this.kindId,e.uid),this._fehler=""}catch(t){this._fehler=x(this._t,t)}await this._lade()}async _zeigeIgnorierte(){try{await this._api.kalenderWiederherstellen(this.kindId),this._fehler=""}catch(e){this._fehler=x(this._t,e)}await this._lade()}async _pruefeKalender(){this._kalenderLaeuft=!0;try{await this._api.kalenderPruefen(this.kindId),this._fehler=""}catch(e){this._fehler=x(this._t,e)}finally{this._kalenderLaeuft=!1}await this._lade()}_faecher(e){let t=this._t,i=this.hass?.language??"en",n=s=>r`
      <div class="zeile">
        <div class="mitte">
          <div class="titel">
            ${s.name}
            <span class="klein">
              ${s.typ==="mathe"?t("fachart_mathe"):s.typ==="sach"?t("fachart_sach"):s.sprachen.map(l=>E(i,l)).join(" \u2194 ")}
            </span>
          </div>
          <div class="klein">
            ${t("fach_aufgaben",{n:s.aufgaben,l:s.lektionen})}
            ${s.ungeprueft?r` · ${t("ungeprueft",{n:s.ungeprueft})}`:c}
            ${s.trefferquote===null?c:r` · ${t("kz_trefferquote")} ${Math.round(s.trefferquote)} %`}
          </div>
          <div class="mini">${this._balken(s.boxen)} ${this._sicher(s.sicher)}</div>
        </div>
        <div class="fachknoepfe">
          <button
            ?disabled=${this._beschaeftigt||s.aufgaben===0}
            @click=${()=>this._jetztFragen(s.id)}
          >
            ${t("jetzt_fragen_kurz")}
          </button>
          <button @click=${()=>this._oeffne("aufgaben",s.id)}>
            ${t("aufgaben_oeffnen")}
          </button>
        </div>
      </div>
    `;return r`
      <h2>${t("faecher_titel")}</h2>
      ${e.faecher.length?e.faecher.map(n):r`<div class="leer">${t("keine_faecher")}</div>`}
    `}_lernstand(e){let t=this._t,i=e.statistik.boxen,n=i.reduce((s,l)=>s+l,0);return r`
      <h2>${t("lernstand")}</h2>
      ${n===0?r`<div class="leer">${t("keine_karten")}</div>`:r`
            ${this._balken(i,!0)} ${this._legende(i)}
            <p class="klein">${t("lernstand_hinweis")}</p>
          `}
    `}_schwierig(e){let t=this._t;return r`
      <h2>
        ${t(e.faecher.some(i=>i.typ!=="vokabel")?"schwierig_aufgaben":"schwierig")}
      </h2>
      ${e.schwierig.length?e.schwierig.map(i=>r`
              <div class="zeile">
                <div class="mitte">
                  <div class="titel">
                    ${i.aufgabe??Object.values(i.frage??{}).join(" \u2013 ")}
                  </div>
                  <div class="klein">
                    ${i.fach} · ${t("fehler_mal",{n:i.falsch})}
                  </div>
                </div>
                <span class="marke ${i.fehlerquote>=50?"warn":""}">
                  ${Math.round(i.fehlerquote)} %
                </span>
              </div>
            `):r`<div class="leer">${t("keine_schwierig")}</div>`}
    `}_abfrageText(e,t){let i=this._t,n=[],s=(o,_)=>o!=null&&_!=null?i("abfrage_seiten",{von:o,bis:_}):o!=null?i("abfrage_ab_seite",{n:o}):_!=null?i("abfrage_bis_seite",{n:_}):"",l=new Map((t.lektion_seiten??[]).map(o=>[o.lektion,s(o.von,o.bis)])),h=t.lektionen?.length?t.lektionen:[...l.keys()];h.length&&n.push(h.map(o=>l.get(o)?`${o} ${l.get(o)}`:o).join(", "));let d=s(t.seite_von,t.seite_bis);d&&n.push(d),t.bereiche?.length&&n.push(i("abfrage_themen",{n:t.bereiche.length})),t.aufgabe_ids?.length&&n.push(i("abfrage_einzeln",{n:t.aufgabe_ids.length})),t.fehlerquote_ab!=null&&n.push(i("abfrage_ab_fehlerquote",{n:t.fehlerquote_ab}));let g=n.length?`${e} (${n.join(" \xB7 ")})`:e;return i("abfrage_laeuft_text",{ort:g,n:t.weitere})}_auswahl(e,t){if(!e.faecher.find(l=>l.id===t.fachId))return{};let n=Math.round(Number(t.fehlerquote)),s=t.fehlerquote.trim()!==""&&Number.isFinite(n)&&n>=1?Math.min(n,100):null;return t.modus==="alle"?{fehlerquote_ab:s}:{lektionen:[...t.lektionen],bereiche:[...t.bereiche],aufgabe_ids:[...t.ids],fehlerquote_ab:s}}_setzeAbfrage(e){let t=this._daten;if(!t)return;let i=this._auswahl(t,e),n=++this._zaehlung;this._abfrage={...e,umfang:i===null?0:null,fehler:""},i!==null&&this._api.abfrageUmfang(this.kindId,e.fachId,i).then(s=>{n===this._zaehlung&&this._abfrage&&(this._abfrage={...this._abfrage,umfang:s})}).catch(s=>{n===this._zaehlung&&this._abfrage&&(this._abfrage={...this._abfrage,umfang:0,fehler:x(this._t,s)})})}_abfrageDialog(e,t){let i=this._t,n=()=>{this._abfrage=null},s=e.faecher.find(p=>p.id===t.fachId)??null,l=s?.lektionsliste??[],h=s?.bereiche??[],[d="",g=""]=s?.sprachen??[],o=t.umfang,_=p=>{this._setzeAbfrage({...t,...p})},f=p=>p.name??i(`bereich_standard_${p.art}`),k=p=>{let A=e.faecher.find(T=>T.id===p);_({fachId:A?A.id:null,modus:"alle",lektionen:new Set,bereiche:new Set,ids:new Set,seit:"",seiteVon:"",seiteBis:"",aufgaben:[]}),A&&this._ladeAufgaben(A.id)},z=(p,A,T)=>{let be=new Set(t[p]);T?be.add(A):be.delete(A),_({[p]:be})},y=p=>{let A=new Set(t.ids);for(let T of t.aufgaben)p(T)&&A.add(T.id);_({ids:A})},w=()=>{let p=Math.min(lt,Math.max(1,Math.round(t.anzahl)||1)),A=this._auswahl(e,t);if(A!==null){let T=t.frist.trim()===""?NaN:Math.round(Number(t.frist));this._frage(t.fachId,Number.isFinite(T)&&T>=0?{...A,frist_minuten:T}:A,p)}},j=s!==null&&t.modus==="auswahl";return r`
      <div
        class="overlay"
        @click=${p=>{p.target===p.currentTarget&&n()}}
      >
        <div class="dialog" role="dialog" aria-modal="true" style="width: min(640px, 100%)">
          <h2>${i("abfrage_titel")}</h2>
          <label class="feld">
            ${i("abfrage_fach")}
            <select
              .value=${t.fachId??""}
              @change=${p=>k(p.target.value)}
            >
              ${e.faecher.length>1?r`<option value="" ?selected=${t.fachId===null}>
                    ${i("egal_welches")}
                  </option>`:c}
              ${e.faecher.map(p=>r`
                  <option
                    value=${p.id}
                    ?selected=${p.id===t.fachId}
                    ?disabled=${p.aufgaben===0}
                  >
                    ${p.name} (${p.aufgaben})
                  </option>
                `)}
            </select>
          </label>
          ${s?r`
                <fieldset>
                  <legend>${i("abfrage_aufgaben")}</legend>
                  <div class="chips" style="margin-bottom: 10px">
                    ${["alle","auswahl"].map(p=>r`
                        <label class="feld zeile">
                          <input
                            type="radio"
                            name="abfrage-modus"
                            .checked=${t.modus===p}
                            @change=${()=>_({modus:p})}
                          />
                          ${i(p==="alle"?"auswahl_alle":"auswahl_gezielt")}
                        </label>
                      `)}
                  </div>
                  ${j?r`
                        ${h.length>1?r`
                              <div class="klein">${i("schnell_bereiche")}</div>
                              <div class="chips" style="margin: 6px 0 12px">
                                ${h.map(p=>r`
                                    <label class="feld zeile">
                                      <input
                                        type="checkbox"
                                        .checked=${t.bereiche.has(p.id)}
                                        @change=${A=>z("bereiche",p.id,A.target.checked)}
                                      />
                                      ${f(p)}
                                      <span class="klein">(${p.aufgaben})</span>
                                    </label>
                                  `)}
                              </div>
                            `:c}
                        ${l.length?r`
                              <div class="klein">${i("schnell_lektionen")}</div>
                              <div class="chips" style="margin: 6px 0 12px">
                                ${l.map(p=>r`
                                    <label class="feld zeile">
                                      <input
                                        type="checkbox"
                                        .checked=${t.lektionen.has(p.name)}
                                        @change=${A=>z("lektionen",p.name,A.target.checked)}
                                      />
                                      ${p.name}
                                      <span class="klein">(${p.aufgaben})</span>
                                    </label>
                                  `)}
                              </div>
                            `:c}
                        <div class="leiste" style="align-items: flex-end">
                          <label class="feld" style="flex: 1; max-width: 220px">
                            ${i("schnell_seit")}
                            <input
                              type="date"
                              .value=${t.seit}
                              @change=${p=>_({seit:p.target.value})}
                            />
                          </label>
                          <button
                            ?disabled=${!t.seit}
                            @click=${()=>y(p=>p.erstellt.slice(0,10)>=t.seit)}
                          >
                            ${i("hinzufuegen")}
                          </button>
                        </div>
                        <div class="leiste" style="align-items: flex-end">
                          <label class="feld" style="flex: 1; max-width: 220px">
                            ${i("schnell_seiten")}
                            <input
                              type="number"
                              min="1"
                              .value=${t.seiteVon}
                              @input=${p=>_({seiteVon:p.target.value})}
                            />
                          </label>
                          <label class="feld" style="flex: 1; max-width: 220px">
                            ${i("schnell_seiten_bis")}
                            <input
                              type="number"
                              min="1"
                              .value=${t.seiteBis}
                              @input=${p=>_({seiteBis:p.target.value})}
                            />
                          </label>
                          <button
                            ?disabled=${!t.seiteVon&&!t.seiteBis}
                            @click=${()=>y(p=>p.seite!==null&&ge(p.seite,t.seiteVon,t.seiteBis))}
                          >
                            ${i("hinzufuegen")}
                          </button>
                          <span class="abstand"></span>
                          <button
                            ?disabled=${t.ids.size===0}
                            @click=${()=>_({ids:new Set})}
                          >
                            ${i("auswahl_leeren")}
                          </button>
                        </div>
                        <div class="klein">${i("einzelne_aufgaben")} (${t.ids.size})</div>
                        <div class="liste" style="margin-top: 6px; max-height: 260px; overflow: auto">
                          <div class="eintrag kopf">
                            <span class="haken"></span>
                            <span style="flex: 1">${i("spalte_aufgabe")}</span>
                            <span class="seite">${i("spalte_seite")}</span>
                            <span class="lektion">${i("spalte_lektion")}</span>
                          </div>
                          ${t.aufgaben.map(p=>{let A=p.lektion!==null&&t.lektionen.has(p.lektion)||t.bereiche.has(p.bereich??"standard");return r`
                              <label>
                                <input
                                  type="checkbox"
                                  .checked=${A||t.ids.has(p.id)}
                                  ?disabled=${A}
                                  @change=${T=>z("ids",p.id,T.target.checked)}
                                />
                                <span style="flex: 1">${_e(p,d,g)}</span>
                                <span class="klein seite">${p.seite??""}</span>
                                <span class="klein lektion">${p.lektion??""}</span>
                              </label>
                            `})}
                        </div>
                      `:c}
                </fieldset>
                <div class="raster">
                  <label class="feld">
                    ${i("abfrage_fehlerquote")}
                    <input
                      type="number"
                      min="1"
                      max="100"
                      .value=${t.fehlerquote}
                      @input=${p=>_({fehlerquote:p.target.value})}
                    />
                  </label>
                </div>
                <div class="klein">${i("abfrage_filter_hinweis")}</div>
              `:c}
          <label class="feld">
            ${i("abfrage_anzahl")}
            <input
              type="number"
              min="1"
              max=${lt}
              .value=${String(t.anzahl)}
              @input=${p=>{this._abfrage={...t,anzahl:Number(p.target.value)}}}
            />
          </label>
          <label class="feld">
            ${i("abfrage_frist")}
            <input
              type="number"
              min="0"
              max="1440"
              .value=${t.frist}
              @input=${p=>{this._abfrage={...t,frist:p.target.value}}}
            />
          </label>
          <div class="klein">${i("abfrage_frist_hinweis")}</div>
          ${t.fehler?r`<div class="fehler">${t.fehler}</div>`:c}
          <div class="klein">
            ${o===null?i("abfrage_umfang_laedt"):i("abfrage_umfang",{n:o})}
          </div>
          <div class="aktionen">
            <button @click=${n}>${i("abbrechen")}</button>
            <button
              class="primaer"
              ?disabled=${this._beschaeftigt||!o}
              @click=${w}
            >
              ${i("abfrage_senden")}
            </button>
          </div>
        </div>
      </div>
    `}};b([F({attribute:!1})],L.prototype,"hass",2),b([F({type:Boolean,reflect:!0})],L.prototype,"narrow",2),b([F()],L.prototype,"kindId",2),b([m()],L.prototype,"_daten",2),b([m()],L.prototype,"_fehler",2),b([m()],L.prototype,"_kalenderLaeuft",2),b([m()],L.prototype,"_erfolg",2),b([m()],L.prototype,"_abfrage",2),b([m()],L.prototype,"_beschaeftigt",2);customElements.get("lh-uebersicht")||customElements.define("lh-uebersicht",L);var W="standard";var ht=.012,fe=30,D=4;function Ut(u){if(!u)return"";let a=new Date(u);if(Number.isNaN(a.getTime()))return"";let e=t=>String(t).padStart(2,"0");return`${a.getFullYear()}-${e(a.getMonth()+1)}-${e(a.getDate())}T${e(a.getHours())}:${e(a.getMinutes())}`}function ot(u){return u.split(`
`).map(a=>a.trim()).filter(a=>a.length>0)}var ct={aufgabe:"",loesung:"",alternativen:""},Kt=["fremdsprache","mathe","sach"],Ht=["en","fr","es","it","la","de"],Le={typ:"fremdsprache",name:"",sprache:"en"},P="\0ohne",ie={suche:"",lektion:"",quelle:"",geprueft:"",fehlerquote:"",von:"",bis:"",seiteVon:"",seiteBis:""};function v(u){return u.target.value}function B(u){return u.target.checked}function ne(u){return u.split("|").map(a=>a.trim()).filter(a=>a.length>0)}var ut=(()=>{try{return new URL(import.meta.url).searchParams.get("v")}catch{return null}})();function Ct(u){return new Promise(a=>setTimeout(a,u))}var $=class extends R{constructor(){super(...arguments);this.narrow=!1;this._kindId="";this._fachId="";this._aufgaben=[];this._tab="uebersicht";this._filter={...ie};this._auswahl=new Set;this._entwurf=null;this._dialog=null;this._generieren=null;this._bildEntwurf=null;this._bildAdressen={};this._grossbild="";this._bildText="";this._seiten=null;this._saetze=null;this._foto=null;this._label=null;this._labelZug=null;this._sim=null;this._veraltet=!1;this._nachgerechnet=null;this._nurIds=null;this._meldung=null;this._laedt=!0;this._beschaeftigt=!1;this._importText="";this._importLektion="";this._importTrenner="";this._importGeprueft=!0;this._vorschau=null;this._mitStatistik=!1;this._jsonDaten=null;this._arbeit=null;this._neuesFach=null;this._dialogFehler="";this._lektionName="";this._bereichId="";this._bereichName="";this._bereichArt="vokabel";this._bereichUmbenennen=null;this._jsonLektion="";this._gestartet=!1;this._taste=e=>{e.key==="Escape"&&(this._dialog?this._schliesseDialog():this._entwurf&&(this._entwurf=null))}}static{this.styles=Y}get _t(){return Q(this.hass?.language??"en")}get _api(){return new K(this.hass)}get _fach(){return this._uebersicht?.faecher.find(e=>e.id===this._fachId)}get _faecherDesKindes(){return(this._uebersicht?.faecher??[]).filter(e=>e.kind_id===this._kindId)}get _arbeitenDesFachs(){return(this._uebersicht?.arbeiten??[]).filter(e=>e.fach_id===this._fachId).sort((e,t)=>e.datum.localeCompare(t.datum))}connectedCallback(){super.connectedCallback(),window.addEventListener("keydown",this._taste)}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("keydown",this._taste)}updated(e){e.has("hass")&&this.hass&&!this._gestartet&&(this._gestartet=!0,this._ladeUebersicht())}async _ladeUebersicht(e=0){let t=0;for(;;)try{this._uebersicht=await this._api.uebersicht();break}catch(n){if(n.code==="not_loaded"&&t<e){t+=1,await Ct(500);continue}this._zeigeFehler(n),this._laedt=!1;return}let i=this._uebersicht;this._veraltet=!!(ut&&i.panel_version&&i.panel_version!==ut),i.kinder.some(n=>n.id===this._kindId)||(this._kindId=i.kinder[0]?.id??""),this._faecherDesKindes.some(n=>n.id===this._fachId)||(this._fachId=this._faecherDesKindes[0]?.id??""),await this._ladeAufgaben(),this._laedt=!1}async _ladeAufgaben(){if(!this._fachId){this._aufgaben=[];return}try{this._aufgaben=await this._api.aufgaben(this._fachId)}catch(t){this._aufgaben=[],this._zeigeFehler(t)}let e=new Set(this._aufgaben.map(t=>t.id));this._auswahl=new Set([...this._auswahl].filter(t=>e.has(t))),this._ladeBildAdressen()}async _ladeBildAdressen(){let e=new Set;for(let t of this._aufgaben){let i=t.typ==="mathe"?t.bild:t.typ==="sach"?t.bild??t.quelle_bild:null;i&&!(i in this._bildAdressen)&&e.add(i)}for(let t of e)try{let i=await this._api.bildAdresse(t);this._bildAdressen={...this._bildAdressen,[t]:i}}catch{}}async _neuLaden(e=0){await this._ladeUebersicht(e)}_zeigeFehler(e){this._meldung={text:x(this._t,e),fehler:!0}}_zeigeErfolg(e){this._meldung={text:e,fehler:!1}}_gefiltert(){let e=this._filter,t=e.suche.trim().toLowerCase(),i=e.fehlerquote===""?null:Number(e.fehlerquote),n=this._nurIds&&this._aufgaben.some(s=>this._nurIds?.has(s.id))?this._nurIds:null;return this._aufgaben.filter(s=>{if(n&&!n.has(s.id)||this._aktiverBereich&&(s.bereich??W)!==this._aktiverBereich||t&&![...s.typ==="mathe"?[s.aufgabe,s.loesung,...s.alternativen]:s.typ==="sach"?[s.frage,s.antwort,...s.kernpunkte,...s.falsche_optionen]:[...Object.values(s.frage),...Object.values(s.alternativen).flat()],s.hinweis??""].join(" ").toLowerCase().includes(t)||e.lektion===P&&s.lektion||e.lektion&&e.lektion!==P&&s.lektion!==e.lektion||e.quelle&&s.quelle!==e.quelle||e.geprueft&&s.geprueft!==(e.geprueft==="ja")||i!==null&&!Number.isNaN(i)&&(s.fehlerquote===null||s.fehlerquote<i))return!1;let l=s.erstellt.slice(0,10);return!(e.von&&l<e.von||e.bis&&l>e.bis||!ge(s.seite,e.seiteVon,e.seiteBis))})}async _waehleKind(e){e!==this._kindId&&(this._kindId=e,this._fachId=this._faecherDesKindes[0]?.id??"",this._zuruecksetzen(),await this._ladeAufgaben())}async _waehleFach(e){this._fachId=e,this._zuruecksetzen(),await this._ladeAufgaben()}_zuruecksetzen(){this._auswahl=new Set,this._entwurf=null,this._bereichId="",this._filter={...ie}}get _bereiche(){return this._fach?.bereiche??[]}get _hatBereiche(){return this._bereiche.length>0}get _mehrere(){return this._bereiche.length>1}get _aktiverBereich(){return this._hatBereiche?this._bereiche.some(e=>e.id===this._bereichId)?this._bereichId:this._mehrere?"":this._bereiche[0]?.id??"":""}_ansichtVon(e){return e.art==="satz"?"sach":this._fach?.typ??"vokabel"}get _ansicht(){return this._bereiche.find(t=>t.id===this._aktiverBereich)?.art==="satz"?"sach":this._fach?.typ??"vokabel"}get _satzAnsicht(){return this._ansicht==="sach"&&this._fach?.typ==="vokabel"}_neuBereich(){let e=this._aktiverBereich;return e&&e!==W?e:null}_bereichName_(e){return e.name??this._t(`bereich_standard_${e.art}`)}_oeffneBereiche(){this._bereichName="",this._bereichUmbenennen=null,this._dialogFehler="",this._dialog="bereiche"}async _bereichAnlegen(){let e=this._bereichName.trim();if(!(!e||!this._fachId)){this._dialogFehler="";try{await this._api.bereichHinzufuegen(this._fachId,e,this._fach?.typ==="vokabel"?this._bereichArt:null),this._bereichName="",this._zeigeErfolg(this._t("bereich_angelegt",{name:e})),await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}}}async _bereichUmbenennenSpeichern(){let e=this._bereichUmbenennen;if(!(!e||!e.name.trim())){this._dialogFehler="";try{await this._api.bereichUmbenennen(this._fachId,e.id,e.name.trim()),this._bereichUmbenennen=null,await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}}}async _bereichLoeschen(e){this._dialogFehler="";try{await this._api.bereichLoeschen(this._fachId,e),this._bereichId===e&&(this._bereichId=""),await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}}async _setzeHilfeSenden(e,t){let i=this._aufgaben.filter(n=>e.includes(n.id)&&n.typ==="sach"&&(n.form==="luecke"||n.form==="auswahl")&&n.hilfe&&(n.hilfe_senden??!1)!==t);if(!(!i.length||!this._fachId)){this._beschaeftigt=!0;try{for(let n of i)await this._api.aufgabeAendern(this._fachId,n.id,{hilfe_senden:t});this._zeigeErfolg(this._t("hilfe_gesetzt",{n:i.length})),await this._neuLaden()}catch(n){this._zeigeFehler(n)}finally{this._beschaeftigt=!1}}}async _verschiebe(e){let t=[...this._auswahl];if(!(!e||!t.length||!this._fachId)){this._beschaeftigt=!0;try{for(let i of t)await this._api.aufgabeAendern(this._fachId,i,{bereich:e});this._auswahl=new Set,this._zeigeErfolg(this._t("verschoben",{n:t.length})),await this._neuLaden()}catch(i){this._zeigeFehler(i)}finally{this._beschaeftigt=!1}}}_setzeFilter(e,t){this._filter={...this._filter,[e]:t},this._nurIds=null}_umschalten(e,t){let i=new Set(this._auswahl);t?i.add(e):i.delete(e),this._auswahl=i}_alleUmschalten(e,t){let i=new Set(this._auswahl);for(let n of e)t?i.add(n.id):i.delete(n.id);this._auswahl=i}_bearbeite(e){let[t="",i=""]=this._fach?.sprachen??[],n=e?.typ==="mathe"?e:null,s=e?.typ==="vokabel"?e:null,l=e?.typ==="sach"?e:null;this._entwurf={id:e?.id??null,art:e?.typ??this._ansicht,a:n?n.aufgabe:l?l.frage:s?.frage[t]??"",b:n?n.loesung:l?l.antwort:s?.frage[i]??"",form:l?.form??(this._satzAnsicht&&!e?"luecke":"kurz"),kernpunkte:(l?.kernpunkte??[]).join(`
`),falsche:(l?.falsche_optionen??[]).join(`
`),altA:(s?.alternativen[t]??[]).join(" | "),altB:(n?n.alternativen:l?l.alternativen:s?.alternativen[i]??[]).join(" | "),rechenweg:(n?.rechenweg??[]).join(`
`),schwierigkeit:n?.schwierigkeit?.toString()??"",hinweis:e?.hinweis??"",hilfe:l?.hilfe??"",hilfeSenden:l?.hilfe_senden??!1,seite:e?.seite?.toString()??"",lektion:e?.lektion??(this._filter.lektion===P?"":this._filter.lektion),geprueft:e?.geprueft??!0}}_setzeEntwurf(e,t){this._entwurf&&(this._entwurf={...this._entwurf,[e]:t})}async _speichereAufgabe(){let e=this._entwurf,t=this._fach;if(!e||!t)return;let[i="",n=""]=t.sprachen,s={...t.typ==="mathe"?{aufgabe:e.a,loesung:e.b,alternativen:ne(e.altB),rechenweg:e.rechenweg.split(`
`).map(l=>l.trim()).filter(l=>l.length>0),schwierigkeit:e.schwierigkeit===""?null:Number(e.schwierigkeit)}:e.art==="sach"?{frage:e.a,antwort:e.b,form:e.form,kernpunkte:e.form==="kurz"?ot(e.kernpunkte):[],falsche_optionen:e.form==="auswahl"?ot(e.falsche):[],alternativen:e.form==="luecke"||e.form==="uebersetzung"||e.form==="beschriftung"?ne(e.altB):[],hilfe:(e.form==="luecke"||e.form==="auswahl")&&e.hilfe.trim()||null,hilfe_senden:(e.form==="luecke"||e.form==="auswahl")&&e.hilfeSenden}:{frage:{[i]:e.a,[n]:e.b},alternativen:{[i]:ne(e.altA),[n]:ne(e.altB)}},hinweis:e.hinweis||null,seite:e.seite.trim()===""?null:Number(e.seite),lektion:e.lektion||null,geprueft:e.geprueft,...e.id?{}:{bereich:this._neuBereich()}};this._beschaeftigt=!0;try{e.id?await this._api.aufgabeAendern(t.id,e.id,s):await this._api.aufgabeAnlegen(t.id,s),this._entwurf=null,this._zeigeErfolg(this._t("gespeichert")),await this._neuLaden()}catch(l){this._zeigeFehler(l)}finally{this._beschaeftigt=!1}}async _setzeGeprueft(e,t){try{await this._api.aufgabeAendern(e.fach_id,e.id,{geprueft:t}),await this._ladeAufgaben()}catch(i){this._zeigeFehler(i)}}async _freigeben(){let e=this._aufgaben.filter(t=>this._auswahl.has(t.id)&&!t.geprueft);if(e.length){this._beschaeftigt=!0;try{for(let t of e)await this._api.aufgabeAendern(t.fach_id,t.id,{geprueft:!0});this._auswahl=new Set,this._zeigeErfolg(this._t("freigegeben",{n:e.length}))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1,await this._neuLaden()}}}async _nachrechnen(){let e=[...this._auswahl];if(!(!e.length||!this._fachId)){this._beschaeftigt=!0,this._meldung={text:this._t("nachrechnen_laeuft"),fehler:!1};try{let t=await this._api.nachrechnen(this._fachId,e);await this._ladeAufgaben(),t.abweichend.length?(this._meldung=null,this._nachgerechnet=t,this._dialogFehler="",this._dialog="nachrechnen"):this._zeigeErfolg(this._t("nachgerechnet",{bestaetigt:t.bestaetigt,abweichend:0,offen:t.nicht_pruefbar}))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}_neueAufgabe(){this._fach?.typ==="mathe"?(this._dialogFehler="",this._dialog="aufgabenart"):this._bearbeite(null)}_oeffneBildaufgabe(){let e=this._filter.lektion===P?"":this._filter.lektion;this._bildEntwurf={datei:null,vorschau:"",einleitung:"",lektion:e,seite:"",teile:[{...ct}]},this._dialogFehler="",this._dialog="bildaufgabe"}_setzeBild(e,t){this._bildEntwurf&&(this._bildEntwurf={...this._bildEntwurf,[e]:t})}_bildGewaehlt(e){let t=e.target.files?.[0]??null,i=this._bildEntwurf;i&&(i.vorschau&&URL.revokeObjectURL(i.vorschau),this._bildEntwurf={...i,datei:t,vorschau:t?URL.createObjectURL(t):""})}_setzeTeil(e,t,i){let n=this._bildEntwurf;if(!n)return;let s=n.teile.map((l,h)=>h===e?{...l,[t]:i}:l);this._bildEntwurf={...n,teile:s}}async _speichereBildaufgabe(){let e=this._bildEntwurf,t=this._fach;if(!e||!t)return;let i=e.teile.filter(s=>s.aufgabe.trim()!==""&&s.loesung.trim()!=="");if(!e.datei){this._dialogFehler=this._t("bild_fehlt");return}if(!i.length){this._dialogFehler=this._t("teil_fehlt");return}this._beschaeftigt=!0,this._dialogFehler="";let n=0;try{let s=await this._api.bildHochladen(e.datei),l=e.einleitung.trim();for(let h of i)await this._api.aufgabeAnlegen(t.id,{aufgabe:l?`${l} ${h.aufgabe.trim()}`:h.aufgabe.trim(),loesung:h.loesung,alternativen:ne(h.alternativen),bild:s,lektion:e.lektion||null,bereich:this._neuBereich(),seite:e.seite.trim()===""?null:Number(e.seite)}),n+=1;this._schliesseDialog(),this._zeigeErfolg(this._t("bildaufgaben_gespeichert",{n}))}catch(s){this._dialogFehler=x(this._t,s)}finally{this._beschaeftigt=!1,n&&await this._neuLaden()}}async _erzeugeRechenwege(){let e=[...this._auswahl];if(!(!e.length||!this._fachId)){this._beschaeftigt=!0,this._meldung={text:this._t("rechenweg_erzeugen_laeuft"),fehler:!1};try{let t=await this._api.rechenwegeErzeugen(this._fachId,e);await this._ladeAufgaben(),this._zeigeErfolg(this._t("rechenwege_erzeugt",t))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}async _markiereGeprueft(){let e=[...this._auswahl];if(!(!e.length||!this._fachId)){this._beschaeftigt=!0;try{let t=await this._api.alsGeprueftMarkieren(this._fachId,e);await this._ladeAufgaben(),this._zeigeErfolg(this._t("selbst_nachgerechnet_fertig",{n:t}))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}async _uebernimmVorschlag(e){if(!(!e.length||!this._fachId)){this._beschaeftigt=!0;try{let t=await this._api.vorschlagUebernehmen(this._fachId,e),i=new Set(e);if(this._nachgerechnet){let n=this._nachgerechnet.abweichend.filter(s=>!i.has(s.id));this._nachgerechnet={...this._nachgerechnet,abweichend:n},!n.length&&this._dialog==="nachrechnen"&&this._schliesseDialog()}this._zeigeErfolg(this._t("uebernommen",{n:t})),await this._ladeAufgaben()}catch(t){this._dialog==="nachrechnen"?this._dialogFehler=x(this._t,t):this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}_uebernimmAlle(){let e=this._nachgerechnet?.abweichend??[],t=this._t("alle_uebernehmen_frage",{n:e.length,ki:e.filter(i=>i.durch==="ki").length});window.confirm(t)&&this._uebernimmVorschlag(e.map(i=>i.id))}_oeffneGenerieren(){let e=this._filter.lektion===P?"":this._filter.lektion;this._generieren={lektion:e,anzahl:10,schwierigkeit:"",beschreibung:""},this._dialogFehler="",this._dialog="generieren"}async _generiere(){let e=this._generieren;if(!(!e||!this._fachId)){this._beschaeftigt=!0,this._dialogFehler="";try{let t=await this._api.generieren(this._fachId,{anzahl:e.anzahl,lektion:e.lektion||null,schwierigkeit:e.schwierigkeit===""?null:Number(e.schwierigkeit),beschreibung:e.beschreibung.trim()||null,beispiel_ids:[...this._auswahl],bereich:this._neuBereich()});this._schliesseDialog(),this._auswahl=new Set,t.erzeugt&&(this._filter={...ie,geprueft:"nein"}),this._zeigeErfolg(this._t("generiert",{erzeugt:t.erzeugt,verworfen:t.verworfen,doppelt:t.uebersprungen})),await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}finally{this._beschaeftigt=!1}}}async _loesche(e){if(!(!e.length||!this._fachId)&&window.confirm(this._t("loeschen_frage",{n:e.length}))){this._beschaeftigt=!0;try{let t=await this._api.aufgabenLoeschen(this._fachId,e,!1),i=Object.keys(t.zugeordnet);if(i.length){let n=new Set(Object.values(t.zugeordnet).flat()),s=(this._uebersicht?.arbeiten??[]).filter(h=>n.has(h.id)).map(h=>`${h.thema} (${this._datum(h.datum)})`).join(", "),l=this._t("loeschen_warnung",{n:i.length,arbeiten:s});if(!window.confirm(l))return;t=await this._api.aufgabenLoeschen(this._fachId,e,!0)}this._zeigeErfolg(this._t("geloescht",{n:t.geloescht})),await this._neuLaden()}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}_schliesseDialog(){this._dialog=null,this._vorschau=null,this._jsonDaten=null,this._arbeit=null,this._neuesFach=null,this._generieren=null,this._nachgerechnet=null,this._bildEntwurf?.vorschau&&URL.revokeObjectURL(this._bildEntwurf.vorschau),this._bildEntwurf=null,this._grossbild="",this._bildText="";for(let e of this._seiten?.vorschauen??[])URL.revokeObjectURL(e);this._seiten=null;for(let e of this._foto?.vorschauen??[])URL.revokeObjectURL(e);this._foto=null,this._label?.adresse.startsWith("blob:")&&URL.revokeObjectURL(this._label.adresse),this._label=null,this._labelZug=null,this._sim=null,this._dialogFehler=""}_simVerfuegbar(e){return e.arbeit.simulierbar?.[e.weg]??fe}_oeffneSimulation(e){let t={arbeit:e,anzahl:10,weg:"ausdruck",seiten:null};t.anzahl=Math.max(1,Math.min(10,this._simVerfuegbar(t))),this._sim=t,this._dialogFehler="",this._dialog="simulation"}async _simuliere(){let e=this._sim;if(e){this._beschaeftigt=!0,this._dialogFehler="";try{let t=await this._api.simulieren(e.arbeit.id,e.anzahl,e.weg);if(t.weg==="messenger"){this._schliesseDialog(),this._zeigeErfolg(this._t("sim_gestartet",{n:t.anzahl})),this._tab="uebersicht";return}let i=[];for(let n of t.bilder)i.push(await this._api.bildAdresse(n));this._sim={...e,anzahl:t.anzahl,seiten:i}}catch(t){this._dialogFehler=x(this._t,t)}finally{this._beschaeftigt=!1}}}_druckeSimulation(){let e=this._sim?.seiten??[],t=window.open("","_blank");if(!t){this._dialogFehler=this._t("sim_druck_blockiert");return}let i=t.document;i.title=this._sim?.arbeit.thema??"";let n=i.createElement("style");n.textContent="@page{size:A4;margin:0}body{margin:0}img{display:block;width:100%;page-break-after:always}",i.head.append(n);let s=e.length;for(let l of e){let h=i.createElement("img");h.addEventListener("load",()=>{s-=1,s===0&&(t.focus(),t.print())}),h.src=new URL(l,window.location.origin).href,i.body.append(h)}}_oeffneFoto(){this._foto={dateien:[],vorschauen:[],lektion:this._filter.lektion===P?"":this._filter.lektion,zeilen:null},this._dialogFehler="",this._dialog="foto"}_fotoGewaehlt(e){let t=this._foto;if(!t)return;let i=[...e.target.files??[]];for(let s of t.vorschauen)URL.revokeObjectURL(s);let n=i.slice(0,D);this._dialogFehler=i.length>D?this._t("seiten_zu_viele",{n:D}):"",this._foto={...t,dateien:n,vorschauen:n.map(s=>URL.createObjectURL(s))}}async _leseFoto(){let e=this._foto,t=this._fach;if(!e||!e.dateien.length||!t)return;let[i="",n=""]=t.sprachen;this._beschaeftigt=!0,this._dialogFehler="";try{let s=[];for(let h of e.dateien)s.push(await this._api.bildHochladen(h,!0));let l=await this._api.fotoAuslesen(t.id,s);if(!l.zeilen.length){this._dialogFehler=this._t("foto_leer");return}this._foto={...e,zeilen:l.zeilen.map(h=>({an:!h.vorhanden&&!h.braucht_bild,a:l.typ==="mathe"?h.aufgabe??"":h.frage?.[i]??"",b:l.typ==="mathe"?h.loesung??"":h.frage?.[n]??"",hinweis:h.hinweis??"",seite:h.seite?.toString()??"",geaendert:!1,roh:h}))}}catch(s){this._dialogFehler=x(this._t,s)}finally{this._beschaeftigt=!1}}_setzeFotoZeile(e,t){let i=this._foto;i?.zeilen&&(this._foto={...i,zeilen:i.zeilen.map((n,s)=>s===e?{...n,...t}:n)})}async _uebernimmFoto(){let e=this._foto,t=this._fach;if(!e?.zeilen||!t)return;let[i="",n=""]=t.sprachen,s=e.zeilen.filter(l=>l.an).map(l=>{let h=l.seite.trim()===""?null:Number(l.seite);return t.typ==="mathe"?{aufgabe:l.a,loesung:l.b,seite:h,verifikation:l.geaendert?"keine":l.roh.verifikation}:{frage:{[i]:l.a,[n]:l.b},alternativen:l.geaendert?{}:l.roh.alternativen??{},hinweis:l.hinweis||null,seite:h}});if(s.length){this._beschaeftigt=!0,this._dialogFehler="";try{let l=await this._api.fotoUebernehmen(t.id,s,e.lektion||null,this._neuBereich());if(l.fehler.length&&!l.importiert){this._dialogFehler=this._t("foto_fehler",{n:l.fehler.length});return}this._schliesseDialog(),this._zeigeErfolg(this._t("foto_fertig",{n:l.importiert,doppelt:l.uebersprungen,fehler:l.fehler.length})),await this._neuLaden()}catch(l){this._dialogFehler=x(this._t,l)}finally{this._beschaeftigt=!1}}}_originalBild(e){let t=this._aufgaben.find(i=>i.id===e);return t?.typ==="sach"?t.original_bild??null:null}async _oeffneLabel(e){let t=this._fach;if(!t)return;this._entwurf=null,this._dialogFehler="";let i={schritt:"wahl",datei:null,bild:null,adresse:"",felder:[],gewaehlt:null,lektion:this._filter.lektion===P?"":this._filter.lektion,bestehend:!1,vorschau:null,vorschauAdresse:""};if(this._label=i,this._dialog="beschriftung",!!e){this._beschaeftigt=!0;try{let n=await this._api.beschriftungLesen(t.id,e),s=await this._api.bildAdresse(e);this._label={...i,schritt:"editor",bild:e,adresse:s,bestehend:!0,lektion:n.lektion??"",felder:n.felder.map(l=>({nr:l.nr,x:l.x,y:l.y,b:l.b,h:l.h,text:l.text,alt:l.alternativen.join(" | ")}))}}catch(n){this._dialogFehler=x(this._t,n)}finally{this._beschaeftigt=!1}}}_labelDatei(e){let t=this._label;if(!t)return;let i=e.target.files?.[0]??null;t.adresse.startsWith("blob:")&&URL.revokeObjectURL(t.adresse),this._label={...t,datei:i,adresse:i?URL.createObjectURL(i):""}}async _labelStart(e){let t=this._label,i=this._fach;if(!(!t?.datei||!i)){this._beschaeftigt=!0,this._dialogFehler="";try{let n=await this._api.bildHochladen(t.datei),s=[];if(e)try{s=(await this._api.beschriftungenFinden(i.id,n)).felder.map(h=>({nr:h.nr,x:h.x,y:h.y,b:h.b,h:h.h,text:h.text,alt:""})),s.length||(this._dialogFehler=this._t("beschriftung_nichts_gefunden"))}catch(l){this._dialogFehler=x(this._t,l)}this._label={...t,schritt:"editor",bild:n,felder:s,gewaehlt:null}}catch(n){this._dialogFehler=x(this._t,n)}finally{this._beschaeftigt=!1}}}_setzeLabel(e){this._label&&(this._label={...this._label,...e})}_setzeLabelFeld(e,t){let i=this._label;i&&(this._label={...i,felder:i.felder.map((n,s)=>s===e?{...n,...t}:n)})}_loescheLabelFeld(e){let t=this._label;if(!t)return;let i=t.felder.filter((n,s)=>s!==e);t.bestehend||(i=i.map((n,s)=>({...n,nr:s+1}))),this._label={...t,felder:i,gewaehlt:null}}_labelZeigerRunter(e){let t=this._label,i=e.currentTarget;if(!t||t.schritt!=="editor")return;let n=i.getBoundingClientRect(),s=e.target,l={rahmen:n,startX:(e.clientX-n.left)/n.width,startY:(e.clientY-n.top)/n.height},h=s.dataset.griff,d=s.dataset.box;if(h!==void 0||d!==void 0){let g=Number(h??d),o=t.felder[g];if(!o)return;this._labelZug={...l,modus:h!==void 0?"groesse":"bewegen",index:g,ursprung:o},this._setzeLabel({gewaehlt:g})}else{let o={nr:Math.max(0,...t.felder.map(_=>_.nr))+1,x:Math.min(Math.max(l.startX,0),1),y:Math.min(Math.max(l.startY,0),1),b:0,h:0,text:"",alt:""};this._labelZug={...l,modus:"neu",index:t.felder.length,ursprung:o},this._label={...t,felder:[...t.felder,o],gewaehlt:t.felder.length}}i.setPointerCapture(e.pointerId),e.preventDefault()}_labelZeigerBewegt(e){let t=this._labelZug;if(!t)return;let i=(e.clientX-t.rahmen.left)/t.rahmen.width,n=(e.clientY-t.rahmen.top)/t.rahmen.height,s=t.ursprung,l=(h,d)=>Math.min(Math.max(h,0),d);if(t.modus==="bewegen")this._setzeLabelFeld(t.index,{x:l(s.x+i-t.startX,1-s.b),y:l(s.y+n-t.startY,1-s.h)});else if(t.modus==="groesse")this._setzeLabelFeld(t.index,{b:l(s.b+i-t.startX,1-s.x),h:l(s.h+n-t.startY,1-s.y)});else{let h=l(Math.min(t.startX,i),1),d=l(Math.min(t.startY,n),1);this._setzeLabelFeld(t.index,{x:h,y:d,b:l(Math.max(t.startX,i),1)-h,h:l(Math.max(t.startY,n),1)-d})}}_labelZeigerHoch(){let e=this._labelZug,t=this._label;if(this._labelZug=null,!e||!t)return;let i=t.felder[e.index];e.modus==="neu"&&i&&(i.b<ht||i.h<ht)&&(this._label={...t,felder:t.felder.filter((n,s)=>s!==e.index),gewaehlt:null})}_labelFelderFuerServer(e){return e.felder.map(t=>({nr:t.nr,x:t.x,y:t.y,b:t.b,h:t.h,text:t.text.trim(),alternativen:ne(t.alt)}))}async _labelVorschau(){let e=this._label,t=this._fach;if(!(!e?.bild||!t)){this._beschaeftigt=!0,this._dialogFehler="";try{let i=await this._api.beschriftungVorschau(t.id,e.bild,this._labelFelderFuerServer(e),e.vorschau),n=await this._api.bildAdresse(i.vorschau);this._label={...e,schritt:"vorschau",vorschau:i.vorschau,vorschauAdresse:n}}catch(i){this._dialogFehler=x(this._t,i)}finally{this._beschaeftigt=!1}}}async _labelSpeichern(){let e=this._label,t=this._fach;if(!(!e?.bild||!t)){this._beschaeftigt=!0,this._dialogFehler="";try{let i=await this._api.beschriftungSpeichern(t.id,e.bild,this._labelFelderFuerServer(e),e.lektion||null,e.bestehend?null:this._neuBereich(),e.vorschau);this._schliesseDialog(),this._zeigeErfolg(this._t("beschriftung_fertig",{neu:i.neu,geaendert:i.geaendert,entfernt:i.entfernt})),await this._neuLaden()}catch(i){this._dialogFehler=x(this._t,i)}finally{this._beschaeftigt=!1}}}_oeffneSeiten(){this._seiten={dateien:[],vorschauen:[],lektion:this._filter.lektion===P?"":this._filter.lektion,anzahl:8,form:"gemischt",schwerpunkt:""},this._dialogFehler="",this._dialog="seiten"}_seitenGewaehlt(e){let t=this._seiten;if(!t)return;let i=[...e.target.files??[]];for(let s of t.vorschauen)URL.revokeObjectURL(s);let n=i.slice(0,D);this._dialogFehler=i.length>D?this._t("seiten_zu_viele",{n:D}):"",this._seiten={...t,dateien:n,vorschauen:n.map(s=>URL.createObjectURL(s))}}async _erzeugeFragen(){let e=this._seiten;if(!(!e||!e.dateien.length||!this._fachId)){this._beschaeftigt=!0,this._dialogFehler="";try{let t=[];for(let n of e.dateien)t.push(await this._api.bildHochladen(n,!0));let i=await this._api.fragenAusSeiten(this._fachId,{seiten:t,anzahl:e.anzahl,form:e.form,lektion:e.lektion||null,schwerpunkt:e.schwerpunkt.trim()||null,bereich:this._neuBereich()});this._schliesseDialog(),this._auswahl=new Set,i.erzeugt&&(this._filter={...ie,geprueft:"nein"}),this._zeigeErfolg(this._t("seiten_fertig",{erzeugt:i.erzeugt,verworfen:i.verworfen,doppelt:i.uebersprungen})),await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}finally{this._beschaeftigt=!1}}}_oeffneSaetze(){let e=this._bereiche.filter(i=>i.art==="satz"),t=e.find(i=>i.id===this._aktiverBereich);this._saetze={bereich:(t??e[0])?.id??"",dateien:[],vorschauen:[],lektion:this._filter.lektion===P?"":this._filter.lektion,anzahl:8,form:"gemischt",beschreibung:"",uebernehmen:!1},this._dialogFehler="",this._dialog="saetze"}_saetzeSeitenGewaehlt(e){let t=this._saetze;if(!t)return;let i=[...e.target.files??[]];for(let s of t.vorschauen)URL.revokeObjectURL(s);let n=i.slice(0,D);this._dialogFehler=i.length>D?this._t("seiten_zu_viele",{n:D}):"",this._saetze={...t,dateien:n,vorschauen:n.map(s=>URL.createObjectURL(s))}}async _erzeugeSaetze(){let e=this._saetze;if(!(!e||!this._fachId)){this._beschaeftigt=!0,this._dialogFehler="";try{let t=[];for(let n of e.dateien)t.push(await this._api.bildHochladen(n,!0));let i=await this._api.satzaufgabenErzeugen(this._fachId,{bereich:e.bereich,anzahl:e.anzahl,form:e.form,beschreibung:e.beschreibung.trim()||null,seiten:t,uebernehmen:t.length>0&&e.uebernehmen,lektion:e.lektion||null});this._schliesseDialog(),this._auswahl=new Set,this._bereichId=e.bereich,i.erzeugt&&(this._filter={...ie,geprueft:"nein"}),this._zeigeErfolg(this._t("saetze_fertig",{erzeugt:i.erzeugt,verworfen:i.verworfen,doppelt:i.uebersprungen})),await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}finally{this._beschaeftigt=!1}}}_oeffneLektionen(){this._lektionName="",this._dialogFehler="",this._dialog="lektion"}async _lektionAnlegen(){let e=this._lektionName.trim();if(!(!e||!this._fachId)){this._dialogFehler="";try{await this._api.lektionHinzufuegen(this._fachId,e),this._lektionName="",this._zeigeErfolg(this._t("lektion_angelegt",{name:e})),await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}}}async _lektionLoeschen(e){this._dialogFehler="";try{await this._api.lektionLoeschen(this._fachId,e),this._filter.lektion===e&&this._setzeFilter("lektion",""),await this._neuLaden()}catch(t){this._dialogFehler=x(this._t,t)}}_lektionAuswahl(e,t,i){let n=[...this._fach?.lektionen??[]];return e&&!n.includes(e)&&n.push(e),r`
      <select
        aria-label=${i}
        .value=${e}
        @change=${s=>t(v(s))}
      >
        <option value="" ?selected=${e===""}>
          ${this._t("keine_lektion")}
        </option>
        ${n.map(s=>r`<option value=${s} ?selected=${s===e}>
              ${s}
            </option>`)}
      </select>
    `}_oeffneImport(){this._importText="",this._importTrenner="",this._importGeprueft=!0,this._importLektion=this._filter.lektion===P?"":this._filter.lektion,this._vorschau=null,this._dialogFehler="",this._dialog="import"}async _importVorschau(){this._dialogFehler="";try{this._vorschau=await this._api.importVorschau(this._fachId,this._importText,this._importTrenner||null)}catch(e){this._dialogFehler=x(this._t,e)}}async _importUebernehmen(){this._beschaeftigt=!0,this._dialogFehler="";try{let e=await this._api.importText(this._fachId,this._importText,this._importLektion.trim()||null,this._importTrenner||null,this._importGeprueft,this._neuBereich());this._schliesseDialog(),this._zeigeErfolg(this._t("import_ergebnis",{n:e.importiert,u:e.uebersprungen})),await this._neuLaden()}catch(e){this._dialogFehler=x(this._t,e)}finally{this._beschaeftigt=!1}}async _exportiere(){let e=this._fach;if(e)try{let t=await this._api.export(e.id,this._mitStatistik),i=new Blob([JSON.stringify(t,null,2)],{type:"application/json"}),n=document.createElement("a");n.href=URL.createObjectURL(i);let s=e.name.replace(/[^\p{L}\p{N}_-]+/gu,"_");n.download=`learnbuddy-${s}-${new Date().toISOString().slice(0,10)}.json`,n.click(),URL.revokeObjectURL(n.href),this._schliesseDialog();let l=Number(t.ausgelassen_mit_bild??0);l&&this._zeigeErfolg(this._t("export_ohne_bild",{n:l}))}catch(t){this._dialogFehler=x(this._t,t)}}async _dateiGewaehlt(e){let t=e.target,i=t.files?.[0];if(t.value="",!!i)try{let n=JSON.parse(await i.text());if(typeof n!="object"||n===null||Array.isArray(n))throw new Error("no object");this._jsonDaten=n,this._jsonLektion="",this._dialogFehler="",this._dialog="importJson"}catch{this._meldung={text:this._t("datei_ungueltig"),fehler:!0}}}async _importiereJson(){if(this._jsonDaten){this._beschaeftigt=!0;try{let e=await this._api.importJson(this._fachId,this._jsonDaten,this._mitStatistik,this._jsonLektion||null,this._neuBereich());this._schliesseDialog();let t=this._t("import_ergebnis",{n:e.importiert,u:e.uebersprungen});e.fehler.length&&(t+=` ${this._t("import_fehler",{n:e.fehler.length})}`),this._zeigeErfolg(t),await this._neuLaden()}catch(e){this._dialogFehler=x(this._t,e)}finally{this._beschaeftigt=!1}}}_oeffneArbeit(e,t=[]){let i=e?e.lektionen.length>0||e.aufgaben_ids.length>0:t.length>0;this._arbeit={id:e?.id??null,art:e?.art??"arbeit",datum:e?.datum??"",thema:e?.thema??"",abfragen:e?.abfragen_pro_tag??3,start:e?.start_tage_vorher??7,intensivierung:e?.intensivierung??!0,frist:e?.antwortfrist_minuten??null,simAktiv:!!e?.simulation_um,simUm:Ut(e?.simulation_um??null),simAnzahl:e?.simulation_anzahl??10,kalenderUid:null,fachOffen:!1,modus:i?"auswahl":"alle",lektionen:new Set(e?.lektionen??[]),bereiche:new Set(e?.bereiche??[]),ids:new Set(e?.aufgaben_ids??t),seit:"",seiteVon:"",seiteBis:""},this._neuesFach=null,this._dialogFehler="",this._dialog="arbeit"}async _oeffneVorschlag(e){let{vorschlag:t}=e.detail,i=this._faecherDesKindes,n=(t.fach_id&&i.some(s=>s.id===t.fach_id)?t.fach_id:null)??(i.some(s=>s.id===this._fachId)?this._fachId:i[0]?.id)??"";n!==this._fachId&&(this._fachId=n,this._zuruecksetzen(),await this._ladeAufgaben()),this._oeffneArbeit(null),this._arbeit&&(this._arbeit={...this._arbeit,art:t.art,datum:t.datum,thema:t.text,kalenderUid:t.uid,fachOffen:n!==t.fach_id}),n||(this._neuesFach={...Le})}async _wechsleFachImDialog(e){if(!(!this._arbeit||!e)){if(e===this._fachId){this._arbeit={...this._arbeit,fachOffen:!1};return}this._fachId=e,this._zuruecksetzen(),await this._ladeAufgaben(),this._arbeit={...this._arbeit,fachOffen:!1,modus:"alle",lektionen:new Set,bereiche:new Set,ids:new Set,seit:"",seiteVon:"",seiteBis:""}}}async _legeFachAn(){let e=this._neuesFach;if(e){this._beschaeftigt=!0,this._dialogFehler="";try{let t=await this._api.fachAnlegen(this._kindId,e.typ,e.name.trim(),e.typ==="fremdsprache"?e.sprache:null);this._uebersicht=await this._api.uebersicht(),this._neuesFach=null,this._fachId="",await this._wechsleFachImDialog(t)}catch(t){this._dialogFehler=x(this._t,t)}finally{this._beschaeftigt=!1}}}_setzeArbeit(e,t){this._arbeit&&(this._arbeit={...this._arbeit,[e]:t})}_arbeitMenge(e,t,i){if(!this._arbeit)return;let n=new Set(this._arbeit[e]);i?n.add(t):n.delete(t),this._setzeArbeit(e,n),e==="lektionen"&&i&&!this._arbeit.thema.trim()&&this._setzeArbeit("thema",t)}_arbeitSeit(){let e=this._arbeit;if(!e?.seit)return;let t=new Set(e.ids);for(let i of this._aufgaben)i.erstellt.slice(0,10)>=e.seit&&t.add(i.id);this._setzeArbeit("ids",t)}_arbeitSeiten(){let e=this._arbeit;if(!e||!e.seiteVon&&!e.seiteBis)return;let t=new Set(e.ids);for(let i of this._aufgaben)ge(i.seite,e.seiteVon,e.seiteBis)&&t.add(i.id);this._setzeArbeit("ids",t)}_arbeitUmfang(e){let t=new Set(e.lektionen),i=new Set(e.bereiche??[]),n=new Set(e.ids);return!t.size&&!i.size&&!n.size?null:this._aufgaben.filter(s=>n.has(s.id)||s.lektion!==null&&t.has(s.lektion)||i.has(s.bereich??W)).length}async _speichereArbeit(){let e=this._arbeit;if(!e)return;if(e.simAktiv&&!e.simUm){this._zeigeFehler({message:"simulation_um_ungueltig"});return}let t=e.modus==="auswahl",i={datum:e.datum,thema:e.thema,art:e.art,lektionen:t?[...e.lektionen]:[],bereiche:t?[...e.bereiche]:[],aufgaben_ids:t?[...e.ids]:[],abfragen_pro_tag:e.abfragen,start_tage_vorher:e.start,intensivierung:e.intensivierung,antwortfrist_minuten:e.frist,simulation_um:e.simAktiv&&e.simUm?new Date(e.simUm).toISOString():null,simulation_anzahl:e.simAnzahl};e.kalenderUid&&(i.kalender_uid=e.kalenderUid),e.id||(i.fach_id=this._fachId),this._beschaeftigt=!0,this._dialogFehler="";try{await this._api.arbeitSpeichern(e.id,i),this._schliesseDialog(),this._auswahl=new Set,this._tab="arbeiten",this._zeigeErfolg(this._t("gespeichert")),await this._neuLaden(20)}catch(n){this._dialogFehler=x(this._t,n)}finally{this._beschaeftigt=!1}}async _loescheArbeit(e){if(window.confirm(this._t("arbeit_loeschen_frage",{thema:e.thema})))try{await this._api.arbeitLoeschen(e.id),this._zeigeErfolg(this._t("geloescht_arbeit")),await this._neuLaden(20)}catch(t){this._zeigeFehler(t)}}_datum(e){let t=new Date(`${e.slice(0,10)}T00:00:00`);return Number.isNaN(t.getTime())?e:t.toLocaleDateString(this.hass?.language??"en",{year:"numeric",month:"2-digit",day:"2-digit"})}_zeitpunkt(e){let t=new Date(e);return Number.isNaN(t.getTime())?e:t.toLocaleString(this.hass?.language??"en",{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"})}_menue(){this.dispatchEvent(new CustomEvent("hass-toggle-menu",{bubbles:!0,composed:!0}))}render(){let e=this._t,t=this._uebersicht;return r`
      <header>
        ${this.narrow?r`<button class="icon" aria-label="Menu" @click=${this._menue}>
              <ha-icon icon="mdi:menu"></ha-icon>
            </button>`:c}
        <h1>${e("titel")}</h1>
        ${t&&t.kinder.length>0?r`<div class="kinder" role="group" aria-label=${e("kind")}>
              ${t.kinder.map(i=>r`<button
                    class="kindwahl"
                    aria-pressed=${i.id===this._kindId?"true":"false"}
                    @click=${()=>this._waehleKind(i.id)}
                  >
                    ${i.name}
                  </button>`)}
            </div>`:c}
      </header>
      <main>
        ${this._veraltet?r`<div class="meldung" role="status">
              <span>${e("neue_version")}</span>
              <button class="primaer" @click=${()=>window.location.reload()}>
                ${e("neu_laden")}
              </button>
            </div>`:c}
        ${this._uebersicht?.kinder.find(i=>i.id===this._kindId)?.absender===!1?r`<div class="meldung fehler" role="status">
              <span>${e("absender_fehlt")}</span>
            </div>`:c}
        ${(this._uebersicht?.unbekannte_absender??[]).map(i=>r`<div class="meldung" role="status">
              <span>
                ${e("absender_unbekannt",{kennung:i.kennung,quelle:e(`quelle_${i.quelle}`)})}
              </span>
              <button
                class="primaer"
                @click=${()=>this._absenderZuordnen(i.kennung)}
              >
                ${e("absender_uebernehmen",{name:this._uebersicht?.kinder.find(n=>n.id===this._kindId)?.name??""})}
              </button>
              <button @click=${()=>this._absenderVerwerfen(i.kennung)}>
                ${e("absender_verwerfen")}
              </button>
            </div>`)}
        ${this._meldung?r`<div
              class="meldung ${this._meldung.fehler?"fehler":""}"
              role=${this._meldung.fehler?"alert":"status"}
            >
              <span>${this._meldung.text}</span>
              <button
                class="icon"
                aria-label=${e("schliessen")}
                @click=${()=>{this._meldung=null}}
              >
                <ha-icon icon="mdi:close"></ha-icon>
              </button>
            </div>`:c}
        ${this._inhalt()}
      </main>
      ${this._dialogInhalt()}
    `}async _oeffne(e){let{ziel:t,fachId:i}=e.detail;i!==this._fachId&&(this._fachId=i,this._zuruecksetzen()),this._tab=t,await this._neuLaden()}async _absenderZuordnen(e){try{await this._api.absenderZuordnen(this._kindId,e),await this._neuLaden(),this._zeigeErfolg(this._t("absender_uebernommen"))}catch(t){this._zeigeFehler(t)}}async _absenderVerwerfen(e){try{await this._api.absenderVerwerfen(e),await this._neuLaden()}catch(t){this._zeigeFehler(t)}}async _waehleTab(e){this._tab=e,e!=="uebersicht"&&await this._neuLaden()}_inhalt(){let e=this._t;if(this._laedt)return r`<div class="leer">${e("laden")}</div>`;if(!this._uebersicht?.kinder.length)return r`<div class="card leer">${e("keine_kinder")}</div>`;let t={uebersicht:null,aufgaben:this._fach?this._aufgaben.length:null,arbeiten:this._fach?this._arbeitenDesFachs.length:null},i={uebersicht:e("tab_uebersicht"),aufgaben:e("tab_aufgaben"),arbeiten:e("tab_arbeiten")};return r`
      <div class="tabs" role="tablist">
        ${["uebersicht","aufgaben","arbeiten"].map(n=>r`<button
              role="tab"
              aria-selected=${this._tab===n?"true":"false"}
              @click=${()=>this._waehleTab(n)}
            >
              ${i[n]}${t[n]===null?"":` (${t[n]})`}
            </button>`)}
      </div>
      ${this._tab==="aufgaben"&&this._fach?this._werkzeuge():c}
      ${this._tab==="uebersicht"?r`<lh-uebersicht
            .hass=${this.hass}
            .narrow=${this.narrow}
            .kindId=${this._kindId}
            @lh-oeffnen=${this._oeffne}
            @lh-vorschlag=${this._oeffneVorschlag}
          ></lh-uebersicht>`:this._fachBereich()}
    `}_fachBereich(){let e=this._t,t=this._faecherDesKindes;return r`
      <div class="abschnittskopf">
        <h3 class="abschnitt">${e("faecher_titel")}</h3>
        <button @click=${this._oeffneFaecher}>${e("faecher_verwalten")}</button>
      </div>
      ${t.length>0?r`<div class="kinder fachwahl" role="group" aria-label=${e("fach")}>
            ${t.map(i=>r`<button
                  class="kindwahl"
                  aria-pressed=${i.id===this._fachId?"true":"false"}
                  @click=${()=>this._waehleFach(i.id)}
                >
                  ${i.name}
                </button>`)}
          </div>`:r`<div class="card leer">${e("keine_faecher")}</div>`}
      ${this._fach?r`${this._tab==="aufgaben"?this._themenBereich():c}
          ${this._tab==="aufgaben"?this._aufgabenAnsicht():this._arbeitenAnsicht()}`:c}
    `}_werkzeuge(){let e=this._t,t=this._fach?.typ!=="sach"&&!this._satzAnsicht,i=(n,s,l,h=!1)=>r`<button
      class="icon"
      title=${s}
      aria-label=${s}
      ?disabled=${h}
      @click=${l}
    >
      <ha-icon icon=${n}></ha-icon>
    </button>`;return r`
      <div class="werkzeuge">
        ${t?i("mdi:text-box-plus-outline",e("import_aus_text"),()=>this._oeffneImport()):c}
        ${i("mdi:file-export-outline",e("export_json"),()=>{this._mitStatistik=!1,this._dialogFehler="",this._dialog="export"},!this._aufgaben.length)}
        ${i("mdi:file-import-outline",e("import_json"),()=>{this.renderRoot.querySelector("#datei")?.click()})}
        <input
          id="datei"
          type="file"
          accept="application/json,.json"
          hidden
          @change=${this._dateiGewaehlt}
        />
      </div>
    `}_themenBereich(){let e=this._t,t=r`<h3 class="abschnitt trenner">${e("aufgabenverwaltung")}</h3>`;return this._hatBereiche?r`
      <div class="abschnittskopf trenner">
        <h3 class="abschnitt">${e("themen_titel")}</h3>
        <button @click=${this._oeffneBereiche}>${e("bereiche_verwalten")}</button>
      </div>
      <div class="kinder fachwahl" role="group" aria-label=${e("bereich")}>
            ${this._mehrere?r`<button
                  class="kindwahl"
                  aria-pressed=${this._aktiverBereich===""?"true":"false"}
                  @click=${()=>{this._bereichId="",this._auswahl=new Set}}
                >
                  ${e("alle")} (${this._aufgaben.length})
                </button>`:c}
            ${this._bereiche.map(i=>r`<button
                  class="kindwahl"
                  aria-pressed=${this._aktiverBereich===i.id?"true":"false"}
                  @click=${()=>{this._bereichId=i.id,this._auswahl=new Set}}
                >
                  ${this._bereichName_(i)} (${i.aufgaben})
                </button>`)}
          </div>
      ${t}
    `:t}_aufgabenAnsicht(){let e=this._t,t=this._fach,i=this._gefiltert(),n=[...this._auswahl],[s="",l=""]=t.sprachen,h=this._filter,d=t.typ==="mathe",g=t.typ==="sach",o=this._satzAnsicht,_=this._uebersicht?.kinder.find(w=>w.id===this._kindId),f=t.ki_status??(t.ki?t.ki_bilder?"ok":"ohne_bilder":"keine"),k=f==="ok"||f==="ohne_bilder",z=f==="ok",y=f==="ok"?"":e(`ki_${f}`);return r`
      <div class="leiste">
        <button class="primaer" @click=${this._neueAufgabe}>
          ${e(g?"neue_frage":"neue_aufgabe")}
        </button>
        <button @click=${this._oeffneLektionen}>${e("lektion_hinzufuegen")}</button>
        ${d?r`<button
              ?disabled=${!k}
              title=${k?"":y}
              @click=${this._oeffneGenerieren}
            >
              ${e("generieren")}
            </button>`:c}
        ${o?r`<button
              ?disabled=${!k}
              title=${k?"":y}
              @click=${()=>this._oeffneSaetze()}
            >
              ${e("saetze_erzeugen")}
            </button>`:c}
        ${o?c:g?r`<button
                ?disabled=${!z}
                title=${y}
                @click=${this._oeffneSeiten}
              >
                ${e("seiten")}
              </button>
              <button @click=${()=>void this._oeffneLabel(null)}>
                ${e("beschriftung_neu")}
              </button>`:r`
              <button
                ?disabled=${!z}
                title=${y}
                @click=${this._oeffneFoto}
              >
                ${e("foto_import")}
              </button>
            `}
        <span class="abstand"></span>
        ${n.length?r`
              <span>${e("ausgewaehlt",{n:n.length})}</span>
              ${this._aufgaben.some(w=>this._auswahl.has(w.id)&&!w.geprueft)?r`<button ?disabled=${this._beschaeftigt} @click=${this._freigeben}>
                    ${e("freigeben")}
                  </button>`:c}
              ${d?r`<button ?disabled=${this._beschaeftigt} @click=${this._nachrechnen}>
                    ${e("nachrechnen")}
                  </button>`:c}
              ${d?r`<button
                    ?disabled=${this._beschaeftigt}
                    title=${e("selbst_nachgerechnet_hinweis")}
                    @click=${this._markiereGeprueft}
                  >
                    ${e("selbst_nachgerechnet")}
                  </button>`:c}
              ${d?r`<button
                    ?disabled=${this._beschaeftigt||!k}
                    title=${k?"":y}
                    @click=${this._erzeugeRechenwege}
                  >
                    ${e("rechenweg_erzeugen")}
                  </button>`:c}
              ${this._aufgaben.some(w=>this._auswahl.has(w.id)&&w.typ==="sach"&&w.hilfe)?r`
                    <button
                      ?disabled=${this._beschaeftigt}
                      @click=${()=>this._setzeHilfeSenden(n,!0)}
                    >
                      ${e("hilfe_alle_an")}
                    </button>
                    <button
                      ?disabled=${this._beschaeftigt}
                      @click=${()=>this._setzeHilfeSenden(n,!1)}
                    >
                      ${e("hilfe_alle_aus")}
                    </button>
                  `:c}
              ${this._mehrere?r`<select
                    aria-label=${e("verschieben_nach")}
                    ?disabled=${this._beschaeftigt}
                    @change=${w=>{let j=v(w);w.target.value="",this._verschiebe(j)}}
                  >
                    <option value="">${e("verschieben_nach")}</option>
                    ${this._bereiche.map(w=>r`<option value=${w.id}>
                          ${this._bereichName_(w)}
                        </option>`)}
                  </select>`:c}
              <button @click=${()=>this._oeffneArbeit(null,n)}>
                ${e("arbeit_aus_auswahl")}
              </button>
              <button
                class="gefahr"
                ?disabled=${this._beschaeftigt}
                @click=${()=>this._loesche(n)}
              >
                ${e("loeschen")}
              </button>
            `:c}
      </div>

      ${f==="nicht_verfuegbar"?r`<div class="meldung fehler" role="status">
            <span>
              ${e("ki_hinweis_nicht_verfuegbar")}
              ${g?e("ki_hinweis_sach_zusatz"):""}
            </span>
          </div>`:f==="keine"&&g?r`<div class="meldung fehler" role="status">
              <span>${e("sach_ohne_ki")}</span>
            </div>`:f==="ok"?c:r`<p class="klein" role="note" style="margin: 0 0 12px">
                <ha-icon icon="mdi:information-outline" style="--mdc-icon-size: 16px"></ha-icon>
                ${e(`ki_hinweis_${f}`)}
              </p>`}
      ${d&&_&&!_.bilder&&this._aufgaben.some(w=>w.typ==="mathe"&&w.bild)?r`<div class="meldung fehler" role="status">
            <span>${e("keine_bilder",{name:_.name})}</span>
          </div>`:c}

      <div class="card filter">
        <label class="feld">
          ${e("filter_suche")}
          <input
            type="search"
            .value=${h.suche}
            @input=${w=>this._setzeFilter("suche",v(w))}
          />
        </label>
        <label class="feld">
          ${e("filter_lektion")}
          <select
            .value=${h.lektion}
            @change=${w=>this._setzeFilter("lektion",v(w))}
          >
            <option value="">${e("alle")}</option>
            ${t.lektionen.map(w=>r`<option value=${w} ?selected=${h.lektion===w}>
                  ${w}
                </option>`)}
            <option value=${P}>${e("ohne_lektion")}</option>
          </select>
        </label>
        <label class="feld">
          ${e("filter_quelle")}
          <select
            .value=${h.quelle}
            @change=${w=>this._setzeFilter("quelle",v(w))}
          >
            <option value="">${e("alle")}</option>
            <option value="manuell">${e("quelle_manuell")}</option>
            <option value="upload">${e("quelle_upload")}</option>
            <option value="generiert">${e("quelle_generiert")}</option>
          </select>
        </label>
        <label class="feld">
          ${e("filter_geprueft")}
          <select
            .value=${h.geprueft}
            @change=${w=>this._setzeFilter("geprueft",v(w))}
          >
            <option value="">${e("alle")}</option>
            <option value="ja">${e("ja")}</option>
            <option value="nein">${e("nein")}</option>
          </select>
        </label>
        <label class="feld">
          ${e("filter_fehlerquote")}
          <input
            type="number"
            min="0"
            max="100"
            .value=${h.fehlerquote}
            @input=${w=>this._setzeFilter("fehlerquote",v(w))}
          />
        </label>
        <label class="feld">
          ${e("filter_von")}
          <input
            type="date"
            .value=${h.von}
            @change=${w=>this._setzeFilter("von",v(w))}
          />
        </label>
        <label class="feld">
          ${e("filter_bis")}
          <input
            type="date"
            .value=${h.bis}
            @change=${w=>this._setzeFilter("bis",v(w))}
          />
        </label>
        <label class="feld">
          ${e("filter_seite_von")}
          <input
            type="number"
            min="1"
            .value=${h.seiteVon}
            @input=${w=>this._setzeFilter("seiteVon",v(w))}
          />
        </label>
        <label class="feld">
          ${e("filter_seite_bis")}
          <input
            type="number"
            min="1"
            .value=${h.seiteBis}
            @input=${w=>this._setzeFilter("seiteBis",v(w))}
          />
        </label>
        <button
          @click=${()=>{this._filter={...ie},this._nurIds=null}}
        >
          ${e("filter_zuruecksetzen")}
        </button>
      </div>

      <div class="klein" style="margin: 0 4px 8px">
        ${e("anzahl",{n:i.length,gesamt:this._aufgaben.length})}
      </div>

      ${this._tabellen(i,s,l)}
    `}_tabellen(e,t,i){if(this._aktiverBereich||!this._hatBereiche)return this._tabelle(e,this._ansicht,t,i,!0);let s=this._neuBereich()??W,l=this._bereiche.map(h=>({bereich:h,aufgaben:e.filter(d=>(d.bereich??W)===h.id)}));return r`${l.map(({bereich:h,aufgaben:d})=>r`
        <h3 class="abschnitt">
          ${this._bereichName_(h)} <span class="klein">(${d.length})</span>
        </h3>
        ${this._tabelle(d,this._ansichtVon(h),t,i,h.id===s)}
      `)}`}_tabelle(e,t,i,n,s){let l=this._t,h=this.hass?.language??"en",d=t==="mathe",g=t==="sach",o=e.length>0&&e.every(f=>this._auswahl.has(f.id)),_=e;return r`
      <div class="card tabelle-rahmen">
        <table>
          <thead>
            <tr>
              <th class="schmal">
                <input
                  type="checkbox"
                  aria-label=${l("alle_auswaehlen")}
                  .checked=${o}
                  @change=${f=>this._alleUmschalten(_,B(f))}
                />
              </th>
              <th>
                ${d?l("spalte_aufgabe"):g?l(this._fach?.typ==="vokabel"?"spalte_satz":"spalte_frage"):E(h,i)}
              </th>
              <th>
                ${d?l("spalte_loesung"):g?l(this._fach?.typ==="vokabel"?"spalte_satz_loesung":"spalte_musterantwort"):E(h,n)}
              </th>
              ${d?r`<th class="schmal" title=${l("schwierigkeit_hinweis")}>
                    ${l("spalte_schwierigkeit")}
                  </th>`:c}
              <th>${l("spalte_hinweis")}</th>
              <th class="schmal">${l("spalte_seite")}</th>
              <th>${l("spalte_lektion")}</th>
              <th class="schmal" title=${l("box_hinweis")}>${l("spalte_box")}</th>
              <th class="schmal">${l("spalte_fehler")}</th>
              <th class="schmal">${l("spalte_geprueft")}</th>
              <th class="schmal">${l("spalte_erstellt")}</th>
              <th class="schmal"></th>
            </tr>
          </thead>
          <tbody>
            ${s&&this._entwurf&&this._entwurf.id===null?this._editorZeile(this._entwurf,i,n):c}
            ${_.map(f=>this._entwurf?.id===f.id?this._editorZeile(this._entwurf,i,n):this._zeile(f,i,n))}
          </tbody>
        </table>
        ${_.length===0&&!(s&&this._entwurf)?r`<div class="leer">
              ${l(this._aufgaben.length?"keine_treffer":"keine_aufgaben")}
            </div>`:c}
      </div>
    `}_zeile(e,t,i){let n=this._t,s=this.hass?.language??"en",l=e.typ==="mathe"?e:null,h=e.typ==="sach"?e:null,d=(l?["mathe"]:h?["sach"]:[`${t}>${i}`,`${i}>${t}`]).map(o=>e.statistik[o]?.box??1).join(" \xB7 "),g=o=>e.typ!=="vokabel"?r``:r`
            ${e.frage[o]??""}
            ${e.alternativen[o]?.length?r`<div class="klein">${e.alternativen[o]?.join(" | ")}</div>`:c}
          `;return r`
      <tr class=${this._auswahl.has(e.id)?"gewaehlt":""}>
        <td class="schmal">
          <input
            type="checkbox"
            aria-label=${_e(e,t,i)}
            .checked=${this._auswahl.has(e.id)}
            @change=${o=>this._umschalten(e.id,B(o))}
          />
        </td>
        ${l?this._matheZellen(l):h?this._sachZellen(h):r`
              <td data-label=${E(s,t)}>${g(t)}</td>
              <td data-label=${E(s,i)}>${g(i)}</td>
            `}
        <td data-label=${n("spalte_hinweis")}>${e.hinweis??""}</td>
        <td class="schmal" data-label=${n("spalte_seite")}>${e.seite??""}</td>
        <td data-label=${n("spalte_lektion")}>
          ${e.lektion??""}
          ${e.arbeiten.length?r`<span class="marke" title=${n("tab_arbeiten")}>
                ${e.arbeiten.length} ×
                <ha-icon
                  icon="mdi:calendar-star"
                  style="--mdc-icon-size: 12px"
                ></ha-icon>
              </span>`:c}
        </td>
        <td class="schmal" data-label=${n("spalte_box")} title=${n("box_hinweis")}>
          ${d}
        </td>
        <td class="schmal" data-label=${n("spalte_fehler")}>
          ${e.fehlerquote===null?r`<span class="klein">–</span>`:r`<span class="marke ${e.fehlerquote>=50?"warn":"ok"}">
                ${Math.round(e.fehlerquote)} %
              </span>`}
        </td>
        <td class="schmal" data-label=${n("spalte_geprueft")}>
          <input
            type="checkbox"
            aria-label=${n("spalte_geprueft")}
            .checked=${e.geprueft}
            @change=${o=>this._setzeGeprueft(e,B(o))}
          />
        </td>
        <td class="schmal klein" data-label=${n("spalte_erstellt")}>
          ${this._datum(e.erstellt)}
        </td>
        <td class="schmal">
          <button
            class="icon"
            title=${n("bearbeiten")}
            aria-label=${n("bearbeiten")}
            @click=${()=>this._bearbeite(e)}
          >
            <ha-icon icon="mdi:pencil"></ha-icon>
          </button>
          <button
            class="icon"
            title=${n("loeschen")}
            aria-label=${n("loeschen")}
            ?disabled=${this._beschaeftigt}
            @click=${()=>this._loesche([e.id])}
          >
            <ha-icon icon="mdi:delete"></ha-icon>
          </button>
        </td>
      </tr>
    `}_sachZellen(e){let t=this._t,i=e.bild?this._bildAdressen[e.bild]:e.quelle_bild?this._bildAdressen[e.quelle_bild]:void 0,n=this._fach?.typ==="vokabel";return r`
      <td data-label=${t(n?"spalte_satz":"spalte_frage")}>
        ${i?r`<button
              class="vorschaubild"
              style="float: right; margin-left: 8px; border: none; background: none"
              title=${t("quellseite_anzeigen")}
              aria-label=${t("quellseite_anzeigen")}
              @click=${()=>{this._grossbild=i,this._bildText=e.stelle?`${t("belegstelle")}: \u201E${e.stelle}\u201C`:"",this._dialogFehler="",this._dialog="bild"}}
            >
              <img class="vorschaubild" src=${i} alt="" loading="lazy" />
            </button>`:c}
        ${e.frage}
        ${e.hilfe&&(e.form==="luecke"||e.form==="auswahl")?r`<div class="klein">
              (${e.hilfe})
              <label class="feld zeile" title=${t("hilfe_senden")}>
                <input
                  type="checkbox"
                  aria-label=${t("hilfe_senden")}
                  .checked=${e.hilfe_senden??!1}
                  @change=${s=>this._setzeHilfeSenden([e.id],B(s))}
                />
                ${t("hilfe_senden_kurz")}
              </label>
            </div>`:c}
        <div class="klein">
          <span class="marke">${t(`form_${e.form}`)}</span>
          ${e.stelle&&!i?r`<span class="marke" title=${e.stelle}>
                <ha-icon
                  icon="mdi:format-quote-close"
                  style="--mdc-icon-size: 12px"
                ></ha-icon>
                ${t("belegstelle")}
              </span>`:c}
        </div>
      </td>
      <td data-label=${t(n?"spalte_satz_loesung":"spalte_musterantwort")}>
        ${e.antwort}
        ${e.alternativen?.length?r`<div class="klein">${e.alternativen.join(" | ")}</div>`:c}
        ${e.form==="auswahl"?r`<div class="klein">
              ${e.falsche_optionen.map(s=>r`<div>✗ ${s}</div>`)}
            </div>`:e.kernpunkte.length?r`<div class="klein">
                ${e.kernpunkte.map(s=>r`<div>• ${s}</div>`)}
              </div>`:c}
      </td>
    `}_matheZellen(e){let t=this._t,i=e.bild?this._bildAdressen[e.bild]:void 0;return r`
      <td data-label=${t("spalte_aufgabe")}>
        ${i?r`<button
              class="vorschaubild"
              style="float: right; margin-left: 8px; border: none; background: none"
              title=${t("bild_anzeigen")}
              aria-label=${t("bild_anzeigen")}
              @click=${()=>{this._grossbild=i,this._dialogFehler="",this._dialog="bild"}}
            >
              <img class="vorschaubild" src=${i} alt="" loading="lazy" />
            </button>`:e.bild?r`<ha-icon
                icon="mdi:image-outline"
                style="float: right; --mdc-icon-size: 18px"
              ></ha-icon>`:c}
        ${e.aufgabe}
        <div class="klein">
          ${e.verifikation==="keine"?c:e.verifikation==="abweichung"?r`<span class="marke warn">
                  <ha-icon icon="mdi:alert" style="--mdc-icon-size: 12px"></ha-icon>
                  ${t("verifikation_abweichung")}
                </span>`:r`<span class="marke ok">
                  <ha-icon
                    icon="mdi:check-decagram"
                    style="--mdc-icon-size: 12px"
                  ></ha-icon>
                  ${t(`verifikation_${e.verifikation}`)}
                </span>`}
          ${e.rechenweg.length?r`<span class="marke" title=${e.rechenweg.join(`
`)}>
                <ha-icon icon="mdi:stairs" style="--mdc-icon-size: 12px"></ha-icon>
                ${t("rechenweg_vorhanden")}
              </span>`:c}
        </div>
      </td>
      <td data-label=${t("spalte_loesung")}>
        ${e.loesung}
        ${e.alternativen.length?r`<div class="klein">${e.alternativen.join(" | ")}</div>`:c}
        ${e.vorschlag?r`<div class="klein" style="margin-top: 4px">
              ${t(e.vorschlag_durch==="ki"?"vorschlag_ki":"vorschlag")}:
              <strong>${e.vorschlag}</strong>
              <button
                style="margin-left: 4px; padding: 2px 8px"
                title=${t("uebernehmen_titel")}
                ?disabled=${this._beschaeftigt}
                @click=${()=>this._uebernimmVorschlag([e.id])}
              >
                ${t("uebernehmen_loesung")}
              </button>
            </div>`:c}
      </td>
      <td
        class="schmal"
        data-label=${t("spalte_schwierigkeit")}
        title=${t("schwierigkeit_hinweis")}
      >
        ${e.schwierigkeit??r`<span class="klein">–</span>`}
      </td>
    `}_editorZeile(e,t,i){let n=this._t,s=this._fach?.typ==="mathe",l=e.art==="sach",h=l&&this._fach?.typ==="vokabel",d=this.hass?.language??"en",g=(f,k,z=64)=>r`
      <textarea
        style="min-height: ${z}px"
        aria-label=${k}
        placeholder=${k}
        maxlength="500"
        .value=${e[f]}
        @input=${y=>this._setzeEntwurf(f,v(y))}
      ></textarea>
    `,o=(f,k,z="")=>r`
      <input
        type="text"
        aria-label=${k}
        placeholder=${z}
        maxlength="500"
        .value=${e[f]}
        @input=${y=>this._setzeEntwurf(f,v(y))}
        @keydown=${y=>{y.key==="Enter"&&this._speichereAufgabe()}}
      />
    `,_=`${n("spalte_alternativen")} (${n("alternativen_hinweis")})`;return r`
      <tr class="gewaehlt">
        <td class="schmal"></td>
        ${s?r`
              <td data-label=${n("spalte_aufgabe")}>
                ${o("a",n("spalte_aufgabe"))}
                <textarea
                  style="margin-top: 4px; min-height: 64px"
                  aria-label=${n("rechenweg")}
                  placeholder=${n("rechenweg")}
                  .value=${e.rechenweg}
                  @input=${f=>this._setzeEntwurf("rechenweg",v(f))}
                ></textarea>
              </td>
              <td data-label=${n("spalte_loesung")}>
                ${o("b",n("spalte_loesung"))}
                <div style="margin-top: 4px">${o("altB",_,_)}</div>
              </td>
              <td class="schmal" data-label=${n("spalte_schwierigkeit")}>
                <select
                  aria-label=${n("schwierigkeit")}
                  title=${n("schwierigkeit_hinweis")}
                  .value=${e.schwierigkeit}
                  @change=${f=>this._setzeEntwurf("schwierigkeit",v(f))}
                >
                  <option value="" ?selected=${e.schwierigkeit===""}>–</option>
                  ${["1","2","3","4","5"].map(f=>r`<option value=${f} ?selected=${e.schwierigkeit===f}>
                        ${f}
                      </option>`)}
                </select>
              </td>
            `:l?r`
                <td data-label=${n(h?"spalte_satz":"spalte_frage")}>
                  ${e.form==="beschriftung"?r`<div>${e.a}</div>
                        ${this._originalBild(e.id)?r`<button
                              style="margin-top: 4px"
                              @click=${()=>void this._oeffneLabel(this._originalBild(e.id))}
                            >
                              ${n("beschriftung_bearbeiten")}
                            </button>`:c}`:g("a",n(h?"spalte_satz":"spalte_frage"))}
                  <select
                    style="margin-top: 4px"
                    ?hidden=${e.form==="beschriftung"}
                    aria-label=${n("form")}
                    .value=${e.form}
                    @change=${f=>{let k=v(f);this._setzeEntwurf("form",k==="auswahl"||k==="luecke"||k==="uebersetzung"?k:"kurz")}}
                  >
                    ${h?r`<option value="luecke" ?selected=${e.form==="luecke"}>
                            ${n("form_luecke")}
                          </option>
                          <option
                            value="uebersetzung"
                            ?selected=${e.form==="uebersetzung"}
                          >
                            ${n("form_uebersetzung")}
                          </option>`:c}
                    <option value="kurz" ?selected=${e.form==="kurz"}>
                      ${n("form_kurz")}
                    </option>
                    <option value="auswahl" ?selected=${e.form==="auswahl"}>
                      ${n("form_auswahl")}
                    </option>
                  </select>
                </td>
                <td
                  data-label=${n(h?"spalte_satz_loesung":"spalte_musterantwort")}
                >
                  ${g("b",n(e.form==="auswahl"?"richtige_antwort":h?"spalte_satz_loesung":"spalte_musterantwort"),e.form==="auswahl"?32:64)}
                  <div style="margin-top: 4px">
                    ${e.form==="auswahl"?g("falsche",n("falsche_optionen")):e.form==="luecke"||e.form==="uebersetzung"||e.form==="beschriftung"?o("altB",_,_):g("kernpunkte",n("kernpunkte"))}
                  </div>
                  ${h&&(e.form==="luecke"||e.form==="auswahl")?r`<div style="margin-top: 4px">
                        ${o("hilfe",n("hilfe_label",{sprache:E(d,t)}),n("hilfe_label",{sprache:E(d,t)}))}
                        <label class="feld zeile" style="margin-top: 4px">
                          <input
                            type="checkbox"
                            .checked=${e.hilfeSenden}
                            @change=${f=>this._setzeEntwurf("hilfeSenden",B(f))}
                          />
                          ${n("hilfe_senden")}
                        </label>
                      </div>`:c}
                </td>
              `:r`
              <td data-label=${E(d,t)}>
                ${o("a",E(d,t))}
                <div style="margin-top: 4px">${o("altA",_,_)}</div>
              </td>
              <td data-label=${E(d,i)}>
                ${o("b",E(d,i))}
                <div style="margin-top: 4px">${o("altB",_,_)}</div>
              </td>
            `}
        <td data-label=${n("spalte_hinweis")}>
          ${o("hinweis",n("spalte_hinweis"))}
        </td>
        <td class="schmal" data-label=${n("spalte_seite")}>
          <input
            type="number"
            min="1"
            max="9999"
            style="width: 5em"
            aria-label=${n("spalte_seite")}
            .value=${e.seite}
            @input=${f=>this._setzeEntwurf("seite",v(f))}
          />
        </td>
        <td data-label=${n("spalte_lektion")}>
          ${this._lektionAuswahl(e.lektion,f=>this._setzeEntwurf("lektion",f),n("spalte_lektion"))}
        </td>
        <td class="schmal"></td>
        <td class="schmal"></td>
        <td class="schmal" data-label=${n("spalte_geprueft")}>
          <input
            type="checkbox"
            aria-label=${n("spalte_geprueft")}
            .checked=${e.geprueft}
            @change=${f=>this._setzeEntwurf("geprueft",B(f))}
          />
        </td>
        <td class="schmal"></td>
        <td class="schmal">
          <button
            class="icon"
            title=${n("speichern")}
            aria-label=${n("speichern")}
            ?disabled=${this._beschaeftigt}
            @click=${this._speichereAufgabe}
          >
            <ha-icon icon="mdi:check"></ha-icon>
          </button>
          <button
            class="icon"
            title=${n("abbrechen")}
            aria-label=${n("abbrechen")}
            @click=${()=>{this._entwurf=null}}
          >
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </td>
      </tr>
    `}_arbeitenAnsicht(){let e=this._t,t=new Date().toISOString().slice(0,10),i=this._arbeitenDesFachs;return r`
      <div class="leiste">
        <button class="primaer" @click=${()=>this._oeffneArbeit(null)}>
          ${e("neue_arbeit")}
        </button>
      </div>
      ${i.length===0?r`<div class="card leer">${e("keine_arbeiten")}</div>`:i.map(n=>{let s=this._arbeitUmfang({lektionen:n.lektionen,bereiche:n.bereiche,ids:n.aufgaben_ids});return r`
              <div class="card arbeit">
                <div class="info">
                  <div class="titel">
                    ${n.thema}
                    <span class="marke">
                      ${e(n.art==="hue"?"art_hue":"art_arbeit")}
                    </span>
                    ${n.datum<t?r`<span class="marke warn">${e("vergangen")}</span>`:c}
                  </div>
                  <div class="klein">
                    ${this._datum(n.datum)} ·
                    ${s===null?e("arbeit_alle"):e("arbeit_umfang",{n:s})}
                    ${n.lektionen.length?r` · ${n.lektionen.join(", ")}`:c}
                    · ${n.abfragen_pro_tag} × / ${n.start_tage_vorher} d
                  </div>
                  ${n.simulation_um?r`<div class="klein">
                        <ha-icon
                          icon="mdi:calendar-clock"
                          style="--mdc-icon-size: 14px"
                        ></ha-icon>
                        ${e(n.simulation_geplant?"sim_plan_offen":"sim_plan_erledigt",{zeit:this._zeitpunkt(n.simulation_um),n:n.simulation_anzahl??10})}
                      </div>`:c}
                </div>
                <button
                  ?disabled=${n.simulierbar?.ausdruck===0}
                  title=${n.simulierbar?.ausdruck===0?e("sim_keine_aufgaben"):""}
                  @click=${()=>this._oeffneSimulation(n)}
                >
                  ${e(n.art==="hue"?"sim_knopf_hue":"sim_knopf_arbeit")}
                </button>
                <button @click=${()=>this._oeffneArbeit(n)}>
                  ${e("bearbeiten")}
                </button>
                <button class="gefahr" @click=${()=>this._loescheArbeit(n)}>
                  ${e("loeschen")}
                </button>
              </div>
            `})}
    `}_dialogInhalt(){if(!this._dialog)return c;let e;switch(this._dialog){case"generieren":e=this._generierenDialog();break;case"aufgabenart":e=this._aufgabenartDialog();break;case"bildaufgabe":e=this._bildaufgabeDialog();break;case"bild":e=r`
          <img class="grossbild" src=${this._grossbild} alt=${this._t("bild")} />
          ${this._bildText?r`<p style="margin: 12px 0 0">${this._bildText}</p>`:c}
          <div class="aktionen">
            <button class="primaer" @click=${this._schliesseDialog}>
              ${this._t("schliessen")}
            </button>
          </div>
        `;break;case"nachrechnen":e=this._nachrechnenDialog();break;case"seiten":e=this._seitenDialog();break;case"saetze":e=this._saetzeDialog();break;case"foto":e=this._fotoDialog();break;case"beschriftung":e=this._labelDialog();break;case"simulation":e=this._simulationDialog();break;case"import":e=this._importDialog();break;case"export":e=this._exportDialog();break;case"importJson":e=this._importJsonDialog();break;case"lektion":e=this._lektionDialog();break;case"bereiche":e=this._bereicheDialog();break;case"faecher":e=this._faecherDialog();break;default:e=this._arbeitDialog()}return r`
      <div
        class="overlay"
        @click=${t=>{t.target===t.currentTarget&&this._schliesseDialog()}}
      >
        <div
          class="dialog ${this._dialog==="foto"&&this._foto?.zeilen||this._dialog==="beschriftung"?"breit":""}"
          role="dialog"
          aria-modal="true"
        >
          ${e}
          ${this._dialogFehler?r`<div class="meldung fehler" role="alert" style="margin-top: 12px">
                <span>${this._dialogFehler}</span>
              </div>`:c}
        </div>
      </div>
    `}_simulationDialog(){let e=this._t,t=this._sim;if(!t)return r``;let i=t.arbeit.art==="hue",n=`${e(i?"sim_knopf_hue":"sim_knopf_arbeit")}: ${t.arbeit.thema}`;if(t.seiten)return r`
        <h2>${n}</h2>
        <p class="klein">${e("sim_blatt_hilfe",{n:t.anzahl})}</p>
        ${t.seiten.map((g,o)=>r`
            <img
              class="grossbild"
              style="max-height: 60vh; margin: 12px auto; border: 1px solid var(--lh-border)"
              src=${g}
              alt=${`${e("spalte_seite")} ${o+1}`}
            />
            <div class="aktionen" style="margin-top: 4px">
              <a
                class="knopf"
                href=${g}
                download=${`${i?"hue":"klassenarbeit"}-${o+1}.png`}
              >
                ${e("sim_herunterladen",{n:o+1})}
              </a>
            </div>
          `)}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${e("schliessen")}</button>
          <button class="primaer" @click=${this._druckeSimulation}>${e("sim_drucken")}</button>
        </div>
      `;let s=this._simVerfuegbar(t),l=Math.min(s,fe),h=this._uebersicht?.kinder.find(g=>g.id===this._kindId),d=["ausdruck","messenger"];return r`
      <h2>${n}</h2>
      <p class="klein">${e("sim_hilfe")}</p>
      <div class="wahl">
        ${d.map(g=>r`
            <button
              class=${t.weg===g?"primaer":""}
              aria-pressed=${t.weg===g?"true":"false"}
              @click=${()=>{let o={...t,weg:g},_=Math.min(this._simVerfuegbar(o),fe);this._sim={...o,anzahl:Math.max(1,Math.min(o.anzahl,_))}}}
            >
              <strong>${e(`sim_weg_${g}`)}</strong>
              <span class="klein">
                ${e(`sim_weg_${g}_hilfe`,{name:h?.name??""})}
              </span>
            </button>
          `)}
      </div>
      <label class="feld" style="margin-top: 12px; max-width: 260px">
        ${e("sim_anzahl")}
        <input
          type="number"
          min="1"
          max=${l}
          .value=${String(t.anzahl)}
          @input=${g=>{let o=Math.round(Number(v(g)))||1;this._sim={...t,anzahl:Math.max(1,Math.min(o,l))}}}
        />
        <span class="klein">${e("sim_verfuegbar",{n:s})}</span>
      </label>
      ${s===0?r`<div class="meldung fehler" role="status" style="margin-top: 12px">
            <span>${e("sim_keine_aufgaben")}</span>
          </div>`:c}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||s===0}
          @click=${this._simuliere}
        >
          ${e(t.weg==="messenger"?"sim_start_messenger":"sim_start_ausdruck")}
        </button>
      </div>
    `}_labelDialog(){let e=this._t,t=this._label,i=this._fach;if(!t||!i)return r``;if(t.schritt==="wahl"){let s=i.ki_status??(i.ki?i.ki_bilder?"ok":"ohne_bilder":"keine");return r`
        <h2>${e("beschriftung_titel")}</h2>
        <p class="klein">${e("beschriftung_hilfe")}</p>
        <label class="feld">
          ${e("beschriftung_bild")} *
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp"
            aria-label=${e("beschriftung_bild")}
            @change=${this._labelDatei}
          />
        </label>
        ${t.adresse?r`<img
              class="grossbild"
              style="max-height: 240px; margin-top: 12px"
              src=${t.adresse}
              alt=${e("beschriftung_bild")}
            />`:c}
        ${s==="ok"?c:r`<p class="klein" role="note">${e(`ki_${s}`)}</p>`}
        ${this._beschaeftigt?r`<p class="klein" role="status">${e("seiten_laeuft")}</p>`:c}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
          <button
            ?disabled=${this._beschaeftigt||!t.datei}
            @click=${()=>void this._labelStart(!1)}
          >
            ${e("beschriftung_von_hand")}
          </button>
          <button
            class="primaer"
            ?disabled=${this._beschaeftigt||!t.datei||s!=="ok"}
            @click=${()=>void this._labelStart(!0)}
          >
            ${e("beschriftung_suchen")}
          </button>
        </div>
      `}if(t.schritt==="vorschau")return r`
        <h2>${e("beschriftung_vorschau")}</h2>
        <p class="klein">${e("beschriftung_vorschau_hilfe")}</p>
        <img
          class="grossbild"
          src=${t.vorschauAdresse}
          alt=${e("beschriftung_vorschau")}
        />
        <ol class="klein" style="columns: 2; margin: 12px 0">
          ${t.felder.map(s=>r`<li value=${s.nr}>
                ${s.text}${s.alt?r` <span class="klein">(${s.alt})</span>`:c}
              </li>`)}
        </ol>
        <div class="aktionen">
          <button
            ?disabled=${this._beschaeftigt}
            @click=${()=>this._setzeLabel({schritt:"editor"})}
          >
            ${e("zurueck")}
          </button>
          <button
            class="primaer"
            ?disabled=${this._beschaeftigt}
            @click=${()=>void this._labelSpeichern()}
          >
            ${e(t.bestehend?"beschriftung_aktualisieren":"beschriftung_speichern",{n:t.felder.length})}
          </button>
        </div>
      `;let n=t.felder.some(s=>!s.text.trim());return r`
      <h2>${e("beschriftung_titel")}</h2>
      <p class="klein">${e("beschriftung_editor_hilfe")}</p>
      <div
        class="label-flaeche"
        @pointerdown=${this._labelZeigerRunter}
        @pointermove=${this._labelZeigerBewegt}
        @pointerup=${this._labelZeigerHoch}
        @pointercancel=${this._labelZeigerHoch}
      >
        <img src=${t.adresse} alt=${e("beschriftung_bild")} draggable="false" />
        ${t.felder.map((s,l)=>r`
            <div
              class="label-box ${t.gewaehlt===l?"gewaehlt":""}"
              data-box=${l}
              style="left:${s.x*100}%;top:${s.y*100}%;width:${s.b*100}%;height:${s.h*100}%"
            >
              <span class="label-nr" data-box=${l}>${s.nr}</span>
              <span class="label-griff" data-griff=${l}></span>
            </div>
          `)}
      </div>
      <div class="label-liste">
        ${t.felder.map((s,l)=>r`
            <div class="label-zeile ${t.gewaehlt===l?"gewaehlt":""}">
              <strong>${s.nr}</strong>
              <input
                type="text"
                aria-label=${e("beschriftung_text",{nr:s.nr})}
                placeholder=${e("beschriftung_text",{nr:s.nr})}
                .value=${s.text}
                @focus=${()=>this._setzeLabel({gewaehlt:l})}
                @input=${h=>this._setzeLabelFeld(l,{text:v(h)})}
              />
              <input
                type="text"
                aria-label=${e("beschriftung_alternativen",{nr:s.nr})}
                placeholder=${e("beschriftung_alternativen",{nr:s.nr})}
                .value=${s.alt}
                @input=${h=>this._setzeLabelFeld(l,{alt:v(h)})}
              />
              <button
                aria-label=${e("loeschen")}
                title=${e("loeschen")}
                @click=${()=>this._loescheLabelFeld(l)}
              >
                ✕
              </button>
            </div>
          `)}
      </div>
      <label class="feld" style="margin-top: 12px">
        ${e("spalte_lektion")}
        ${this._lektionAuswahl(t.lektion,s=>this._setzeLabel({lektion:s}),e("spalte_lektion"))}
      </label>
      ${n&&t.felder.length?r`<p class="klein" role="note">${e("beschriftung_text_fehlt")}</p>`:c}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||!t.felder.length||n}
          @click=${()=>void this._labelVorschau()}
        >
          ${e("beschriftung_pruefen")}
        </button>
      </div>
    `}_fotoDialog(){let e=this._t,t=this._foto,i=this._fach;if(!t||!i)return r``;let n=i.typ==="mathe",[s="",l=""]=i.sprachen,h=this.hass?.language??"en",d=t.zeilen;if(!d)return r`
        <h2>${e("foto_titel")}</h2>
        <p class="klein">${e(n?"foto_hilfe_mathe":"foto_hilfe")}</p>
        <label class="feld">
          ${e("seiten_waehlen",{n:D})} *
          <input
            type="file"
            multiple
            accept="image/png,image/jpeg,image/webp"
            aria-label=${e("seiten_waehlen",{n:D})}
            @change=${this._fotoGewaehlt}
          />
        </label>
        ${t.vorschauen.length?r`<div class="leiste" style="margin: 12px 0 0">
              ${t.vorschauen.map((_,f)=>r`<img
                    class="grossbild"
                    style="max-height: 140px; margin: 0"
                    src=${_}
                    alt=${`${e("spalte_seite")} ${f+1}`}
                  />`)}
            </div>`:c}
        ${this._beschaeftigt?r`<p class="klein" role="status">${e("seiten_laeuft")}</p>`:c}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
          <button
            class="primaer"
            ?disabled=${this._beschaeftigt||!t.dateien.length}
            @click=${this._leseFoto}
          >
            ${e("foto_auslesen")}
          </button>
        </div>
      `;let g=d.filter(_=>_.an).length,o=(_,f,k,z)=>r`
      <input
        type="text"
        aria-label=${k}
        maxlength="500"
        .value=${z}
        @input=${y=>this._setzeFotoZeile(_,{[f]:v(y),geaendert:!0})}
      />
    `;return r`
      <h2>${e("foto_vorschau_titel")}</h2>
      <p class="klein">${e("foto_vorschau_hilfe")}</p>
      <div class="tabelle-rahmen" style="max-height: 50vh; overflow: auto">
        <table>
          <thead>
            <tr>
              <th class="schmal">
                <input
                  type="checkbox"
                  aria-label=${e("alle_auswaehlen")}
                  .checked=${g===d.length}
                  @change=${_=>{let f=B(_);this._foto={...t,zeilen:d.map(k=>({...k,an:f}))}}}
                />
              </th>
              <th>${n?e("spalte_aufgabe"):E(h,s)}</th>
              <th>${n?e("spalte_loesung"):E(h,l)}</th>
              ${n?c:r`<th>${e("spalte_hinweis")}</th>`}
              <th class="schmal">${e("spalte_seite")}</th>
            </tr>
          </thead>
          <tbody>
            ${d.map((_,f)=>{let k=_.roh,z=!_.geaendert&&k.verifikation==="abweichung"&&k.vorschlag;return r`
                <tr class=${_.an?"gewaehlt":""}>
                  <td class="schmal">
                    <input
                      type="checkbox"
                      aria-label=${_.a}
                      .checked=${_.an}
                      @change=${y=>this._setzeFotoZeile(f,{an:B(y)})}
                    />
                  </td>
                  <td>
                    ${o(f,"a",n?e("spalte_aufgabe"):E(h,s),_.a)}
                    <div class="klein">
                      ${k.vorhanden?r`<span class="marke">${e("foto_vorhanden")}</span>`:c}
                      ${k.braucht_bild?r`<span class="marke warn">${e("foto_braucht_bild")}</span>`:c}
                    </div>
                  </td>
                  <td>
                    ${o(f,"b",n?e("spalte_loesung"):E(h,l),_.b)}
                    ${n&&!k.braucht_bild?r`<div class="klein">
                          ${_.geaendert||k.verifikation==="keine"?r`<span class="marke">${e("foto_unbestaetigt")}</span>`:z?r`<span class="marke warn">
                                    ${e(k.vorschlag_durch==="ki"?"nachrechnen_ki":"nachrechnen_berechnet")}:
                                    ${k.vorschlag}
                                  </span>
                                  <button
                                    @click=${()=>this._setzeFotoZeile(f,{b:k.vorschlag??_.b,roh:{...k,verifikation:k.vorschlag_durch==="ki"?"ki":"rechnerisch",vorschlag:null}})}
                                  >
                                    ${e("uebernehmen_loesung")}
                                  </button>`:r`<span class="marke ok">
                                  ${e(`verifikation_${k.verifikation??"ki"}`)}
                                </span>`}
                        </div>`:c}
                    ${!n&&!_.geaendert?r`<div class="klein">
                          ${Object.values(k.alternativen??{}).flat().join(" | ")}
                        </div>`:c}
                  </td>
                  ${n?c:r`<td>${o(f,"hinweis",e("spalte_hinweis"),_.hinweis)}</td>`}
                  <td class="schmal">
                    <input
                      type="number"
                      min="1"
                      max="9999"
                      style="width: 5em"
                      aria-label=${e("spalte_seite")}
                      .value=${_.seite}
                      @input=${y=>this._setzeFotoZeile(f,{seite:v(y)})}
                    />
                  </td>
                </tr>
              `})}
          </tbody>
        </table>
      </div>
      <label class="feld" style="margin-top: 12px">
        ${e("spalte_lektion")}
        ${this._lektionAuswahl(t.lektion,_=>{this._foto={...t,lektion:_}},e("spalte_lektion"))}
      </label>
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||!g}
          @click=${this._uebernimmFoto}
        >
          ${e("foto_uebernehmen",{n:g})}
        </button>
      </div>
    `}_seitenDialog(){let e=this._t,t=this._seiten;if(!t)return r``;let i=(s,l)=>{this._seiten={...t,[s]:l}},n=["gemischt","kurz","auswahl"];return r`
      <h2>${e("seiten_titel")}</h2>
      <p class="klein">${e("seiten_hilfe")}</p>
      <label class="feld">
        ${e("seiten_waehlen",{n:D})} *
        <input
          type="file"
          multiple
          accept="image/png,image/jpeg,image/webp"
          aria-label=${e("seiten_waehlen",{n:D})}
          @change=${this._seitenGewaehlt}
        />
      </label>
      ${t.vorschauen.length?r`<div class="leiste" style="margin: 12px 0 0">
            ${t.vorschauen.map((s,l)=>r`<img
                  class="grossbild"
                  style="max-height: 140px; margin: 0"
                  src=${s}
                  alt=${`${e("spalte_seite")} ${l+1}`}
                />`)}
          </div>`:c}
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(t.lektion,s=>i("lektion",s),e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("seiten_anzahl")}
          <input
            type="number"
            min="1"
            max="15"
            .value=${String(t.anzahl)}
            @input=${s=>i("anzahl",Math.min(Math.max(Math.round(Number(v(s)))||1,1),15))}
          />
        </label>
        <label class="feld">
          ${e("form")}
          <select
            .value=${t.form}
            @change=${s=>i("form",n.find(l=>l===v(s))??"gemischt")}
          >
            ${n.map(s=>r`<option value=${s} ?selected=${t.form===s}>
                  ${e(`form_${s}`)}
                </option>`)}
          </select>
        </label>
      </div>
      <label class="feld" style="margin-top: 12px">
        ${e("seiten_schwerpunkt")}
        <input
          type="text"
          maxlength="500"
          placeholder=${e("seiten_schwerpunkt_hilfe")}
          .value=${t.schwerpunkt}
          @input=${s=>i("schwerpunkt",v(s))}
        />
      </label>
      ${this._beschaeftigt?r`<p class="klein" role="status">${e("seiten_laeuft")}</p>`:c}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||!t.dateien.length}
          @click=${this._erzeugeFragen}
        >
          ${e("seiten_start")}
        </button>
      </div>
    `}_saetzeDialog(){let e=this._t,t=this._saetze;if(!t)return r``;let i=(o,_)=>{this._saetze={...t,[o]:_}},n=["gemischt","luecke","auswahl","uebersetzung"],s=this._bereiche.filter(o=>o.art==="satz"),l=this._fach,h=l?.ki_status??(l?.ki?l.ki_bilder?"ok":"ohne_bilder":"keine"),d=h==="ok",g=!t.dateien.length&&!t.beschreibung.trim();return r`
      <h2>${e("saetze_erzeugen")}</h2>
      <p class="klein">${e("saetze_hilfe")}</p>
      <label class="feld">
        ${e("saetze_fotos",{n:D})}
        <input
          type="file"
          multiple
          ?disabled=${!d}
          accept="image/png,image/jpeg,image/webp"
          aria-label=${e("saetze_fotos",{n:D})}
          @change=${this._saetzeSeitenGewaehlt}
        />
      </label>
      ${d?c:r`<p class="klein" role="note">${e(`ki_${h}`)}</p>`}
      ${t.vorschauen.length?r`<div class="leiste" style="margin: 12px 0 0">
              ${t.vorschauen.map((o,_)=>r`<img
                    class="grossbild"
                    style="max-height: 140px; margin: 0"
                    src=${o}
                    alt=${`${e("spalte_seite")} ${_+1}`}
                  />`)}
            </div>
            <div class="chips" style="margin: 12px 0">
              ${[!1,!0].map(o=>r`
                  <label class="feld zeile">
                    <input
                      type="radio"
                      name="saetze-modus"
                      .checked=${t.uebernehmen===o}
                      @change=${()=>i("uebernehmen",o)}
                    />
                    ${e(o?"saetze_uebernehmen":"saetze_aehnliche")}
                  </label>
                `)}
            </div>`:c}
      <label class="feld" style="margin-top: 12px">
        ${e("saetze_beschreibung")}
        <textarea
          maxlength="500"
          placeholder=${e("saetze_beschreibung_hilfe")}
          .value=${t.beschreibung}
          @input=${o=>i("beschreibung",v(o))}
        ></textarea>
      </label>
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${e("bereich")}
          <select
            .value=${t.bereich}
            @change=${o=>i("bereich",v(o))}
          >
            ${s.map(o=>r`<option value=${o.id} ?selected=${t.bereich===o.id}>
                  ${this._bereichName_(o)}
                </option>`)}
          </select>
        </label>
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(t.lektion,o=>i("lektion",o),e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("seiten_anzahl")}
          <input
            type="number"
            min="1"
            max="20"
            .value=${String(t.anzahl)}
            @input=${o=>i("anzahl",Math.min(Math.max(Math.round(Number(v(o)))||1,1),20))}
          />
        </label>
        <label class="feld">
          ${e("form")}
          <select
            .value=${t.form}
            @change=${o=>i("form",n.find(_=>_===v(o))??"gemischt")}
          >
            ${n.map(o=>r`<option value=${o} ?selected=${t.form===o}>
                  ${e(`form_${o}`)}
                </option>`)}
          </select>
        </label>
      </div>
      ${this._beschaeftigt?r`<p class="klein" role="status">${e("saetze_laeuft")}</p>`:c}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||g||!t.bereich}
          @click=${this._erzeugeSaetze}
        >
          ${e("saetze_start")}
        </button>
      </div>
    `}_aufgabenartDialog(){let e=this._t;return r`
      <h2>${e("aufgabenart_titel")}</h2>
      <div class="wahl">
        <button
          @click=${()=>{this._schliesseDialog(),this._bearbeite(null)}}
        >
          <strong>${e("aufgabenart_rechnen")}</strong>
          <span class="klein">${e("aufgabenart_rechnen_hilfe")}</span>
        </button>
        <button @click=${this._oeffneBildaufgabe}>
          <strong>${e("aufgabenart_bild")}</strong>
          <span class="klein">${e("aufgabenart_bild_hilfe")}</span>
        </button>
      </div>
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
      </div>
    `}_bildaufgabeDialog(){let e=this._t,t=this._bildEntwurf;if(!t)return r``;let i=this._uebersicht?.kinder.find(s=>s.id===this._kindId),n=`${e("spalte_alternativen")} (${e("alternativen_hinweis")})`;return r`
      <h2>${e("bildaufgabe_titel")}</h2>
      ${i&&!i.bilder?r`<div class="meldung fehler" role="status" style="margin-bottom: 12px">
            <span>${e("keine_bilder",{name:i.name})}</span>
          </div>`:c}
      <label class="feld">
        ${e("bild")} *
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          aria-label=${e("bild_waehlen")}
          @change=${this._bildGewaehlt}
        />
        <span>${e("bild_hilfe")}</span>
      </label>
      ${t.vorschau?r`<img
            class="grossbild"
            style="max-height: 240px; margin: 12px auto"
            src=${t.vorschau}
            alt=${e("bild_vorschau")}
          />`:c}
      <label class="feld" style="margin-top: 12px">
        ${e("einleitung")}
        <textarea
          maxlength="300"
          style="min-height: 56px"
          placeholder=${e("einleitung_hilfe")}
          .value=${t.einleitung}
          @input=${s=>this._setzeBild("einleitung",v(s))}
        ></textarea>
      </label>
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(t.lektion,s=>this._setzeBild("lektion",s),e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("spalte_seite")}
          <input
            type="number"
            min="1"
            max="9999"
            .value=${t.seite}
            @input=${s=>this._setzeBild("seite",v(s))}
          />
        </label>
      </div>
      <fieldset>
        <legend>${e("teilaufgaben")}</legend>
        <p class="klein" style="margin-top: 0">${e("teilaufgaben_hilfe")}</p>
        ${t.teile.map((s,l)=>r`
            <div class="teil">
              <label class="feld">
                ${e("teilaufgabe",{n:l+1})}
                <input
                  type="text"
                  maxlength="400"
                  placeholder="a) …"
                  .value=${s.aufgabe}
                  @input=${h=>this._setzeTeil(l,"aufgabe",v(h))}
                />
              </label>
              <label class="feld">
                ${e("spalte_loesung")}
                <input
                  type="text"
                  maxlength="100"
                  .value=${s.loesung}
                  @input=${h=>this._setzeTeil(l,"loesung",v(h))}
                />
              </label>
              <label class="feld">
                ${e("spalte_alternativen")}
                <input
                  type="text"
                  maxlength="300"
                  placeholder=${n}
                  .value=${s.alternativen}
                  @input=${h=>this._setzeTeil(l,"alternativen",v(h))}
                />
              </label>
              <button
                class="icon"
                title=${e("teilaufgabe_entfernen")}
                aria-label=${e("teilaufgabe_entfernen")}
                ?disabled=${t.teile.length<2}
                @click=${()=>this._setzeBild("teile",t.teile.filter((h,d)=>d!==l))}
              >
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            </div>
          `)}
        <button
          ?disabled=${t.teile.length>=8}
          @click=${()=>this._setzeBild("teile",[...t.teile,{...ct}])}
        >
          ${e("teilaufgabe_hinzufuegen")}
        </button>
      </fieldset>
      <div class="aktionen">
        <button ?disabled=${this._beschaeftigt} @click=${this._schliesseDialog}>
          ${e("abbrechen")}
        </button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt}
          @click=${this._speichereBildaufgabe}
        >
          ${e("speichern")}
        </button>
      </div>
    `}_nachrechnenDialog(){let e=this._t,t=this._nachgerechnet;return t?r`
      <h2>${e("nachrechnen_titel")}</h2>
      <p class="klein">
        ${e("nachrechnen_zusammenfassung",{bestaetigt:t.bestaetigt,offen:t.nicht_pruefbar})}
      </p>
      <div class="liste">
        ${t.abweichend.map(i=>r`
            <div class="eintrag">
              <span style="flex: 1">
                ${i.aufgabe}
                <div class="klein">
                  ${e("nachrechnen_eingetragen")}: ${i.loesung} ·
                  ${e(i.durch==="ki"?"nachrechnen_ki":"nachrechnen_berechnet")}:
                  <strong>${i.berechnet??"?"}</strong>
                </div>
              </span>
              ${i.berechnet?r`<button
                    title=${e("uebernehmen_titel")}
                    ?disabled=${this._beschaeftigt}
                    @click=${()=>this._uebernimmVorschlag([i.id])}
                  >
                    ${e("uebernehmen_loesung")}
                  </button>`:c}
            </div>
          `)}
      </div>
      <div class="aktionen">
        <button
          @click=${()=>{this._nurIds=new Set(t.abweichend.map(i=>i.id)),this._auswahl=new Set,this._schliesseDialog()}}
        >
          ${e("nur_abweichende")}
        </button>
        <button ?disabled=${this._beschaeftigt} @click=${this._uebernimmAlle}>
          ${e("alle_uebernehmen")}
        </button>
        <button class="primaer" @click=${this._schliesseDialog}>${e("schliessen")}</button>
      </div>
    `:r``}_generierenDialog(){let e=this._t,t=this._generieren;if(!t)return r``;let i=(s,l)=>{this._generieren={...t,[s]:l}},n=this._auswahl.size;return r`
      <h2>${e("generieren_titel")}</h2>
      <p class="klein">${e("generieren_hilfe")}</p>
      <div class="raster">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(t.lektion,s=>i("lektion",s),e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("generieren_anzahl")}
          <input
            type="number"
            min="1"
            max="20"
            .value=${String(t.anzahl)}
            @input=${s=>i("anzahl",Math.min(20,Math.max(1,Number(v(s))||1)))}
          />
        </label>
        <label class="feld">
          ${e("schwierigkeit")}
          <select
            title=${e("schwierigkeit_hinweis")}
            .value=${t.schwierigkeit}
            @change=${s=>i("schwierigkeit",v(s))}
          >
            <option value="" ?selected=${t.schwierigkeit===""}>
              ${e("schwierigkeit_beliebig")}
            </option>
            ${["1","2","3","4","5"].map(s=>r`<option value=${s} ?selected=${t.schwierigkeit===s}>
                  ${s}
                </option>`)}
          </select>
        </label>
      </div>
      <label class="feld" style="margin-top: 12px">
        ${e("generieren_beschreibung")}
        <textarea
          maxlength="500"
          placeholder=${e("generieren_beschreibung_hilfe")}
          .value=${t.beschreibung}
          @input=${s=>i("beschreibung",v(s))}
        ></textarea>
      </label>
      <p class="klein">
        ${n?e("generieren_beispiele_auswahl",{n}):e("generieren_beispiele_thema")}
      </p>
      ${this._beschaeftigt?r`<p class="klein" role="status">${e("generieren_laeuft")}</p>`:c}
      <div class="aktionen">
        <button ?disabled=${this._beschaeftigt} @click=${this._schliesseDialog}>
          ${e("abbrechen")}
        </button>
        <button class="primaer" ?disabled=${this._beschaeftigt} @click=${this._generiere}>
          ${e("generieren_start")}
        </button>
      </div>
    `}_importDialog(){let e=this._t,[t="",i=""]=this._fach?.sprachen??[],n=this.hass?.language??"en",s=this._vorschau,l=s?.zeilen.filter(d=>!d.vorhanden).length??0,h=this._fach?.typ==="mathe";return r`
      <h2>${e(h?"import_titel_mathe":"import_titel")}</h2>
      <p class="klein">
        ${h?e("import_hilfe_mathe"):e("import_hilfe",{a:E(n,t),b:E(n,i)})}
      </p>
      <label class="feld">
        ${e("import_inhalt")}
        <textarea
          .value=${this._importText}
          placeholder=${h?`7 \xB7 8; 56
3/4 + 1/8; 7/8 | 0,875; Br\xFCche`:`Hund; dog|hound; Nomen
gehen; to go`}
          @input=${d=>{this._importText=v(d),this._vorschau=null}}
        ></textarea>
      </label>
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(this._importLektion,d=>{this._importLektion=d},e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("import_trennzeichen")}
          <input
            type="text"
            maxlength="5"
            .value=${this._importTrenner}
            @input=${d=>{this._importTrenner=v(d),this._vorschau=null}}
          />
        </label>
      </div>
      <label class="feld zeile">
        <input
          type="checkbox"
          .checked=${this._importGeprueft}
          @change=${d=>{this._importGeprueft=B(d)}}
        />
        ${e("import_geprueft")}
      </label>
      ${s?r`
            <div class="liste" style="margin-top: 12px">
              ${s.zeilen.map(d=>r`
                  <label>
                    <span style="flex: 1">
                      ${d.frage?`${d.frage[t]??""} \u2192 ${d.frage[i]??""}`:`${d.aufgabe??""} \u2192 ${d.loesung??""}`}
                      ${d.hinweis?r`<span class="klein"> (${d.hinweis})</span>`:c}
                    </span>
                    <span class="marke ${d.vorhanden?"":"ok"}">
                      ${e(d.vorhanden?"vorschau_vorhanden":"vorschau_neu")}
                    </span>
                  </label>
                `)}
            </div>
            ${s.fehlerzeilen.length?r`<p class="klein" style="color: var(--lh-error)">
                  ${e("vorschau_fehler",{zeilen:s.fehlerzeilen.join(", ")})}
                </p>`:c}
          `:c}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button ?disabled=${!this._importText.trim()} @click=${this._importVorschau}>
          ${e("vorschau")}
        </button>
        <button
          class="primaer"
          ?disabled=${!s||l===0||this._beschaeftigt}
          @click=${this._importUebernehmen}
        >
          ${e("uebernehmen")} ${s?`(${l})`:""}
        </button>
      </div>
    `}_lektionDialog(){let e=this._t,t=this._fach?.lektionen??[],i=n=>this._aufgaben.filter(s=>s.lektion===n).length;return r`
      <h2>${e("lektion_titel")}</h2>
      <p class="klein">${e("lektion_hilfe")}</p>
      <div class="leiste">
        <label class="feld" style="flex: 1">
          ${e("lektion_name")}
          <input
            id="lektion-name"
            type="text"
            maxlength="100"
            .value=${this._lektionName}
            @input=${n=>{this._lektionName=v(n)}}
            @keydown=${n=>{n.key==="Enter"&&this._lektionAnlegen()}}
          />
        </label>
        <button
          class="primaer"
          style="align-self: flex-end"
          ?disabled=${!this._lektionName.trim()}
          @click=${this._lektionAnlegen}
        >
          ${e("hinzufuegen")}
        </button>
      </div>
      ${t.length===0?r`<div class="leer">${e("lektion_keine")}</div>`:r`<div class="liste">
            ${t.map(n=>{let s=i(n);return r`
                <div class="eintrag">
                  <span style="flex: 1">${n}</span>
                  <span class="klein">${e("lektion_anzahl",{n:s})}</span>
                  <button
                    class="icon"
                    title=${s>0?e("lektion_loeschen_hinweis"):e("loeschen")}
                    aria-label=${`${e("loeschen")}: ${n}`}
                    ?disabled=${s>0}
                    @click=${()=>this._lektionLoeschen(n)}
                  >
                    <ha-icon icon="mdi:delete"></ha-icon>
                  </button>
                </div>
              `})}
          </div>`}
      <div class="aktionen">
        <button class="primaer" @click=${this._schliesseDialog}>
          ${e("schliessen")}
        </button>
      </div>
    `}_bereicheDialog(){let e=this._t,t=this._bereichUmbenennen;return r`
      <h2>${e("bereiche_titel")}</h2>
      <p class="klein">${e("bereiche_hilfe")}</p>
      <div class="leiste">
        <label class="feld" style="flex: 1">
          ${e("bereich_name")}
          <input
            type="text"
            maxlength="60"
            .value=${this._bereichName}
            @input=${i=>{this._bereichName=v(i)}}
            @keydown=${i=>{i.key==="Enter"&&this._bereichAnlegen()}}
          />
        </label>
        ${this._fach?.typ==="vokabel"?r`<label class="feld">
              ${e("bereich_art")}
              <select
                @change=${i=>{this._bereichArt=v(i)==="satz"?"satz":"vokabel"}}
              >
                <option value="vokabel" ?selected=${this._bereichArt==="vokabel"}>
                  ${e("bereich_art_vokabel")}
                </option>
                <option value="satz" ?selected=${this._bereichArt==="satz"}>
                  ${e("bereich_art_satz")}
                </option>
              </select>
            </label>`:c}
        <button
          class="primaer"
          style="align-self: flex-end"
          ?disabled=${!this._bereichName.trim()}
          @click=${this._bereichAnlegen}
        >
          ${e("hinzufuegen")}
        </button>
      </div>
      <div class="liste">
        ${this._bereiche.map(i=>{let n=i.id===W;return r`
            <div class="eintrag">
              ${t?.id===i.id?r`<input
                      type="text"
                      maxlength="60"
                      style="flex: 1"
                      aria-label=${e("bereich_name")}
                      .value=${t.name}
                      @input=${s=>{this._bereichUmbenennen={id:i.id,name:v(s)}}}
                      @keydown=${s=>{s.key==="Enter"&&this._bereichUmbenennenSpeichern()}}
                    />
                    <button class="primaer" @click=${this._bereichUmbenennenSpeichern}>
                      ${e("speichern")}
                    </button>`:r`<span style="flex: 1">${this._bereichName_(i)}</span>
                    <span class="klein">${e("lektion_anzahl",{n:i.aufgaben})}</span>
                    <button
                      class="icon"
                      title=${e("umbenennen")}
                      aria-label=${`${e("umbenennen")}: ${this._bereichName_(i)}`}
                      @click=${()=>{this._bereichUmbenennen={id:i.id,name:this._bereichName_(i)}}}
                    >
                      <ha-icon icon="mdi:pencil"></ha-icon>
                    </button>
                    <button
                      class="icon"
                      title=${n?e("bereich_standard_hinweis"):i.aufgaben>0?e("bereich_loeschen_hinweis"):e("loeschen")}
                      aria-label=${`${e("loeschen")}: ${this._bereichName_(i)}`}
                      ?disabled=${n||i.aufgaben>0}
                      @click=${()=>this._bereichLoeschen(i.id)}
                    >
                      <ha-icon icon="mdi:delete"></ha-icon>
                    </button>`}
            </div>
          `})}
      </div>
      <div class="aktionen">
        <button class="primaer" @click=${this._schliesseDialog}>
          ${e("schliessen")}
        </button>
      </div>
    `}_statistikSchalter(){return r`
      <label class="feld zeile">
        <input
          type="checkbox"
          .checked=${this._mitStatistik}
          @change=${e=>{this._mitStatistik=B(e)}}
        />
        ${this._t("mit_statistik")}
      </label>
    `}_exportDialog(){let e=this._t;return r`
      <h2>${e("export_titel")}</h2>
      ${this._statistikSchalter()}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button class="primaer" @click=${this._exportiere}>${e("herunterladen")}</button>
      </div>
    `}_importJsonDialog(){let e=this._t,t=this._jsonDaten?.aufgaben,i=Array.isArray(t)?t.length:0;return r`
      <h2>${e("import_json_titel")}</h2>
      <p>${e("arbeit_umfang",{n:i})}</p>
      <p class="klein">${e("import_json_hilfe")}</p>
      <label class="feld" style="margin-bottom: 12px">
        ${e("import_json_lektion")}
        <select
          id="json-lektion"
          .value=${this._jsonLektion}
          @change=${n=>{this._jsonLektion=v(n)}}
        >
          <option value="" ?selected=${this._jsonLektion===""}>
            ${e("import_json_aus_datei")}
          </option>
          ${(this._fach?.lektionen??[]).map(n=>r`<option value=${n} ?selected=${n===this._jsonLektion}>
                ${n}
              </option>`)}
        </select>
        <span>${e("import_json_lektion_hilfe")}</span>
      </label>
      ${this._statistikSchalter()}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt}
          @click=${this._importiereJson}
        >
          ${e("uebernehmen")}
        </button>
      </div>
    `}_fachFormular(e,t,i){let n=this._t,s=this.hass?.language??"en",l=h=>{this._neuesFach&&(this._neuesFach={...this._neuesFach,...h})};return r`<fieldset style="margin-bottom: 12px">
      <legend>${n("fach_neu_titel")}</legend>
      <div class="raster">
        <label class="feld">
          ${n("fach_neu_art")}
          <select .value=${e.typ} @change=${h=>l({typ:v(h)})}>
            ${Kt.map(h=>r`<option value=${h} ?selected=${h===e.typ}>
                  ${n(`fachart_${h}`)}
                </option>`)}
          </select>
        </label>
        ${e.typ==="fremdsprache"?r`<label class="feld">
              ${n("fach_neu_sprache")}
              <select .value=${e.sprache} @change=${h=>l({sprache:v(h)})}>
                ${Ht.map(h=>r`<option value=${h} ?selected=${h===e.sprache}>
                      ${E(s,h)}
                    </option>`)}
              </select>
            </label>`:c}
        <label class="feld">
          ${n(e.typ==="sach"?"fach_neu_name":"fach_neu_name_optional")}
          <input
            type="text"
            maxlength="60"
            .value=${e.name}
            @input=${h=>l({name:v(h)})}
          />
        </label>
      </div>
      <div class="zeile" style="margin-top: 8px">
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||e.typ==="sach"&&!e.name.trim()}
          @click=${i}
        >
          ${n("fach_neu_anlegen")}
        </button>
        ${t?r`<button
              @click=${()=>{this._neuesFach=null}}
            >
              ${n("abbrechen")}
            </button>`:c}
      </div>
    </fieldset>`}_oeffneFaecher(){this._neuesFach=null,this._dialogFehler="",this._dialog="faecher"}async _legeFachNeuAn(){let e=this._neuesFach;if(e){this._beschaeftigt=!0,this._dialogFehler="";try{let t=await this._api.fachAnlegen(this._kindId,e.typ,e.name.trim(),e.typ==="fremdsprache"?e.sprache:null);this._uebersicht=await this._api.uebersicht(),this._neuesFach=null,await this._waehleFach(t),this._zeigeErfolg(this._t("fach_angelegt"))}catch(t){this._dialogFehler=x(this._t,t)}finally{this._beschaeftigt=!1}}}_faecherDialog(){let e=this._t,t=this._faecherDesKindes,i=this._neuesFach;return r`
      <h2>${e("faecher_verwalten")}</h2>
      <p class="klein">${e("faecher_hilfe")}</p>
      ${t.length?r`<div class="liste">
            ${t.map(n=>r`
                <div class="eintrag">
                  <span style="flex: 1">${n.name}</span>
                  <span class="klein">
                    ${e(`fachart_${n.typ==="vokabel"?"fremdsprache":n.typ}`)} ·
                    ${e("lektion_anzahl",{n:n.anzahl_aufgaben})}
                  </span>
                </div>
              `)}
          </div>`:r`<div class="leer">${e("keine_faecher")}</div>`}
      ${i?this._fachFormular(i,!0,this._legeFachNeuAn):r`<div class="zeile" style="margin: 12px 0">
            <button
              class="primaer"
              @click=${()=>{this._neuesFach={...Le}}}
            >
              + ${e("fach_neu")}
            </button>
          </div>`}
      <p class="klein">
        <a href="/config/integrations/integration/learnbuddy">${e("faecher_einstellungen")}</a>
      </p>
      <div class="aktionen">
        <button class="primaer" @click=${this._schliesseDialog}>${e("schliessen")}</button>
      </div>
    `}_fachWahl(){let e=this._t,t=this._neuesFach,i=this._faecherDesKindes,n=this._arbeit?.fachOffen??!1;return r`
      ${i.length?r`<div class="zeile" style="align-items: end; margin-bottom: 12px">
            <label class="feld" style="flex: 1">
              ${e("arbeit_fach")}
              <select
                .value=${n?"":this._fachId}
                @change=${s=>this._wechsleFachImDialog(v(s))}
              >
                ${n?r`<option value="" selected disabled>${e("arbeit_fach_waehlen")}</option>`:c}
                ${i.map(s=>r`<option
                      value=${s.id}
                      ?selected=${!n&&s.id===this._fachId}
                    >
                      ${s.name}
                    </option>`)}
              </select>
            </label>
            <button
              title=${e("fach_neu")}
              aria-label=${e("fach_neu")}
              ?disabled=${t!==null}
              @click=${()=>{this._neuesFach={...Le}}}
            >
              + ${e("fach_neu")}
            </button>
          </div>`:c}
      ${t?this._fachFormular(t,i.length>0,this._legeFachAn):c}
    `}_arbeitDialog(){let e=this._t,t=this._arbeit,i=this._fach;if(!t)return r``;if(!i)return r`
        <h2>${e("arbeit_titel_neu")}</h2>
        <p class="klein">${e("fach_neu_fehlt")}</p>
        ${this._fachWahl()}
        ${this._dialogFehler?r`<div class="meldung fehler" role="alert">${this._dialogFehler}</div>`:c}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        </div>
      `;let[n="",s=""]=i.sprachen,l=t.modus==="alle"?this._aufgaben.length:this._arbeitUmfang(t)??this._aufgaben.length,h=(o,_,f)=>r`
      <label class="feld">
        ${_}
        <input
          type="number"
          min="1"
          max=${f??c}
          .value=${String(t[o])}
          @input=${k=>this._setzeArbeit(o,Number(v(k))||1)}
        />
      </label>
    `,d=!t.thema.trim(),g=t.fachOffen?"arbeit_fehlt_fach":d&&!t.datum?"arbeit_fehlt_beides":d?"arbeit_fehlt_thema":t.datum?null:"arbeit_fehlt_datum";return r`
      <h2>${e(t.id?"arbeit_titel_bearbeiten":"arbeit_titel_neu")}</h2>
      ${t.kalenderUid?this._fachWahl():c}
      <div class="raster">
        <label class="feld">
          ${e("thema")} *
          <input
            type="text"
            required
            maxlength="200"
            .value=${t.thema}
            @input=${o=>this._setzeArbeit("thema",v(o))}
          />
        </label>
        <label class="feld">
          ${e("datum")} *
          <input
            type="date"
            required
            .value=${t.datum}
            @change=${o=>this._setzeArbeit("datum",v(o))}
          />
        </label>
        <label class="feld">
          ${e("art")}
          <select
            .value=${t.art}
            @change=${o=>this._setzeArbeit("art",v(o)==="hue"?"hue":"arbeit")}
          >
            <option value="arbeit" ?selected=${t.art==="arbeit"}>
              ${e("art_arbeit")}
            </option>
            <option value="hue" ?selected=${t.art==="hue"}>
              ${e("art_hue")}
            </option>
          </select>
        </label>
        ${h("abfragen",e("abfragen_pro_tag"))}
        ${h("start",e("start_tage_vorher"),90)}
        <label class="feld">
          ${e("antwortfrist")}
          <input
            type="number"
            min="1"
            max="1440"
            placeholder=${e("antwortfrist_leer")}
            .value=${t.frist===null?"":String(t.frist)}
            @input=${o=>{let _=Math.round(Number(v(o)));this._setzeArbeit("frist",_>=1?Math.min(_,1440):null)}}
          />
          <span class="klein">${e("antwortfrist_hinweis")}</span>
        </label>
      </div>
      <label class="feld zeile" style="margin-bottom: 12px">
        <input
          type="checkbox"
          .checked=${t.intensivierung}
          @change=${o=>this._setzeArbeit("intensivierung",B(o))}
        />
        ${e("intensivierung")}
      </label>

      <fieldset>
        <legend>${e("sim_plan")}</legend>
        <label class="feld zeile">
          <input
            type="checkbox"
            .checked=${t.simAktiv}
            @change=${o=>this._setzeArbeit("simAktiv",B(o))}
          />
          ${e("sim_plan_aktiv")}
        </label>
        ${t.simAktiv?r`<p class="klein">${e("sim_plan_hilfe")}</p>
              <div class="raster">
                <label class="feld">
                  ${e("sim_plan_um")}
                  <input
                    type="datetime-local"
                    .value=${t.simUm}
                    @change=${o=>this._setzeArbeit("simUm",v(o))}
                  />
                </label>
                <label class="feld">
                  ${e("sim_anzahl")}
                  <input
                    type="number"
                    min="1"
                    max=${fe}
                    .value=${String(t.simAnzahl)}
                    @input=${o=>this._setzeArbeit("simAnzahl",Math.max(1,Math.min(Math.round(Number(v(o)))||1,fe)))}
                  />
                </label>
              </div>`:c}
      </fieldset>

      <fieldset>
        <legend>
          ${e("aufgaben_der_arbeit")} – ${e("arbeit_umfang",{n:l})}
        </legend>
        <div class="chips" style="margin-bottom: 10px">
          ${["alle","auswahl"].map(o=>r`
              <label class="feld zeile">
                <input
                  type="radio"
                  name="modus"
                  .checked=${t.modus===o}
                  @change=${()=>this._setzeArbeit("modus",o)}
                />
                ${e(o==="alle"?"auswahl_alle":"auswahl_gezielt")}
              </label>
            `)}
        </div>
        ${t.modus==="auswahl"?r`
              ${(i.bereiche?.length??0)>1?r`
                    <div class="klein">${e("schnell_bereiche")}</div>
                    <div class="chips" style="margin: 6px 0 12px">
                      ${(i.bereiche??[]).map(o=>r`
                          <label class="feld zeile">
                            <input
                              type="checkbox"
                              .checked=${t.bereiche.has(o.id)}
                              @change=${_=>this._arbeitMenge("bereiche",o.id,B(_))}
                            />
                            ${this._bereichName_(o)}
                          </label>
                        `)}
                    </div>
                  `:c}
              ${i.lektionen.length?r`
                    <div class="klein">${e("schnell_lektionen")}</div>
                    <div class="chips" style="margin: 6px 0 12px">
                      ${i.lektionen.map(o=>r`
                          <label class="feld zeile">
                            <input
                              type="checkbox"
                              .checked=${t.lektionen.has(o)}
                              @change=${_=>this._arbeitMenge("lektionen",o,B(_))}
                            />
                            ${o}
                          </label>
                        `)}
                    </div>
                  `:c}
              <div class="leiste" style="align-items: flex-end">
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${e("schnell_seit")}
                  <input
                    type="date"
                    .value=${t.seit}
                    @change=${o=>this._setzeArbeit("seit",v(o))}
                  />
                </label>
                <button ?disabled=${!t.seit} @click=${this._arbeitSeit}>
                  ${e("hinzufuegen")}
                </button>
              </div>
              <div class="leiste" style="align-items: flex-end">
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${e("schnell_seiten")}
                  <input
                    type="number"
                    min="1"
                    .value=${t.seiteVon}
                    @input=${o=>this._setzeArbeit("seiteVon",v(o))}
                  />
                </label>
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${e("schnell_seiten_bis")}
                  <input
                    type="number"
                    min="1"
                    .value=${t.seiteBis}
                    @input=${o=>this._setzeArbeit("seiteBis",v(o))}
                  />
                </label>
                <button
                  ?disabled=${!t.seiteVon&&!t.seiteBis}
                  @click=${this._arbeitSeiten}
                >
                  ${e("hinzufuegen")}
                </button>
                <span class="abstand"></span>
                <button
                  ?disabled=${t.ids.size===0}
                  @click=${()=>this._setzeArbeit("ids",new Set)}
                >
                  ${e("auswahl_leeren")}
                </button>
              </div>
              <div class="klein">${e("einzelne_aufgaben")} (${t.ids.size})</div>
              <div class="liste" style="margin-top: 6px">
                <div class="eintrag kopf">
                  <span class="haken"></span>
                  <span style="flex: 1">${e("spalte_aufgabe")}</span>
                  <span class="seite">${e("spalte_seite")}</span>
                  <span class="lektion">${e("spalte_lektion")}</span>
                </div>
                ${this._aufgaben.map(o=>{let _=o.lektion!==null&&t.lektionen.has(o.lektion);return r`
                    <label>
                      <input
                        type="checkbox"
                        .checked=${_||t.ids.has(o.id)}
                        ?disabled=${_}
                        @change=${f=>this._arbeitMenge("ids",o.id,B(f))}
                      />
                      <span style="flex: 1">
                        ${_e(o,n,s)}
                      </span>
                      <span class="klein seite">${o.seite??""}</span>
                      <span class="klein lektion">${o.lektion??""}</span>
                    </label>
                  `})}
              </div>
            `:c}
      </fieldset>
      <div class="aktionen">
        ${g?r`<span class="klein" role="status" style="margin-right: auto">
              ${e(g)}
            </span>`:c}
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||g!==null}
          @click=${this._speichereArbeit}
        >
          ${e("speichern")}
        </button>
      </div>
    `}};b([F({attribute:!1})],$.prototype,"hass",2),b([F({type:Boolean,reflect:!0})],$.prototype,"narrow",2),b([m()],$.prototype,"_uebersicht",2),b([m()],$.prototype,"_kindId",2),b([m()],$.prototype,"_fachId",2),b([m()],$.prototype,"_aufgaben",2),b([m()],$.prototype,"_tab",2),b([m()],$.prototype,"_filter",2),b([m()],$.prototype,"_auswahl",2),b([m()],$.prototype,"_entwurf",2),b([m()],$.prototype,"_dialog",2),b([m()],$.prototype,"_generieren",2),b([m()],$.prototype,"_bildEntwurf",2),b([m()],$.prototype,"_bildAdressen",2),b([m()],$.prototype,"_grossbild",2),b([m()],$.prototype,"_bildText",2),b([m()],$.prototype,"_seiten",2),b([m()],$.prototype,"_saetze",2),b([m()],$.prototype,"_foto",2),b([m()],$.prototype,"_label",2),b([m()],$.prototype,"_sim",2),b([m()],$.prototype,"_veraltet",2),b([m()],$.prototype,"_nachgerechnet",2),b([m()],$.prototype,"_nurIds",2),b([m()],$.prototype,"_meldung",2),b([m()],$.prototype,"_laedt",2),b([m()],$.prototype,"_beschaeftigt",2),b([m()],$.prototype,"_importText",2),b([m()],$.prototype,"_importLektion",2),b([m()],$.prototype,"_importTrenner",2),b([m()],$.prototype,"_importGeprueft",2),b([m()],$.prototype,"_vorschau",2),b([m()],$.prototype,"_mitStatistik",2),b([m()],$.prototype,"_jsonDaten",2),b([m()],$.prototype,"_arbeit",2),b([m()],$.prototype,"_neuesFach",2),b([m()],$.prototype,"_dialogFehler",2),b([m()],$.prototype,"_lektionName",2),b([m()],$.prototype,"_bereichId",2),b([m()],$.prototype,"_bereichName",2),b([m()],$.prototype,"_bereichArt",2),b([m()],$.prototype,"_bereichUmbenennen",2),b([m()],$.prototype,"_jsonLektion",2);customElements.get("learnbuddy-panel")||customElements.define("learnbuddy-panel",$);export{$ as LearnBuddyPanel};
