var Ge=Object.defineProperty;var Ze=Object.getOwnPropertyDescriptor;var f=(o,n,e,t)=>{for(var i=t>1?void 0:t?Ze(n,e):n,s=o.length-1,a;s>=0;s--)(a=o[s])&&(i=(t?a(n,e,i):a(i))||i);return t&&i&&Ge(n,e,i),i};var Y=globalThis,ee=Y.ShadowRoot&&(Y.ShadyCSS===void 0||Y.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,oe=Symbol(),ke=new WeakMap,U=class{constructor(n,e,t){if(this._$cssResult$=!0,t!==oe)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=n,this.t=e}get styleSheet(){let n=this.o,e=this.t;if(ee&&n===void 0){let t=e!==void 0&&e.length===1;t&&(n=ke.get(e)),n===void 0&&((this.o=n=new CSSStyleSheet).replaceSync(this.cssText),t&&ke.set(e,n))}return n}toString(){return this.cssText}},$e=o=>new U(typeof o=="string"?o:o+"",void 0,oe),q=(o,...n)=>{let e=o.length===1?o[0]:n.reduce((t,i,s)=>t+(a=>{if(a._$cssResult$===!0)return a.cssText;if(typeof a=="number")return a;throw Error("Value passed to 'css' function must be a 'css' function result: "+a+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.")})(i)+o[s+1],o[0]);return new U(e,o,oe)},we=(o,n)=>{if(ee)o.adoptedStyleSheets=n.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet);else for(let e of n){let t=document.createElement("style"),i=Y.litNonce;i!==void 0&&t.setAttribute("nonce",i),t.textContent=e.cssText,o.appendChild(t)}},he=ee?o=>o:o=>o instanceof CSSStyleSheet?(n=>{let e="";for(let t of n.cssRules)e+=t.cssText;return $e(e)})(o):o;var{is:We,defineProperty:Je,getOwnPropertyDescriptor:Qe,getOwnPropertyNames:Xe,getOwnPropertySymbols:Ye,getPrototypeOf:et}=Object,te=globalThis,ye=te.trustedTypes,tt=ye?ye.emptyScript:"",it=te.reactiveElementPolyfillSupport,K=(o,n)=>o,O={toAttribute(o,n){switch(n){case Boolean:o=o?tt:null;break;case Object:case Array:o=o==null?o:JSON.stringify(o)}return o},fromAttribute(o,n){let e=o;switch(n){case Boolean:e=o!==null;break;case Number:e=o===null?null:Number(o);break;case Object:case Array:try{e=JSON.parse(o)}catch{e=null}}return e}},ie=(o,n)=>!We(o,n),xe={attribute:!0,type:String,converter:O,reflect:!1,useDefault:!1,hasChanged:ie};Symbol.metadata??=Symbol("metadata"),te.litPropertyMetadata??=new WeakMap;var T=class extends HTMLElement{static addInitializer(n){this._$Ei(),(this.l??=[]).push(n)}static get observedAttributes(){return this.finalize(),this._$Eh&&[...this._$Eh.keys()]}static createProperty(n,e=xe){if(e.state&&(e.attribute=!1),this._$Ei(),this.prototype.hasOwnProperty(n)&&((e=Object.create(e)).wrapped=!0),this.elementProperties.set(n,e),!e.noAccessor){let t=Symbol(),i=this.getPropertyDescriptor(n,t,e);i!==void 0&&Je(this.prototype,n,i)}}static getPropertyDescriptor(n,e,t){let{get:i,set:s}=Qe(this.prototype,n)??{get(){return this[e]},set(a){this[e]=a}};return{get:i,set(a){let l=i?.call(this);s?.call(this,a),this.requestUpdate(n,l,t)},configurable:!0,enumerable:!0}}static getPropertyOptions(n){return this.elementProperties.get(n)??xe}static _$Ei(){if(this.hasOwnProperty(K("elementProperties")))return;let n=et(this);n.finalize(),n.l!==void 0&&(this.l=[...n.l]),this.elementProperties=new Map(n.elementProperties)}static finalize(){if(this.hasOwnProperty(K("finalized")))return;if(this.finalized=!0,this._$Ei(),this.hasOwnProperty(K("properties"))){let e=this.properties,t=[...Xe(e),...Ye(e)];for(let i of t)this.createProperty(i,e[i])}let n=this[Symbol.metadata];if(n!==null){let e=litPropertyMetadata.get(n);if(e!==void 0)for(let[t,i]of e)this.elementProperties.set(t,i)}this._$Eh=new Map;for(let[e,t]of this.elementProperties){let i=this._$Eu(e,t);i!==void 0&&this._$Eh.set(i,e)}this.elementStyles=this.finalizeStyles(this.styles)}static finalizeStyles(n){let e=[];if(Array.isArray(n)){let t=new Set(n.flat(1/0).reverse());for(let i of t)e.unshift(he(i))}else n!==void 0&&e.push(he(n));return e}static _$Eu(n,e){let t=e.attribute;return t===!1?void 0:typeof t=="string"?t:typeof n=="string"?n.toLowerCase():void 0}constructor(){super(),this._$Ep=void 0,this.isUpdatePending=!1,this.hasUpdated=!1,this._$Em=null,this._$Ev()}_$Ev(){this._$ES=new Promise(n=>this.enableUpdating=n),this._$AL=new Map,this._$E_(),this.requestUpdate(),this.constructor.l?.forEach(n=>n(this))}addController(n){(this._$EO??=new Set).add(n),this.renderRoot!==void 0&&this.isConnected&&n.hostConnected?.()}removeController(n){this._$EO?.delete(n)}_$E_(){let n=new Map,e=this.constructor.elementProperties;for(let t of e.keys())this.hasOwnProperty(t)&&(n.set(t,this[t]),delete this[t]);n.size>0&&(this._$Ep=n)}createRenderRoot(){let n=this.shadowRoot??this.attachShadow(this.constructor.shadowRootOptions);return we(n,this.constructor.elementStyles),n}connectedCallback(){this.renderRoot??=this.createRenderRoot(),this.enableUpdating(!0),this._$EO?.forEach(n=>n.hostConnected?.())}enableUpdating(n){}disconnectedCallback(){this._$EO?.forEach(n=>n.hostDisconnected?.())}attributeChangedCallback(n,e,t){this._$AK(n,t)}_$ET(n,e){let t=this.constructor.elementProperties.get(n),i=this.constructor._$Eu(n,t);if(i!==void 0&&t.reflect===!0){let s=(t.converter?.toAttribute!==void 0?t.converter:O).toAttribute(e,t.type);this._$Em=n,s==null?this.removeAttribute(i):this.setAttribute(i,s),this._$Em=null}}_$AK(n,e){let t=this.constructor,i=t._$Eh.get(n);if(i!==void 0&&this._$Em!==i){let s=t.getPropertyOptions(i),a=typeof s.converter=="function"?{fromAttribute:s.converter}:s.converter?.fromAttribute!==void 0?s.converter:O;this._$Em=i;let l=a.fromAttribute(e,s.type);this[i]=l??this._$Ej?.get(i)??l,this._$Em=null}}requestUpdate(n,e,t,i=!1,s){if(n!==void 0){let a=this.constructor;if(i===!1&&(s=this[n]),t??=a.getPropertyOptions(n),!((t.hasChanged??ie)(s,e)||t.useDefault&&t.reflect&&s===this._$Ej?.get(n)&&!this.hasAttribute(a._$Eu(n,t))))return;this.C(n,e,t)}this.isUpdatePending===!1&&(this._$ES=this._$EP())}C(n,e,{useDefault:t,reflect:i,wrapped:s},a){t&&!(this._$Ej??=new Map).has(n)&&(this._$Ej.set(n,a??e??this[n]),s!==!0||a!==void 0)||(this._$AL.has(n)||(this.hasUpdated||t||(e=void 0),this._$AL.set(n,e)),i===!0&&this._$Em!==n&&(this._$Eq??=new Set).add(n))}async _$EP(){this.isUpdatePending=!0;try{await this._$ES}catch(e){Promise.reject(e)}let n=this.scheduleUpdate();return n!=null&&await n,!this.isUpdatePending}scheduleUpdate(){return this.performUpdate()}performUpdate(){if(!this.isUpdatePending)return;if(!this.hasUpdated){if(this.renderRoot??=this.createRenderRoot(),this._$Ep){for(let[i,s]of this._$Ep)this[i]=s;this._$Ep=void 0}let t=this.constructor.elementProperties;if(t.size>0)for(let[i,s]of t){let{wrapped:a}=s,l=this[i];a!==!0||this._$AL.has(i)||l===void 0||this.C(i,void 0,s,l)}}let n=!1,e=this._$AL;try{n=this.shouldUpdate(e),n?(this.willUpdate(e),this._$EO?.forEach(t=>t.hostUpdate?.()),this.update(e)):this._$EM()}catch(t){throw n=!1,this._$EM(),t}n&&this._$AE(e)}willUpdate(n){}_$AE(n){this._$EO?.forEach(e=>e.hostUpdated?.()),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(n)),this.updated(n)}_$EM(){this._$AL=new Map,this.isUpdatePending=!1}get updateComplete(){return this.getUpdateComplete()}getUpdateComplete(){return this._$ES}shouldUpdate(n){return!0}update(n){this._$Eq&&=this._$Eq.forEach(e=>this._$ET(e,this[e])),this._$EM()}updated(n){}firstUpdated(n){}};T.elementStyles=[],T.shadowRootOptions={mode:"open"},T[K("elementProperties")]=new Map,T[K("finalized")]=new Map,it?.({ReactiveElement:T}),(te.reactiveElementVersions??=[]).push("2.1.2");var pe=globalThis,Ae=o=>o,ne=pe.trustedTypes,ze=ne?ne.createPolicy("lit-html",{createHTML:o=>o}):void 0,Ie="$lit$",P=`lit$${Math.random().toFixed(9).slice(2)}$`,Pe="?"+P,nt=`<${Pe}>`,j=document,V=()=>j.createComment(""),G=o=>o===null||typeof o!="object"&&typeof o!="function",be=Array.isArray,st=o=>be(o)||typeof o?.[Symbol.iterator]=="function",ce=`[ 	
\f\r]`,H=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,Ee=/-->/g,Se=/>/g,R=RegExp(`>|${ce}(?:([^\\s"'>=/]+)(${ce}*=${ce}*(?:[^ 	
\f\r"'\`<>=]|("|')|))|$)`,"g"),Te=/'/g,Fe=/"/g,Re=/^(?:script|style|textarea|title)$/i,me=o=>(n,...e)=>({_$litType$:o,strings:n,values:e}),r=me(1),yt=me(2),xt=me(3),L=Symbol.for("lit-noChange"),u=Symbol.for("lit-nothing"),De=new WeakMap,N=j.createTreeWalker(j,129);function Ne(o,n){if(!be(o)||!o.hasOwnProperty("raw"))throw Error("invalid template strings array");return ze!==void 0?ze.createHTML(n):n}var at=(o,n)=>{let e=o.length-1,t=[],i,s=n===2?"<svg>":n===3?"<math>":"",a=H;for(let l=0;l<e;l++){let h=o[l],g,_,c=-1,d=0;for(;d<h.length&&(a.lastIndex=d,_=a.exec(h),_!==null);)d=a.lastIndex,a===H?_[1]==="!--"?a=Ee:_[1]!==void 0?a=Se:_[2]!==void 0?(Re.test(_[2])&&(i=RegExp("</"+_[2],"g")),a=R):_[3]!==void 0&&(a=R):a===R?_[0]===">"?(a=i??H,c=-1):_[1]===void 0?c=-2:(c=a.lastIndex-_[2].length,g=_[1],a=_[3]===void 0?R:_[3]==='"'?Fe:Te):a===Fe||a===Te?a=R:a===Ee||a===Se?a=H:(a=R,i=void 0);let $=a===R&&o[l+1].startsWith("/>")?" ":"";s+=a===H?h+nt:c>=0?(t.push(g),h.slice(0,c)+Ie+h.slice(c)+P+$):h+P+(c===-2?l:$)}return[Ne(o,s+(o[e]||"<?>")+(n===2?"</svg>":n===3?"</math>":"")),t]},Z=class o{constructor({strings:n,_$litType$:e},t){let i;this.parts=[];let s=0,a=0,l=n.length-1,h=this.parts,[g,_]=at(n,e);if(this.el=o.createElement(g,t),N.currentNode=this.el.content,e===2||e===3){let c=this.el.content.firstChild;c.replaceWith(...c.childNodes)}for(;(i=N.nextNode())!==null&&h.length<l;){if(i.nodeType===1){if(i.hasAttributes())for(let c of i.getAttributeNames())if(c.endsWith(Ie)){let d=_[a++],$=i.getAttribute(c).split(P),v=/([.?@])?(.*)/.exec(d);h.push({type:1,index:s,name:v[2],strings:$,ctor:v[1]==="."?de:v[1]==="?"?ge:v[1]==="@"?_e:M}),i.removeAttribute(c)}else c.startsWith(P)&&(h.push({type:6,index:s}),i.removeAttribute(c));if(Re.test(i.tagName)){let c=i.textContent.split(P),d=c.length-1;if(d>0){i.textContent=ne?ne.emptyScript:"";for(let $=0;$<d;$++)i.append(c[$],V()),N.nextNode(),h.push({type:2,index:++s});i.append(c[d],V())}}}else if(i.nodeType===8)if(i.data===Pe)h.push({type:2,index:s});else{let c=-1;for(;(c=i.data.indexOf(P,c+1))!==-1;)h.push({type:7,index:s}),c+=P.length-1}s++}}static createElement(n,e){let t=j.createElement("template");return t.innerHTML=n,t}};function B(o,n,e=o,t){if(n===L)return n;let i=t!==void 0?e._$Co?.[t]:e._$Cl,s=G(n)?void 0:n._$litDirective$;return i?.constructor!==s&&(i?._$AO?.(!1),s===void 0?i=void 0:(i=new s(o),i._$AT(o,e,t)),t!==void 0?(e._$Co??=[])[t]=i:e._$Cl=i),i!==void 0&&(n=B(o,i._$AS(o,n.values),i,t)),n}var ue=class{constructor(n,e){this._$AV=[],this._$AN=void 0,this._$AD=n,this._$AM=e}get parentNode(){return this._$AM.parentNode}get _$AU(){return this._$AM._$AU}u(n){let{el:{content:e},parts:t}=this._$AD,i=(n?.creationScope??j).importNode(e,!0);N.currentNode=i;let s=N.nextNode(),a=0,l=0,h=t[0];for(;h!==void 0;){if(a===h.index){let g;h.type===2?g=new W(s,s.nextSibling,this,n):h.type===1?g=new h.ctor(s,h.name,h.strings,this,n):h.type===6&&(g=new fe(s,this,n)),this._$AV.push(g),h=t[++l]}a!==h?.index&&(s=N.nextNode(),a++)}return N.currentNode=j,i}p(n){let e=0;for(let t of this._$AV)t!==void 0&&(t.strings!==void 0?(t._$AI(n,t,e),e+=t.strings.length-2):t._$AI(n[e])),e++}},W=class o{get _$AU(){return this._$AM?._$AU??this._$Cv}constructor(n,e,t,i){this.type=2,this._$AH=u,this._$AN=void 0,this._$AA=n,this._$AB=e,this._$AM=t,this.options=i,this._$Cv=i?.isConnected??!0}get parentNode(){let n=this._$AA.parentNode,e=this._$AM;return e!==void 0&&n?.nodeType===11&&(n=e.parentNode),n}get startNode(){return this._$AA}get endNode(){return this._$AB}_$AI(n,e=this){n=B(this,n,e),G(n)?n===u||n==null||n===""?(this._$AH!==u&&this._$AR(),this._$AH=u):n!==this._$AH&&n!==L&&this._(n):n._$litType$!==void 0?this.$(n):n.nodeType!==void 0?this.T(n):st(n)?this.k(n):this._(n)}O(n){return this._$AA.parentNode.insertBefore(n,this._$AB)}T(n){this._$AH!==n&&(this._$AR(),this._$AH=this.O(n))}_(n){this._$AH!==u&&G(this._$AH)?this._$AA.nextSibling.data=n:this.T(j.createTextNode(n)),this._$AH=n}$(n){let{values:e,_$litType$:t}=n,i=typeof t=="number"?this._$AC(n):(t.el===void 0&&(t.el=Z.createElement(Ne(t.h,t.h[0]),this.options)),t);if(this._$AH?._$AD===i)this._$AH.p(e);else{let s=new ue(i,this),a=s.u(this.options);s.p(e),this.T(a),this._$AH=s}}_$AC(n){let e=De.get(n.strings);return e===void 0&&De.set(n.strings,e=new Z(n)),e}k(n){be(this._$AH)||(this._$AH=[],this._$AR());let e=this._$AH,t,i=0;for(let s of n)i===e.length?e.push(t=new o(this.O(V()),this.O(V()),this,this.options)):t=e[i],t._$AI(s),i++;i<e.length&&(this._$AR(t&&t._$AB.nextSibling,i),e.length=i)}_$AR(n=this._$AA.nextSibling,e){for(this._$AP?.(!1,!0,e);n!==this._$AB;){let t=Ae(n).nextSibling;Ae(n).remove(),n=t}}setConnected(n){this._$AM===void 0&&(this._$Cv=n,this._$AP?.(n))}},M=class{get tagName(){return this.element.tagName}get _$AU(){return this._$AM._$AU}constructor(n,e,t,i,s){this.type=1,this._$AH=u,this._$AN=void 0,this.element=n,this.name=e,this._$AM=i,this.options=s,t.length>2||t[0]!==""||t[1]!==""?(this._$AH=Array(t.length-1).fill(new String),this.strings=t):this._$AH=u}_$AI(n,e=this,t,i){let s=this.strings,a=!1;if(s===void 0)n=B(this,n,e,0),a=!G(n)||n!==this._$AH&&n!==L,a&&(this._$AH=n);else{let l=n,h,g;for(n=s[0],h=0;h<s.length-1;h++)g=B(this,l[t+h],e,h),g===L&&(g=this._$AH[h]),a||=!G(g)||g!==this._$AH[h],g===u?n=u:n!==u&&(n+=(g??"")+s[h+1]),this._$AH[h]=g}a&&!i&&this.j(n)}j(n){n===u?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,n??"")}},de=class extends M{constructor(){super(...arguments),this.type=3}j(n){this.element[this.name]=n===u?void 0:n}},ge=class extends M{constructor(){super(...arguments),this.type=4}j(n){this.element.toggleAttribute(this.name,!!n&&n!==u)}},_e=class extends M{constructor(n,e,t,i,s){super(n,e,t,i,s),this.type=5}_$AI(n,e=this){if((n=B(this,n,e,0)??u)===L)return;let t=this._$AH,i=n===u&&t!==u||n.capture!==t.capture||n.once!==t.once||n.passive!==t.passive,s=n!==u&&(t===u||i);i&&this.element.removeEventListener(this.name,this,t),s&&this.element.addEventListener(this.name,this,n),this._$AH=n}handleEvent(n){typeof this._$AH=="function"?this._$AH.call(this.options?.host??this.element,n):this._$AH.handleEvent(n)}},fe=class{constructor(n,e,t){this.element=n,this.type=6,this._$AN=void 0,this._$AM=e,this.options=t}get _$AU(){return this._$AM._$AU}_$AI(n){B(this,n)}};var rt=pe.litHtmlPolyfillSupport;rt?.(Z,W),(pe.litHtmlVersions??=[]).push("3.3.3");var je=(o,n,e)=>{let t=e?.renderBefore??n,i=t._$litPart$;if(i===void 0){let s=e?.renderBefore??null;t._$litPart$=i=new W(n.insertBefore(V(),s),s,void 0,e??{})}return i._$AI(o),i};var ve=globalThis,E=class extends T{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0}createRenderRoot(){let n=super.createRenderRoot();return this.renderOptions.renderBefore??=n.firstChild,n}update(n){let e=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(n),this._$Do=je(e,this.renderRoot,this.renderOptions)}connectedCallback(){super.connectedCallback(),this._$Do?.setConnected(!0)}disconnectedCallback(){super.disconnectedCallback(),this._$Do?.setConnected(!1)}render(){return L}};E._$litElement$=!0,E.finalized=!0,ve.litElementHydrateSupport?.({LitElement:E});var lt=ve.litElementPolyfillSupport;lt?.({LitElement:E});(ve.litElementVersions??=[]).push("4.2.2");var ot={attribute:!0,type:String,converter:O,reflect:!1,hasChanged:ie},ht=(o=ot,n,e)=>{let{kind:t,metadata:i}=e,s=globalThis.litPropertyMetadata.get(i);if(s===void 0&&globalThis.litPropertyMetadata.set(i,s=new Map),t==="setter"&&((o=Object.create(o)).wrapped=!0),s.set(e.name,o),t==="accessor"){let{name:a}=e;return{set(l){let h=n.get.call(this);n.set.call(this,l),this.requestUpdate(a,h,o,!0,l)},init(l){return l!==void 0&&this.C(a,void 0,o,l),l}}}if(t==="setter"){let{name:a}=e;return function(l){let h=this[a];n.call(this,l),this.requestUpdate(a,h,o,!0,l)}}throw Error("Unsupported decorator location: "+t)};function F(o){return(n,e)=>typeof e=="object"?ht(o,n,e):((t,i,s)=>{let a=i.hasOwnProperty(s);return i.constructor.createProperty(s,t),a?Object.getOwnPropertyDescriptor(i,s):void 0})(o,n,e)}function b(o){return F({...o,state:!0,attribute:!1})}var C=class{constructor(n){this.hass=n}call(n,e={}){return this.hass.callWS({type:`learnbuddy/${n}`,...e})}uebersicht(){return this.call("overview")}dashboard(n){return this.call("dashboard",{kind_id:n})}frageStellen(n,e){return this.call("ask",{kind_id:n,fach_id:e})}async frageAbbrechen(n){return(await this.call("cancel_question",{kind_id:n})).abgebrochen}setzeAktiv(n,e){return this.call("set_active",{kind_id:n,aktiv:e})}async kalenderPruefen(n){return(await this.call("calendar/refresh",{kind_id:n})).gelesen}kalenderIgnorieren(n,e){return this.call("calendar/ignore",{kind_id:n,uid:e})}kalenderWiederherstellen(n){return this.call("calendar/restore",{kind_id:n})}async fachAnlegen(n,e,t,i){return(await this.call("subjects/create",{kind_id:n,typ:e,name:t||null,sprache:i})).fach_id}absenderZuordnen(n,e){return this.call("sender/assign",{kind_id:n,kennung:e})}absenderVerwerfen(n){return this.call("sender/dismiss",{kennung:n})}async aufgaben(n){return(await this.call("tasks/list",{fach_id:n})).aufgaben}aufgabeAnlegen(n,e){return this.call("tasks/create",{fach_id:n,aufgabe:e})}aufgabeAendern(n,e,t){return this.call("tasks/update",{fach_id:n,aufgabe_id:e,aenderungen:t})}aufgabenLoeschen(n,e,t){return this.call("tasks/delete",{fach_id:n,aufgabe_ids:e,bestaetigt:t})}async lektionHinzufuegen(n,e){return(await this.call("lessons/add",{fach_id:n,name:e})).lektionen}async lektionLoeschen(n,e){return(await this.call("lessons/delete",{fach_id:n,name:e})).lektionen}importVorschau(n,e,t){return this.call("tasks/import_text",{fach_id:n,inhalt:e,trennzeichen:t,vorschau:!0})}importText(n,e,t,i,s){return this.call("tasks/import_text",{fach_id:n,inhalt:e,lektion:t,trennzeichen:i,geprueft:s})}generieren(n,e){return this.call("tasks/generate",{fach_id:n,...e})}fragenAusSeiten(n,e){return this.call("tasks/generate_from_pages",{fach_id:n,...e})}fotoAuslesen(n,e){return this.call("tasks/photo_extract",{fach_id:n,seiten:e})}fotoUebernehmen(n,e,t){return this.call("tasks/photo_accept",{fach_id:n,zeilen:e,lektion:t})}nachrechnen(n,e){return this.call("tasks/verify",{fach_id:n,aufgabe_ids:e})}rechenwegeErzeugen(n,e){return this.call("tasks/generate_steps",{fach_id:n,aufgabe_ids:e})}async bildHochladen(n,e=!1){let t=new FormData;t.append("file",n);let i=`/api/learnbuddy/bilder${e?"?zweck=seite":""}`,s=await this.hass.fetchWithAuth(i,{method:"POST",body:t}),a=await s.json().catch(()=>({}));if(!s.ok||!a.bild)throw{code:String(s.status),message:a.message??"bild_ungueltig"};return a.bild}async bildAdresse(n){return(await this.hass.callWS({type:"auth/sign_path",path:`/api/learnbuddy/bilder/${n}`,expires:3600})).path}async vorschlagUebernehmen(n,e){return(await this.call("tasks/accept_suggestion",{fach_id:n,aufgabe_ids:e})).uebernommen}async alsGeprueftMarkieren(n,e){return(await this.call("tasks/mark_verified",{fach_id:n,aufgabe_ids:e})).markiert}export(n,e){return this.call("tasks/export",{fach_id:n,mit_statistik:e})}importJson(n,e,t,i){return this.call("tasks/import_json",{fach_id:n,daten:e,mit_statistik:t,lektion:i})}async arbeitSpeichern(n,e){return(await this.call("exams/save",{arbeit_id:n,arbeit:e})).arbeit_id}simulieren(n,e,t){return this.call("exams/simulate",{arbeit_id:n,anzahl:e,weg:t})}async simulationAbbrechen(n){return(await this.call("exams/simulate_stop",{kind_id:n})).abgebrochen}arbeitLoeschen(n){return this.call("exams/delete",{arbeit_id:n})}};var Le={titel:"LearnBuddy",kind:"Kind",fach:"Fach",keine_kinder:"Es ist noch kein Kind angelegt. Lege unter Einstellungen \u2192 Ger\xE4te & Dienste \u2192 LearnBuddy zuerst ein Kind und ein Fach an.",keine_faecher:"F\xFCr dieses Kind gibt es noch kein Fach.",tab_uebersicht:"\xDCbersicht",status_aktiv:"Abfragen aktiv",status_pausiert:"Abfragen pausiert",status_pausiert_bis:"Pausiert bis {zeit}",pausieren:"Pausieren",fortsetzen:"Fortsetzen",offene_frage:"Offene Frage",offene_frage_text:"{fach}, gestellt um {von}, l\xE4uft bis {bis}",keine_offene_frage:"Keine offene Frage",naechste_abfrage:"N\xE4chste Abfrage",keine_geplant:"Keine geplant",nach_offener_frage:"Nach der offenen Frage",letzte_frage:"Letzte Frage",noch_nie:"Noch nie",jetzt_fragen:"Jetzt eine Aufgabe stellen",jetzt_fragen_kurz:"Jetzt abfragen",fach_waehlen:"Aus welchem Fach?",egal_welches:"Egal welches Fach",frage_gesendet:"Die Frage wurde gesendet.",kz_gefragt:"Gestellte Fragen",kz_richtig:"Richtig",kz_falsch:"Falsch",kz_unbeantwortet:"Unbeantwortet",ki_keine:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt.",ki_nicht_verfuegbar:"Die gew\xE4hlte KI-Entit\xE4t ist gerade nicht verf\xFCgbar.",ki_ohne_bilder:"Die gew\xE4hlte KI-Entit\xE4t kann keine Bilder lesen.",ki_hinweis_keine:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt. Aufgaben erzeugen, Rechenwege schreiben und der Import aus Fotos sind deshalb ausgeschaltet; Antworten werden nur lokal bewertet. Einrichten unter Einstellungen \u2192 Ger\xE4te & Dienste \u2192 LearnBuddy \u2192 Zahnrad.",ki_hinweis_ohne_bilder:"Die gew\xE4hlte KI-Entit\xE4t kann keine Bilder lesen. Funktionen mit Fotos sind deshalb ausgeschaltet.",ki_hinweis_nicht_verfuegbar:"Die gew\xE4hlte KI-Entit\xE4t ist gerade nicht verf\xFCgbar. Die KI-Funktionen sind ausgeschaltet und Antworten werden nur lokal bewertet. Pr\xFCfe die KI-Integration in Home Assistant.",ki_hinweis_sach_zusatz:" Kurzantworten werden so lange nicht gestellt, nur Auswahlfragen.",err_ki_nicht_verfuegbar:"Die gew\xE4hlte KI-Entit\xE4t ist gerade nicht verf\xFCgbar.",err_ki_nicht_erreichbar:"Die KI war nicht erreichbar oder hat den Auftrag abgelehnt (Verbindung, Konto, Guthaben). Bitte sp\xE4ter erneut versuchen.",neue_version:"LearnBuddy wurde aktualisiert. Diese Seite zeigt noch die alte Version; lade sie neu, damit alle Funktionen sichtbar sind.",neu_laden:"Seite neu laden",absender_unbekannt:"Eine Nachricht von einem unbekannten Absender ist eingegangen: {kennung} ({quelle}). Sie konnte keinem Kind zugeordnet werden.",absender_uebernehmen:"Als Absenderkennung f\xFCr {name} \xFCbernehmen",absender_verwerfen:"Verwerfen",absender_uebernommen:"Absenderkennung \xFCbernommen. Die n\xE4chste Antwort wird zugeordnet.",quelle_telegram:"Telegram",quelle_whatsapp:"WhatsApp",quelle_event:"eigenes Ereignis",err_absender_leer:"Die Absenderkennung ist leer.",err_absender_vergeben:"Diese Absenderkennung geh\xF6rt schon zu einem anderen Kind.",absender_fehlt:"Bei diesem Kind fehlt die Absenderkennung (Chat-ID oder Telefonnummer). Fragen gehen raus, aber Antworten k\xF6nnen nicht zugeordnet werden. Eintragen unter Einstellungen \u2192 Ger\xE4te & Dienste \u2192 LearnBuddy \u2192 Kind bearbeiten.",sim_plan:"Simulation einplanen (optional)",sim_plan_aktiv:"Zu einem festen Zeitpunkt automatisch eine Simulation schicken",sim_plan_hilfe:"Zum gew\xE4hlten Zeitpunkt bekommt das Kind automatisch eine Simulation dieser Arbeit per Messenger: das Aufgabenblatt als Bild, dann die Aufgaben nacheinander, am Ende die Auswertung. Ist das Kind dann pausiert oder l\xE4uft schon eine Simulation, entf\xE4llt sie.",sim_plan_um:"Datum und Uhrzeit",sim_plan_offen:"Simulation geplant f\xFCr {zeit} ({n} Aufgaben)",sim_plan_erledigt:"Geplante Simulation vom {zeit} ist erledigt",err_simulation_um_vergangen:"Der Zeitpunkt der Simulation liegt in der Vergangenheit.",err_simulation_um_ungueltig:"Bitte Datum und Uhrzeit der Simulation pr\xFCfen.",sim_knopf_arbeit:"Klassenarbeit simulieren",sim_knopf_hue:"H\xDC simulieren",sim_hilfe:"Aus den freigegebenen Aufgaben dieser Arbeit wird zuf\xE4llig ein Aufgabenblatt zusammengestellt. Die Lernstatistik bleibt davon unber\xFChrt.",sim_weg_ausdruck:"Per Ausdruck",sim_weg_ausdruck_hilfe:"Das Aufgabenblatt entsteht als Bild zum Herunterladen und Drucken. Es wird nichts verschickt.",sim_weg_messenger:"Per Messenger",sim_weg_messenger_hilfe:"{name} bekommt das Blatt als Bild und danach die Aufgaben nacheinander. R\xFCckmeldung gibt es erst am Ende: Punkte, Prozent und die L\xF6sungen zu den Fehlern.",sim_anzahl:"Anzahl der Aufgaben",sim_verfuegbar:"Auf diesem Weg verf\xFCgbar: {n}",sim_keine_aufgaben:"F\xFCr diese Arbeit gibt es keine freigegebenen Aufgaben.",sim_start_ausdruck:"Blatt erzeugen",sim_start_messenger:"Simulation starten",sim_gestartet:"Die Simulation mit {n} Aufgaben l\xE4uft. Die Auswertung geht am Ende ans Kind.",sim_blatt_hilfe:"Das Blatt mit {n} Aufgaben ist fertig. Die Bilder werden nach 24 Stunden gel\xF6scht; lade sie herunter, wenn du sie behalten willst.",sim_herunterladen:"Seite {n} herunterladen",sim_drucken:"Drucken",sim_druck_blockiert:"Der Browser hat das Druckfenster blockiert. Lade die Seiten herunter und drucke sie von dort.",sim_laeuft:"Simulation",sim_laeuft_text:"l\xE4uft: Aufgabe {nr} von {n}",sim_abbrechen:"Simulation abbrechen",frage_abbrechen:"Frage abbrechen",frage_abbrechen_frage:"Die offene Frage zur\xFCckziehen? Sie wird nicht gez\xE4hlt, und das Kind bekommt eine kurze Nachricht.",sim_abbrechen_frage:"Die laufende Simulation ohne Auswertung beenden?",err_simulation_laeuft:"F\xFCr dieses Kind l\xE4uft gerade eine Simulation.",err_weg_ungueltig:"Unbekannter Weg f\xFCr die Simulation.",foto_import:"Aus Foto importieren",foto_titel:"Aufgaben aus Fotos auslesen",foto_hilfe:"Fotografiere die Vokabelseiten m\xF6glichst gerade und gut lesbar. Die KI liest Wort, \xDCbersetzung, Seitenzahl und den Verweis auf die Unit-Seite aus. Beispiels\xE4tze und Lautschrift l\xE4sst sie weg. Danach pr\xFCfst du die Vorschau. Die Fotos gehen an den KI-Dienst und werden anschlie\xDFend gel\xF6scht.",foto_hilfe_mathe:"Fotografiere Buchseite oder Arbeitsblatt m\xF6glichst gerade und gut lesbar. Die KI liest die Aufgaben aus und l\xF6st sie; die L\xF6sungen werden nachgerechnet. Danach pr\xFCfst du die Vorschau. Die Fotos gehen an den KI-Dienst und werden anschlie\xDFend gel\xF6scht.",foto_auslesen:"Auslesen",foto_leer:"Auf den Fotos wurde nichts Verwertbares gefunden.",foto_vorschau_titel:"Vorschau pr\xFCfen",foto_vorschau_hilfe:"Vergleiche die Zeilen mit dem Buch, korrigiere sie bei Bedarf und entferne das H\xE4kchen bei allem, was nicht \xFCbernommen werden soll. Gespeichert wird erst mit \u201E\xDCbernehmen\u201C.",foto_vorhanden:"schon vorhanden",foto_braucht_bild:"braucht eine Abbildung \u2013 als \u201EAufgabe mit Bild\u201C anlegen",foto_unbestaetigt:"L\xF6sung nicht best\xE4tigt",foto_uebernehmen:"{n} \xFCbernehmen",foto_fertig:"{n} \xFCbernommen, {doppelt} schon vorhanden, {fehler} fehlerhaft.",foto_fehler:"{n} Zeilen sind fehlerhaft (leere oder zu lange Felder). Bitte korrigieren.",err_foto_sachfach:"F\xFCr Sachf\xE4cher gibt es \u201EFragen aus Buchseite\u201C.",kz_teilweise:"Teilweise richtig",neue_frage:"Neue Frage",spalte_frage:"Frage",spalte_musterantwort:"Musterantwort",richtige_antwort:"Richtige Antwort",form:"Frageform",form_kurz:"Kurzantwort",form_auswahl:"Auswahl",form_gemischt:"Gemischt",kernpunkte:"Kernpunkte (einer je Zeile, optional): was eine vollst\xE4ndige Antwort enth\xE4lt",falsche_optionen:"Falsche Antworten (eine je Zeile, 2 bis 3)",belegstelle:"Belegstelle",quellseite_anzeigen:"Buchseite anzeigen",sach_ohne_ki:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt. Deshalb werden nur Auswahlfragen gestellt; Kurzantworten kann nur die KI bewerten.",seiten:"Fragen aus Buchseite",seiten_titel:"Fragen aus Buchseiten erzeugen",seiten_hilfe:"Fotografiere die Seiten m\xF6glichst gerade und gut lesbar. Die KI liest sie und schl\xE4gt Fragen mit Musterantwort vor. Die Fragen warten danach auf deine Freigabe. Die Fotos gehen an den KI-Dienst.",seiten_waehlen:"Fotos der Seiten (bis zu {n})",seiten_zu_viele:"Es werden nur die ersten {n} Fotos verwendet.",seiten_anzahl:"Anzahl Fragen",seiten_schwerpunkt:"Schwerpunkt (optional)",seiten_schwerpunkt_hilfe:"z. B. nur der Abschnitt \xFCber die Zellatmung",seiten_start:"Fragen erzeugen",seiten_laeuft:"Die KI liest die Seiten. Das kann eine Minute dauern \u2026",seiten_fertig:"{erzeugt} Fragen erzeugt, {verworfen} unbrauchbar, {doppelt} doppelt. Bitte pr\xFCfen und freigeben.",err_sach_frage_ungueltig:"Bitte eine Frage eingeben (h\xF6chstens 500 Zeichen).",err_sach_antwort_ungueltig:"Bitte eine Antwort eingeben (h\xF6chstens 500 Zeichen).",err_form_ungueltig:"Unbekannte Frageform.",err_kernpunkte_ungueltig:"H\xF6chstens 6 Kernpunkte mit je 200 Zeichen.",err_falsche_optionen_ungueltig:"Eine Auswahlfrage braucht 2 bis 3 falsche Antworten, die sich untereinander und von der richtigen unterscheiden.",err_stelle_ungueltig:"Die Belegstelle darf h\xF6chstens 300 Zeichen lang sein.",err_import_sachfach:"In Sachf\xE4cher lassen sich keine Listen importieren.",err_seiten_nur_sachfach:"Fragen aus Buchseiten gibt es nur f\xFCr Sachf\xE4cher.",err_seiten_ungueltig:"Bitte 1 bis 4 Fotos w\xE4hlen.",err_ki_ohne_bilder:"Die gew\xE4hlte KI-Entit\xE4t kann keine Bilder lesen.",kz_trefferquote:"Trefferquote",kz_aufgaben:"Aufgaben",anstehend:"Anstehende Arbeiten und H\xDCs",vorschlaege:"Vorschl\xE4ge aus dem Kalender",vorschlag_eintragen:"Eintragen",vorschlag_ignorieren:"Ignorieren",vorschlag_gleicher_tag:"Am selben Tag gibt es schon: {arbeiten}",keine_vorschlaege:"Keine neuen Termine im Kalender.",kalender_pruefen:"Jetzt pr\xFCfen",kalender_geprueft:"Zuletzt gepr\xFCft: {zeit}",kalender_nie:"Der Kalender wurde noch nicht gelesen.",kalender_fehler:"Der Kalender konnte zuletzt nicht gelesen werden. Angezeigt wird der Stand davor.",kalender_ignorierte:"{n} ignorierte wieder anzeigen",arbeit_fach:"Fach",fach_neu:"Neues Fach",fach_neu_titel:"Neues Fach anlegen",fach_neu_art:"Art des Fachs",fach_neu_sprache:"Sprache",fach_neu_name:"Name",fach_neu_name_optional:"Name (leer: wie die Sprache bzw. \u201EMathe\u201C)",fach_neu_anlegen:"Fach anlegen",fach_neu_fehlt:"F\xFCr dieses Kind gibt es noch kein Fach. Lege zuerst eines an.",fachart_fremdsprache:"Fremdsprache",err_kalender_aus:"F\xFCr dieses Kind ist kein Pr\xFCfungskalender eingeschaltet.",err_termin_unbekannt:"Der Termin steht nicht mehr im Kalender.",err_sprache_ungueltig:"Bitte eine Fremdsprache w\xE4hlen, die nicht die Muttersprache ist.",err_fachart_ungueltig:"Bitte die Art des Fachs w\xE4hlen.",err_fach_vorhanden:"Ein Fach mit diesem Namen gibt es schon.",err_name_leer:"Bitte einen Namen eingeben.",keine_anstehend:"Keine Arbeit oder H\xDC geplant.",heute:"heute",morgen:"morgen",in_tagen:"in {n} Tagen",heute_abfragen:"heute {n} Abfragen",sicher:"{n} % sicher",sicher_hinweis:"Anteil der Karten in Box 3 bis 5",faecher_titel:"F\xE4cher",fach_aufgaben:"{n} Aufgaben in {l} Lektionen",ungeprueft:"{n} ungepr\xFCft",aufgaben_oeffnen:"Aufgaben",lernstand:"Lernstand",lernstand_hinweis:"Karten je Leitner-Box: Box 1 ist neu oder zuletzt falsch, Box 5 sitzt sicher.",box:"Box {n}",karten:"{n} Karten",keine_karten:"Noch keine Aufgaben vorhanden.",schwierig:"Schwierigste Vokabeln",keine_schwierig:"Noch keine falschen Antworten.",fehler_mal:"{n} \xD7 falsch",arbeiten_oeffnen:"Arbeiten verwalten",tab_aufgaben:"Aufgaben",tab_arbeiten:"Arbeiten",laden:"Lade \u2026",neue_aufgabe:"Neue Aufgabe",importieren:"Importieren",lektion_hinzufuegen:"Lektion/Thema hinzuf\xFCgen",lektion_titel:"Lektionen und Themen",lektion_hilfe:"Lektionen und Themen werden hier angelegt und stehen danach beim Anlegen, Importieren und in Arbeiten zur Auswahl.",lektion_name:"Name der Lektion oder des Themas",lektion_keine:"Noch keine Lektion angelegt.",lektion_anzahl:"{n} Aufgaben",lektion_loeschen_hinweis:"Nur leere Lektionen lassen sich l\xF6schen",lektion_angelegt:"\u201E{name}\u201C angelegt.",keine_lektion:"\u2013 keine \u2013",export_json:"JSON exportieren",import_json:"JSON importieren",ausgewaehlt:"{n} ausgew\xE4hlt",loeschen:"L\xF6schen",arbeit_aus_auswahl:"Arbeit aus Auswahl",filter_suche:"Suche",filter_lektion:"Lektion/Thema",filter_quelle:"Quelle",filter_geprueft:"Gepr\xFCft",filter_fehlerquote:"Fehlerquote ab %",filter_von:"Erstellt ab",filter_bis:"Erstellt bis",filter_seite_von:"Buchseite von",filter_seite_bis:"Buchseite bis",filter_zuruecksetzen:"Filter zur\xFCcksetzen",alle:"Alle",ohne_lektion:"Ohne Lektion",ja:"Ja",nein:"Nein",quelle_manuell:"Manuell",quelle_upload:"Upload",quelle_generiert:"Generiert",spalte_alternativen:"Alternativen",spalte_hinweis:"Hinweis",aufgabenart_titel:"Was f\xFCr eine Aufgabe?",aufgabenart_rechnen:"Rechenaufgabe",aufgabenart_rechnen_hilfe:"Nur Text, zum Beispiel 3/4 + 1/8 oder eine Textaufgabe.",aufgabenart_bild:"Aufgabe mit Bild",aufgabenart_bild_hilfe:"Ein Diagramm, eine Kurve oder eine Zeichnung ist die Grundlage. Das Bild wird mit der Aufgabe verschickt.",bildaufgabe_titel:"Aufgabe mit Bild",bild:"Bild",bild_waehlen:"Bild ausw\xE4hlen",bild_hilfe:"PNG, JPEG, WebP oder GIF, h\xF6chstens 10 MB. Das Bild wird verkleinert gespeichert, Zusatzdaten wie der Aufnahmeort werden entfernt.",bild_vorschau:"Vorschau des Bildes",bild_anzeigen:"Bild anzeigen",einleitung:"Einleitung (optional)",einleitung_hilfe:"Steht vor jeder Teilaufgabe, z. B. \u201EIn anderen L\xE4ndern sind die Schulferien \u2026\u201C",teilaufgaben:"Teilaufgaben",teilaufgaben_hilfe:"Jede Zeile wird eine eigene Aufgabe mit demselben Bild und wird einzeln abgefragt.",teilaufgabe:"Teilaufgabe {n}",teilaufgabe_hinzufuegen:"Teilaufgabe hinzuf\xFCgen",teilaufgabe_entfernen:"Teilaufgabe entfernen",bildaufgaben_gespeichert:"Aufgaben mit Bild angelegt: {n}",bild_fehlt:"Bitte ein Bild ausw\xE4hlen.",teil_fehlt:"Bitte mindestens eine Teilaufgabe mit L\xF6sung eintragen.",keine_bilder:"{name} kann im Moment keine Bilder empfangen. Aufgaben mit Bild werden deshalb nicht gestellt. Bilder gehen automatisch \xFCber Telegram; f\xFCr andere Messenger tr\xE4gst du beim Kind eine \u201EAktion f\xFCr Bilder\u201C ein.",export_ohne_bild:"Exportiert. Aufgaben mit Bild sind nicht enthalten: {n}",spalte_aufgabe:"Aufgabe",spalte_loesung:"L\xF6sung",spalte_schwierigkeit:"Stufe",schwierigkeit:"Schwierigkeit",schwierigkeit_hinweis:"1 = leicht, 5 = schwer",schwierigkeit_beliebig:"beliebig",rechenweg:"Rechenweg (ein Schritt je Zeile, optional)",rechenweg_vorhanden:"Rechenweg hinterlegt",verifikation_rechnerisch:"nachgerechnet",verifikation_ki:"von der KI gegengepr\xFCft",verifikation_manuell:"selbst nachgerechnet",selbst_nachgerechnet:"Selbst nachgerechnet",selbst_nachgerechnet_hinweis:"Markiert die L\xF6sungen der Auswahl als von dir gepr\xFCft. Ein abweichender Vorschlag wird verworfen.",selbst_nachgerechnet_fertig:"Als selbst nachgerechnet markiert: {n}",verifikation_abweichung:"L\xF6sung weicht ab",nachrechnen:"Auswahl nachrechnen",nachrechnen_laeuft:"Die Aufgaben werden nachgerechnet \u2026",nachgerechnet:"{bestaetigt} best\xE4tigt, {abweichend} abweichend, {offen} nicht pr\xFCfbar.",nachrechnen_titel:"Ergebnis des Nachrechnens",nachrechnen_zusammenfassung:"{bestaetigt} L\xF6sungen wurden best\xE4tigt, {offen} Aufgaben lie\xDFen sich nicht pr\xFCfen. Bei diesen Aufgaben kommt ein anderes Ergebnis heraus. Ge\xE4ndert wurde nichts. Du kannst den gefundenen Wert je Aufgabe \xFCbernehmen oder die Aufgabe sp\xE4ter in der Tabelle bearbeiten. Ein Ergebnis der KI kann auch selbst falsch sein oder die Aufgabe ist mehrdeutig gestellt.",nachrechnen_eingetragen:"eingetragen",nachrechnen_berechnet:"berechnet",nachrechnen_ki:"die KI kommt auf",nur_abweichende:"Diese Aufgaben anzeigen",rechenweg_erzeugen:"Rechenweg erzeugen",rechenweg_erzeugen_laeuft:"Die KI schreibt die Rechenwege \u2026",rechenwege_erzeugt:"Rechenwege erzeugt: {erzeugt}. Schon vorhanden: {vorhanden}. \xDCbersprungen, weil die L\xF6sung abweicht: {abweichend}. Fehlgeschlagen: {fehlgeschlagen}.",vorschlag:"Vorschlag",vorschlag_ki:"Vorschlag der KI",uebernehmen_loesung:"\xDCbernehmen",uebernehmen_titel:"Ersetzt die eingetragene L\xF6sung durch diesen Wert. Der gespeicherte Rechenweg und die bisherige Statistik der Aufgabe werden dabei gel\xF6scht.",alle_uebernehmen:"Alle \xFCbernehmen",alle_uebernehmen_frage:"{n} L\xF6sungen ersetzen? {ki} davon stammen von der KI und k\xF6nnen selbst falsch sein.",uebernommen:"L\xF6sungen \xFCbernommen: {n}",schliessen:"Schlie\xDFen",fachart_mathe:"Mathematik",fachart_sach:"Sachfach",generieren:"Aufgaben generieren",generieren_titel:"Aufgaben von der KI erzeugen lassen",generieren_hilfe:"Die KI erzeugt Aufgaben, die den vorhandenen \xE4hneln. Gespeichert werden nur Aufgaben, deren L\xF6sung nachgerechnet oder gegengepr\xFCft werden konnte. Sie warten danach auf deine Freigabe. Der Name des Kindes wird nicht \xFCbertragen.",generieren_beispiele_auswahl:"Als Beispiele dienen die {n} markierten Aufgaben.",generieren_beispiele_thema:"Als Beispiele dienen die Aufgaben des gew\xE4hlten Themas.",generieren_anzahl:"Anzahl (1\u201320)",generieren_beschreibung:"Beschreibung (optional)",generieren_beschreibung_hilfe:"z. B. Br\xFCche mit gleichem Nenner addieren",generieren_start:"Erzeugen",generieren_laeuft:"Die KI arbeitet, das kann bis zu zwei Minuten dauern \u2026",generieren_ohne_ki:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt (Einstellungen der Integration).",generiert:"{erzeugt} erzeugt, {verworfen} verworfen, {doppelt} doppelt.",freigeben:"Auswahl freigeben",freigegeben:"{n} Aufgaben freigegeben.",import_titel_mathe:"Aufgaben importieren",import_hilfe_mathe:"Eine Aufgabe pro Zeile: Aufgabe; L\xF6sung; optionaler Hinweis. Weitere g\xFCltige Schreibweisen der L\xF6sung mit | trennen.",schwierig_aufgaben:"Schwierigste Aufgaben",spalte_seite:"Seite",spalte_lektion:"Lektion/Thema",spalte_box:"Box",spalte_fehler:"Fehler",spalte_geprueft:"Gepr\xFCft",spalte_erstellt:"Erstellt",box_hinweis:"Leitner-Box je Abfragerichtung (1 = neu oder falsch, 5 = sicher)",alternativen_hinweis:"Mehrere mit | trennen",keine_aufgaben:"Keine Aufgaben vorhanden.",keine_treffer:"Keine Aufgabe passt zu den Filtern.",anzahl:"{n} von {gesamt} Aufgaben",bearbeiten:"Bearbeiten",speichern:"Speichern",abbrechen:"Abbrechen",alle_auswaehlen:"Alle sichtbaren ausw\xE4hlen",loeschen_frage:"{n} Aufgabe(n) wirklich l\xF6schen?",loeschen_warnung:"{n} der ausgew\xE4hlten Aufgaben geh\xF6ren zu anstehenden Arbeiten: {arbeiten}. Trotzdem l\xF6schen?",geloescht:"{n} Aufgabe(n) gel\xF6scht.",geloescht_arbeit:"Arbeit gel\xF6scht.",gespeichert:"Gespeichert.",import_titel:"Vokabeln importieren",import_hilfe:"Eine Vokabel pro Zeile: {a}; {b}; optionaler Hinweis. Alternativen mit | trennen.",import_inhalt:"Inhalt",import_trennzeichen:"Trennzeichen (leer = automatisch)",import_geprueft:"Als gepr\xFCft \xFCbernehmen",vorschau:"Vorschau",uebernehmen:"\xDCbernehmen",vorschau_neu:"neu",vorschau_vorhanden:"bereits vorhanden",vorschau_fehler:"Nicht lesbare Zeilen: {zeilen}",import_ergebnis:"{n} importiert, {u} \xFCbersprungen.",import_fehler:"{n} fehlerhafte Eintr\xE4ge.",export_titel:"Aufgaben exportieren",mit_statistik:"Lernstatistik einschlie\xDFen",herunterladen:"Herunterladen",import_json_titel:"JSON importieren",import_json_hilfe:"Vorhandene Aufgaben bleiben erhalten, gleiche Vokabeln werden \xFCbersprungen.",datei_ungueltig:"Die Datei enth\xE4lt kein g\xFCltiges JSON.",import_json_lektion:"Lektion/Thema der importierten Aufgaben",import_json_aus_datei:"Lektionen aus der Datei \xFCbernehmen",import_json_lektion_hilfe:"Mit einer gew\xE4hlten Lektion landen alle importierten Aufgaben dort, egal was in der Datei steht.",neue_arbeit:"Neue Arbeit / H\xDC",keine_arbeiten:"F\xFCr dieses Fach ist keine Arbeit angelegt.",art:"Art",art_arbeit:"Klassenarbeit",art_hue:"H\xDC",datum:"Datum",thema:"Thema",abfragen_pro_tag:"Abfragen pro Tag",start_tage_vorher:"Beginn (Tage vorher)",intensivierung:"Frequenz zum Termin hin steigern",antwortfrist:"Antwortfrist (Minuten)",antwortfrist_leer:"wie allgemein eingestellt",antwortfrist_hinweis:"Leer: Es gilt die allgemeine Einstellung. Bei mehreren laufenden Arbeiten gilt die k\xFCrzeste Frist.",aufgaben_der_arbeit:"Aufgaben der Arbeit",auswahl_alle:"Alle Aufgaben des Fachs",auswahl_gezielt:"Gezielte Auswahl",schnell_lektionen:"Ganze Lektionen/Themen",arbeit_fehlt_beides:"Zum Speichern fehlen noch Thema und Datum.",arbeit_fehlt_thema:"Zum Speichern fehlt noch das Thema.",arbeit_fehlt_datum:"Zum Speichern fehlt noch das Datum.",schnell_seit:"Alle Aufgaben seit",schnell_seiten:"Alle Aufgaben von Buchseite",schnell_seiten_bis:"bis Buchseite",hinzufuegen:"Hinzuf\xFCgen",einzelne_aufgaben:"Einzelne Aufgaben",auswahl_leeren:"Auswahl leeren",arbeit_umfang:"{n} Aufgaben",arbeit_alle:"alle Aufgaben",arbeit_loeschen_frage:"Arbeit \u201E{thema}\u201C wirklich l\xF6schen?",arbeit_titel_neu:"Arbeit / H\xDC anlegen",arbeit_titel_bearbeiten:"Arbeit / H\xDC bearbeiten",vergangen:"vorbei",fehler_allgemein:"Das hat nicht geklappt: {fehler}",err_nicht_geladen:"LearnBuddy ist gerade nicht geladen.",err_fach_unbekannt:"Das Fach wurde nicht gefunden.",err_aufgabe_unbekannt:"Die Aufgabe wurde nicht gefunden.",err_arbeit_unbekannt:"Die Arbeit wurde nicht gefunden.",err_frage_ungueltig:"Bitte beide W\xF6rter ausf\xFCllen (h\xF6chstens 500 Zeichen).",err_alternativen_ungueltig:"Die Alternativen sind ung\xFCltig.",err_hinweis_ungueltig:"Der Hinweis ist zu lang.",err_aufgabe_ungueltig:"Bitte eine Aufgabe eingeben (h\xF6chstens 500 Zeichen).",err_loesung_ungueltig:"Bitte eine L\xF6sung eingeben (h\xF6chstens 100 Zeichen).",err_rechenweg_ungueltig:"Der Rechenweg darf h\xF6chstens 8 Schritte haben.",err_schwierigkeit_ungueltig:"Die Schwierigkeit muss zwischen 1 und 5 liegen.",err_anzahl_ungueltig:"Die Anzahl muss zwischen 1 und 20 liegen.",err_beschreibung_ungueltig:"Die Beschreibung ist zu lang.",err_ki_fehlt:"F\xFCr dieses Fach ist keine KI-Entit\xE4t gew\xE4hlt.",err_ki_fehler:"Die KI hat keine brauchbaren Aufgaben geliefert. Bitte sp\xE4ter erneut versuchen.",err_generieren_nur_mathe:"Aufgaben lassen sich nur f\xFCr Mathe-F\xE4cher generieren.",err_generieren_ohne_vorgabe:"Bitte ein Thema oder eine Beschreibung angeben oder zuerst Beispielaufgaben anlegen.",err_export_typ:"Die Datei geh\xF6rt zu einer anderen Art von Fach.",err_bild_ungueltig:"Das ist kein Bild in einem unterst\xFCtzten Format (PNG, JPEG, WebP, GIF).",err_bild_zu_gross:"Das Bild ist gr\xF6\xDFer als 10 MB.",err_bild_unbekannt:"Das Bild wurde nicht gefunden. Bitte erneut hochladen.",err_nachrechnen_nur_mathe:"Nachrechnen gibt es nur f\xFCr Mathe-F\xE4cher.",err_rechenweg_nur_mathe:"Rechenwege gibt es nur f\xFCr Mathe-F\xE4cher.",err_auswahl_ungueltig:"Bitte 1 bis 100 Aufgaben ausw\xE4hlen.",err_seite_ungueltig:"Die Seite muss eine Zahl zwischen 1 und 9999 sein.",err_lektion_ungueltig:"Der Name ist zu lang (h\xF6chstens 100 Zeichen).",err_lektion_leer:"Bitte einen Namen eingeben.",err_lektion_vorhanden:"Diese Lektion gibt es schon.",err_lektion_unbekannt:"Diese Lektion gibt es nicht. Bitte zuerst anlegen.",err_lektion_verwendet:"Die Lektion enth\xE4lt noch Aufgaben.",err_import_leer:"Der Inhalt enth\xE4lt keine g\xFCltige Zeile.",err_export_ungueltig:"Die Datei ist kein LearnBuddy-Export.",err_export_version:"Diese Export-Version wird nicht unterst\xFCtzt.",err_export_sprachen:"Die Sprachen des Exports passen nicht zu diesem Fach.",err_thema_leer:"Bitte ein Thema eingeben.",err_datum_vergangen:"Das Datum liegt in der Vergangenheit.",err_arbeit_ungueltig:"Bitte die Angaben zur Arbeit pr\xFCfen.",err_unauthorized:"Daf\xFCr sind Administratorrechte n\xF6tig.",err_kind_unbekannt:"Das Kind wurde nicht gefunden.",err_keine_aufgaben:"Es gibt keine gepr\xFCften Aufgaben, die abgefragt werden k\xF6nnten.",err_senden_fehlgeschlagen:"Die Nachricht konnte nicht zugestellt werden. Bitte das Messenger-Ziel des Kindes pr\xFCfen."},ct={titel:"LearnBuddy",kind:"Child",fach:"Subject",keine_kinder:"No child has been added yet. Add a child and a subject under Settings \u2192 Devices & services \u2192 LearnBuddy first.",keine_faecher:"This child has no subject yet.",tab_uebersicht:"Overview",status_aktiv:"Questions enabled",status_pausiert:"Questions paused",status_pausiert_bis:"Paused until {zeit}",pausieren:"Pause",fortsetzen:"Resume",offene_frage:"Open question",offene_frage_text:"{fach}, asked at {von}, expires at {bis}",keine_offene_frage:"No open question",naechste_abfrage:"Next question",keine_geplant:"None scheduled",nach_offener_frage:"After the open question",letzte_frage:"Last question",noch_nie:"Never",jetzt_fragen:"Ask a question now",jetzt_fragen_kurz:"Ask now",fach_waehlen:"From which subject?",egal_welches:"Any subject",frage_gesendet:"The question was sent.",kz_gefragt:"Questions asked",kz_richtig:"Correct",kz_falsch:"Wrong",kz_unbeantwortet:"Unanswered",ki_keine:"No AI entity is selected for this subject.",ki_nicht_verfuegbar:"The selected AI entity is not available right now.",ki_ohne_bilder:"The selected AI entity cannot read images.",ki_hinweis_keine:"No AI entity is selected for this subject. Creating tasks, writing solution steps and the import from photos are switched off; answers are only judged locally. Set it up under Settings \u2192 Devices & services \u2192 LearnBuddy \u2192 gear.",ki_hinweis_ohne_bilder:"The selected AI entity cannot read images. Features that use photos are switched off.",ki_hinweis_nicht_verfuegbar:"The selected AI entity is not available right now. The AI features are switched off and answers are only judged locally. Check the AI integration in Home Assistant.",ki_hinweis_sach_zusatz:" Short answers are not asked meanwhile, only multiple-choice questions.",err_ki_nicht_verfuegbar:"The selected AI entity is not available right now.",err_ki_nicht_erreichbar:"The AI could not be reached or refused the request (connection, account, credit). Please try again later.",neue_version:"LearnBuddy was updated. This page still shows the old version; reload it to see all features.",neu_laden:"Reload the page",absender_unbekannt:"A message from an unknown sender arrived: {kennung} ({quelle}). It could not be assigned to a child.",absender_uebernehmen:"Use as sender ID for {name}",absender_verwerfen:"Dismiss",absender_uebernommen:"Sender ID saved. The next answer will be assigned.",quelle_telegram:"Telegram",quelle_whatsapp:"WhatsApp",quelle_event:"custom event",err_absender_leer:"The sender ID is empty.",err_absender_vergeben:"This sender ID already belongs to another child.",absender_fehlt:"This child has no sender ID (chat ID or phone number). Questions are sent, but answers cannot be assigned. Set it under Settings \u2192 Devices & services \u2192 LearnBuddy \u2192 edit the child.",sim_plan:"Plan a simulation (optional)",sim_plan_aktiv:"Send a simulation automatically at a fixed time",sim_plan_hilfe:"At the chosen time the child automatically gets a simulation of this exam in the messenger: the sheet as an image, then the tasks one after the other, the result at the end. If the child is paused or a simulation is already running then, it is skipped.",sim_plan_um:"Date and time",sim_plan_offen:"Simulation planned for {zeit} ({n} tasks)",sim_plan_erledigt:"The simulation planned for {zeit} is done",err_simulation_um_vergangen:"The time of the simulation is in the past.",err_simulation_um_ungueltig:"Please check date and time of the simulation.",sim_knopf_arbeit:"Simulate the exam",sim_knopf_hue:"Simulate the homework check",sim_hilfe:"A sheet is put together at random from the approved tasks of this exam. The learning statistics stay untouched.",sim_weg_ausdruck:"As a printout",sim_weg_ausdruck_hilfe:"The sheet is made as an image to download and print. Nothing is sent.",sim_weg_messenger:"In the messenger",sim_weg_messenger_hilfe:"{name} gets the sheet as an image and then the tasks one after the other. Feedback only comes at the end: points, percent and the solutions to the mistakes.",sim_anzahl:"Number of tasks",sim_verfuegbar:"Available this way: {n}",sim_keine_aufgaben:"There are no approved tasks for this exam.",sim_start_ausdruck:"Create the sheet",sim_start_messenger:"Start the simulation",sim_gestartet:"The simulation with {n} tasks is running. The child gets the result at the end.",sim_blatt_hilfe:"The sheet with {n} tasks is ready. The images are deleted after 24 hours; download them if you want to keep them.",sim_herunterladen:"Download page {n}",sim_drucken:"Print",sim_druck_blockiert:"The browser blocked the print window. Download the pages and print them from there.",sim_laeuft:"Simulation",sim_laeuft_text:"running: task {nr} of {n}",sim_abbrechen:"Stop the simulation",frage_abbrechen:"Cancel question",frage_abbrechen_frage:"Withdraw the open question? It is not counted, and the child gets a short message.",sim_abbrechen_frage:"Stop the running simulation without a result?",err_simulation_laeuft:"A simulation is running for this child.",err_weg_ungueltig:"Unknown way of simulating.",foto_import:"Import from photo",foto_titel:"Read tasks from photos",foto_hilfe:"Take the photos of the vocabulary pages straight and legible. The AI reads word, translation, page number and the reference to the unit page. It leaves out example sentences and phonetic transcriptions. Then you check the preview. The photos are sent to the AI service and deleted afterwards.",foto_hilfe_mathe:"Take the photo of the book page or worksheet straight and legible. The AI reads the tasks and solves them; the results are recalculated. Then you check the preview. The photos are sent to the AI service and deleted afterwards.",foto_auslesen:"Read",foto_leer:"Nothing usable was found on the photos.",foto_vorschau_titel:"Check the preview",foto_vorschau_hilfe:"Compare the lines with the book, correct them if needed and untick everything that should not be imported. Nothing is stored before you click the button.",foto_vorhanden:"already there",foto_braucht_bild:"needs a figure \u2013 create it as a task with an image",foto_unbestaetigt:"result not confirmed",foto_uebernehmen:"Import {n}",foto_fertig:"{n} imported, {doppelt} already there, {fehler} faulty.",foto_fehler:"{n} lines are faulty (empty or too long fields). Please correct them.",err_foto_sachfach:"Knowledge subjects have their own way to create questions from pages.",kz_teilweise:"Partly right",neue_frage:"New question",spalte_frage:"Question",spalte_musterantwort:"Model answer",richtige_antwort:"Correct answer",form:"Form",form_kurz:"Short answer",form_auswahl:"Multiple choice",form_gemischt:"Mixed",kernpunkte:"Key points (one per line, optional): what a complete answer contains",falsche_optionen:"Wrong answers (one per line, 2 to 3)",belegstelle:"Source passage",quellseite_anzeigen:"Show the book page",sach_ohne_ki:"No AI entity is selected for this subject. Therefore only multiple-choice questions are asked; short answers can only be judged by the AI.",seiten:"Questions from a book page",seiten_titel:"Create questions from book pages",seiten_hilfe:"Take the photos straight and legible. The AI reads the pages and suggests questions with a model answer. The questions then wait for your approval. The photos are sent to the AI service.",seiten_waehlen:"Photos of the pages (up to {n})",seiten_zu_viele:"Only the first {n} photos are used.",seiten_anzahl:"Number of questions",seiten_schwerpunkt:"Focus (optional)",seiten_schwerpunkt_hilfe:"e.g. only the section about cellular respiration",seiten_start:"Create questions",seiten_laeuft:"The AI is reading the pages. This can take a minute \u2026",seiten_fertig:"{erzeugt} questions created, {verworfen} unusable, {doppelt} duplicates. Please check and approve them.",err_sach_frage_ungueltig:"Please enter a question (at most 500 characters).",err_sach_antwort_ungueltig:"Please enter an answer (at most 500 characters).",err_form_ungueltig:"Unknown form of question.",err_kernpunkte_ungueltig:"At most 6 key points with 200 characters each.",err_falsche_optionen_ungueltig:"A multiple-choice question needs 2 to 3 wrong answers that differ from each other and from the correct one.",err_stelle_ungueltig:"The source passage may be 300 characters long at most.",err_import_sachfach:"Lists cannot be imported into knowledge subjects.",err_seiten_nur_sachfach:"Questions from book pages only exist for knowledge subjects.",err_seiten_ungueltig:"Please choose 1 to 4 photos.",err_ki_ohne_bilder:"The selected AI entity cannot read images.",kz_trefferquote:"Success rate",kz_aufgaben:"Tasks",anstehend:"Upcoming exams",vorschlaege:"Suggestions from the calendar",vorschlag_eintragen:"Enter",vorschlag_ignorieren:"Ignore",vorschlag_gleicher_tag:"Already on the same day: {arbeiten}",keine_vorschlaege:"No new dates in the calendar.",kalender_pruefen:"Check now",kalender_geprueft:"Last checked: {zeit}",kalender_nie:"The calendar has not been read yet.",kalender_fehler:"The calendar could not be read last time. Shown is what was read before.",kalender_ignorierte:"Show {n} ignored again",arbeit_fach:"Subject",fach_neu:"New subject",fach_neu_titel:"Add a subject",fach_neu_art:"Kind of subject",fach_neu_sprache:"Language",fach_neu_name:"Name",fach_neu_name_optional:"Name (empty: like the language or \u201CMath\u201D)",fach_neu_anlegen:"Add subject",fach_neu_fehlt:"This child has no subject yet. Add one first.",fachart_fremdsprache:"Foreign language",err_kalender_aus:"No exam calendar is switched on for this child.",err_termin_unbekannt:"The date is no longer in the calendar.",err_sprache_ungueltig:"Please choose a foreign language other than the native language.",err_fachart_ungueltig:"Please choose the kind of subject.",err_fach_vorhanden:"A subject with this name already exists.",err_name_leer:"Please enter a name.",keine_anstehend:"No exam is planned.",heute:"today",morgen:"tomorrow",in_tagen:"in {n} days",heute_abfragen:"{n} questions today",sicher:"{n} % mastered",sicher_hinweis:"Share of cards in boxes 3 to 5",faecher_titel:"Subjects",fach_aufgaben:"{n} tasks in {l} lessons",ungeprueft:"{n} not approved",aufgaben_oeffnen:"Tasks",lernstand:"Progress",lernstand_hinweis:"Cards per Leitner box: box 1 is new or was wrong last time, box 5 is mastered.",box:"Box {n}",karten:"{n} cards",keine_karten:"There are no tasks yet.",schwierig:"Hardest words",keine_schwierig:"No wrong answers yet.",fehler_mal:"{n} \xD7 wrong",arbeiten_oeffnen:"Manage exams",tab_aufgaben:"Tasks",tab_arbeiten:"Exams",laden:"Loading \u2026",neue_aufgabe:"New task",importieren:"Import",lektion_hinzufuegen:"Add lesson/topic",lektion_titel:"Lessons and topics",lektion_hilfe:"Lessons and topics are created here and can then be selected when adding or importing tasks and in exams.",lektion_name:"Name of the lesson or topic",lektion_keine:"No lesson has been created yet.",lektion_anzahl:"{n} tasks",lektion_loeschen_hinweis:"Only empty lessons can be deleted",lektion_angelegt:"\u201C{name}\u201D created.",keine_lektion:"\u2013 none \u2013",export_json:"Export JSON",import_json:"Import JSON",ausgewaehlt:"{n} selected",loeschen:"Delete",arbeit_aus_auswahl:"Exam from selection",filter_suche:"Search",filter_lektion:"Lesson/topic",filter_quelle:"Source",filter_geprueft:"Approved",filter_fehlerquote:"Error rate from %",filter_von:"Created from",filter_bis:"Created until",filter_seite_von:"Book page from",filter_seite_bis:"Book page to",filter_zuruecksetzen:"Reset filters",alle:"All",ohne_lektion:"Without lesson",ja:"Yes",nein:"No",quelle_manuell:"Manual",quelle_upload:"Upload",quelle_generiert:"Generated",spalte_alternativen:"Alternatives",spalte_hinweis:"Hint",aufgabenart_titel:"What kind of task?",aufgabenart_rechnen:"Calculation",aufgabenart_rechnen_hilfe:"Text only, for example 3/4 + 1/8 or a word problem.",aufgabenart_bild:"Task with an image",aufgabenart_bild_hilfe:"A diagram, a graph or a drawing is the basis. The image is sent with the task.",bildaufgabe_titel:"Task with an image",bild:"Image",bild_waehlen:"Choose an image",bild_hilfe:"PNG, JPEG, WebP or GIF, at most 10 MB. The image is stored smaller, extra data such as the location is removed.",bild_vorschau:"Preview of the image",bild_anzeigen:"Show the image",einleitung:"Introduction (optional)",einleitung_hilfe:"Is put in front of every part, e.g. \u201CIn other countries the holidays \u2026\u201D",teilaufgaben:"Parts",teilaufgaben_hilfe:"Every row becomes a task of its own with the same image and is asked separately.",teilaufgabe:"Part {n}",teilaufgabe_hinzufuegen:"Add a part",teilaufgabe_entfernen:"Remove the part",bildaufgaben_gespeichert:"Tasks with an image created: {n}",bild_fehlt:"Please choose an image.",teil_fehlt:"Please enter at least one part with its result.",keine_bilder:"{name} cannot receive images at the moment, so tasks with an image are not asked. Images are sent automatically through Telegram; for other messengers enter an \u201Caction for images\u201D at the child.",export_ohne_bild:"Exported. Tasks with an image are not included: {n}",spalte_aufgabe:"Task",spalte_loesung:"Result",spalte_schwierigkeit:"Level",schwierigkeit:"Difficulty",schwierigkeit_hinweis:"1 = easy, 5 = hard",schwierigkeit_beliebig:"any",rechenweg:"Steps of the solution (one per line, optional)",rechenweg_vorhanden:"Steps of the solution are stored",verifikation_rechnerisch:"recalculated",verifikation_ki:"double-checked by the AI",verifikation_manuell:"checked by yourself",selbst_nachgerechnet:"Checked by myself",selbst_nachgerechnet_hinweis:"Marks the solutions of the selection as checked by you. A differing suggestion is dropped.",selbst_nachgerechnet_fertig:"Marked as checked by yourself: {n}",verifikation_abweichung:"result differs",nachrechnen:"Recalculate selection",nachrechnen_laeuft:"The tasks are being recalculated \u2026",nachgerechnet:"{bestaetigt} confirmed, {abweichend} differing, {offen} not checkable.",nachrechnen_titel:"Result of recalculating",nachrechnen_zusammenfassung:"{bestaetigt} results were confirmed, {offen} tasks could not be checked. These tasks give another result. Nothing was changed. You can apply the value that was found per task or edit the task in the table later. A result of the AI can be wrong itself, or the task is ambiguous.",nachrechnen_eingetragen:"stored",nachrechnen_berechnet:"calculated",nachrechnen_ki:"the AI gets",nur_abweichende:"Show these tasks",rechenweg_erzeugen:"Create solution steps",rechenweg_erzeugen_laeuft:"The AI is writing the solution steps \u2026",rechenwege_erzeugt:"Solution steps created: {erzeugt}. Already there: {vorhanden}. Skipped because the result differs: {abweichend}. Failed: {fehlgeschlagen}.",vorschlag:"Suggestion",vorschlag_ki:"Suggestion of the AI",uebernehmen_loesung:"Apply",uebernehmen_titel:"Replaces the stored result with this value. The stored solution steps and the statistics of the task are deleted.",alle_uebernehmen:"Apply all",alle_uebernehmen_frage:"Replace {n} results? {ki} of them come from the AI and can be wrong themselves.",uebernommen:"Results applied: {n}",schliessen:"Close",fachart_mathe:"Mathematics",fachart_sach:"Knowledge subject",generieren:"Generate tasks",generieren_titel:"Let the AI create tasks",generieren_hilfe:"The AI creates tasks similar to the existing ones. Only tasks whose solution could be recalculated or double-checked are stored. They wait for your approval afterwards. The name of the child is not sent.",generieren_beispiele_auswahl:"The {n} selected tasks serve as examples.",generieren_beispiele_thema:"The tasks of the chosen topic serve as examples.",generieren_anzahl:"Number (1\u201320)",generieren_beschreibung:"Description (optional)",generieren_beschreibung_hilfe:"e.g. adding fractions with the same denominator",generieren_start:"Create",generieren_laeuft:"The AI is working, this can take up to two minutes \u2026",generieren_ohne_ki:"No AI entity is selected for this subject (settings of the integration).",generiert:"{erzeugt} created, {verworfen} discarded, {doppelt} duplicates.",freigeben:"Approve selection",freigegeben:"{n} tasks approved.",import_titel_mathe:"Import tasks",import_hilfe_mathe:"One task per line: task; result; optional hint. Separate other accepted spellings of the result with |.",schwierig_aufgaben:"Hardest tasks",spalte_seite:"Page",spalte_lektion:"Lesson/topic",spalte_box:"Box",spalte_fehler:"Errors",spalte_geprueft:"Approved",spalte_erstellt:"Created",box_hinweis:"Leitner box per direction (1 = new or wrong, 5 = mastered)",alternativen_hinweis:"Separate several with |",keine_aufgaben:"There are no tasks yet.",keine_treffer:"No task matches the filters.",anzahl:"{n} of {gesamt} tasks",bearbeiten:"Edit",speichern:"Save",abbrechen:"Cancel",alle_auswaehlen:"Select all visible",loeschen_frage:"Really delete {n} task(s)?",loeschen_warnung:"{n} of the selected tasks belong to upcoming exams: {arbeiten}. Delete anyway?",geloescht:"{n} task(s) deleted.",geloescht_arbeit:"Exam deleted.",gespeichert:"Saved.",import_titel:"Import vocabulary",import_hilfe:"One word per line: {a}; {b}; optional hint. Separate alternatives with |.",import_inhalt:"Content",import_trennzeichen:"Separator (empty = automatic)",import_geprueft:"Import as approved",vorschau:"Preview",uebernehmen:"Import",vorschau_neu:"new",vorschau_vorhanden:"already exists",vorschau_fehler:"Unreadable lines: {zeilen}",import_ergebnis:"{n} imported, {u} skipped.",import_fehler:"{n} invalid entries.",export_titel:"Export tasks",mit_statistik:"Include learning statistics",herunterladen:"Download",import_json_titel:"Import JSON",import_json_hilfe:"Existing tasks are kept, identical words are skipped.",datei_ungueltig:"The file does not contain valid JSON.",import_json_lektion:"Lesson/topic of the imported tasks",import_json_aus_datei:"Keep the lessons from the file",import_json_lektion_hilfe:"With a selected lesson all imported tasks go there, whatever the file says.",neue_arbeit:"New exam",keine_arbeiten:"There is no exam for this subject.",art:"Type",art_arbeit:"Exam",art_hue:"Homework check",datum:"Date",thema:"Topic",abfragen_pro_tag:"Questions per day",start_tage_vorher:"Start (days before)",intensivierung:"Increase frequency towards the date",antwortfrist:"Time to answer (minutes)",antwortfrist_leer:"as set in general",antwortfrist_hinweis:"Empty: the general setting applies. With several running exams the shortest time wins.",aufgaben_der_arbeit:"Tasks of the exam",auswahl_alle:"All tasks of the subject",auswahl_gezielt:"Specific selection",schnell_lektionen:"Whole lessons",arbeit_fehlt_beides:"Topic and date are still missing.",arbeit_fehlt_thema:"The topic is still missing.",arbeit_fehlt_datum:"The date is still missing.",schnell_seit:"All tasks since",schnell_seiten:"All tasks from book page",schnell_seiten_bis:"to book page",hinzufuegen:"Add",einzelne_aufgaben:"Single tasks",auswahl_leeren:"Clear selection",arbeit_umfang:"{n} tasks",arbeit_alle:"all tasks",arbeit_loeschen_frage:"Really delete the exam \u201C{thema}\u201D?",arbeit_titel_neu:"Add exam",arbeit_titel_bearbeiten:"Edit exam",vergangen:"past",fehler_allgemein:"That did not work: {fehler}",err_nicht_geladen:"LearnBuddy is not loaded right now.",err_fach_unbekannt:"The subject was not found.",err_aufgabe_unbekannt:"The task was not found.",err_arbeit_unbekannt:"The exam was not found.",err_frage_ungueltig:"Please fill in both words (500 characters at most).",err_alternativen_ungueltig:"The alternatives are invalid.",err_hinweis_ungueltig:"The hint is too long.",err_aufgabe_ungueltig:"Please enter a task (at most 500 characters).",err_loesung_ungueltig:"Please enter a result (at most 100 characters).",err_rechenweg_ungueltig:"The solution may have at most 8 steps.",err_schwierigkeit_ungueltig:"The difficulty must be between 1 and 5.",err_anzahl_ungueltig:"The number must be between 1 and 20.",err_beschreibung_ungueltig:"The description is too long.",err_ki_fehlt:"No AI entity is selected for this subject.",err_ki_fehler:"The AI did not return usable tasks. Please try again later.",err_generieren_nur_mathe:"Tasks can only be generated for math subjects.",err_generieren_ohne_vorgabe:"Enter a topic or a description, or add example tasks first.",err_export_typ:"The file belongs to another kind of subject.",err_bild_ungueltig:"This is not an image in a supported format (PNG, JPEG, WebP, GIF).",err_bild_zu_gross:"The image is larger than 10 MB.",err_bild_unbekannt:"The image was not found. Please upload it again.",err_nachrechnen_nur_mathe:"Only math subjects can be recalculated.",err_rechenweg_nur_mathe:"Only math subjects have solution steps.",err_auswahl_ungueltig:"Please select 1 to 100 tasks.",err_seite_ungueltig:"The page must be a number between 1 and 9999.",err_lektion_ungueltig:"The name is too long (100 characters at most).",err_lektion_leer:"Please enter a name.",err_lektion_vorhanden:"This lesson already exists.",err_lektion_unbekannt:"This lesson does not exist. Please create it first.",err_lektion_verwendet:"The lesson still contains tasks.",err_import_leer:"The content does not contain any valid line.",err_export_ungueltig:"The file is not a LearnBuddy export.",err_export_version:"This export version is not supported.",err_export_sprachen:"The languages of the export do not match this subject.",err_thema_leer:"Please enter a topic.",err_datum_vergangen:"The date is in the past.",err_arbeit_ungueltig:"Please check the details of the exam.",err_unauthorized:"Administrator rights are required.",err_kind_unbekannt:"The child was not found.",err_keine_aufgaben:"There are no approved tasks that could be asked.",err_senden_fehlgeschlagen:"The message could not be delivered. Please check the messenger target of the child."},ut={de:{de:"Deutsch",en:"Englisch",fr:"Franz\xF6sisch",es:"Spanisch",it:"Italienisch",la:"Latein"},en:{de:"German",en:"English",fr:"French",es:"Spanish",it:"Italian",la:"Latin"}};function Be(o){return o.toLowerCase().startsWith("de")?"de":"en"}function ae(o){let n=Be(o)==="de"?Le:ct;return(e,t={})=>n[e].replace(/\{(\w+)\}/g,(i,s)=>String(t[s]??""))}function y(o,n){return ut[Be(o)]?.[n]??n}function w(o,n){let e=n,t=[`err_${e?.message??""}`,`err_${e?.code??""}`];for(let i of t)if(i in Le)return o(i);return o("fehler_allgemein",{fehler:e?.message??String(n)})}var re=q`
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
`;var Me=["#86b6ef","#5598e7","#2a78d6","#1c5cab","#104281"],Ce=["#184f95","#256abf","#3987e5","#6da7ec","#b7d3f6"],dt=6e4,gt=["learnbuddy_question_sent","learnbuddy_answer_evaluated"],A=class extends E{constructor(){super(...arguments);this.narrow=!1;this.kindId="";this._fehler="";this._kalenderLaeuft=!1;this._erfolg="";this._waehleFach=!1;this._beschaeftigt=!1;this._abos=[]}static{this.styles=[re,q`
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
    `]}get _t(){return ae(this.hass?.language??"en")}get _api(){return new C(this.hass)}connectedCallback(){super.connectedCallback(),this._timer=window.setInterval(()=>void this._lade(),dt)}_abonniere(){let e=this.hass?.connection;!e||this._abos.length||(this._abos=gt.map(t=>e.subscribeEvents(()=>void this._lade(),t)))}disconnectedCallback(){super.disconnectedCallback(),window.clearInterval(this._timer);for(let e of this._abos)e.then(t=>t()).catch(()=>{});this._abos=[]}willUpdate(e){this._abonniere(),e.has("kindId")&&(this._daten=void 0,this._fehler="",this._erfolg="",this._lade())}async _lade(){if(!this.hass||!this.kindId)return;let e=this.kindId;try{let t=await this._api.dashboard(e);e===this.kindId&&(this._daten=t,this._fehler="")}catch(t){this._fehler=w(this._t,t)}}async _frage(e){this._waehleFach=!1,this._beschaeftigt=!0,this._erfolg="";try{await this._api.frageStellen(this.kindId,e),this._fehler="",this._erfolg=this._t("frage_gesendet")}catch(t){this._fehler=w(this._t,t)}finally{this._beschaeftigt=!1,await this._lade()}}_jetztFragen(){let e=this._daten?.faecher??[];e.length===1?this._frage(e[0]?.id??null):this._waehleFach=!0}async _brichFrageAb(){if(window.confirm(this._t("frage_abbrechen_frage"))){try{await this._api.frageAbbrechen(this.kindId),this._fehler=""}catch(e){this._fehler=w(this._t,e)}await this._lade()}}async _brichSimulationAb(){if(window.confirm(this._t("sim_abbrechen_frage"))){try{await this._api.simulationAbbrechen(this.kindId),this._fehler=""}catch(e){this._fehler=w(this._t,e)}await this._lade()}}async _setzeAktiv(e){try{await this._api.setzeAktiv(this.kindId,e),this._fehler=""}catch(t){this._fehler=w(this._t,t)}await this._lade()}_oeffne(e,t){this.dispatchEvent(new CustomEvent("lh-oeffnen",{detail:{ziel:e,fachId:t}}))}_zeit(e){if(!e)return"";let t=new Date(e),i=this.hass?.language??"en",s=new Date().toDateString()===t.toDateString();return t.toLocaleString(i,{...s?{}:{weekday:"short",day:"2-digit",month:"2-digit"},hour:"2-digit",minute:"2-digit"})}_uhr(e){return new Date(e).toLocaleTimeString(this.hass?.language??"en",{hour:"2-digit",minute:"2-digit"})}_datum(e){return new Date(`${e}T00:00:00`).toLocaleDateString(this.hass?.language??"en",{weekday:"short",day:"2-digit",month:"2-digit"})}_tage(e){return e<=0?this._t("heute"):e===1?this._t("morgen"):this._t("in_tagen",{n:e})}_balken(e,t=!1){let i=this.hass?.themes?.darkMode?Ce:Me,s=e.reduce((h,g)=>h+g,0),a=this._t,l=e.map((h,g)=>`${a("box",{n:g+1})}: ${h}`).join(", ");return r`
      <div class="balken ${t?"gross":""}" role="img" aria-label=${l}>
        ${s===0?u:e.map((h,g)=>h===0?u:r`<span
                    style="flex: ${h}; background: ${i[g]??""}"
                    title="${a("box",{n:g+1})}: ${a("karten",{n:h})}"
                  ></span>`)}
      </div>
    `}_legende(e){let t=this.hass?.themes?.darkMode?Ce:Me;return r`
      <div class="legende">
        ${e.map((i,s)=>r`
            <span>
              <i style="background: ${t[s]??""}"></i>${this._t("box",{n:s+1})}:
              <b>${i}</b>
            </span>
          `)}
      </div>
    `}render(){let e=this._t,t=this._daten;return r`
      ${this._fehler?r`<div class="meldung fehler" role="alert">
            <span>${this._fehler}</span>
          </div>`:u}
      ${this._erfolg?r`<div class="meldung" role="status">
            <span>${this._erfolg}</span>
            <button
              class="icon"
              aria-label=${e("schliessen")}
              @click=${()=>{this._erfolg=""}}
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>`:u}
      ${t?r`
            <div class="raster">
              <div class="card breit">${this._status(t)}</div>
              <div class="kacheln breit">${this._kacheln(t)}</div>
              <div class="card">${this._arbeiten(t)}</div>
              <div class="card">${this._faecher(t)}</div>
              <div class="card">${this._lernstand(t)}</div>
              <div class="card">${this._schwierig(t)}</div>
            </div>
          `:this._fehler?u:r`<div class="leer">${e("laden")}</div>`}
      ${this._waehleFach&&t?this._fachDialog(t):u}
    `}_status(e){let t=this._t,i=e.zustand,s=i.offene_frage,a=i.pausiert?i.pausiert_bis?t("status_pausiert_bis",{zeit:this._zeit(i.pausiert_bis)}):t("status_pausiert"):t("status_aktiv"),l=(h,g)=>r`
      <div class="fakt">
        <div class="klein">${h}</div>
        <div class="wert">${g}</div>
      </div>
    `;return r`
      <div class="status">
        <div class="zustand ${i.pausiert?"aus":"gut"}">
          <ha-icon
            icon=${i.pausiert?"mdi:pause-circle":"mdi:check-circle"}
          ></ha-icon>
          ${a}
        </div>
        <div class="fakten">
          ${i.simulation?l(t("sim_laeuft"),t("sim_laeuft_text",{nr:Math.min(i.simulation.nummer,i.simulation.anzahl),n:i.simulation.anzahl})):u}
          ${l(t("offene_frage"),s?t("offene_frage_text",{fach:s.fach,von:this._uhr(s.gestellt_um),bis:this._uhr(s.timeout_um)}):t("keine_offene_frage"))}
          ${l(t("naechste_abfrage"),s&&!i.pausiert?t("nach_offener_frage"):i.naechste_abfrage&&!i.pausiert?this._zeit(i.naechste_abfrage):t("keine_geplant"))}
          ${l(t("letzte_frage"),i.letzte_frage_um?this._zeit(i.letzte_frage_um):t("noch_nie"))}
        </div>
        <div class="knoepfe">
          <button
            class="primaer"
            ?disabled=${this._beschaeftigt||e.faecher.length===0||!!i.simulation}
            @click=${this._jetztFragen}
          >
            ${t("jetzt_fragen")}
          </button>
          <button @click=${()=>this._setzeAktiv(!i.aktiv||i.pausiert)}>
            ${t(i.pausiert?"fortsetzen":"pausieren")}
          </button>
          ${s&&!i.simulation?r`<button class="gefahr" @click=${this._brichFrageAb}>
                ${t("frage_abbrechen")}
              </button>`:u}
          ${i.simulation?r`<button class="gefahr" @click=${this._brichSimulationAb}>
                ${t("sim_abbrechen")}
              </button>`:u}
        </div>
      </div>
    `}_kacheln(e){let t=this._t,i=e.statistik,s=(a,l,h)=>r`
      <div class="kachel">
        <div class="zahl">${l}</div>
        <div class="name"><ha-icon icon=${h}></ha-icon>${a}</div>
      </div>
    `;return r`
      ${s(t("kz_gefragt"),String(i.gefragt),"mdi:chat-question")}
      ${s(t("kz_richtig"),String(i.richtig),"mdi:check")}
      ${s(t("kz_falsch"),String(i.falsch),"mdi:close")}
      ${i.teilweise?s(t("kz_teilweise"),String(i.teilweise),"mdi:circle-half-full"):u}
      ${s(t("kz_unbeantwortet"),String(i.unbeantwortet),"mdi:timer-sand")}
      ${s(t("kz_trefferquote"),i.trefferquote===null?"\u2013":`${Math.round(i.trefferquote)} %`,"mdi:bullseye-arrow")}
      ${s(t("kz_aufgaben"),String(i.aufgaben),"mdi:cards-outline")}
    `}_sicher(e){return e===null?u:r`<span class="klein" title=${this._t("sicher_hinweis")}>
          ${this._t("sicher",{n:e})}
        </span>`}_arbeiten(e){let t=this._t,i=s=>r`
      <div class="zeile">
        <div class="countdown ${s.tage_bis<=2?"bald":""}">
          <div class="tage">${this._tage(s.tage_bis)}</div>
          <div class="klein">${this._datum(s.datum)}</div>
        </div>
        <div class="mitte">
          <div class="titel">
            ${s.fach}: ${s.thema}
            <span class="marke">
              ${t(s.art==="hue"?"art_hue":"art_arbeit")}
            </span>
          </div>
          <div class="klein">
            ${t("arbeit_umfang",{n:s.aufgaben})} ·
            ${t("heute_abfragen",{n:s.abfragen_heute})}
          </div>
          <div class="mini">${this._balken(s.boxen)} ${this._sicher(s.sicher)}</div>
        </div>
        <button
          class="icon"
          title=${t("arbeiten_oeffnen")}
          aria-label=${t("arbeiten_oeffnen")}
          @click=${()=>this._oeffne("arbeiten",s.fach_id)}
        >
          <ha-icon icon="mdi:chevron-right"></ha-icon>
        </button>
      </div>
    `;return r`
      <h2>${t("anstehend")}</h2>
      ${e.arbeiten.length?e.arbeiten.map(i):r`<div class="leer">${t("keine_anstehend")}</div>`}
      ${this._vorschlaege(e)}
    `}_vorschlaege(e){let t=e.kalender;if(!t)return u;let i=this._t,s=e.vorschlaege??[],a=l=>r`
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
              </div>`:u}
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
      ${t.fehler?r`<div class="klein warnung" role="status">${i("kalender_fehler")}</div>`:u}
      ${s.length?s.map(a):r`<div class="leer">${i("keine_vorschlaege")}</div>`}
      <div class="kalenderfuss">
        <span class="klein">
          ${t.geprueft_um?i("kalender_geprueft",{zeit:this._zeit(t.geprueft_um)}):i("kalender_nie")}
        </span>
        <button ?disabled=${this._kalenderLaeuft} @click=${this._pruefeKalender}>
          ${i("kalender_pruefen")}
        </button>
        ${t.ignoriert?r`<button @click=${this._zeigeIgnorierte}>
              ${i("kalender_ignorierte",{n:t.ignoriert})}
            </button>`:u}
      </div>
    `}_trageEin(e){this.dispatchEvent(new CustomEvent("lh-vorschlag",{detail:{vorschlag:e}}))}async _ignoriere(e){try{await this._api.kalenderIgnorieren(this.kindId,e.uid),this._fehler=""}catch(t){this._fehler=w(this._t,t)}await this._lade()}async _zeigeIgnorierte(){try{await this._api.kalenderWiederherstellen(this.kindId),this._fehler=""}catch(e){this._fehler=w(this._t,e)}await this._lade()}async _pruefeKalender(){this._kalenderLaeuft=!0;try{await this._api.kalenderPruefen(this.kindId),this._fehler=""}catch(e){this._fehler=w(this._t,e)}finally{this._kalenderLaeuft=!1}await this._lade()}_faecher(e){let t=this._t,i=this.hass?.language??"en",s=a=>r`
      <div class="zeile">
        <div class="mitte">
          <div class="titel">
            ${a.name}
            <span class="klein">
              ${a.typ==="mathe"?t("fachart_mathe"):a.typ==="sach"?t("fachart_sach"):a.sprachen.map(l=>y(i,l)).join(" \u2194 ")}
            </span>
          </div>
          <div class="klein">
            ${t("fach_aufgaben",{n:a.aufgaben,l:a.lektionen})}
            ${a.ungeprueft?r` · ${t("ungeprueft",{n:a.ungeprueft})}`:u}
            ${a.trefferquote===null?u:r` · ${t("kz_trefferquote")} ${Math.round(a.trefferquote)} %`}
          </div>
          <div class="mini">${this._balken(a.boxen)} ${this._sicher(a.sicher)}</div>
        </div>
        <div class="fachknoepfe">
          <button
            ?disabled=${this._beschaeftigt||a.aufgaben===0}
            @click=${()=>this._frage(a.id)}
          >
            ${t("jetzt_fragen_kurz")}
          </button>
          <button @click=${()=>this._oeffne("aufgaben",a.id)}>
            ${t("aufgaben_oeffnen")}
          </button>
        </div>
      </div>
    `;return r`
      <h2>${t("faecher_titel")}</h2>
      ${e.faecher.length?e.faecher.map(s):r`<div class="leer">${t("keine_faecher")}</div>`}
    `}_lernstand(e){let t=this._t,i=e.statistik.boxen,s=i.reduce((a,l)=>a+l,0);return r`
      <h2>${t("lernstand")}</h2>
      ${s===0?r`<div class="leer">${t("keine_karten")}</div>`:r`
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
    `}_fachDialog(e){let t=this._t,i=()=>{this._waehleFach=!1};return r`
      <div
        class="overlay"
        @click=${s=>{s.target===s.currentTarget&&i()}}
      >
        <div class="dialog" role="dialog" aria-modal="true" style="width: min(420px, 100%)">
          <h2>${t("fach_waehlen")}</h2>
          <div class="auswahl">
            ${e.faecher.map(s=>r`
                <button ?disabled=${s.aufgaben===0} @click=${()=>this._frage(s.id)}>
                  ${s.name}
                  <div class="klein">${t("arbeit_umfang",{n:s.aufgaben})}</div>
                </button>
              `)}
            <button @click=${()=>this._frage(null)}>${t("egal_welches")}</button>
          </div>
          <div class="aktionen">
            <button @click=${i}>${t("abbrechen")}</button>
          </div>
        </div>
      </div>
    `}};f([F({attribute:!1})],A.prototype,"hass",2),f([F({type:Boolean,reflect:!0})],A.prototype,"narrow",2),f([F()],A.prototype,"kindId",2),f([b()],A.prototype,"_daten",2),f([b()],A.prototype,"_fehler",2),f([b()],A.prototype,"_kalenderLaeuft",2),f([b()],A.prototype,"_erfolg",2),f([b()],A.prototype,"_waehleFach",2),f([b()],A.prototype,"_beschaeftigt",2);customElements.get("lh-uebersicht")||customElements.define("lh-uebersicht",A);var J=30,S=4;function _t(o){if(!o)return"";let n=new Date(o);if(Number.isNaN(n.getTime()))return"";let e=t=>String(t).padStart(2,"0");return`${n.getFullYear()}-${e(n.getMonth()+1)}-${e(n.getDate())}T${e(n.getHours())}:${e(n.getMinutes())}`}function Ue(o){return o.split(`
`).map(n=>n.trim()).filter(n=>n.length>0)}var qe={aufgabe:"",loesung:"",alternativen:""},ft=["fremdsprache","mathe","sach"],pt=["en","fr","es","it","la","de"],Ke={typ:"fremdsprache",name:"",sprache:"en"},D="\0ohne",Q={suche:"",lektion:"",quelle:"",geprueft:"",fehlerquote:"",von:"",bis:"",seiteVon:"",seiteBis:""};function Oe(o,n,e){let t=n.trim()===""?null:Number(n),i=e.trim()===""?null:Number(e);return t===null&&i===null?!0:o===null?!1:(t===null||o>=t)&&(i===null||o<=i)}function He(o,n,e){return o.typ==="mathe"?`${o.aufgabe} = ${o.loesung}`:o.typ==="sach"?`${o.frage} \u2013 ${o.antwort}`:`${o.frage[n]??""} \u2013 ${o.frage[e]??""}`}function p(o){return o.target.value}function z(o){return o.target.checked}function le(o){return o.split("|").map(n=>n.trim()).filter(n=>n.length>0)}var Ve=(()=>{try{return new URL(import.meta.url).searchParams.get("v")}catch{return null}})();function bt(o){return new Promise(n=>setTimeout(n,o))}var m=class extends E{constructor(){super(...arguments);this.narrow=!1;this._kindId="";this._fachId="";this._aufgaben=[];this._tab="uebersicht";this._filter={...Q};this._auswahl=new Set;this._entwurf=null;this._dialog=null;this._generieren=null;this._bildEntwurf=null;this._bildAdressen={};this._grossbild="";this._bildText="";this._seiten=null;this._foto=null;this._sim=null;this._veraltet=!1;this._nachgerechnet=null;this._nurIds=null;this._meldung=null;this._laedt=!0;this._beschaeftigt=!1;this._importText="";this._importLektion="";this._importTrenner="";this._importGeprueft=!0;this._vorschau=null;this._mitStatistik=!1;this._jsonDaten=null;this._arbeit=null;this._neuesFach=null;this._dialogFehler="";this._lektionName="";this._jsonLektion="";this._gestartet=!1;this._taste=e=>{e.key==="Escape"&&(this._dialog?this._schliesseDialog():this._entwurf&&(this._entwurf=null))}}static{this.styles=re}get _t(){return ae(this.hass?.language??"en")}get _api(){return new C(this.hass)}get _fach(){return this._uebersicht?.faecher.find(e=>e.id===this._fachId)}get _faecherDesKindes(){return(this._uebersicht?.faecher??[]).filter(e=>e.kind_id===this._kindId)}get _arbeitenDesFachs(){return(this._uebersicht?.arbeiten??[]).filter(e=>e.fach_id===this._fachId).sort((e,t)=>e.datum.localeCompare(t.datum))}connectedCallback(){super.connectedCallback(),window.addEventListener("keydown",this._taste)}disconnectedCallback(){super.disconnectedCallback(),window.removeEventListener("keydown",this._taste)}updated(e){e.has("hass")&&this.hass&&!this._gestartet&&(this._gestartet=!0,this._ladeUebersicht())}async _ladeUebersicht(e=0){let t=0;for(;;)try{this._uebersicht=await this._api.uebersicht();break}catch(s){if(s.code==="not_loaded"&&t<e){t+=1,await bt(500);continue}this._zeigeFehler(s),this._laedt=!1;return}let i=this._uebersicht;this._veraltet=!!(Ve&&i.panel_version&&i.panel_version!==Ve),i.kinder.some(s=>s.id===this._kindId)||(this._kindId=i.kinder[0]?.id??""),this._faecherDesKindes.some(s=>s.id===this._fachId)||(this._fachId=this._faecherDesKindes[0]?.id??""),await this._ladeAufgaben(),this._laedt=!1}async _ladeAufgaben(){if(!this._fachId){this._aufgaben=[];return}try{this._aufgaben=await this._api.aufgaben(this._fachId)}catch(t){this._aufgaben=[],this._zeigeFehler(t)}let e=new Set(this._aufgaben.map(t=>t.id));this._auswahl=new Set([...this._auswahl].filter(t=>e.has(t))),this._ladeBildAdressen()}async _ladeBildAdressen(){let e=new Set;for(let t of this._aufgaben){let i=t.typ==="mathe"?t.bild:t.typ==="sach"?t.quelle_bild:null;i&&!(i in this._bildAdressen)&&e.add(i)}for(let t of e)try{let i=await this._api.bildAdresse(t);this._bildAdressen={...this._bildAdressen,[t]:i}}catch{}}async _neuLaden(e=0){await this._ladeUebersicht(e)}_zeigeFehler(e){this._meldung={text:w(this._t,e),fehler:!0}}_zeigeErfolg(e){this._meldung={text:e,fehler:!1}}_gefiltert(){let e=this._filter,t=e.suche.trim().toLowerCase(),i=e.fehlerquote===""?null:Number(e.fehlerquote),s=this._nurIds&&this._aufgaben.some(a=>this._nurIds?.has(a.id))?this._nurIds:null;return this._aufgaben.filter(a=>{if(s&&!s.has(a.id)||t&&![...a.typ==="mathe"?[a.aufgabe,a.loesung,...a.alternativen]:a.typ==="sach"?[a.frage,a.antwort,...a.kernpunkte,...a.falsche_optionen]:[...Object.values(a.frage),...Object.values(a.alternativen).flat()],a.hinweis??""].join(" ").toLowerCase().includes(t)||e.lektion===D&&a.lektion||e.lektion&&e.lektion!==D&&a.lektion!==e.lektion||e.quelle&&a.quelle!==e.quelle||e.geprueft&&a.geprueft!==(e.geprueft==="ja")||i!==null&&!Number.isNaN(i)&&(a.fehlerquote===null||a.fehlerquote<i))return!1;let l=a.erstellt.slice(0,10);return!(e.von&&l<e.von||e.bis&&l>e.bis||!Oe(a.seite,e.seiteVon,e.seiteBis))})}async _waehleKind(e){e!==this._kindId&&(this._kindId=e,this._fachId=this._faecherDesKindes[0]?.id??"",this._zuruecksetzen(),await this._ladeAufgaben())}async _waehleFach(e){this._fachId=e,this._zuruecksetzen(),await this._ladeAufgaben()}_zuruecksetzen(){this._auswahl=new Set,this._entwurf=null,this._filter={...Q}}_setzeFilter(e,t){this._filter={...this._filter,[e]:t},this._nurIds=null}_umschalten(e,t){let i=new Set(this._auswahl);t?i.add(e):i.delete(e),this._auswahl=i}_alleUmschalten(e,t){let i=new Set(this._auswahl);for(let s of e)t?i.add(s.id):i.delete(s.id);this._auswahl=i}_bearbeite(e){let[t="",i=""]=this._fach?.sprachen??[],s=e?.typ==="mathe"?e:null,a=e?.typ==="vokabel"?e:null,l=e?.typ==="sach"?e:null;this._entwurf={id:e?.id??null,a:s?s.aufgabe:l?l.frage:a?.frage[t]??"",b:s?s.loesung:l?l.antwort:a?.frage[i]??"",form:l?.form??"kurz",kernpunkte:(l?.kernpunkte??[]).join(`
`),falsche:(l?.falsche_optionen??[]).join(`
`),altA:(a?.alternativen[t]??[]).join(" | "),altB:(s?s.alternativen:a?.alternativen[i]??[]).join(" | "),rechenweg:(s?.rechenweg??[]).join(`
`),schwierigkeit:s?.schwierigkeit?.toString()??"",hinweis:e?.hinweis??"",seite:e?.seite?.toString()??"",lektion:e?.lektion??(this._filter.lektion===D?"":this._filter.lektion),geprueft:e?.geprueft??!0}}_setzeEntwurf(e,t){this._entwurf&&(this._entwurf={...this._entwurf,[e]:t})}async _speichereAufgabe(){let e=this._entwurf,t=this._fach;if(!e||!t)return;let[i="",s=""]=t.sprachen,a={...t.typ==="mathe"?{aufgabe:e.a,loesung:e.b,alternativen:le(e.altB),rechenweg:e.rechenweg.split(`
`).map(l=>l.trim()).filter(l=>l.length>0),schwierigkeit:e.schwierigkeit===""?null:Number(e.schwierigkeit)}:t.typ==="sach"?{frage:e.a,antwort:e.b,form:e.form,kernpunkte:e.form==="kurz"?Ue(e.kernpunkte):[],falsche_optionen:e.form==="auswahl"?Ue(e.falsche):[]}:{frage:{[i]:e.a,[s]:e.b},alternativen:{[i]:le(e.altA),[s]:le(e.altB)}},hinweis:e.hinweis||null,seite:e.seite.trim()===""?null:Number(e.seite),lektion:e.lektion||null,geprueft:e.geprueft};this._beschaeftigt=!0;try{e.id?await this._api.aufgabeAendern(t.id,e.id,a):await this._api.aufgabeAnlegen(t.id,a),this._entwurf=null,this._zeigeErfolg(this._t("gespeichert")),await this._neuLaden()}catch(l){this._zeigeFehler(l)}finally{this._beschaeftigt=!1}}async _setzeGeprueft(e,t){try{await this._api.aufgabeAendern(e.fach_id,e.id,{geprueft:t}),await this._ladeAufgaben()}catch(i){this._zeigeFehler(i)}}async _freigeben(){let e=this._aufgaben.filter(t=>this._auswahl.has(t.id)&&!t.geprueft);if(e.length){this._beschaeftigt=!0;try{for(let t of e)await this._api.aufgabeAendern(t.fach_id,t.id,{geprueft:!0});this._auswahl=new Set,this._zeigeErfolg(this._t("freigegeben",{n:e.length}))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1,await this._neuLaden()}}}async _nachrechnen(){let e=[...this._auswahl];if(!(!e.length||!this._fachId)){this._beschaeftigt=!0,this._meldung={text:this._t("nachrechnen_laeuft"),fehler:!1};try{let t=await this._api.nachrechnen(this._fachId,e);await this._ladeAufgaben(),t.abweichend.length?(this._meldung=null,this._nachgerechnet=t,this._dialogFehler="",this._dialog="nachrechnen"):this._zeigeErfolg(this._t("nachgerechnet",{bestaetigt:t.bestaetigt,abweichend:0,offen:t.nicht_pruefbar}))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}_neueAufgabe(){this._fach?.typ==="mathe"?(this._dialogFehler="",this._dialog="aufgabenart"):this._bearbeite(null)}_oeffneBildaufgabe(){let e=this._filter.lektion===D?"":this._filter.lektion;this._bildEntwurf={datei:null,vorschau:"",einleitung:"",lektion:e,seite:"",teile:[{...qe}]},this._dialogFehler="",this._dialog="bildaufgabe"}_setzeBild(e,t){this._bildEntwurf&&(this._bildEntwurf={...this._bildEntwurf,[e]:t})}_bildGewaehlt(e){let t=e.target.files?.[0]??null,i=this._bildEntwurf;i&&(i.vorschau&&URL.revokeObjectURL(i.vorschau),this._bildEntwurf={...i,datei:t,vorschau:t?URL.createObjectURL(t):""})}_setzeTeil(e,t,i){let s=this._bildEntwurf;if(!s)return;let a=s.teile.map((l,h)=>h===e?{...l,[t]:i}:l);this._bildEntwurf={...s,teile:a}}async _speichereBildaufgabe(){let e=this._bildEntwurf,t=this._fach;if(!e||!t)return;let i=e.teile.filter(a=>a.aufgabe.trim()!==""&&a.loesung.trim()!=="");if(!e.datei){this._dialogFehler=this._t("bild_fehlt");return}if(!i.length){this._dialogFehler=this._t("teil_fehlt");return}this._beschaeftigt=!0,this._dialogFehler="";let s=0;try{let a=await this._api.bildHochladen(e.datei),l=e.einleitung.trim();for(let h of i)await this._api.aufgabeAnlegen(t.id,{aufgabe:l?`${l} ${h.aufgabe.trim()}`:h.aufgabe.trim(),loesung:h.loesung,alternativen:le(h.alternativen),bild:a,lektion:e.lektion||null,seite:e.seite.trim()===""?null:Number(e.seite)}),s+=1;this._schliesseDialog(),this._zeigeErfolg(this._t("bildaufgaben_gespeichert",{n:s}))}catch(a){this._dialogFehler=w(this._t,a)}finally{this._beschaeftigt=!1,s&&await this._neuLaden()}}async _erzeugeRechenwege(){let e=[...this._auswahl];if(!(!e.length||!this._fachId)){this._beschaeftigt=!0,this._meldung={text:this._t("rechenweg_erzeugen_laeuft"),fehler:!1};try{let t=await this._api.rechenwegeErzeugen(this._fachId,e);await this._ladeAufgaben(),this._zeigeErfolg(this._t("rechenwege_erzeugt",t))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}async _markiereGeprueft(){let e=[...this._auswahl];if(!(!e.length||!this._fachId)){this._beschaeftigt=!0;try{let t=await this._api.alsGeprueftMarkieren(this._fachId,e);await this._ladeAufgaben(),this._zeigeErfolg(this._t("selbst_nachgerechnet_fertig",{n:t}))}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}async _uebernimmVorschlag(e){if(!(!e.length||!this._fachId)){this._beschaeftigt=!0;try{let t=await this._api.vorschlagUebernehmen(this._fachId,e),i=new Set(e);if(this._nachgerechnet){let s=this._nachgerechnet.abweichend.filter(a=>!i.has(a.id));this._nachgerechnet={...this._nachgerechnet,abweichend:s},!s.length&&this._dialog==="nachrechnen"&&this._schliesseDialog()}this._zeigeErfolg(this._t("uebernommen",{n:t})),await this._ladeAufgaben()}catch(t){this._dialog==="nachrechnen"?this._dialogFehler=w(this._t,t):this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}_uebernimmAlle(){let e=this._nachgerechnet?.abweichend??[],t=this._t("alle_uebernehmen_frage",{n:e.length,ki:e.filter(i=>i.durch==="ki").length});window.confirm(t)&&this._uebernimmVorschlag(e.map(i=>i.id))}_oeffneGenerieren(){let e=this._filter.lektion===D?"":this._filter.lektion;this._generieren={lektion:e,anzahl:10,schwierigkeit:"",beschreibung:""},this._dialogFehler="",this._dialog="generieren"}async _generiere(){let e=this._generieren;if(!(!e||!this._fachId)){this._beschaeftigt=!0,this._dialogFehler="";try{let t=await this._api.generieren(this._fachId,{anzahl:e.anzahl,lektion:e.lektion||null,schwierigkeit:e.schwierigkeit===""?null:Number(e.schwierigkeit),beschreibung:e.beschreibung.trim()||null,beispiel_ids:[...this._auswahl]});this._schliesseDialog(),this._auswahl=new Set,t.erzeugt&&(this._filter={...Q,geprueft:"nein"}),this._zeigeErfolg(this._t("generiert",{erzeugt:t.erzeugt,verworfen:t.verworfen,doppelt:t.uebersprungen})),await this._neuLaden()}catch(t){this._dialogFehler=w(this._t,t)}finally{this._beschaeftigt=!1}}}async _loesche(e){if(!(!e.length||!this._fachId)&&window.confirm(this._t("loeschen_frage",{n:e.length}))){this._beschaeftigt=!0;try{let t=await this._api.aufgabenLoeschen(this._fachId,e,!1),i=Object.keys(t.zugeordnet);if(i.length){let s=new Set(Object.values(t.zugeordnet).flat()),a=(this._uebersicht?.arbeiten??[]).filter(h=>s.has(h.id)).map(h=>`${h.thema} (${this._datum(h.datum)})`).join(", "),l=this._t("loeschen_warnung",{n:i.length,arbeiten:a});if(!window.confirm(l))return;t=await this._api.aufgabenLoeschen(this._fachId,e,!0)}this._zeigeErfolg(this._t("geloescht",{n:t.geloescht})),await this._neuLaden()}catch(t){this._zeigeFehler(t)}finally{this._beschaeftigt=!1}}}_schliesseDialog(){this._dialog=null,this._vorschau=null,this._jsonDaten=null,this._arbeit=null,this._neuesFach=null,this._generieren=null,this._nachgerechnet=null,this._bildEntwurf?.vorschau&&URL.revokeObjectURL(this._bildEntwurf.vorschau),this._bildEntwurf=null,this._grossbild="",this._bildText="";for(let e of this._seiten?.vorschauen??[])URL.revokeObjectURL(e);this._seiten=null;for(let e of this._foto?.vorschauen??[])URL.revokeObjectURL(e);this._foto=null,this._sim=null,this._dialogFehler=""}_simVerfuegbar(e){return e.arbeit.simulierbar?.[e.weg]??J}_oeffneSimulation(e){let t={arbeit:e,anzahl:10,weg:"ausdruck",seiten:null};t.anzahl=Math.max(1,Math.min(10,this._simVerfuegbar(t))),this._sim=t,this._dialogFehler="",this._dialog="simulation"}async _simuliere(){let e=this._sim;if(e){this._beschaeftigt=!0,this._dialogFehler="";try{let t=await this._api.simulieren(e.arbeit.id,e.anzahl,e.weg);if(t.weg==="messenger"){this._schliesseDialog(),this._zeigeErfolg(this._t("sim_gestartet",{n:t.anzahl})),this._tab="uebersicht";return}let i=[];for(let s of t.bilder)i.push(await this._api.bildAdresse(s));this._sim={...e,anzahl:t.anzahl,seiten:i}}catch(t){this._dialogFehler=w(this._t,t)}finally{this._beschaeftigt=!1}}}_druckeSimulation(){let e=this._sim?.seiten??[],t=window.open("","_blank");if(!t){this._dialogFehler=this._t("sim_druck_blockiert");return}let i=t.document;i.title=this._sim?.arbeit.thema??"";let s=i.createElement("style");s.textContent="@page{size:A4;margin:0}body{margin:0}img{display:block;width:100%;page-break-after:always}",i.head.append(s);let a=e.length;for(let l of e){let h=i.createElement("img");h.addEventListener("load",()=>{a-=1,a===0&&(t.focus(),t.print())}),h.src=new URL(l,window.location.origin).href,i.body.append(h)}}_oeffneFoto(){this._foto={dateien:[],vorschauen:[],lektion:this._filter.lektion===D?"":this._filter.lektion,zeilen:null},this._dialogFehler="",this._dialog="foto"}_fotoGewaehlt(e){let t=this._foto;if(!t)return;let i=[...e.target.files??[]];for(let a of t.vorschauen)URL.revokeObjectURL(a);let s=i.slice(0,S);this._dialogFehler=i.length>S?this._t("seiten_zu_viele",{n:S}):"",this._foto={...t,dateien:s,vorschauen:s.map(a=>URL.createObjectURL(a))}}async _leseFoto(){let e=this._foto,t=this._fach;if(!e||!e.dateien.length||!t)return;let[i="",s=""]=t.sprachen;this._beschaeftigt=!0,this._dialogFehler="";try{let a=[];for(let h of e.dateien)a.push(await this._api.bildHochladen(h,!0));let l=await this._api.fotoAuslesen(t.id,a);if(!l.zeilen.length){this._dialogFehler=this._t("foto_leer");return}this._foto={...e,zeilen:l.zeilen.map(h=>({an:!h.vorhanden&&!h.braucht_bild,a:l.typ==="mathe"?h.aufgabe??"":h.frage?.[i]??"",b:l.typ==="mathe"?h.loesung??"":h.frage?.[s]??"",hinweis:h.hinweis??"",seite:h.seite?.toString()??"",geaendert:!1,roh:h}))}}catch(a){this._dialogFehler=w(this._t,a)}finally{this._beschaeftigt=!1}}_setzeFotoZeile(e,t){let i=this._foto;i?.zeilen&&(this._foto={...i,zeilen:i.zeilen.map((s,a)=>a===e?{...s,...t}:s)})}async _uebernimmFoto(){let e=this._foto,t=this._fach;if(!e?.zeilen||!t)return;let[i="",s=""]=t.sprachen,a=e.zeilen.filter(l=>l.an).map(l=>{let h=l.seite.trim()===""?null:Number(l.seite);return t.typ==="mathe"?{aufgabe:l.a,loesung:l.b,seite:h,verifikation:l.geaendert?"keine":l.roh.verifikation}:{frage:{[i]:l.a,[s]:l.b},alternativen:l.geaendert?{}:l.roh.alternativen??{},hinweis:l.hinweis||null,seite:h}});if(a.length){this._beschaeftigt=!0,this._dialogFehler="";try{let l=await this._api.fotoUebernehmen(t.id,a,e.lektion||null);if(l.fehler.length&&!l.importiert){this._dialogFehler=this._t("foto_fehler",{n:l.fehler.length});return}this._schliesseDialog(),this._zeigeErfolg(this._t("foto_fertig",{n:l.importiert,doppelt:l.uebersprungen,fehler:l.fehler.length})),await this._neuLaden()}catch(l){this._dialogFehler=w(this._t,l)}finally{this._beschaeftigt=!1}}}_oeffneSeiten(){this._seiten={dateien:[],vorschauen:[],lektion:this._filter.lektion===D?"":this._filter.lektion,anzahl:8,form:"gemischt",schwerpunkt:""},this._dialogFehler="",this._dialog="seiten"}_seitenGewaehlt(e){let t=this._seiten;if(!t)return;let i=[...e.target.files??[]];for(let a of t.vorschauen)URL.revokeObjectURL(a);let s=i.slice(0,S);this._dialogFehler=i.length>S?this._t("seiten_zu_viele",{n:S}):"",this._seiten={...t,dateien:s,vorschauen:s.map(a=>URL.createObjectURL(a))}}async _erzeugeFragen(){let e=this._seiten;if(!(!e||!e.dateien.length||!this._fachId)){this._beschaeftigt=!0,this._dialogFehler="";try{let t=[];for(let s of e.dateien)t.push(await this._api.bildHochladen(s,!0));let i=await this._api.fragenAusSeiten(this._fachId,{seiten:t,anzahl:e.anzahl,form:e.form,lektion:e.lektion||null,schwerpunkt:e.schwerpunkt.trim()||null});this._schliesseDialog(),this._auswahl=new Set,i.erzeugt&&(this._filter={...Q,geprueft:"nein"}),this._zeigeErfolg(this._t("seiten_fertig",{erzeugt:i.erzeugt,verworfen:i.verworfen,doppelt:i.uebersprungen})),await this._neuLaden()}catch(t){this._dialogFehler=w(this._t,t)}finally{this._beschaeftigt=!1}}}_oeffneLektionen(){this._lektionName="",this._dialogFehler="",this._dialog="lektion"}async _lektionAnlegen(){let e=this._lektionName.trim();if(!(!e||!this._fachId)){this._dialogFehler="";try{await this._api.lektionHinzufuegen(this._fachId,e),this._lektionName="",this._zeigeErfolg(this._t("lektion_angelegt",{name:e})),await this._neuLaden()}catch(t){this._dialogFehler=w(this._t,t)}}}async _lektionLoeschen(e){this._dialogFehler="";try{await this._api.lektionLoeschen(this._fachId,e),this._filter.lektion===e&&this._setzeFilter("lektion",""),await this._neuLaden()}catch(t){this._dialogFehler=w(this._t,t)}}_lektionAuswahl(e,t,i){let s=[...this._fach?.lektionen??[]];return e&&!s.includes(e)&&s.push(e),r`
      <select
        aria-label=${i}
        .value=${e}
        @change=${a=>t(p(a))}
      >
        <option value="" ?selected=${e===""}>
          ${this._t("keine_lektion")}
        </option>
        ${s.map(a=>r`<option value=${a} ?selected=${a===e}>
              ${a}
            </option>`)}
      </select>
    `}_oeffneImport(){this._importText="",this._importTrenner="",this._importGeprueft=!0,this._importLektion=this._filter.lektion===D?"":this._filter.lektion,this._vorschau=null,this._dialogFehler="",this._dialog="import"}async _importVorschau(){this._dialogFehler="";try{this._vorschau=await this._api.importVorschau(this._fachId,this._importText,this._importTrenner||null)}catch(e){this._dialogFehler=w(this._t,e)}}async _importUebernehmen(){this._beschaeftigt=!0,this._dialogFehler="";try{let e=await this._api.importText(this._fachId,this._importText,this._importLektion.trim()||null,this._importTrenner||null,this._importGeprueft);this._schliesseDialog(),this._zeigeErfolg(this._t("import_ergebnis",{n:e.importiert,u:e.uebersprungen})),await this._neuLaden()}catch(e){this._dialogFehler=w(this._t,e)}finally{this._beschaeftigt=!1}}async _exportiere(){let e=this._fach;if(e)try{let t=await this._api.export(e.id,this._mitStatistik),i=new Blob([JSON.stringify(t,null,2)],{type:"application/json"}),s=document.createElement("a");s.href=URL.createObjectURL(i);let a=e.name.replace(/[^\p{L}\p{N}_-]+/gu,"_");s.download=`learnbuddy-${a}-${new Date().toISOString().slice(0,10)}.json`,s.click(),URL.revokeObjectURL(s.href),this._schliesseDialog();let l=Number(t.ausgelassen_mit_bild??0);l&&this._zeigeErfolg(this._t("export_ohne_bild",{n:l}))}catch(t){this._dialogFehler=w(this._t,t)}}async _dateiGewaehlt(e){let t=e.target,i=t.files?.[0];if(t.value="",!!i)try{let s=JSON.parse(await i.text());if(typeof s!="object"||s===null||Array.isArray(s))throw new Error("no object");this._jsonDaten=s,this._jsonLektion="",this._dialogFehler="",this._dialog="importJson"}catch{this._meldung={text:this._t("datei_ungueltig"),fehler:!0}}}async _importiereJson(){if(this._jsonDaten){this._beschaeftigt=!0;try{let e=await this._api.importJson(this._fachId,this._jsonDaten,this._mitStatistik,this._jsonLektion||null);this._schliesseDialog();let t=this._t("import_ergebnis",{n:e.importiert,u:e.uebersprungen});e.fehler.length&&(t+=` ${this._t("import_fehler",{n:e.fehler.length})}`),this._zeigeErfolg(t),await this._neuLaden()}catch(e){this._dialogFehler=w(this._t,e)}finally{this._beschaeftigt=!1}}}_oeffneArbeit(e,t=[]){let i=e?e.lektionen.length>0||e.aufgaben_ids.length>0:t.length>0;this._arbeit={id:e?.id??null,art:e?.art??"arbeit",datum:e?.datum??"",thema:e?.thema??"",abfragen:e?.abfragen_pro_tag??3,start:e?.start_tage_vorher??7,intensivierung:e?.intensivierung??!0,frist:e?.antwortfrist_minuten??null,simAktiv:!!e?.simulation_um,simUm:_t(e?.simulation_um??null),simAnzahl:e?.simulation_anzahl??10,kalenderUid:null,modus:i?"auswahl":"alle",lektionen:new Set(e?.lektionen??[]),ids:new Set(e?.aufgaben_ids??t),seit:"",seiteVon:"",seiteBis:""},this._neuesFach=null,this._dialogFehler="",this._dialog="arbeit"}async _oeffneVorschlag(e){let{vorschlag:t}=e.detail,i=this._faecherDesKindes,s=(t.fach_id&&i.some(a=>a.id===t.fach_id)?t.fach_id:null)??(i.some(a=>a.id===this._fachId)?this._fachId:i[0]?.id)??"";s!==this._fachId&&(this._fachId=s,this._zuruecksetzen(),await this._ladeAufgaben()),this._oeffneArbeit(null),this._arbeit&&(this._arbeit={...this._arbeit,art:t.art,datum:t.datum,thema:t.text,kalenderUid:t.uid}),s||(this._neuesFach={...Ke})}async _wechsleFachImDialog(e){!this._arbeit||e===this._fachId||(this._fachId=e,this._zuruecksetzen(),await this._ladeAufgaben(),this._arbeit={...this._arbeit,modus:"alle",lektionen:new Set,ids:new Set,seit:"",seiteVon:"",seiteBis:""})}async _legeFachAn(){let e=this._neuesFach;if(e){this._beschaeftigt=!0,this._dialogFehler="";try{let t=await this._api.fachAnlegen(this._kindId,e.typ,e.name.trim(),e.typ==="fremdsprache"?e.sprache:null);this._uebersicht=await this._api.uebersicht(),this._neuesFach=null,this._fachId="",await this._wechsleFachImDialog(t)}catch(t){this._dialogFehler=w(this._t,t)}finally{this._beschaeftigt=!1}}}_setzeArbeit(e,t){this._arbeit&&(this._arbeit={...this._arbeit,[e]:t})}_arbeitMenge(e,t,i){if(!this._arbeit)return;let s=new Set(this._arbeit[e]);i?s.add(t):s.delete(t),this._setzeArbeit(e,s),e==="lektionen"&&i&&!this._arbeit.thema.trim()&&this._setzeArbeit("thema",t)}_arbeitSeit(){let e=this._arbeit;if(!e?.seit)return;let t=new Set(e.ids);for(let i of this._aufgaben)i.erstellt.slice(0,10)>=e.seit&&t.add(i.id);this._setzeArbeit("ids",t)}_arbeitSeiten(){let e=this._arbeit;if(!e||!e.seiteVon&&!e.seiteBis)return;let t=new Set(e.ids);for(let i of this._aufgaben)Oe(i.seite,e.seiteVon,e.seiteBis)&&t.add(i.id);this._setzeArbeit("ids",t)}_arbeitUmfang(e){let t=new Set(e.lektionen),i=new Set(e.ids);return!t.size&&!i.size?null:this._aufgaben.filter(s=>i.has(s.id)||s.lektion!==null&&t.has(s.lektion)).length}async _speichereArbeit(){let e=this._arbeit;if(!e)return;if(e.simAktiv&&!e.simUm){this._zeigeFehler({message:"simulation_um_ungueltig"});return}let t=e.modus==="auswahl",i={datum:e.datum,thema:e.thema,art:e.art,lektionen:t?[...e.lektionen]:[],aufgaben_ids:t?[...e.ids]:[],abfragen_pro_tag:e.abfragen,start_tage_vorher:e.start,intensivierung:e.intensivierung,antwortfrist_minuten:e.frist,simulation_um:e.simAktiv&&e.simUm?new Date(e.simUm).toISOString():null,simulation_anzahl:e.simAnzahl};e.kalenderUid&&(i.kalender_uid=e.kalenderUid),e.id||(i.fach_id=this._fachId),this._beschaeftigt=!0,this._dialogFehler="";try{await this._api.arbeitSpeichern(e.id,i),this._schliesseDialog(),this._auswahl=new Set,this._tab="arbeiten",this._zeigeErfolg(this._t("gespeichert")),await this._neuLaden(20)}catch(s){this._dialogFehler=w(this._t,s)}finally{this._beschaeftigt=!1}}async _loescheArbeit(e){if(window.confirm(this._t("arbeit_loeschen_frage",{thema:e.thema})))try{await this._api.arbeitLoeschen(e.id),this._zeigeErfolg(this._t("geloescht_arbeit")),await this._neuLaden(20)}catch(t){this._zeigeFehler(t)}}_datum(e){let t=new Date(`${e.slice(0,10)}T00:00:00`);return Number.isNaN(t.getTime())?e:t.toLocaleDateString(this.hass?.language??"en",{year:"numeric",month:"2-digit",day:"2-digit"})}_zeitpunkt(e){let t=new Date(e);return Number.isNaN(t.getTime())?e:t.toLocaleString(this.hass?.language??"en",{year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"})}_menue(){this.dispatchEvent(new CustomEvent("hass-toggle-menu",{bubbles:!0,composed:!0}))}render(){let e=this._t,t=this._uebersicht;return r`
      <header>
        ${this.narrow?r`<button class="icon" aria-label="Menu" @click=${this._menue}>
              <ha-icon icon="mdi:menu"></ha-icon>
            </button>`:u}
        <h1>${e("titel")}</h1>
        ${t&&t.kinder.length>0?r`<div class="kinder" role="group" aria-label=${e("kind")}>
              ${t.kinder.map(i=>r`<button
                    class="kindwahl"
                    aria-pressed=${i.id===this._kindId?"true":"false"}
                    @click=${()=>this._waehleKind(i.id)}
                  >
                    ${i.name}
                  </button>`)}
            </div>`:u}
      </header>
      <main>
        ${this._veraltet?r`<div class="meldung" role="status">
              <span>${e("neue_version")}</span>
              <button class="primaer" @click=${()=>window.location.reload()}>
                ${e("neu_laden")}
              </button>
            </div>`:u}
        ${this._uebersicht?.kinder.find(i=>i.id===this._kindId)?.absender===!1?r`<div class="meldung fehler" role="status">
              <span>${e("absender_fehlt")}</span>
            </div>`:u}
        ${(this._uebersicht?.unbekannte_absender??[]).map(i=>r`<div class="meldung" role="status">
              <span>
                ${e("absender_unbekannt",{kennung:i.kennung,quelle:e(`quelle_${i.quelle}`)})}
              </span>
              <button
                class="primaer"
                @click=${()=>this._absenderZuordnen(i.kennung)}
              >
                ${e("absender_uebernehmen",{name:this._uebersicht?.kinder.find(s=>s.id===this._kindId)?.name??""})}
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
            </div>`:u}
        ${this._inhalt()}
      </main>
      ${this._dialogInhalt()}
    `}async _oeffne(e){let{ziel:t,fachId:i}=e.detail;i!==this._fachId&&(this._fachId=i,this._zuruecksetzen()),this._tab=t,await this._neuLaden()}async _absenderZuordnen(e){try{await this._api.absenderZuordnen(this._kindId,e),await this._neuLaden(),this._zeigeErfolg(this._t("absender_uebernommen"))}catch(t){this._zeigeFehler(t)}}async _absenderVerwerfen(e){try{await this._api.absenderVerwerfen(e),await this._neuLaden()}catch(t){this._zeigeFehler(t)}}async _waehleTab(e){this._tab=e,e!=="uebersicht"&&await this._neuLaden()}_inhalt(){let e=this._t;if(this._laedt)return r`<div class="leer">${e("laden")}</div>`;if(!this._uebersicht?.kinder.length)return r`<div class="card leer">${e("keine_kinder")}</div>`;let t={uebersicht:null,aufgaben:this._fach?this._aufgaben.length:null,arbeiten:this._fach?this._arbeitenDesFachs.length:null},i={uebersicht:e("tab_uebersicht"),aufgaben:e("tab_aufgaben"),arbeiten:e("tab_arbeiten")};return r`
      <div class="tabs" role="tablist">
        ${["uebersicht","aufgaben","arbeiten"].map(s=>r`<button
              role="tab"
              aria-selected=${this._tab===s?"true":"false"}
              @click=${()=>this._waehleTab(s)}
            >
              ${i[s]}${t[s]===null?"":` (${t[s]})`}
            </button>`)}
      </div>
      ${this._tab==="uebersicht"?r`<lh-uebersicht
            .hass=${this.hass}
            .narrow=${this.narrow}
            .kindId=${this._kindId}
            @lh-oeffnen=${this._oeffne}
            @lh-vorschlag=${this._oeffneVorschlag}
          ></lh-uebersicht>`:this._fachBereich()}
    `}_fachBereich(){let e=this._t,t=this._faecherDesKindes;return this._fach?r`
      ${t.length>0?r`<div class="kinder fachwahl" role="group" aria-label=${e("fach")}>
            ${t.map(i=>r`<button
                  class="kindwahl"
                  aria-pressed=${i.id===this._fachId?"true":"false"}
                  @click=${()=>this._waehleFach(i.id)}
                >
                  ${i.name}
                </button>`)}
          </div>`:u}
      ${this._tab==="aufgaben"?this._aufgabenAnsicht():this._arbeitenAnsicht()}
    `:r`<div class="card leer">${e("keine_faecher")}</div>`}_aufgabenAnsicht(){let e=this._t,t=this._fach,i=this._gefiltert(),s=[...this._auswahl],a=i.length>0&&i.every(k=>this._auswahl.has(k.id)),[l="",h=""]=t.sprachen,g=this.hass?.language??"en",_=this._filter,c=t.typ==="mathe",d=t.typ==="sach",$=this._uebersicht?.kinder.find(k=>k.id===this._kindId),v=t.ki_status??(t.ki?t.ki_bilder?"ok":"ohne_bilder":"keine"),x=v==="ok"||v==="ohne_bilder",I=v==="ok",X=v==="ok"?"":e(`ki_${v}`);return r`
      <div class="leiste">
        <button class="primaer" @click=${this._neueAufgabe}>
          ${e(d?"neue_frage":"neue_aufgabe")}
        </button>
        <button @click=${this._oeffneLektionen}>${e("lektion_hinzufuegen")}</button>
        ${c?r`<button
              ?disabled=${!x}
              title=${x?"":X}
              @click=${this._oeffneGenerieren}
            >
              ${e("generieren")}
            </button>`:u}
        ${d?r`<button
              ?disabled=${!I}
              title=${X}
              @click=${this._oeffneSeiten}
            >
              ${e("seiten")}
            </button>`:r`
              <button @click=${this._oeffneImport}>${e("importieren")}</button>
              <button
                ?disabled=${!I}
                title=${X}
                @click=${this._oeffneFoto}
              >
                ${e("foto_import")}
              </button>
            `}
        <button
          ?disabled=${!this._aufgaben.length}
          @click=${()=>{this._mitStatistik=!1,this._dialogFehler="",this._dialog="export"}}
        >
          ${e("export_json")}
        </button>
        <button
          @click=${()=>{this.renderRoot.querySelector("#datei")?.click()}}
        >
          ${e("import_json")}
        </button>
        <input
          id="datei"
          type="file"
          accept="application/json,.json"
          hidden
          @change=${this._dateiGewaehlt}
        />
        <span class="abstand"></span>
        ${s.length?r`
              <span>${e("ausgewaehlt",{n:s.length})}</span>
              ${this._aufgaben.some(k=>this._auswahl.has(k.id)&&!k.geprueft)?r`<button ?disabled=${this._beschaeftigt} @click=${this._freigeben}>
                    ${e("freigeben")}
                  </button>`:u}
              ${c?r`<button ?disabled=${this._beschaeftigt} @click=${this._nachrechnen}>
                    ${e("nachrechnen")}
                  </button>`:u}
              ${c?r`<button
                    ?disabled=${this._beschaeftigt}
                    title=${e("selbst_nachgerechnet_hinweis")}
                    @click=${this._markiereGeprueft}
                  >
                    ${e("selbst_nachgerechnet")}
                  </button>`:u}
              ${c?r`<button
                    ?disabled=${this._beschaeftigt||!x}
                    title=${x?"":X}
                    @click=${this._erzeugeRechenwege}
                  >
                    ${e("rechenweg_erzeugen")}
                  </button>`:u}
              <button @click=${()=>this._oeffneArbeit(null,s)}>
                ${e("arbeit_aus_auswahl")}
              </button>
              <button
                class="gefahr"
                ?disabled=${this._beschaeftigt}
                @click=${()=>this._loesche(s)}
              >
                ${e("loeschen")}
              </button>
            `:u}
      </div>

      ${v==="nicht_verfuegbar"?r`<div class="meldung fehler" role="status">
            <span>
              ${e("ki_hinweis_nicht_verfuegbar")}
              ${d?e("ki_hinweis_sach_zusatz"):""}
            </span>
          </div>`:v==="keine"&&d?r`<div class="meldung fehler" role="status">
              <span>${e("sach_ohne_ki")}</span>
            </div>`:v==="ok"?u:r`<p class="klein" role="note" style="margin: 0 0 12px">
                <ha-icon icon="mdi:information-outline" style="--mdc-icon-size: 16px"></ha-icon>
                ${e(`ki_hinweis_${v}`)}
              </p>`}
      ${c&&$&&!$.bilder&&this._aufgaben.some(k=>k.typ==="mathe"&&k.bild)?r`<div class="meldung fehler" role="status">
            <span>${e("keine_bilder",{name:$.name})}</span>
          </div>`:u}

      <div class="card filter">
        <label class="feld">
          ${e("filter_suche")}
          <input
            type="search"
            .value=${_.suche}
            @input=${k=>this._setzeFilter("suche",p(k))}
          />
        </label>
        <label class="feld">
          ${e("filter_lektion")}
          <select
            .value=${_.lektion}
            @change=${k=>this._setzeFilter("lektion",p(k))}
          >
            <option value="">${e("alle")}</option>
            ${t.lektionen.map(k=>r`<option value=${k} ?selected=${_.lektion===k}>
                  ${k}
                </option>`)}
            <option value=${D}>${e("ohne_lektion")}</option>
          </select>
        </label>
        <label class="feld">
          ${e("filter_quelle")}
          <select
            .value=${_.quelle}
            @change=${k=>this._setzeFilter("quelle",p(k))}
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
            .value=${_.geprueft}
            @change=${k=>this._setzeFilter("geprueft",p(k))}
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
            .value=${_.fehlerquote}
            @input=${k=>this._setzeFilter("fehlerquote",p(k))}
          />
        </label>
        <label class="feld">
          ${e("filter_von")}
          <input
            type="date"
            .value=${_.von}
            @change=${k=>this._setzeFilter("von",p(k))}
          />
        </label>
        <label class="feld">
          ${e("filter_bis")}
          <input
            type="date"
            .value=${_.bis}
            @change=${k=>this._setzeFilter("bis",p(k))}
          />
        </label>
        <label class="feld">
          ${e("filter_seite_von")}
          <input
            type="number"
            min="1"
            .value=${_.seiteVon}
            @input=${k=>this._setzeFilter("seiteVon",p(k))}
          />
        </label>
        <label class="feld">
          ${e("filter_seite_bis")}
          <input
            type="number"
            min="1"
            .value=${_.seiteBis}
            @input=${k=>this._setzeFilter("seiteBis",p(k))}
          />
        </label>
        <button
          @click=${()=>{this._filter={...Q},this._nurIds=null}}
        >
          ${e("filter_zuruecksetzen")}
        </button>
      </div>

      <div class="klein" style="margin: 0 4px 8px">
        ${e("anzahl",{n:i.length,gesamt:this._aufgaben.length})}
      </div>

      <div class="card tabelle-rahmen">
        <table>
          <thead>
            <tr>
              <th class="schmal">
                <input
                  type="checkbox"
                  aria-label=${e("alle_auswaehlen")}
                  .checked=${a}
                  @change=${k=>this._alleUmschalten(i,z(k))}
                />
              </th>
              <th>
                ${c?e("spalte_aufgabe"):d?e("spalte_frage"):y(g,l)}
              </th>
              <th>
                ${c?e("spalte_loesung"):d?e("spalte_musterantwort"):y(g,h)}
              </th>
              ${c?r`<th class="schmal" title=${e("schwierigkeit_hinweis")}>
                    ${e("spalte_schwierigkeit")}
                  </th>`:u}
              <th>${e("spalte_hinweis")}</th>
              <th class="schmal">${e("spalte_seite")}</th>
              <th>${e("spalte_lektion")}</th>
              <th class="schmal" title=${e("box_hinweis")}>${e("spalte_box")}</th>
              <th class="schmal">${e("spalte_fehler")}</th>
              <th class="schmal">${e("spalte_geprueft")}</th>
              <th class="schmal">${e("spalte_erstellt")}</th>
              <th class="schmal"></th>
            </tr>
          </thead>
          <tbody>
            ${this._entwurf&&this._entwurf.id===null?this._editorZeile(this._entwurf,l,h):u}
            ${i.map(k=>this._entwurf?.id===k.id?this._editorZeile(this._entwurf,l,h):this._zeile(k,l,h))}
          </tbody>
        </table>
        ${i.length===0&&!this._entwurf?r`<div class="leer">
              ${e(this._aufgaben.length?"keine_treffer":"keine_aufgaben")}
            </div>`:u}
      </div>
    `}_zeile(e,t,i){let s=this._t,a=this.hass?.language??"en",l=e.typ==="mathe"?e:null,h=e.typ==="sach"?e:null,g=(l?["mathe"]:h?["sach"]:[`${t}>${i}`,`${i}>${t}`]).map(c=>e.statistik[c]?.box??1).join(" \xB7 "),_=c=>e.typ!=="vokabel"?r``:r`
            ${e.frage[c]??""}
            ${e.alternativen[c]?.length?r`<div class="klein">${e.alternativen[c]?.join(" | ")}</div>`:u}
          `;return r`
      <tr class=${this._auswahl.has(e.id)?"gewaehlt":""}>
        <td class="schmal">
          <input
            type="checkbox"
            aria-label=${He(e,t,i)}
            .checked=${this._auswahl.has(e.id)}
            @change=${c=>this._umschalten(e.id,z(c))}
          />
        </td>
        ${l?this._matheZellen(l):h?this._sachZellen(h):r`
              <td data-label=${y(a,t)}>${_(t)}</td>
              <td data-label=${y(a,i)}>${_(i)}</td>
            `}
        <td data-label=${s("spalte_hinweis")}>${e.hinweis??""}</td>
        <td class="schmal" data-label=${s("spalte_seite")}>${e.seite??""}</td>
        <td data-label=${s("spalte_lektion")}>
          ${e.lektion??""}
          ${e.arbeiten.length?r`<span class="marke" title=${s("tab_arbeiten")}>
                ${e.arbeiten.length} ×
                <ha-icon
                  icon="mdi:calendar-star"
                  style="--mdc-icon-size: 12px"
                ></ha-icon>
              </span>`:u}
        </td>
        <td class="schmal" data-label=${s("spalte_box")} title=${s("box_hinweis")}>
          ${g}
        </td>
        <td class="schmal" data-label=${s("spalte_fehler")}>
          ${e.fehlerquote===null?r`<span class="klein">–</span>`:r`<span class="marke ${e.fehlerquote>=50?"warn":"ok"}">
                ${Math.round(e.fehlerquote)} %
              </span>`}
        </td>
        <td class="schmal" data-label=${s("spalte_geprueft")}>
          <input
            type="checkbox"
            aria-label=${s("spalte_geprueft")}
            .checked=${e.geprueft}
            @change=${c=>this._setzeGeprueft(e,z(c))}
          />
        </td>
        <td class="schmal klein" data-label=${s("spalte_erstellt")}>
          ${this._datum(e.erstellt)}
        </td>
        <td class="schmal">
          <button
            class="icon"
            title=${s("bearbeiten")}
            aria-label=${s("bearbeiten")}
            @click=${()=>this._bearbeite(e)}
          >
            <ha-icon icon="mdi:pencil"></ha-icon>
          </button>
          <button
            class="icon"
            title=${s("loeschen")}
            aria-label=${s("loeschen")}
            ?disabled=${this._beschaeftigt}
            @click=${()=>this._loesche([e.id])}
          >
            <ha-icon icon="mdi:delete"></ha-icon>
          </button>
        </td>
      </tr>
    `}_sachZellen(e){let t=this._t,i=e.quelle_bild?this._bildAdressen[e.quelle_bild]:void 0;return r`
      <td data-label=${t("spalte_frage")}>
        ${i?r`<button
              class="vorschaubild"
              style="float: right; margin-left: 8px; border: none; background: none"
              title=${t("quellseite_anzeigen")}
              aria-label=${t("quellseite_anzeigen")}
              @click=${()=>{this._grossbild=i,this._bildText=e.stelle?`${t("belegstelle")}: \u201E${e.stelle}\u201C`:"",this._dialogFehler="",this._dialog="bild"}}
            >
              <img class="vorschaubild" src=${i} alt="" loading="lazy" />
            </button>`:u}
        ${e.frage}
        <div class="klein">
          <span class="marke">${t(`form_${e.form}`)}</span>
          ${e.stelle&&!i?r`<span class="marke" title=${e.stelle}>
                <ha-icon
                  icon="mdi:format-quote-close"
                  style="--mdc-icon-size: 12px"
                ></ha-icon>
                ${t("belegstelle")}
              </span>`:u}
        </div>
      </td>
      <td data-label=${t("spalte_musterantwort")}>
        ${e.antwort}
        ${e.form==="auswahl"?r`<div class="klein">
              ${e.falsche_optionen.map(s=>r`<div>✗ ${s}</div>`)}
            </div>`:e.kernpunkte.length?r`<div class="klein">
                ${e.kernpunkte.map(s=>r`<div>• ${s}</div>`)}
              </div>`:u}
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
              ></ha-icon>`:u}
        ${e.aufgabe}
        <div class="klein">
          ${e.verifikation==="keine"?u:e.verifikation==="abweichung"?r`<span class="marke warn">
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
              </span>`:u}
        </div>
      </td>
      <td data-label=${t("spalte_loesung")}>
        ${e.loesung}
        ${e.alternativen.length?r`<div class="klein">${e.alternativen.join(" | ")}</div>`:u}
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
            </div>`:u}
      </td>
      <td
        class="schmal"
        data-label=${t("spalte_schwierigkeit")}
        title=${t("schwierigkeit_hinweis")}
      >
        ${e.schwierigkeit??r`<span class="klein">–</span>`}
      </td>
    `}_editorZeile(e,t,i){let s=this._t,a=this._fach?.typ==="mathe",l=this._fach?.typ==="sach",h=this.hass?.language??"en",g=(d,$,v=64)=>r`
      <textarea
        style="min-height: ${v}px"
        aria-label=${$}
        placeholder=${$}
        maxlength="500"
        .value=${e[d]}
        @input=${x=>this._setzeEntwurf(d,p(x))}
      ></textarea>
    `,_=(d,$,v="")=>r`
      <input
        type="text"
        aria-label=${$}
        placeholder=${v}
        maxlength="500"
        .value=${e[d]}
        @input=${x=>this._setzeEntwurf(d,p(x))}
        @keydown=${x=>{x.key==="Enter"&&this._speichereAufgabe()}}
      />
    `,c=`${s("spalte_alternativen")} (${s("alternativen_hinweis")})`;return r`
      <tr class="gewaehlt">
        <td class="schmal"></td>
        ${a?r`
              <td data-label=${s("spalte_aufgabe")}>
                ${_("a",s("spalte_aufgabe"))}
                <textarea
                  style="margin-top: 4px; min-height: 64px"
                  aria-label=${s("rechenweg")}
                  placeholder=${s("rechenweg")}
                  .value=${e.rechenweg}
                  @input=${d=>this._setzeEntwurf("rechenweg",p(d))}
                ></textarea>
              </td>
              <td data-label=${s("spalte_loesung")}>
                ${_("b",s("spalte_loesung"))}
                <div style="margin-top: 4px">${_("altB",c,c)}</div>
              </td>
              <td class="schmal" data-label=${s("spalte_schwierigkeit")}>
                <select
                  aria-label=${s("schwierigkeit")}
                  title=${s("schwierigkeit_hinweis")}
                  .value=${e.schwierigkeit}
                  @change=${d=>this._setzeEntwurf("schwierigkeit",p(d))}
                >
                  <option value="" ?selected=${e.schwierigkeit===""}>–</option>
                  ${["1","2","3","4","5"].map(d=>r`<option value=${d} ?selected=${e.schwierigkeit===d}>
                        ${d}
                      </option>`)}
                </select>
              </td>
            `:l?r`
                <td data-label=${s("spalte_frage")}>
                  ${g("a",s("spalte_frage"))}
                  <select
                    style="margin-top: 4px"
                    aria-label=${s("form")}
                    .value=${e.form}
                    @change=${d=>this._setzeEntwurf("form",p(d)==="auswahl"?"auswahl":"kurz")}
                  >
                    <option value="kurz" ?selected=${e.form==="kurz"}>
                      ${s("form_kurz")}
                    </option>
                    <option value="auswahl" ?selected=${e.form==="auswahl"}>
                      ${s("form_auswahl")}
                    </option>
                  </select>
                </td>
                <td data-label=${s("spalte_musterantwort")}>
                  ${g("b",s(e.form==="auswahl"?"richtige_antwort":"spalte_musterantwort"),e.form==="auswahl"?32:64)}
                  <div style="margin-top: 4px">
                    ${e.form==="auswahl"?g("falsche",s("falsche_optionen")):g("kernpunkte",s("kernpunkte"))}
                  </div>
                </td>
              `:r`
              <td data-label=${y(h,t)}>
                ${_("a",y(h,t))}
                <div style="margin-top: 4px">${_("altA",c,c)}</div>
              </td>
              <td data-label=${y(h,i)}>
                ${_("b",y(h,i))}
                <div style="margin-top: 4px">${_("altB",c,c)}</div>
              </td>
            `}
        <td data-label=${s("spalte_hinweis")}>
          ${_("hinweis",s("spalte_hinweis"))}
        </td>
        <td class="schmal" data-label=${s("spalte_seite")}>
          <input
            type="number"
            min="1"
            max="9999"
            style="width: 5em"
            aria-label=${s("spalte_seite")}
            .value=${e.seite}
            @input=${d=>this._setzeEntwurf("seite",p(d))}
          />
        </td>
        <td data-label=${s("spalte_lektion")}>
          ${this._lektionAuswahl(e.lektion,d=>this._setzeEntwurf("lektion",d),s("spalte_lektion"))}
        </td>
        <td class="schmal"></td>
        <td class="schmal"></td>
        <td class="schmal" data-label=${s("spalte_geprueft")}>
          <input
            type="checkbox"
            aria-label=${s("spalte_geprueft")}
            .checked=${e.geprueft}
            @change=${d=>this._setzeEntwurf("geprueft",z(d))}
          />
        </td>
        <td class="schmal"></td>
        <td class="schmal">
          <button
            class="icon"
            title=${s("speichern")}
            aria-label=${s("speichern")}
            ?disabled=${this._beschaeftigt}
            @click=${this._speichereAufgabe}
          >
            <ha-icon icon="mdi:check"></ha-icon>
          </button>
          <button
            class="icon"
            title=${s("abbrechen")}
            aria-label=${s("abbrechen")}
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
      ${i.length===0?r`<div class="card leer">${e("keine_arbeiten")}</div>`:i.map(s=>{let a=this._arbeitUmfang({lektionen:s.lektionen,ids:s.aufgaben_ids});return r`
              <div class="card arbeit">
                <div class="info">
                  <div class="titel">
                    ${s.thema}
                    <span class="marke">
                      ${e(s.art==="hue"?"art_hue":"art_arbeit")}
                    </span>
                    ${s.datum<t?r`<span class="marke warn">${e("vergangen")}</span>`:u}
                  </div>
                  <div class="klein">
                    ${this._datum(s.datum)} ·
                    ${a===null?e("arbeit_alle"):e("arbeit_umfang",{n:a})}
                    ${s.lektionen.length?r` · ${s.lektionen.join(", ")}`:u}
                    · ${s.abfragen_pro_tag} × / ${s.start_tage_vorher} d
                  </div>
                  ${s.simulation_um?r`<div class="klein">
                        <ha-icon
                          icon="mdi:calendar-clock"
                          style="--mdc-icon-size: 14px"
                        ></ha-icon>
                        ${e(s.simulation_geplant?"sim_plan_offen":"sim_plan_erledigt",{zeit:this._zeitpunkt(s.simulation_um),n:s.simulation_anzahl??10})}
                      </div>`:u}
                </div>
                <button
                  ?disabled=${s.simulierbar?.ausdruck===0}
                  title=${s.simulierbar?.ausdruck===0?e("sim_keine_aufgaben"):""}
                  @click=${()=>this._oeffneSimulation(s)}
                >
                  ${e(s.art==="hue"?"sim_knopf_hue":"sim_knopf_arbeit")}
                </button>
                <button @click=${()=>this._oeffneArbeit(s)}>
                  ${e("bearbeiten")}
                </button>
                <button class="gefahr" @click=${()=>this._loescheArbeit(s)}>
                  ${e("loeschen")}
                </button>
              </div>
            `})}
    `}_dialogInhalt(){if(!this._dialog)return u;let e;switch(this._dialog){case"generieren":e=this._generierenDialog();break;case"aufgabenart":e=this._aufgabenartDialog();break;case"bildaufgabe":e=this._bildaufgabeDialog();break;case"bild":e=r`
          <img class="grossbild" src=${this._grossbild} alt=${this._t("bild")} />
          ${this._bildText?r`<p style="margin: 12px 0 0">${this._bildText}</p>`:u}
          <div class="aktionen">
            <button class="primaer" @click=${this._schliesseDialog}>
              ${this._t("schliessen")}
            </button>
          </div>
        `;break;case"nachrechnen":e=this._nachrechnenDialog();break;case"seiten":e=this._seitenDialog();break;case"foto":e=this._fotoDialog();break;case"simulation":e=this._simulationDialog();break;case"import":e=this._importDialog();break;case"export":e=this._exportDialog();break;case"importJson":e=this._importJsonDialog();break;case"lektion":e=this._lektionDialog();break;default:e=this._arbeitDialog()}return r`
      <div
        class="overlay"
        @click=${t=>{t.target===t.currentTarget&&this._schliesseDialog()}}
      >
        <div
          class="dialog ${this._dialog==="foto"&&this._foto?.zeilen?"breit":""}"
          role="dialog"
          aria-modal="true"
        >
          ${e}
          ${this._dialogFehler?r`<div class="meldung fehler" role="alert" style="margin-top: 12px">
                <span>${this._dialogFehler}</span>
              </div>`:u}
        </div>
      </div>
    `}_simulationDialog(){let e=this._t,t=this._sim;if(!t)return r``;let i=t.arbeit.art==="hue",s=`${e(i?"sim_knopf_hue":"sim_knopf_arbeit")}: ${t.arbeit.thema}`;if(t.seiten)return r`
        <h2>${s}</h2>
        <p class="klein">${e("sim_blatt_hilfe",{n:t.anzahl})}</p>
        ${t.seiten.map((_,c)=>r`
            <img
              class="grossbild"
              style="max-height: 60vh; margin: 12px auto; border: 1px solid var(--lh-border)"
              src=${_}
              alt=${`${e("spalte_seite")} ${c+1}`}
            />
            <div class="aktionen" style="margin-top: 4px">
              <a
                class="knopf"
                href=${_}
                download=${`${i?"hue":"klassenarbeit"}-${c+1}.png`}
              >
                ${e("sim_herunterladen",{n:c+1})}
              </a>
            </div>
          `)}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${e("schliessen")}</button>
          <button class="primaer" @click=${this._druckeSimulation}>${e("sim_drucken")}</button>
        </div>
      `;let a=this._simVerfuegbar(t),l=Math.min(a,J),h=this._uebersicht?.kinder.find(_=>_.id===this._kindId),g=["ausdruck","messenger"];return r`
      <h2>${s}</h2>
      <p class="klein">${e("sim_hilfe")}</p>
      <div class="wahl">
        ${g.map(_=>r`
            <button
              class=${t.weg===_?"primaer":""}
              aria-pressed=${t.weg===_?"true":"false"}
              @click=${()=>{let c={...t,weg:_},d=Math.min(this._simVerfuegbar(c),J);this._sim={...c,anzahl:Math.max(1,Math.min(c.anzahl,d))}}}
            >
              <strong>${e(`sim_weg_${_}`)}</strong>
              <span class="klein">
                ${e(`sim_weg_${_}_hilfe`,{name:h?.name??""})}
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
          @input=${_=>{let c=Math.round(Number(p(_)))||1;this._sim={...t,anzahl:Math.max(1,Math.min(c,l))}}}
        />
        <span class="klein">${e("sim_verfuegbar",{n:a})}</span>
      </label>
      ${a===0?r`<div class="meldung fehler" role="status" style="margin-top: 12px">
            <span>${e("sim_keine_aufgaben")}</span>
          </div>`:u}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||a===0}
          @click=${this._simuliere}
        >
          ${e(t.weg==="messenger"?"sim_start_messenger":"sim_start_ausdruck")}
        </button>
      </div>
    `}_fotoDialog(){let e=this._t,t=this._foto,i=this._fach;if(!t||!i)return r``;let s=i.typ==="mathe",[a="",l=""]=i.sprachen,h=this.hass?.language??"en",g=t.zeilen;if(!g)return r`
        <h2>${e("foto_titel")}</h2>
        <p class="klein">${e(s?"foto_hilfe_mathe":"foto_hilfe")}</p>
        <label class="feld">
          ${e("seiten_waehlen",{n:S})} *
          <input
            type="file"
            multiple
            accept="image/png,image/jpeg,image/webp"
            aria-label=${e("seiten_waehlen",{n:S})}
            @change=${this._fotoGewaehlt}
          />
        </label>
        ${t.vorschauen.length?r`<div class="leiste" style="margin: 12px 0 0">
              ${t.vorschauen.map((d,$)=>r`<img
                    class="grossbild"
                    style="max-height: 140px; margin: 0"
                    src=${d}
                    alt=${`${e("spalte_seite")} ${$+1}`}
                  />`)}
            </div>`:u}
        ${this._beschaeftigt?r`<p class="klein" role="status">${e("seiten_laeuft")}</p>`:u}
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
      `;let _=g.filter(d=>d.an).length,c=(d,$,v,x)=>r`
      <input
        type="text"
        aria-label=${v}
        maxlength="500"
        .value=${x}
        @input=${I=>this._setzeFotoZeile(d,{[$]:p(I),geaendert:!0})}
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
                  .checked=${_===g.length}
                  @change=${d=>{let $=z(d);this._foto={...t,zeilen:g.map(v=>({...v,an:$}))}}}
                />
              </th>
              <th>${s?e("spalte_aufgabe"):y(h,a)}</th>
              <th>${s?e("spalte_loesung"):y(h,l)}</th>
              ${s?u:r`<th>${e("spalte_hinweis")}</th>`}
              <th class="schmal">${e("spalte_seite")}</th>
            </tr>
          </thead>
          <tbody>
            ${g.map((d,$)=>{let v=d.roh,x=!d.geaendert&&v.verifikation==="abweichung"&&v.vorschlag;return r`
                <tr class=${d.an?"gewaehlt":""}>
                  <td class="schmal">
                    <input
                      type="checkbox"
                      aria-label=${d.a}
                      .checked=${d.an}
                      @change=${I=>this._setzeFotoZeile($,{an:z(I)})}
                    />
                  </td>
                  <td>
                    ${c($,"a",s?e("spalte_aufgabe"):y(h,a),d.a)}
                    <div class="klein">
                      ${v.vorhanden?r`<span class="marke">${e("foto_vorhanden")}</span>`:u}
                      ${v.braucht_bild?r`<span class="marke warn">${e("foto_braucht_bild")}</span>`:u}
                    </div>
                  </td>
                  <td>
                    ${c($,"b",s?e("spalte_loesung"):y(h,l),d.b)}
                    ${s&&!v.braucht_bild?r`<div class="klein">
                          ${d.geaendert||v.verifikation==="keine"?r`<span class="marke">${e("foto_unbestaetigt")}</span>`:x?r`<span class="marke warn">
                                    ${e(v.vorschlag_durch==="ki"?"nachrechnen_ki":"nachrechnen_berechnet")}:
                                    ${v.vorschlag}
                                  </span>
                                  <button
                                    @click=${()=>this._setzeFotoZeile($,{b:v.vorschlag??d.b,roh:{...v,verifikation:v.vorschlag_durch==="ki"?"ki":"rechnerisch",vorschlag:null}})}
                                  >
                                    ${e("uebernehmen_loesung")}
                                  </button>`:r`<span class="marke ok">
                                  ${e(`verifikation_${v.verifikation??"ki"}`)}
                                </span>`}
                        </div>`:u}
                    ${!s&&!d.geaendert?r`<div class="klein">
                          ${Object.values(v.alternativen??{}).flat().join(" | ")}
                        </div>`:u}
                  </td>
                  ${s?u:r`<td>${c($,"hinweis",e("spalte_hinweis"),d.hinweis)}</td>`}
                  <td class="schmal">
                    <input
                      type="number"
                      min="1"
                      max="9999"
                      style="width: 5em"
                      aria-label=${e("spalte_seite")}
                      .value=${d.seite}
                      @input=${I=>this._setzeFotoZeile($,{seite:p(I)})}
                    />
                  </td>
                </tr>
              `})}
          </tbody>
        </table>
      </div>
      <label class="feld" style="margin-top: 12px">
        ${e("spalte_lektion")}
        ${this._lektionAuswahl(t.lektion,d=>{this._foto={...t,lektion:d}},e("spalte_lektion"))}
      </label>
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||!_}
          @click=${this._uebernimmFoto}
        >
          ${e("foto_uebernehmen",{n:_})}
        </button>
      </div>
    `}_seitenDialog(){let e=this._t,t=this._seiten;if(!t)return r``;let i=(a,l)=>{this._seiten={...t,[a]:l}},s=["gemischt","kurz","auswahl"];return r`
      <h2>${e("seiten_titel")}</h2>
      <p class="klein">${e("seiten_hilfe")}</p>
      <label class="feld">
        ${e("seiten_waehlen",{n:S})} *
        <input
          type="file"
          multiple
          accept="image/png,image/jpeg,image/webp"
          aria-label=${e("seiten_waehlen",{n:S})}
          @change=${this._seitenGewaehlt}
        />
      </label>
      ${t.vorschauen.length?r`<div class="leiste" style="margin: 12px 0 0">
            ${t.vorschauen.map((a,l)=>r`<img
                  class="grossbild"
                  style="max-height: 140px; margin: 0"
                  src=${a}
                  alt=${`${e("spalte_seite")} ${l+1}`}
                />`)}
          </div>`:u}
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(t.lektion,a=>i("lektion",a),e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("seiten_anzahl")}
          <input
            type="number"
            min="1"
            max="15"
            .value=${String(t.anzahl)}
            @input=${a=>i("anzahl",Math.min(Math.max(Math.round(Number(p(a)))||1,1),15))}
          />
        </label>
        <label class="feld">
          ${e("form")}
          <select
            .value=${t.form}
            @change=${a=>i("form",s.find(l=>l===p(a))??"gemischt")}
          >
            ${s.map(a=>r`<option value=${a} ?selected=${t.form===a}>
                  ${e(`form_${a}`)}
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
          @input=${a=>i("schwerpunkt",p(a))}
        />
      </label>
      ${this._beschaeftigt?r`<p class="klein" role="status">${e("seiten_laeuft")}</p>`:u}
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
    `}_bildaufgabeDialog(){let e=this._t,t=this._bildEntwurf;if(!t)return r``;let i=this._uebersicht?.kinder.find(a=>a.id===this._kindId),s=`${e("spalte_alternativen")} (${e("alternativen_hinweis")})`;return r`
      <h2>${e("bildaufgabe_titel")}</h2>
      ${i&&!i.bilder?r`<div class="meldung fehler" role="status" style="margin-bottom: 12px">
            <span>${e("keine_bilder",{name:i.name})}</span>
          </div>`:u}
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
          />`:u}
      <label class="feld" style="margin-top: 12px">
        ${e("einleitung")}
        <textarea
          maxlength="300"
          style="min-height: 56px"
          placeholder=${e("einleitung_hilfe")}
          .value=${t.einleitung}
          @input=${a=>this._setzeBild("einleitung",p(a))}
        ></textarea>
      </label>
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(t.lektion,a=>this._setzeBild("lektion",a),e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("spalte_seite")}
          <input
            type="number"
            min="1"
            max="9999"
            .value=${t.seite}
            @input=${a=>this._setzeBild("seite",p(a))}
          />
        </label>
      </div>
      <fieldset>
        <legend>${e("teilaufgaben")}</legend>
        <p class="klein" style="margin-top: 0">${e("teilaufgaben_hilfe")}</p>
        ${t.teile.map((a,l)=>r`
            <div class="teil">
              <label class="feld">
                ${e("teilaufgabe",{n:l+1})}
                <input
                  type="text"
                  maxlength="400"
                  placeholder="a) …"
                  .value=${a.aufgabe}
                  @input=${h=>this._setzeTeil(l,"aufgabe",p(h))}
                />
              </label>
              <label class="feld">
                ${e("spalte_loesung")}
                <input
                  type="text"
                  maxlength="100"
                  .value=${a.loesung}
                  @input=${h=>this._setzeTeil(l,"loesung",p(h))}
                />
              </label>
              <label class="feld">
                ${e("spalte_alternativen")}
                <input
                  type="text"
                  maxlength="300"
                  placeholder=${s}
                  .value=${a.alternativen}
                  @input=${h=>this._setzeTeil(l,"alternativen",p(h))}
                />
              </label>
              <button
                class="icon"
                title=${e("teilaufgabe_entfernen")}
                aria-label=${e("teilaufgabe_entfernen")}
                ?disabled=${t.teile.length<2}
                @click=${()=>this._setzeBild("teile",t.teile.filter((h,g)=>g!==l))}
              >
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            </div>
          `)}
        <button
          ?disabled=${t.teile.length>=8}
          @click=${()=>this._setzeBild("teile",[...t.teile,{...qe}])}
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
                  </button>`:u}
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
    `:r``}_generierenDialog(){let e=this._t,t=this._generieren;if(!t)return r``;let i=(a,l)=>{this._generieren={...t,[a]:l}},s=this._auswahl.size;return r`
      <h2>${e("generieren_titel")}</h2>
      <p class="klein">${e("generieren_hilfe")}</p>
      <div class="raster">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(t.lektion,a=>i("lektion",a),e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("generieren_anzahl")}
          <input
            type="number"
            min="1"
            max="20"
            .value=${String(t.anzahl)}
            @input=${a=>i("anzahl",Math.min(20,Math.max(1,Number(p(a))||1)))}
          />
        </label>
        <label class="feld">
          ${e("schwierigkeit")}
          <select
            title=${e("schwierigkeit_hinweis")}
            .value=${t.schwierigkeit}
            @change=${a=>i("schwierigkeit",p(a))}
          >
            <option value="" ?selected=${t.schwierigkeit===""}>
              ${e("schwierigkeit_beliebig")}
            </option>
            ${["1","2","3","4","5"].map(a=>r`<option value=${a} ?selected=${t.schwierigkeit===a}>
                  ${a}
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
          @input=${a=>i("beschreibung",p(a))}
        ></textarea>
      </label>
      <p class="klein">
        ${s?e("generieren_beispiele_auswahl",{n:s}):e("generieren_beispiele_thema")}
      </p>
      ${this._beschaeftigt?r`<p class="klein" role="status">${e("generieren_laeuft")}</p>`:u}
      <div class="aktionen">
        <button ?disabled=${this._beschaeftigt} @click=${this._schliesseDialog}>
          ${e("abbrechen")}
        </button>
        <button class="primaer" ?disabled=${this._beschaeftigt} @click=${this._generiere}>
          ${e("generieren_start")}
        </button>
      </div>
    `}_importDialog(){let e=this._t,[t="",i=""]=this._fach?.sprachen??[],s=this.hass?.language??"en",a=this._vorschau,l=a?.zeilen.filter(g=>!g.vorhanden).length??0,h=this._fach?.typ==="mathe";return r`
      <h2>${e(h?"import_titel_mathe":"import_titel")}</h2>
      <p class="klein">
        ${h?e("import_hilfe_mathe"):e("import_hilfe",{a:y(s,t),b:y(s,i)})}
      </p>
      <label class="feld">
        ${e("import_inhalt")}
        <textarea
          .value=${this._importText}
          placeholder=${h?`7 \xB7 8; 56
3/4 + 1/8; 7/8 | 0,875; Br\xFCche`:`Hund; dog|hound; Nomen
gehen; to go`}
          @input=${g=>{this._importText=p(g),this._vorschau=null}}
        ></textarea>
      </label>
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${e("spalte_lektion")}
          ${this._lektionAuswahl(this._importLektion,g=>{this._importLektion=g},e("spalte_lektion"))}
        </label>
        <label class="feld">
          ${e("import_trennzeichen")}
          <input
            type="text"
            maxlength="5"
            .value=${this._importTrenner}
            @input=${g=>{this._importTrenner=p(g),this._vorschau=null}}
          />
        </label>
      </div>
      <label class="feld zeile">
        <input
          type="checkbox"
          .checked=${this._importGeprueft}
          @change=${g=>{this._importGeprueft=z(g)}}
        />
        ${e("import_geprueft")}
      </label>
      ${a?r`
            <div class="liste" style="margin-top: 12px">
              ${a.zeilen.map(g=>r`
                  <label>
                    <span style="flex: 1">
                      ${g.frage?`${g.frage[t]??""} \u2192 ${g.frage[i]??""}`:`${g.aufgabe??""} \u2192 ${g.loesung??""}`}
                      ${g.hinweis?r`<span class="klein"> (${g.hinweis})</span>`:u}
                    </span>
                    <span class="marke ${g.vorhanden?"":"ok"}">
                      ${e(g.vorhanden?"vorschau_vorhanden":"vorschau_neu")}
                    </span>
                  </label>
                `)}
            </div>
            ${a.fehlerzeilen.length?r`<p class="klein" style="color: var(--lh-error)">
                  ${e("vorschau_fehler",{zeilen:a.fehlerzeilen.join(", ")})}
                </p>`:u}
          `:u}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button ?disabled=${!this._importText.trim()} @click=${this._importVorschau}>
          ${e("vorschau")}
        </button>
        <button
          class="primaer"
          ?disabled=${!a||l===0||this._beschaeftigt}
          @click=${this._importUebernehmen}
        >
          ${e("uebernehmen")} ${a?`(${l})`:""}
        </button>
      </div>
    `}_lektionDialog(){let e=this._t,t=this._fach?.lektionen??[],i=s=>this._aufgaben.filter(a=>a.lektion===s).length;return r`
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
            @input=${s=>{this._lektionName=p(s)}}
            @keydown=${s=>{s.key==="Enter"&&this._lektionAnlegen()}}
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
            ${t.map(s=>{let a=i(s);return r`
                <div class="eintrag">
                  <span style="flex: 1">${s}</span>
                  <span class="klein">${e("lektion_anzahl",{n:a})}</span>
                  <button
                    class="icon"
                    title=${a>0?e("lektion_loeschen_hinweis"):e("loeschen")}
                    aria-label=${`${e("loeschen")}: ${s}`}
                    ?disabled=${a>0}
                    @click=${()=>this._lektionLoeschen(s)}
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
    `}_statistikSchalter(){return r`
      <label class="feld zeile">
        <input
          type="checkbox"
          .checked=${this._mitStatistik}
          @change=${e=>{this._mitStatistik=z(e)}}
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
          @change=${s=>{this._jsonLektion=p(s)}}
        >
          <option value="" ?selected=${this._jsonLektion===""}>
            ${e("import_json_aus_datei")}
          </option>
          ${(this._fach?.lektionen??[]).map(s=>r`<option value=${s} ?selected=${s===this._jsonLektion}>
                ${s}
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
    `}_fachWahl(){let e=this._t,t=this.hass?.language??"en",i=this._neuesFach,s=this._faecherDesKindes,a=l=>{this._neuesFach&&(this._neuesFach={...this._neuesFach,...l})};return r`
      ${s.length?r`<div class="zeile" style="align-items: end; margin-bottom: 12px">
            <label class="feld" style="flex: 1">
              ${e("arbeit_fach")}
              <select
                .value=${this._fachId}
                @change=${l=>this._wechsleFachImDialog(p(l))}
              >
                ${s.map(l=>r`<option value=${l.id} ?selected=${l.id===this._fachId}>
                      ${l.name}
                    </option>`)}
              </select>
            </label>
            <button
              title=${e("fach_neu")}
              aria-label=${e("fach_neu")}
              ?disabled=${i!==null}
              @click=${()=>{this._neuesFach={...Ke}}}
            >
              + ${e("fach_neu")}
            </button>
          </div>`:u}
      ${i?r`<fieldset style="margin-bottom: 12px">
            <legend>${e("fach_neu_titel")}</legend>
            <div class="raster">
              <label class="feld">
                ${e("fach_neu_art")}
                <select
                  .value=${i.typ}
                  @change=${l=>a({typ:p(l)})}
                >
                  ${ft.map(l=>r`<option value=${l} ?selected=${l===i.typ}>
                        ${e(`fachart_${l}`)}
                      </option>`)}
                </select>
              </label>
              ${i.typ==="fremdsprache"?r`<label class="feld">
                    ${e("fach_neu_sprache")}
                    <select
                      .value=${i.sprache}
                      @change=${l=>a({sprache:p(l)})}
                    >
                      ${pt.map(l=>r`<option value=${l} ?selected=${l===i.sprache}>
                            ${y(t,l)}
                          </option>`)}
                    </select>
                  </label>`:u}
              <label class="feld">
                ${e(i.typ==="sach"?"fach_neu_name":"fach_neu_name_optional")}
                <input
                  type="text"
                  maxlength="60"
                  .value=${i.name}
                  @input=${l=>a({name:p(l)})}
                />
              </label>
            </div>
            <div class="zeile" style="margin-top: 8px">
              <button
                class="primaer"
                ?disabled=${this._beschaeftigt||i.typ==="sach"&&!i.name.trim()}
                @click=${this._legeFachAn}
              >
                ${e("fach_neu_anlegen")}
              </button>
              ${s.length?r`<button
                    @click=${()=>{this._neuesFach=null}}
                  >
                    ${e("abbrechen")}
                  </button>`:u}
            </div>
          </fieldset>`:u}
    `}_arbeitDialog(){let e=this._t,t=this._arbeit,i=this._fach;if(!t)return r``;if(!i)return r`
        <h2>${e("arbeit_titel_neu")}</h2>
        <p class="klein">${e("fach_neu_fehlt")}</p>
        ${this._fachWahl()}
        ${this._dialogFehler?r`<div class="meldung fehler" role="alert">${this._dialogFehler}</div>`:u}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        </div>
      `;let[s="",a=""]=i.sprachen,l=t.modus==="alle"?this._aufgaben.length:this._arbeitUmfang(t)??this._aufgaben.length,h=(c,d,$)=>r`
      <label class="feld">
        ${d}
        <input
          type="number"
          min="1"
          max=${$}
          .value=${String(t[c])}
          @input=${v=>this._setzeArbeit(c,Number(p(v))||1)}
        />
      </label>
    `,g=!t.thema.trim(),_=g&&!t.datum?"arbeit_fehlt_beides":g?"arbeit_fehlt_thema":t.datum?null:"arbeit_fehlt_datum";return r`
      <h2>${e(t.id?"arbeit_titel_bearbeiten":"arbeit_titel_neu")}</h2>
      ${t.kalenderUid?this._fachWahl():u}
      <div class="raster">
        <label class="feld">
          ${e("thema")} *
          <input
            type="text"
            required
            maxlength="200"
            .value=${t.thema}
            @input=${c=>this._setzeArbeit("thema",p(c))}
          />
        </label>
        <label class="feld">
          ${e("datum")} *
          <input
            type="date"
            required
            .value=${t.datum}
            @change=${c=>this._setzeArbeit("datum",p(c))}
          />
        </label>
        <label class="feld">
          ${e("art")}
          <select
            .value=${t.art}
            @change=${c=>this._setzeArbeit("art",p(c)==="hue"?"hue":"arbeit")}
          >
            <option value="arbeit" ?selected=${t.art==="arbeit"}>
              ${e("art_arbeit")}
            </option>
            <option value="hue" ?selected=${t.art==="hue"}>
              ${e("art_hue")}
            </option>
          </select>
        </label>
        ${h("abfragen",e("abfragen_pro_tag"),24)}
        ${h("start",e("start_tage_vorher"),90)}
        <label class="feld">
          ${e("antwortfrist")}
          <input
            type="number"
            min="1"
            max="1440"
            placeholder=${e("antwortfrist_leer")}
            .value=${t.frist===null?"":String(t.frist)}
            @input=${c=>{let d=Math.round(Number(p(c)));this._setzeArbeit("frist",d>=1?Math.min(d,1440):null)}}
          />
          <span class="klein">${e("antwortfrist_hinweis")}</span>
        </label>
      </div>
      <label class="feld zeile" style="margin-bottom: 12px">
        <input
          type="checkbox"
          .checked=${t.intensivierung}
          @change=${c=>this._setzeArbeit("intensivierung",z(c))}
        />
        ${e("intensivierung")}
      </label>

      <fieldset>
        <legend>${e("sim_plan")}</legend>
        <label class="feld zeile">
          <input
            type="checkbox"
            .checked=${t.simAktiv}
            @change=${c=>this._setzeArbeit("simAktiv",z(c))}
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
                    @change=${c=>this._setzeArbeit("simUm",p(c))}
                  />
                </label>
                <label class="feld">
                  ${e("sim_anzahl")}
                  <input
                    type="number"
                    min="1"
                    max=${J}
                    .value=${String(t.simAnzahl)}
                    @input=${c=>this._setzeArbeit("simAnzahl",Math.max(1,Math.min(Math.round(Number(p(c)))||1,J)))}
                  />
                </label>
              </div>`:u}
      </fieldset>

      <fieldset>
        <legend>
          ${e("aufgaben_der_arbeit")} – ${e("arbeit_umfang",{n:l})}
        </legend>
        <div class="chips" style="margin-bottom: 10px">
          ${["alle","auswahl"].map(c=>r`
              <label class="feld zeile">
                <input
                  type="radio"
                  name="modus"
                  .checked=${t.modus===c}
                  @change=${()=>this._setzeArbeit("modus",c)}
                />
                ${e(c==="alle"?"auswahl_alle":"auswahl_gezielt")}
              </label>
            `)}
        </div>
        ${t.modus==="auswahl"?r`
              ${i.lektionen.length?r`
                    <div class="klein">${e("schnell_lektionen")}</div>
                    <div class="chips" style="margin: 6px 0 12px">
                      ${i.lektionen.map(c=>r`
                          <label class="feld zeile">
                            <input
                              type="checkbox"
                              .checked=${t.lektionen.has(c)}
                              @change=${d=>this._arbeitMenge("lektionen",c,z(d))}
                            />
                            ${c}
                          </label>
                        `)}
                    </div>
                  `:u}
              <div class="leiste">
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${e("schnell_seit")}
                  <input
                    type="date"
                    .value=${t.seit}
                    @change=${c=>this._setzeArbeit("seit",p(c))}
                  />
                </label>
                <button ?disabled=${!t.seit} @click=${this._arbeitSeit}>
                  ${e("hinzufuegen")}
                </button>
              </div>
              <div class="leiste">
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${e("schnell_seiten")}
                  <input
                    type="number"
                    min="1"
                    .value=${t.seiteVon}
                    @input=${c=>this._setzeArbeit("seiteVon",p(c))}
                  />
                </label>
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${e("schnell_seiten_bis")}
                  <input
                    type="number"
                    min="1"
                    .value=${t.seiteBis}
                    @input=${c=>this._setzeArbeit("seiteBis",p(c))}
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
                ${this._aufgaben.map(c=>{let d=c.lektion!==null&&t.lektionen.has(c.lektion);return r`
                    <label>
                      <input
                        type="checkbox"
                        .checked=${d||t.ids.has(c.id)}
                        ?disabled=${d}
                        @change=${$=>this._arbeitMenge("ids",c.id,z($))}
                      />
                      <span style="flex: 1">
                        ${He(c,s,a)}
                      </span>
                      <span class="klein">${c.lektion??""}</span>
                    </label>
                  `})}
              </div>
            `:u}
      </fieldset>
      <div class="aktionen">
        ${_?r`<span class="klein" role="status" style="margin-right: auto">
              ${e(_)}
            </span>`:u}
        <button @click=${this._schliesseDialog}>${e("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt||_!==null}
          @click=${this._speichereArbeit}
        >
          ${e("speichern")}
        </button>
      </div>
    `}};f([F({attribute:!1})],m.prototype,"hass",2),f([F({type:Boolean,reflect:!0})],m.prototype,"narrow",2),f([b()],m.prototype,"_uebersicht",2),f([b()],m.prototype,"_kindId",2),f([b()],m.prototype,"_fachId",2),f([b()],m.prototype,"_aufgaben",2),f([b()],m.prototype,"_tab",2),f([b()],m.prototype,"_filter",2),f([b()],m.prototype,"_auswahl",2),f([b()],m.prototype,"_entwurf",2),f([b()],m.prototype,"_dialog",2),f([b()],m.prototype,"_generieren",2),f([b()],m.prototype,"_bildEntwurf",2),f([b()],m.prototype,"_bildAdressen",2),f([b()],m.prototype,"_grossbild",2),f([b()],m.prototype,"_bildText",2),f([b()],m.prototype,"_seiten",2),f([b()],m.prototype,"_foto",2),f([b()],m.prototype,"_sim",2),f([b()],m.prototype,"_veraltet",2),f([b()],m.prototype,"_nachgerechnet",2),f([b()],m.prototype,"_nurIds",2),f([b()],m.prototype,"_meldung",2),f([b()],m.prototype,"_laedt",2),f([b()],m.prototype,"_beschaeftigt",2),f([b()],m.prototype,"_importText",2),f([b()],m.prototype,"_importLektion",2),f([b()],m.prototype,"_importTrenner",2),f([b()],m.prototype,"_importGeprueft",2),f([b()],m.prototype,"_vorschau",2),f([b()],m.prototype,"_mitStatistik",2),f([b()],m.prototype,"_jsonDaten",2),f([b()],m.prototype,"_arbeit",2),f([b()],m.prototype,"_neuesFach",2),f([b()],m.prototype,"_dialogFehler",2),f([b()],m.prototype,"_lektionName",2),f([b()],m.prototype,"_jsonLektion",2);customElements.get("learnbuddy-panel")||customElements.define("learnbuddy-panel",m);export{m as LearnBuddyPanel};
