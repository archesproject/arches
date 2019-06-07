define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'viewmodels/card-component',
    'bindings/sortable'
], function($, _, arches, ko, CardComponentViewModel) {
    return ko.components.register('map-card', {
        viewModel: function(params) {
            var self = this;
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
            this.overlays = ko.observableArray();
            this.activeBasemap = ko.observable();
            this.activeTab = ko.observable();
            this.hideSidePanel = function() {
                self.activeTab(undefined);
            };

            arches.mapLayers.forEach(function(layer) {
                if (!layer.isoverlay) {
                    self.basemaps.push(layer);
                    if (layer.addtomap) self.activeBasemap(layer);
                }
                else {
                    layer.onMap = ko.observable(layer.addtomap);
                    self.overlays.push(layer);
                }
            });

            _.each(arches.mapSources, function(sourceConfig, name) {
                if (sourceConfig.tiles) {
                    sourceConfig.tiles.forEach(function(url, i) {
                        if (url.startsWith('/')) {
                            sourceConfig.tiles[i] = window.location.origin + url;
                        }
                    });
                }
            });

            var layers = ko.pureComputed(function() {
                var layers = self.activeBasemap().layer_definitions;
                self.overlays().forEach(function(layer) {
                    if (layer.onMap()) {
                        layers = layers.concat(layer.layer_definitions);
                    }
                });
                return layers;
            }, this);

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
                "layers": layers()
            };

            this.toggleTab = function(tabName) {
                if (self.activeTab() === tabName) {
                    self.activeTab(null);
                } else {
                    self.activeTab(tabName);
                }
            };

            this.setupMap = function(map) {
                self.map = map;

                layers.subscribe(function(layers) {
                    var style = map.getStyle();
                    style.layers = layers;
                    map.setStyle(style);
                });
            };

            CardComponentViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
});
