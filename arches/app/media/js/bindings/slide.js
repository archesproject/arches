// Here's a custom Knockout binding that makes elements shown/hidden via jQuery's fadeIn()/fadeOut() methods
// Could be stored in a separate utility library
define([
  'jquery',
  'knockout',
], function ($, ko) {
    ko.bindingHandlers.slide = {
        init: function(element, valueAccessor,allBindingsAccessor, viewModel, bindingContent) {
            var value = valueAccessor();
            var bindings = allBindingsAccessor();
            var value = valueAccessor();
        },
        update: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContent) {
            var value = valueAccessor();
            var bindings = allBindingsAccessor();
            var duration = bindings.duration;
            var direction = bindings.direction;
            var easing = bindings.easing;
            var callback = bindings.callback;

            if (value() === true) {
                $(element).toggle(easing, direction);
            } else {
                $(element).toggle(easing, direction);
            }
        }
    };
    return ko.bindingHandlers.slide;
});
