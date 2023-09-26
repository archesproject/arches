define([
    'jquery',
    'underscore',
    'knockout',
    'leaflet'
], function($, _, ko, L) {
    ko.bindingHandlers.leaflet = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var config = ko.unwrap(valueAccessor());
            var map = L.map(element, config);
            if (typeof config.afterRender === 'function') {
                config.afterRender(map);
            }

            $(element).mousedown(function(event) {
                event.stopPropagation();
            });
        }
    };

    return ko.bindingHandlers.leaflet;
});
