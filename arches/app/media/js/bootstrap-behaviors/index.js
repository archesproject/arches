import $ from 'jquery';

import * as collapse from './collapse.js';
import * as dropdown from './dropdown.js';
import * as modal from './modal.js';
import * as tab from './tab.js';

/**
 * Dependency-free replacements for the four Bootstrap 3 plugins arches used. Bootstrap
 * 3's unfixable advisories (GHSA-vxmc-5x29-h64v, GHSA-q58r-hwc8-rm9j) are both in its
 * JavaScript, so only its stylesheet is vendored, at css/vendor/bootstrap-3.4.1.css.
 * Both go away once the legacy screens move to PrimeVue.
 *
 * Tooltips are not here: they are the CSS-only `[data-tooltip]` rule in
 * css/components/_tooltip.scss.
 *
 * The `$.fn.*` shims below keep the existing jQuery call sites working unchanged, and
 * are the only reason jQuery is imported.
 */

const installed = new WeakSet();

export function install(root = document) {
    if (installed.has(root)) {
        return;
    }
    installed.add(root);

    collapse.install(root);
    dropdown.install(root);
    modal.install(root);
    tab.install(root);
}

/**
 * `rdm.js` assigns to `$.fn.modal.Constructor.prototype` at startup, which would throw
 * against a bare function and take every RDM click handler down with it. Nothing reads
 * these stubs; they only give that assignment somewhere harmless to land.
 */
function withConstructorStub(fn) {
    fn.Constructor = function () {};
    fn.Constructor.prototype = {};
    return fn;
}

function applyToEach(collection, actions, action) {
    return collection.each(function () {
        const handler = actions[action];
        if (handler) {
            handler(this);
        }
    });
}

$.fn.modal = withConstructorStub(function (action) {
    return applyToEach(this, {
        show: modal.show,
        hide: modal.hide,
        toggle: modal.toggle,
    }, action);
});

$.fn.dropdown = withConstructorStub(function (action) {
    return applyToEach(this, {
        toggle: dropdown.toggle,
        hide: () => dropdown.hideAll(),
    }, action);
});

$.fn.collapse = withConstructorStub(function (action) {
    return applyToEach(this, {
        show: collapse.show,
        hide: collapse.hide,
        toggle: collapse.toggle,
    }, action);
});

$.fn.tab = withConstructorStub(function (action) {
    return applyToEach(this, { show: tab.show }, action);
});

// No-ops rather than throwing, for projects still calling these. The CSS-only tooltip
// needs no initialisation, and popover has no replacement.
$.fn.tooltip = withConstructorStub(function () {
    return this;
});

$.fn.popover = withConstructorStub(function () {
    return this;
});

install();

export { collapse, dropdown, modal, tab };
