define([
    'jquery',
    'underscore',
    'knockout',
    'mapbox-gl',
    'arches',
    'plugins/mapbox-gl-draw'
], function ($, _, ko, mapboxgl, arches, Draw) {
    ko.bindingHandlers.mapboxgl = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var defaults = {
                container: element
            };
            var options = ko.unwrap(valueAccessor());
            mapboxgl.accessToken = arches.mapboxApiKey;
            var mapCenter = new mapboxgl.LngLat(viewModel.centerX(), viewModel.centerY());
            options.zoom = viewModel.zoom();
            options.center = mapCenter;
            var map = new mapboxgl.Map(
                _.defaults(options, defaults)
            );

            viewModel.map = map;
            viewModel.setBasemap = function(basemapType) {
                arches.basemapLayers.forEach(function(layer) {
                    if (layer.name === basemapType && !map.getLayer(layer.layer.id)) {
                        map.addLayer(layer.layer)
                    } else if (map.getLayer(layer.layer.id) && layer.name !== basemapType) {
                        map.removeLayer(layer.layer.id)
                    }
                })
            };

            var draw = Draw();
            map.addControl(draw);
        }
    }

    return ko.bindingHandlers.mapboxgl;
});
