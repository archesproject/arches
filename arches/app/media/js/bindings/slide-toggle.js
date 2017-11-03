// Here's a custom Knockout binding that makes elements shown/hidden via jQuery's fadeIn()/fadeOut() methods
// Could be stored in a separate utility library
define([
  'jquery',
  'knockout',
], function ($, ko) {
    ko.bindingHandlers.slideToggle = {
        init: function(element, valueAccessor,allBindingsAccessor, viewModel, bindingContent) {
            var value = valueAccessor();
            var bindings = allBindingsAccessor();
            var value = valueAccessor();
            if (value()) {
                $(element).slideToggle( "slow", function() {console.log('expanding')});
            }
        },
        update: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContent) {
            var value = valueAccessor();
            var bindings = allBindingsAccessor();
            var duration = bindings.duration;
            var easing = bindings.easing;
            var callback = bindings.callback;

            if (value() === true) {
                $(element).slideToggle( duration, easing, callback);
            } else {
                $(element).slideToggle( duration, easing, callback);
            }
        }
    };
    return ko.bindingHandlers.slideToggle;
});
