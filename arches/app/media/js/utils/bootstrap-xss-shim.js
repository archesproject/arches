/**
 * Bootstrap 3.4.1 XSS mitigation shim.
 *
 * Patches two known vulnerabilities:
 * - SNYK-JS-BOOTSTRAP-10176066: XSS via tooltip/popover title (html option)
 * - SNYK-JS-BOOTSTRAP-7444617: XSS via button data-loading-text
 *
 * This module is loaded instead of bootstrap.min.js via the webpack alias in
 * package.json nodeModulesPaths. It imports the real bootstrap, then
 * monkey-patches the vulnerable prototype methods.
 */

import 'bootstrap-original';
import $ from 'jquery';

var Tooltip = $.fn.tooltip.Constructor;
var Popover = $.fn.popover.Constructor;
var Button = $.fn.button.Constructor;

// --- Tooltip XSS fix (SNYK-JS-BOOTSTRAP-10176066) ---
// The built-in sanitizeHtml has known bypasses. Override setContent to always
// use .text() for the title, preventing any HTML injection regardless of the
// `html` option.
var originalTooltipSetContent = Tooltip.prototype.setContent;
Tooltip.prototype.setContent = function () {
    var $tip = this.tip();
    var title = this.getTitle();

    // Always insert as text, never as raw HTML
    $tip.find('.tooltip-inner').text(title);
    $tip.removeClass('fade in top bottom left right');
};

// --- Popover XSS fix (SNYK-JS-BOOTSTRAP-10176066) ---
// Same approach: force text-only rendering for title and content.
Popover.prototype.setContent = function () {
    var $tip = this.tip();
    var title = this.getTitle();
    var content = this.getContent();

    $tip.find('.popover-title').text(title);

    if (typeof content === 'function') {
        content = content.call(this.$element[0]);
    }
    if (typeof content === 'string') {
        $tip.find('.popover-content').text(content);
    } else {
        $tip.find('.popover-content').children().detach().end().append(content);
    }

    $tip.removeClass('fade top bottom left right in');
};

// --- Button XSS fix (SNYK-JS-BOOTSTRAP-7444617) ---
// Button.prototype.setState uses $el.html(data[state]) for non-input elements,
// allowing XSS via data-loading-text or similar data attributes.
// Override to always use .text() for non-input elements.
Button.prototype.setState = function (state) {
    var d = 'disabled';
    var $el = this.$element;
    var isInput = $el.is('input');
    var data = $el.data();

    state += 'Text';

    if (data.resetText == null) {
        $el.data('resetText', isInput ? $el.val() : $el.text());
    }

    setTimeout($.proxy(function () {
        var value = data[state] == null ? this.options[state] : data[state];

        if (isInput) {
            $el.val(value);
        } else {
            $el.text(value);
        }

        if (state == 'loadingText') {
            this.isLoading = true;
            $el.addClass(d).attr(d, d).prop(d, true);
        } else if (this.isLoading) {
            this.isLoading = false;
            $el.removeClass(d).removeAttr(d).prop(d, false);
        }
    }, this), 0);
};
