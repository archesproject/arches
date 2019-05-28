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
            this.basemaps = [];
            this.activeBasemap = ko.observable();
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
                    "resource": {
                        "type": "geojson",
                        "data": {
                            "type": "FeatureCollection",
                            "features": []
                        }
                    },
                    "search-results-hex": {
                        "type": "geojson",
                        "data": {
                            "type": "FeatureCollection",
                            "features": []
                        }
                    },
                    "search-results-hashes": {
                        "type": "geojson",
                        "data": {
                            "type": "FeatureCollection",
                            "features": []
                        }
                    },
                    "search-results-points": {
                        "type": "geojson",
                        "data": {
                            "type": "FeatureCollection",
                            "features": []
                        }
                    }
                }, arches.mapSources),
                "sprite": arches.mapboxSprites,
                "glyphs": arches.mapboxGlyphs,
                "layers": layers
            };
            this.activeTab = ko.observable();
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
