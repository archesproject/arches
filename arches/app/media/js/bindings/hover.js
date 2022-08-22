define([
    'knockout',
], function(ko) {
    ko.bindingHandlers.hover = {
        init: function(element, valueAccessor) {
            var value = valueAccessor();
            ko.applyBindingsToNode(element, {
                event: {
                    mouseenter: function() { value(true); },
                    mouseleave: function() { value(false); }
                }
            });
        }
    };
    return ko.bindingHandlers.hover;
});
