define([
    'jquery',
    'knockout',
], function($, ko) {
    ko.bindingHandlers.fadeVisible = {
        init: function(element, valueAccessor) {
            // Initially set the element to be instantly visible/hidden depending on the value
            var value = valueAccessor();
            $(element).toggle(ko.unwrap(value)); // Use "unwrapObservable" so we can handle values that may or may not be observable
        },
        update: function(element, valueAccessor) {
            // Whenever the value subsequently changes, slowly fade the element in or out
            var value = valueAccessor();
            if (ko.unwrap(value) === false) {
                $(element).fadeOut();
            } else {
                $(element).delay(200).fadeIn(400);
            }
            // ko.unwrap(value) ? $(element).fadeOut() : $(element).fadeIn();
        }
    };
    return ko.bindingHandlers.fadeVisible;
});
