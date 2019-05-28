define([
    'jquery',
    'arches',
    'knockout',
    'viewmodels/card-component'
], function($, arches, ko, CardComponentViewModel) {
    return ko.components.register('map-card', {
        viewModel: function(params) {
            var self = this;
            var layers = [];
            var geojsonSourceFactory = function() {
                return {
                    "type": "geojson",
                    "data": {
                        "type": "FeatureCollection",
                        "features": []
                    }
                };
            };

            this.basemaps = [];
            this.activeBasemap = ko.observable();
            this.activeTab = ko.observable();

            arches.mapLayers.forEach(function(layer) {
                if (!layer.isoverlay) self.basemaps.push(layer);
                if (layer.addtomap) {
                    layers = layers.concat(layer.layer_definitions);
                    if (!layer.isoverlay) self.activeBasemap(layer);
                }
            });

            this.mapStyle = {
                "version": 8,
                "sources": $.extend(true, {
                    "resource": geojsonSourceFactory(),
                    "search-results-hex": geojsonSourceFactory(),
                    "search-results-hashes": geojsonSourceFactory(),
                    "search-results-points": geojsonSourceFactory()
                }, arches.mapSources),
                "sprite": arches.mapboxSprites,
                "glyphs": arches.mapboxGlyphs,
                "layers": layers
            };

            this.toggleTab = function(tabName) {
                if (self.activeTab() === tabName) {
                    self.activeTab(null);
                } else {
                    self.activeTab(tabName);
                }
            };

            CardComponentViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
});
