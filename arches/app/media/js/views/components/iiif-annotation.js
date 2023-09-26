define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'leaflet',
    'uuid',
    'geojson-extent',
    'views/components/iiif-viewer',
    'leaflet-draw'
], function($, _, ko, koMapping, L, uuid, geojsonExtent, IIIFViewerViewmodel) {
    var viewModel = function(params) {
        var self = this;

        var drawControl;
        var drawFeatures = ko.observableArray();
        var editItems = new L.FeatureGroup();
        var tools;

        this.drawFeatures = drawFeatures;
        this.widgets = params.widgets || [];
        this.newNodeId = null;
        this.featureLookup = {};
        this.selectedFeatureIds = ko.observableArray();
        this.lineColor = ko.observable("#3388ff");
        this.fillColor = ko.observable("#3388ff");
        this.lineWidth = ko.observable(3);
        this.pointRadius = ko.observable(10);
        this.lineOpacity = ko.observable(1);
        this.fillOpacity = ko.observable(0.2);
        this.showStylingTools = ko.observable(false);

        this.hideEditorTab = params.hideEditorTab || ko.observable(false);

        this.cancelDrawing = function() {
            _.each(tools, function(tool) {
                tool.disable();
            });
        };

        this.setDrawTool = function(tool) {
            self.cancelDrawing();
            if (tool && tools) tools[tool].enable();
        };

        self.widgets.forEach(function(widget) {
            var id = ko.unwrap(widget.node_id);
            self.featureLookup[id] = {
                features: ko.computed(function() {
                    var value = koMapping.toJS(self.tile.data[id]);
                    if (value) return value.features;
                    else return [];
                }),
                selectedTool: ko.observable()
            };
            self.featureLookup[id].selectedTool.subscribe(function(tool) {
                if (drawControl) {
                    if (tool) {
                        _.each(self.featureLookup, function(value, key) {
                            if (key !== id) {
                                value.selectedTool(null);
                            }
                        });
                        self.newNodeId = id;
                    }
                    self.setDrawTool(tool);
                    disableEditing();
                }
            });
        });

        this.selectedTool = ko.pureComputed(function() {
            var tool;
            _.find(self.featureLookup, function(value) {
                var selectedTool = value.selectedTool();
                if (selectedTool) tool = selectedTool;
            });
            return tool;
        });

        this.editing = ko.pureComputed(function() {
            return !!(self.selectedFeatureIds().length > 0 || self.selectedTool());
        });

        this.updateTiles = function() {
            _.each(self.featureLookup, function(value) {
                value.selectedTool(null);
            });
            self.widgets.forEach(function(widget) {
                var id = ko.unwrap(widget.node_id);
                var features = [];
                drawFeatures().forEach(function(feature){
                    if (feature.properties.nodeId === id) {
                        features.push(feature);
                    }
                });
                if (ko.isObservable(self.tile.data[id])) {
                    self.tile.data[id]({
                        type: 'FeatureCollection',
                        features: features
                    });
                } 
                else {
                    self.tile.data[id].features(features);
                }
            });
        };

        var updateDrawFeatures = function() {
            drawFeatures([]);
            self.widgets.forEach(function(widget) {
                var id = ko.unwrap(widget.node_id);
                var featureCollection = koMapping.toJS(self.tile.data[id]);
                if (featureCollection && featureCollection.features) {
                    featureCollection.features.forEach(function(feature) {
                        if (feature.properties.manifest && !params.manifest)
                            params.manifest = feature.properties.manifest;
                        if (feature.properties.canvas && !params.canvas)
                            params.canvas = feature.properties.canvas;
                        feature.properties.nodeId = id;
                    });
                    drawFeatures(drawFeatures().concat(featureCollection.features));
                }
            });
        };
        updateDrawFeatures();

        IIIFViewerViewmodel.apply(this, [params]);


        var setTab = this.canvas.subscribe(function(val){
            if (val) {
                self.expandGallery(false);
                self.activeTab(ko.unwrap(self.activeTab) || 'editor');
                setTab.dispose();
            }
        });

        this.expandGallery.subscribe(function(val){
            if (val) {
                self.hideSidePanel();
            }
        });

        this.getAnnotationCount = function(canvas) {
            return drawFeatures().filter(function(feature) {
                return feature.properties.canvas === canvas;
            }).length;
        };

        var disableEditing = function() {
            if (editingFeature && editingFeature.editing) editingFeature.editing.disable();
            editingFeature = undefined;
            self.selectedFeatureIds([]);
        };
        var enableEditing = function(feature) {
            disableEditing();
            editingFeature = feature;
            editingFeature.options.editing || (editingFeature.options.editing = {});
            editingFeature.editing.enable();
            self.styleProperties(feature.feature.properties);
            self.selectedFeatureIds([feature.feature.id]);
        };

        this.styleProperties = ko.computed({
            read: function() {
                return {
                    color: self.lineColor(),
                    fillColor: self.fillColor(),
                    weight: self.lineWidth(),
                    radius: self.pointRadius(),
                    opacity: self.lineOpacity(),
                    fillOpacity: self.fillOpacity()
                };
            },
            write: function(style) {
                self.lineColor(style.color);
                self.fillColor(style.fillColor);
                self.lineWidth(style.weight);
                self.pointRadius(style.radius);
                self.lineOpacity(style.opacity);
                self.fillOpacity(style.fillOpacity);
            }
        });

        var featureClick;
        this.featureClick = featureClick;
        var drawLayer = ko.computed(function() {
            var selectedFeatureIds = self.selectedFeatureIds();
            var styleProperties = self.styleProperties();
            return L.geoJson({
                type: 'FeatureCollection',
                features: drawFeatures()
            }, {
                pointToLayer: function(feature, latlng) {
                    var style;
                    if (selectedFeatureIds.includes(feature.id)) style = styleProperties;
                    else style = {
                        color: feature.properties.color,
                        fillColor: feature.properties.fillColor,
                        weight: feature.properties.weight,
                        radius: feature.properties.radius,
                        opacity: feature.properties.opacity,
                        fillOpacity: feature.properties.fillOpacity
                    };
                    return L.circleMarker(latlng, style);
                },
                style: function(feature) {
                    var style;
                    if (selectedFeatureIds.includes(feature.id)) style = styleProperties;
                    else style = {
                        color: feature.properties.color,
                        fillColor: feature.properties.fillColor,
                        weight: feature.properties.weight,
                        radius: feature.properties.radius,
                        opacity: feature.properties.opacity,
                        fillOpacity: feature.properties.fillOpacity
                    };
                    return style;
                },
                filter: function(feature) {
                    return feature.properties.canvas === self.canvas();
                },
                onEachFeature: function(feature, layer) {
                    layer.on('click', function(e) {
                        enableEditing(e.target);
                        featureClick = true;
                    });
                }
            });
        });
        this.drawLayer = drawLayer;

        drawLayer.subscribe(function(newDrawLayer) {
            var map = self.map();
            var selectedFeatureIds = self.selectedFeatureIds();
            if (map) {
                editItems.clearLayers();
                editItems.addLayer(newDrawLayer);
                newDrawLayer.getLayers().forEach(function(layer) {
                    if (selectedFeatureIds.includes(layer.feature.id)) {
                        layer.options.editing || (layer.options.editing = {});
                        layer.editing.enable();
                    }
                });
            }
        });

        if (this.card) {
            this.card.triggerUpdate = updateDrawFeatures; // can be called by the provisional tile view model to update the drawing
        }

        this.disableDrawing = ko.computed(function() {
            return !self.canvas();
        });

        this.showFeature = function(feature) {
            self.canvas(feature.properties.canvas);
            if (self.manifest() !== feature.properties.manifest) {
                self.manifest(feature.properties.manifest);
                self.getManifestData();
            }
            setTimeout(function() {
                if (feature.geometry.type === 'Point') {
                    var coords = feature.geometry.coordinates;
                    self.map().panTo([coords[1], coords[0]]);
                } else {
                    var extent = geojsonExtent(feature);
                    self.map().fitBounds([
                        [extent[1], extent[0]],
                        [extent[3], extent[2]]
                    ]);
                }
            }, 200);
        };

        var editingFeature;
        this.editFeature = function(feature) {
            var layers = editItems.getLayers()[0].getLayers();
            if (self.manifest() !== feature.properties.manifest) {
                self.manifest(feature.properties.manifest);
                self.getManifestData();
            }
            self.canvas(feature.properties.canvas);
            layers.forEach(function(layer) {
                if (layer.feature.id === feature.id) enableEditing(layer);
            });
        };

        this.deleteFeature = function(feature) {
            drawFeatures().forEach(function(drawFeature) {
                if (drawFeature.id === feature.id) drawFeatures.remove(drawFeature);
            });
            self.updateTiles();
        };

        this.canvas.subscribe(disableEditing);

        this.map.subscribe(function(map) {
            if (map && !drawControl) {
                map.addLayer(editItems);
                editItems.addLayer(drawLayer());

                drawControl = new L.Control.Draw({
                    edit: {
                        featureGroup: editItems
                    }
                });
                map.addControl(drawControl);

                tools = {
                    'draw_point': new L.Draw.CircleMarker(map, drawControl.options.circlemarker),
                    'draw_line_string': new L.Draw.Polyline(map, drawControl.options.polyline),
                    'draw_polygon': new L.Draw.Polygon(map, drawControl.options.polygon)
                };
                self.styleProperties.subscribe(function(styleProperties) {
                    _.each(tools, function(tool) {
                        if (tool.type === "circlemarker") tool.setOptions(styleProperties);
                        else tool.setOptions({ shapeOptions: styleProperties });
                    });
                    self.selectedFeatureIds().forEach(function(id) {
                        drawFeatures().forEach(function(drawFeature) {
                            if (drawFeature.id === id) {
                                drawFeature.properties = Object.assign(
                                    drawFeature.properties,
                                    styleProperties
                                );
                            }
                        });
                        self.updateTiles();
                    });
                });

                map.on('draw:created', function(e) {
                    var feature = e.layer.toGeoJSON();
                    feature.id = uuid.generate();
                    feature.properties = Object.assign({
                        nodeId: self.newNodeId,
                        canvas: self.canvas(),
                        manifest: self.manifest()
                    }, self.styleProperties());
                    drawFeatures.push(feature);
                    self.updateTiles();
                    self.editFeature(feature);
                });

                map.on('draw:editvertex draw:editmove', function() {
                    var layers = editItems.getLayers()[0].getLayers();
                    drawFeatures().forEach(function(drawFeature) {
                        layers.forEach(function(layer) {
                            if (drawFeature.id === layer.feature.id)
                                drawFeature.geometry = layer.toGeoJSON().geometry;
                        });
                    });
                    self.updateTiles();
                });

                map.on('click', function() {
                    if (!featureClick) disableEditing();
                    featureClick = false;
                });

                if (self.form) self.form.on('tile-reset', function() {
                    disableEditing();
                    updateDrawFeatures();
                    _.each(self.featureLookup, function(value) {
                        if (value.selectedTool()) value.selectedTool('');
                    });
                });
            }
        });
    };
    return viewModel;
});
