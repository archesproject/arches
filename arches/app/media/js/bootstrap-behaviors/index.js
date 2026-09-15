import $ from 'jquery';

import * as collapse from './collapse.js';
import * as dropdown from './dropdown.js';
import * as modal from './modal.js';
import * as tab from './tab.js';

/**
 * Dependency-free replacements for the Bootstrap 3 plugins arches used.
 *
 * Bootstrap 3's stylesheet is vendored at
 * `arches/app/media/css/vendor/bootstrap-3.4.1.css`; its JavaScript is not, because
 * both of Bootstrap 3's unfixable advisories — GHSA-vxmc-5x29-h64v and
 * GHSA-q58r-hwc8-rm9j — live there. Dropping the package removes the advisories; these
 * modules keep the legacy screens working until they move to PrimeVue, at which point
 * this directory and the vendored stylesheet both go away.
 *
 * Only four behaviours were actually in use, measured across the templates:
 *
 *     modal      29 jQuery calls (all RDM) + 33 data-dismiss
 *     tab        16 triggers
 *     dropdown   12 triggers + 1 jQuery call
 *     collapse    5 triggers
 *
 * Tooltips are not here: arches has its own CSS-only `[data-tooltip]` implementation,
 * which those 29 sites now use instead. Popover was never used at all — notable,
 * because it is one of the two components the advisories concern.
 *
 * The `$.fn.*` shims below exist so the existing call sites need no edit. They are the
 * only reason jQuery is imported; nothing else here depends on it.
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
 * Bootstrap 3 exposed each plugin's class as `$.fn.<plugin>.Constructor`, and legacy
 * code assigns to its prototype: `rdm.js` does
 * `$.fn.modal.Constructor.prototype.enforceFocus = function () {}` at startup. Against
 * a bare function that throws, and because it runs inside RDM's `initialize`, it takes
 * every RDM click handler down with it — the modals then look inert with no error at
 * the point of failure.
 *
 * These stubs give those assignments somewhere harmless to land. Nothing reads them:
 * focus trapping is deliberately not implemented, which is what that override wanted.
 */
function withConstructorStub(fn) {
    fn.Constructor = function () {};
    fn.Constructor.prototype = {};
    return fn;
}

function applyToEach(collection, actions, action, options) {
    return collection.each(function () {
        const handler = actions[action];
        if (handler) {
            handler(this, options);
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

/**
 * Bootstrap 3's tooltip and popover plugins are gone. `.tooltip()` is still called in a
 * few places — `page-view.js` initialises every `[data-toggle="tooltip"]` on load — so
 * these stay as no-ops rather than throwing. The CSS-only tooltip needs no
 * initialisation.
 */
$.fn.tooltip = withConstructorStub(function () {
    return this;
});

$.fn.popover = withConstructorStub(function () {
    return this;
});

install();

export { collapse, dropdown, modal, tab };
