import * as bootstrap from 'bootstrap-bundle';
import $ from 'jquery';

$.fn.modal = function (action) {
    return this.each(function () {
        var instance = bootstrap.Modal.getOrCreateInstance(this);
        if (action === 'show') {
            instance.show();
        } else if (action === 'hide') {
            instance.hide();
        } else if (action === 'toggle') {
            instance.toggle();
        }
    });
};

$.fn.tooltip = function (action) {
    return this.each(function () {
        if (action === 'destroy' || action === 'dispose') {
            var existing = bootstrap.Tooltip.getInstance(this);
            if (existing) { existing.dispose(); }
        } else if (action === 'show') {
            bootstrap.Tooltip.getOrCreateInstance(this).show();
        } else if (action === 'hide') {
            bootstrap.Tooltip.getOrCreateInstance(this).hide();
        } else {
            new bootstrap.Tooltip(this, typeof action === 'object' ? action : {});
        }
    });
};

$.fn.dropdown = function (action) {
    return this.each(function () {
        var instance = bootstrap.Dropdown.getOrCreateInstance(this);
        if (action === 'toggle') {
            instance.toggle();
        } else if (action === 'show') {
            instance.show();
        } else if (action === 'hide') {
            instance.hide();
        }
    });
};

$.fn.collapse = function (action) {
    return this.each(function () {
        var instance = bootstrap.Collapse.getOrCreateInstance(this, { toggle: false });
        if (action === 'show') {
            instance.show();
        } else if (action === 'hide') {
            instance.hide();
        } else if (action === 'toggle') {
            instance.toggle();
        }
    });
};

$.fn.tab = function (action) {
    return this.each(function () {
        if (action === 'show') {
            bootstrap.Tab.getOrCreateInstance(this).show();
        }
    });
};

$.fn.carousel = function (options) {
    return this.each(function () {
        if (typeof options === 'object' || options === undefined) {
            new bootstrap.Carousel(this, options || {});
        }
    });
};

export default bootstrap;
