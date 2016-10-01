define([
    'jquery',
    'underscore',
    'knockout',
    'mapbox-gl',
    'arches',
    'map/mapbox-style',
    'bindings/nouislider',
    'bindings/sortable'
], function($, _, ko, mapboxgl, arches, mapStyle) {
    ko.bindingHandlers.mapboxgl = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext) {
            var defaults = {
                container: element
            };
            var options = ko.unwrap(valueAccessor()).mapOptions;
            var mapCenter = new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY());

            mapboxgl.accessToken = arches.mapboxApiKey;
            options.zoom = viewModel.zoom();
            options.center = mapCenter;
            options.pitch = viewModel.pitch();
            options.bearing = viewModel.bearing();

            var map = new mapboxgl.Map(
                _.defaults(options, defaults)
            );
            viewModel.map = map;

            // prevents drag events from bubbling
            $(element).mousedown(function(event) {
                event.stopPropagation();
            });

            if (typeof ko.unwrap(valueAccessor()).afterRender === 'function') {
                ko.unwrap(valueAccessor()).afterRender(map)
            }
        }
    }

    return ko.bindingHandlers.mapboxgl;
});
