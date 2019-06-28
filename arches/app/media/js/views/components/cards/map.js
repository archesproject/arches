define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'mapbox-gl-draw',
    'viewmodels/card-component',
    'views/components/map'
], function(_, ko, koMapping, uuid, MapboxDraw, CardComponentViewModel, MapComponentViewModel) {
    return ko.components.register('map-card', {
        viewModel: function(params) {
            var self = this;

            CardComponentViewModel.apply(this, [params]);
            MapComponentViewModel.apply(this, [params]);

            this.activeTab('editor');
            this.featureLookup = {};
            var getDrawFeatures = function() {
                var drawFeatures = [];
                self.card.widgets().forEach(function(widget) {
                    var nodeId = widget.node_id();
                    if (self.form && self.form.nodeLookup[nodeId].datatype() === 'geojson-feature-collection' && self.tile) {
                        var featureCollection = koMapping.toJS(self.tile.data[nodeId]);
                        if (featureCollection) {
                            featureCollection.features.forEach(function(feature) {
                                if (!feature.id) {
                                    feature.id = uuid.generate();
                                }
                                feature.properties.nodeId = nodeId;
                            });
                            drawFeatures = drawFeatures.concat(featureCollection.features);
                        }
                    }
                });
                return drawFeatures;
            };
            var drawFeatures = getDrawFeatures();
            var newNodeId;
            this.card.widgets().forEach(function(widget) {
                var nodeId = widget.node_id();
                if (self.form && self.form.nodeLookup[nodeId].datatype() === 'geojson-feature-collection') {
                    self.featureLookup[nodeId] = {
                        features: ko.computed(function() {
                            var features = [];
                            if (self.tile) {
                                var featureCollection = koMapping.toJS(self.tile.data[nodeId]);
                                if (featureCollection) {
                                    features = featureCollection.features;
                                }
                            }
                            return features;
                        }),
                        selectedTool: ko.observable()
                    };
                    self.featureLookup[nodeId].selectedTool.subscribe(function(selectedTool) {
                        if (self.draw) {
                            if (selectedTool === '') {
                                self.draw.changeMode('simple_select');
                            } else if (selectedTool) {
                                _.each(self.featureLookup, function(value, key) {
                                    if (key !== nodeId) {
                                        value.selectedTool(null);
                                    }
                                });
                                newNodeId = nodeId;
                                self.draw.changeMode(selectedTool);
                            }
                        }
                    });
                }
            });

            var updateFeatures = function() {
                var featureCollection = self.draw.getAll();
                _.each(self.featureLookup, function(value) {
                    value.selectedTool(null);
                });
                self.card.widgets().forEach(function(widget) {
                    var nodeId = widget.node_id();
                    if (self.form && self.form.nodeLookup[nodeId].datatype() === 'geojson-feature-collection') {
                        var nodeFeatures = [];
                        featureCollection.features.forEach(function(feature){
                            if (feature.properties.nodeId === nodeId) nodeFeatures.push(feature);
                        });
                        if (ko.isObservable(self.tile.data[nodeId])) {
                            self.tile.data[nodeId]({
                                type: 'FeatureCollection',
                                features: nodeFeatures
                            });
                        } else {
                            self.tile.data[nodeId].features(nodeFeatures);
                        }
                    }
                });
            };

            this.deleteFeature = function(feature) {
                if (self.draw) {
                    self.draw.delete(feature.id);
                    updateFeatures();
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

            this.selectedFeatureIds = ko.observableArray();
            this.draw = null;
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
                    updateFeatures();
                });
                map.on('draw.update', updateFeatures);
                map.on('draw.delete', updateFeatures);
                map.on('draw.modechange', updateFeatures);
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
                });
            });
        },
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
});
