﻿!function(t){var e={};function i(n){if(e[n])return e[n].exports;var o=e[n]={i:n,l:!1,exports:{}};return t[n].call(o.exports,o,o.exports,i),o.l=!0,o.exports}i.m=t,i.c=e,i.d=function(t,e,n){i.o(t,e)||Object.defineProperty(t,e,{enumerable:!0,get:n})},i.r=function(t){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(t,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(t,"__esModule",{value:!0})},i.t=function(t,e){if(1&e&&(t=i(t)),8&e)return t;if(4&e&&"object"==typeof t&&t&&t.__esModule)return t;var n=Object.create(null);if(i.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:t}),2&e&&"string"!=typeof t)for(var o in t)i.d(n,o,function(e){return t[e]}.bind(null,o));return n},i.n=function(t){var e=t&&t.__esModule?function(){return t.default}:function(){return t};return i.d(e,"a",e),e},i.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},i.p="/js/cmodules/",i(i.s=224)}({224:function(t,e,i){t.exports=i("CIIY")},CIIY:function(t,e,i){"use strict";i.r(e);var n=new class{constructor(){this.isInited=!1,this.menuEle=null,this.handleUpdateRequest=this.handleUpdateRequest.bind(this),this.handleScroll=this.handleScroll.bind(this)}init(){if(this.isInited)return!1;this.menuEle=ge("side_bar"),this.menuEle?(this.lastScrollTop=window.scrollGetY(),this.firstScrollUp=!1,this.firstScrollDown=!1,this.resetState()):this._noMenu=!0}handleUpdateRequest(){var t=arguments.length>0&&void 0!==arguments[0]&&arguments[0];this._noMenu||(t?(this.setPositionTop(0),this.setState("STATE_STICKY_BOTTOM")):this.handleScroll())}resetState(){this.setPositionTop(0),this.setState(window.scrollGetY()>10?"STATE_STICKY_TOP":"STATE_STICKY_BOTTOM")}setState(t){this.currentState!==t&&(this.currentState=t,"STATE_STICKY_TOP"===t?addClass(this.menuEle,"sticky_top"):"STATE_STICKY_BOTTOM"===t&&removeClass(this.menuEle,"sticky_top"))}setPositionTop(t){t>=0&&this.menuEle&&this.menuEle.style.setProperty("top",t+"px")}handleScrollDown(t){this.firstScrollDown||("STATE_STICKY_TOP"===this.currentState&&this.setPositionTop(t),this.setState("STATE_STICKY_BOTTOM")),this.firstScrollDown=!0,this.firstScrollUp=!1}handleScrollUp(t){this.firstScrollUp&&"STATE_STICKY_BOTTOM"===this.currentState&&this.menuEle.getBoundingClientRect().bottom<0&&this.setPositionTop(t-this.menuEle.clientHeight),"STATE_STICKY_TOP"!==this.currentState&&this.menuEle.getBoundingClientRect().top>=0&&(this.setState("STATE_STICKY_TOP"),this.setPositionTop(0)),this.firstScrollUp=!0,this.firstScrollDown=!1}handleScroll(){var t=window.scrollGetY();Boolean(this.lastScrollTop)&&(t>this.lastScrollTop?this.handleScrollDown(t):this.handleScrollUp(t)),this.lastScrollTop=t}};window.initPageLayoutUI=window.initPageLayoutUI||function(){n.init(),window.__leftMenu=n};try{stManager.done(jsc("web/page_layout.js"))}catch(t){console.log(t.message)}}});