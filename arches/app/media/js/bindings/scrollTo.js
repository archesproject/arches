define([
    'jquery',
    'knockout'
], function ($, ko) {
    ko.bindingHandlers.scrollTo = {
        update: function (element, valueAccessor, allBindings) {
            var _value = valueAccessor();
            var _valueUnwrapped = ko.unwrap(_value);
            if (_valueUnwrapped) {
                var target = $(element);
                $('html, body').stop().animate({
                    scrollTop: $(target).offset().top
                }, 500);
            }
        }
    };

    return ko.bindingHandlers.scrollTo;
});
