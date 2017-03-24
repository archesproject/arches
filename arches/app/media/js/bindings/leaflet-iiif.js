define([
    'jquery',
    'underscore',
    'knockout',
    'leaflet',
    'leaflet-iiif'
], function($, _, ko, L) {
    ko.bindingHandlers.leafletIIIF = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var map = L.map(element, {
                center: [0, 0],
                crs: L.CRS.Simple,
                zoom: 0
            });

            L.tileLayer.iiif('https://stacks.stanford.edu/image/iiif/hg676jb4964%2F0380_796-44/info.json', {
              attribution: '<a href="http://searchworks.stanford.edu/view/hg676jb4964">Martin Luther King Jr. & Joan Baez march to integrate schools, Grenada, MS, 1966</a>',
              maxZoom: 5
            }).addTo(map);

            // prevents drag events from bubbling
            $(element).mousedown(function(event) {
                event.stopPropagation();
            });
        }
    }

    return ko.bindingHandlers.leafletIIIF;
});
