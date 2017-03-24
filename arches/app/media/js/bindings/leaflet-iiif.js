define([
    'jquery',
    'underscore',
    'knockout',
    'leaflet',
    'leaflet-iiif',
    'leaflet-draw'
], function($, _, ko, L) {
    ko.bindingHandlers.leafletIIIF = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var map = L.map(element, {
                center: [0, 0],
                crs: L.CRS.Simple,
                zoom: 0
            });

            var baseLayer = L.tileLayer.iiif(
                'https://stacks.stanford.edu/image/iiif/cv770rd9515%2F0767_23A_SM/info.json'
            ).addTo(map);

            var drawnItems = new L.FeatureGroup();
            map.addLayer(drawnItems);

            var drawControl = new L.Control.Draw({
                edit: {
                    featureGroup: drawnItems
                }
            });

            map.addControl(drawControl);

            map.on(L.Draw.Event.CREATED, function(e) {
                var type = e.layerType
                var layer = e.layer;

                drawnItems.addLayer(layer);
            });

            $(element).mousedown(function(event) {
                event.stopPropagation();
            });
        }
    }

    return ko.bindingHandlers.leafletIIIF;
});
