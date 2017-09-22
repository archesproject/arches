define([
    'jquery',
    'knockout'
], function ($, ko) {
    ko.bindingHandlers.scrollTo = {
        update: function (element, valueAccessor, allBindings) {
            var _value = valueAccessor();
            var _valueUnwrapped = ko.unwrap(_value);
            var container = $('html, body')
            if (allBindings().container) {
                container = $(allBindings().container)
            }
            if (_valueUnwrapped) {
                var target = $(element);
                var top = $(window).height();
                var container_top = $(container).offset().top
                var bottom = $(target).offset().top + $(target).outerHeight();
                if (bottom > top || bottom < container_top) {
                    container.stop().animate({
                        scrollTop: $(target).offset().top - container.offset().top + container.scrollTop() - 50
                    }, 500);
                }
            }
        }
    };

    return ko.bindingHandlers.scrollTo;
});
