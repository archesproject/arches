define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'mapbox-gl',
    'mapbox-gl-draw',
    'geojson-extent',
    'viewmodels/card-component',
    'views/components/map',
    'bindings/chosen'
], function(_, ko, koMapping, uuid, mapboxgl, MapboxDraw, geojsonExtent, CardComponentViewModel, MapComponentViewModel) {
    return ko.components.register('map-card', {
        viewModel: function(params) {
            var self = this;
            var widgets = [];
            var padding = 40;
            var drawFeatures;
            var newNodeId;
            this.featureLookup = {};
            this.selectedFeatureIds = ko.observableArray();
            this.draw = null;

            CardComponentViewModel.apply(this, [params]);

            if (self.form && self.tile) self.card.widgets().forEach(function(widget) {
                var id = widget.node_id();
                var type = self.form.nodeLookup[id].datatype();
                if (type === 'geojson-feature-collection') {
                    widgets.push(widget);
                    self.featureLookup[id] = {
                        features: ko.computed(function() {
                            var value = koMapping.toJS(self.tile.data[id]);
                            if (value) return value.features;
                            else return [];
                        }),
                        selectedTool: ko.observable()
                    };
                    self.featureLookup[id].selectedTool.subscribe(function(tool) {
                        if (self.draw) {
                            if (tool === '') {
                                self.draw.changeMode('simple_select');
                            } else if (tool) {
                                _.each(self.featureLookup, function(value, key) {
                                    if (key !== id) {
                                        value.selectedTool(null);
                                    }
                                });
                                newNodeId = id;
                                self.draw.changeMode(tool);
                            }
                        }
                    });
                }
            });

            var updateTiles = function() {
                var featureCollection = self.draw.getAll();
                _.each(self.featureLookup, function(value) {
                    value.selectedTool(null);
                });
                widgets.forEach(function(widget) {
                    var id = widget.node_id();
                    var features = [];
                    featureCollection.features.forEach(function(feature){
                        if (feature.properties.nodeId === id) features.push(feature);
                    });
                    if (ko.isObservable(self.tile.data[id])) {
                        self.tile.data[id]({
                            type: 'FeatureCollection',
                            features: features
                        });
                    } else {
                        self.tile.data[id].features(features);
                    }
                });
            };

            var getDrawFeatures = function() {
                var drawFeatures = [];
                widgets.forEach(function(widget) {
                    var id = widget.node_id();
                    var featureCollection = koMapping.toJS(self.tile.data[id]);
                    if (featureCollection) {
                        featureCollection.features.forEach(function(feature) {
                            if (!feature.id) {
                                feature.id = uuid.generate();
                            }
                            feature.properties.nodeId = id;
                        });
                        drawFeatures = drawFeatures.concat(featureCollection.features);
                    }
                });
                return drawFeatures;
            };
            drawFeatures = getDrawFeatures();

            if (drawFeatures.length > 0) {
                params.bounds = geojsonExtent({
                    type: 'FeatureCollection',
                    features: drawFeatures
                });
                params.fitBoundsOptions = { padding: padding };
            }
            params.activeTab = 'editor';

            MapComponentViewModel.apply(this, [params]);

            this.deleteFeature = function(feature) {
                if (self.draw) {
                    self.draw.delete(feature.id);
                    updateTiles();
                }
            };

            this.editFeature = function(feature) {
                if (self.draw) {
                    self.draw.changeMode('simple_select', {
                        featureIds: [feature.id]
                    });
                    self.selectedFeatureIds([feature.id]);
                    _.each(self.featureLookup, function(value) {
                        value.selectedTool(null);
                    });
                }
            };

            this.updateLayers = function(layers) {
                var map = self.map();
                var style = map.getStyle();
                style.layers = layers.concat(self.draw.options.styles);
                map.setStyle(style);
            };

            this.fitFeatures = function(features) {
                var map = self.map();
                var bounds = geojsonExtent({
                    type: 'FeatureCollection',
                    features: features
                });
                var camera = map.cameraForBounds(bounds, { padding: padding });
                map.jumpTo(camera);
            };

            this.map.subscribe(function(map) {
                self.draw = new MapboxDraw({
                    displayControlsDefault: false
                });
                map.addControl(self.draw);
                self.draw.set({
                    type: 'FeatureCollection',
                    features: drawFeatures
                });
                map.on('draw.create', function(e) {
                    e.features.forEach(function(feature) {
                        self.draw.setFeatureProperty(feature.id, 'nodeId', newNodeId);
                    });
                    updateTiles();
                });
                map.on('draw.update', updateTiles);
                map.on('draw.delete', updateTiles);
                map.on('draw.modechange', updateTiles);
                map.on('draw.selectionchange', function(e) {
                    self.selectedFeatureIds(e.features.map(function(feature) {
                        return feature.id;
                    }));
                });

                self.form.on('tile-reset', function() {
                    self.draw.set({
                        type: 'FeatureCollection',
                        features: getDrawFeatures()
                    });
                    _.each(self.featureLookup, function(value) {
                        if (value.selectedTool()) value.selectedTool('');
                    });
                });
            });
        },
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
});
