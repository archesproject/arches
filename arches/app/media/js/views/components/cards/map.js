define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'mapbox-gl',
    'mapbox-gl-draw',
    'geojson-extent',
    'geojsonhint',
    'viewmodels/card-component',
    'views/components/map',
    'bindings/chosen',
    'bindings/codemirror',
    'codemirror/mode/javascript/javascript'
], function(_, ko, koMapping, uuid, mapboxgl, MapboxDraw, geojsonExtent, geojsonhint, CardComponentViewModel, MapComponentViewModel) {
    var viewModel = function(params) {
        var self = this;
        var widgets = [];
        var padding = 40;
        var drawFeatures;
        this.newNodeId = null;
        this.featureLookup = {};
        this.selectedFeatureIds = ko.observableArray();
        this.geoJSONString = ko.observable();
        this.draw = null;
        this.setDrawTool = function(tool) {
            if (tool) self.draw.changeMode(tool);
        };

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
                            self.newNodeId = id;
                        }
                        self.setDrawTool(tool);
                    }
                });
            }
        });

        this.updateTiles = function() {
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
            params.fitBoundsOptions = { padding: {top: padding, left: padding + 200, bottom: padding, right: padding + 200} };
        }
        params.activeTab = 'editor';
        params.sources = {
            "geojson-editor-data": {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            }
        };
        if (!params.layers) {
            params.layers = [];
        }
        params.layers = params.layers.concat([{
            "id": "geojson-editor-polygon-fill",
            "type": "fill",
            "filter": ["==", "$type", "Polygon"],
            "paint": {
                "fill-color": "#3bb2d0",
                "fill-outline-color": "#3bb2d0",
                "fill-opacity": 0.1
            },
            "source": "geojson-editor-data"
        }, {
            "id": "geojson-editor-polygon-stroke",
            "type": "line",
            "filter": ["==", "$type", "Polygon"],
            "layout": {
                "line-cap": "round",
                "line-join": "round"
            },
            "paint": {
                "line-color": "#3bb2d0",
                "line-width": 2
            },
            "source": "geojson-editor-data"
        }, {
            "id": "geojson-editor-line",
            "type": "line",
            "filter": ["==", "$type", "LineString"],
            "layout": {
                "line-cap": "round",
                "line-join": "round"
            },
            "paint": {
                "line-color": "#3bb2d0",
                "line-width": 2
            },
            "source": "geojson-editor-data"
        }, {
            "id": "geojson-editor-point-point-stroke",
            "type": "circle",
            "filter": ["==", "$type", "Point"],
            "paint": {
                "circle-radius": 5,
                "circle-opacity": 1,
                "circle-color": "#fff"
            },
            "source": "geojson-editor-data"
        }, {
            "id": "geojson-editor-point",
            "type": "circle",
            "filter": ["==", "$type", "Point"],
            "paint": {
                "circle-radius": 3,
                "circle-color": "#3bb2d0"
            },
            "source": "geojson-editor-data"
        }]);

        MapComponentViewModel.apply(this, [params]);

        this.deleteFeature = function(feature) {
            if (self.draw) {
                self.draw.delete(feature.id);
                self.updateTiles();
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
            style.layers = self.draw ? layers.concat(self.draw.options.styles) : layers;
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

        this.editGeoJSON = function(features, nodeId) {
            var geoJSONString = JSON.stringify({
                type: 'FeatureCollection',
                features: features
            }, null, '   ');
            this.geoJSONString(geoJSONString);
            self.newNodeId = nodeId;
        };
        this.geoJSONString.subscribe(function(geoJSONString) {
            var map = self.map();
            if (geoJSONString === undefined) {
                setupDraw(map);
            } else if (self.draw) {
                map.removeControl(self.draw);
                self.draw = undefined;
                self.selectedFeatureIds([]);
            }
        });
        this.geoJSONErrors = ko.pureComputed(function() {
            var geoJSONString = self.geoJSONString();
            var hint = geojsonhint.hint(geoJSONString);
            var errors = [];
            hint.forEach(function(item) {
                if (item.level !== 'message') {
                    errors.push(item);
                }
            });
            return errors;
        }).extend({ rateLimit: 50 });
        var geoJSONLayerData = ko.pureComputed(function() {
            var geoJSONString = self.geoJSONString();
            var geoJSONErrors = self.geoJSONErrors();
            if (geoJSONErrors.length === 0) return JSON.parse(geoJSONString);
            else return {
                type: 'FeatureCollection',
                features: []
            };
        }).extend({ rateLimit: 100 });
        geoJSONLayerData.subscribe(function(data) {
            var map = self.map();
            map.getSource('geojson-editor-data').setData(data);
        });
        this.updateGeoJSON = function() {
            if (self.geoJSONErrors().length === 0) {
                var geoJSON = JSON.parse(this.geoJSONString());
                geoJSON.features.forEach(function(feature) {
                    if (!feature.id) feature.id = uuid.generate();
                    if (!feature.properties) feature.properties = {};
                    feature.properties.nodeId = self.newNodeId;
                });
                if (ko.isObservable(self.tile.data[self.newNodeId])) {
                    self.tile.data[self.newNodeId](geoJSON);
                } else {
                    self.tile.data[self.newNodeId].features(geoJSON.features);
                }
                self.geoJSONString(undefined);
            }
        };

        this.drawModeChange = function() {
            return;
        };

        var setupDraw = function(map) {
            var modes = MapboxDraw.modes;
            modes.static = {
                onSetup: function() {
                    this.setActionableState();
                    return {};
                },
                toDisplayFeatures: function(state, geojson, display) {
                    display(geojson);
                }
            };
            self.draw = new MapboxDraw({
                displayControlsDefault: false,
                modes: modes
            });
            map.addControl(self.draw);
            self.draw.set({
                type: 'FeatureCollection',
                features: getDrawFeatures()
            });
            map.on('draw.create', function(e) {
                e.features.forEach(function(feature) {
                    self.draw.setFeatureProperty(feature.id, 'nodeId', self.newNodeId);
                });
                self.updateTiles();
            });
            map.on('draw.update', self.updateTiles);
            map.on('draw.delete', self.updateTiles);
            map.on('draw.modechange', function(e) {
                self.drawModeChange(e);
                self.updateTiles();
            });
            map.on('draw.selectionchange', function(e) {
                self.selectedFeatureIds(e.features.map(function(feature) {
                    return feature.id;
                }));
                if (e.features.length > 0) {
                    _.each(self.featureLookup, function(value) {
                        value.selectedTool(null);
                    });
                }
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
        };

        this.map.subscribe(setupDraw);
    };
    ko.components.register('map-card', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
    return viewModel;
});
