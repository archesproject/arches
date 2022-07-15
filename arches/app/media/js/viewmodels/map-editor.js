define([
    'arches',
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'geojson-extent',
    'geojsonhint',
    'togeojson',
    'proj4',
    'views/components/map',
    'views/components/cards/select-feature-layers',
], function(arches, $, _, ko, koMapping, uuid, geojsonExtent, geojsonhint, toGeoJSON, proj4, MapComponentViewModel, selectFeatureLayersFactory) {
    var viewModel = function(params) {
        var self = this;
        var padding = 40;
        var drawFeatures;
        
        var resourceId = params.tile ? params.tile.resourceinstance_id : '';
        if (this.widgets === undefined) { // could be [], so checking specifically for undefined
            this.widgets = params.widgets || [];
        }

        this.geojsonWidgets = this.widgets.filter(function(widget){ return widget.datatype.datatype === 'geojson-feature-collection'; });
        this.newNodeId = null;
        this.featureLookup = {};
        this.selectedFeatureIds = ko.observableArray();
        this.geoJSONString = ko.observable();
        this.draw = null;
        this.selectSource = this.selectSource || ko.observable();
        this.selectSourceLayer = this.selectSourceLayer || ko.observable();
        this.drawAvailable = ko.observable(false);
        this.bufferNodeId = ko.observable();
        this.bufferDistance = ko.observable(0);
        this.bufferUnits = ko.observable('m');
        this.bufferResult = ko.observable();
        this.bufferAddNew = ko.observable(false);
        this.allowAddNew = this.card && this.card.canAdd() && this.tile !== this.card.newTile;

        var selectSource = this.selectSource();
        var selectSourceLayer = this.selectSourceLayer();
        var selectFeatureLayers = selectFeatureLayersFactory(resourceId, selectSource, selectSourceLayer);

        this.setSelectLayersVisibility = function(visibility) {
            var map = self.map();
            if (map) {
                selectFeatureLayers.forEach(function(layer) {
                    map.setLayoutProperty(
                        layer.id,
                        'visibility',
                        visibility ? 'visible' : 'none'
                    );
                });
            }
        };


        var sources = [];
        for (var sourceName in arches.mapSources) {
            if (arches.mapSources.hasOwnProperty(sourceName)) {
                sources.push(sourceName);
            }
        }
        var updateSelectLayers = function() {
            var source = self.selectSource();
            var sourceLayer = self.selectSourceLayer();
            selectFeatureLayers = sources.indexOf(source) > 0 ?
                selectFeatureLayersFactory(resourceId, source, sourceLayer) :
                [];
            self.additionalLayers(
                extendedLayers.concat(
                    selectFeatureLayers,
                    geojsonLayers
                )
            );
        };
        this.selectSource.subscribe(updateSelectLayers);
        this.selectSourceLayer.subscribe(updateSelectLayers);

        this.setDrawTool = function(tool) {
            var showSelectLayers = (tool === 'select_feature');
            self.setSelectLayersVisibility(showSelectLayers);
            if (showSelectLayers) {
                self.draw.changeMode('simple_select');
                self.selectedFeatureIds([]);
            } else {
                if (tool) {
                    self.draw.changeMode(tool);
                    self.map().draw_mode = tool;
                }
            }
        };

        self.geojsonWidgets.forEach(function(widget) {
            var id = ko.unwrap(widget.node_id);
            self.featureLookup[id] = {
                features: ko.computed(function() {
                    var value = koMapping.toJS(self.tile.data[id]);
                    if (value) return value.features;
                    else return [];
                }),
                selectedTool: ko.observable(),
                dropErrors: ko.observableArray()
            };
            self.featureLookup[id].selectedTool.subscribe(function(tool) {
                if (self.draw) {
                    if (tool === '') {
                        self.draw.trash();
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
        });

        this.selectedTool = ko.pureComputed(function() {
            var tool;
            _.find(self.featureLookup, function(value) {
                var selectedTool = value.selectedTool();
                if (selectedTool) tool = selectedTool;
            });
            return tool;
        });

        this.updateTiles = function() {
            var featureCollection = self.draw.getAll();
            _.each(self.featureLookup, function(value) {
                value.selectedTool(null);
            });
            self.geojsonWidgets.forEach(function(widget) {
                var id = ko.unwrap(widget.node_id);
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
                    if (self.tile.data[id]) {
                        self.tile.data[id].features(features);
                    }
                }
            });
        };

        var getDrawFeatures = function() {
            var drawFeatures = [];
            self.geojsonWidgets.forEach(function(widget) {
                var id = ko.unwrap(widget.node_id);
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
            params.usePosition = false;
            params.bounds = geojsonExtent({
                type: 'FeatureCollection',
                features: drawFeatures
            });
            params.fitBoundsOptions = { padding: {top: padding, left: padding + 200, bottom: padding, right: padding + 200} };
        }

        params.activeTab = 'editor';
        params.sources = Object.assign({
            "geojson-editor-data": {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            }
        }, params.sources);
        var extendedLayers = [];
        if (params.layers) {
            extendedLayers = ko.unwrap(params.layers);
        }
        var geojsonLayers = [{
            "id": "geojson-editor-polygon-fill",
            "type": "fill",
            "filter": ["==", "$type", "Polygon"],
            "paint": {
                "fill-color": "#3bb2d0",
                "fill-outline-color": "#3bb2d0",
                "fill-opacity": 0.1
            },
            "source": "geojson-editor-data"
        },  {
            "id": "geojson-editor-polygon-stroke-base",
            "type": "line",
            "filter": ["==", "$type", "Polygon"],
            "layout": {
                "line-cap": "round",
                "line-join": "round"
            },
            "paint": {
                "line-color": "#fff",
                "line-width": 4
            },
            "source": "geojson-editor-data"
        },  {
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
                "circle-radius": 6,
                "circle-opacity": 1,
                "circle-color": "#fff"
            },
            "source": "geojson-editor-data"
        }, {
            "id": "geojson-editor-point",
            "type": "circle",
            "filter": ["==", "$type", "Point"],
            "paint": {
                "circle-radius": 5,
                "circle-color": "#3bb2d0"
            },
            "source": "geojson-editor-data"
        }];

        params.layers = ko.observable(
            extendedLayers.concat(
                selectFeatureLayers,
                geojsonLayers
            )
        );

        MapComponentViewModel.apply(this, [params]);

        this.deleteFeature = function(feature) {
            if (self.draw) {
                self.draw.delete(feature.id);
                self.selectedFeatureIds(
                    self.selectedFeatureIds().filter(function(id) {
                        return id !== feature.id;
                    })
                );
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
            if (style) {
                style.layers = self.draw ? layers.concat(self.draw.options.styles) : layers;
                map.setStyle(style);
            }
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
            self.setSelectLayersVisibility(false);
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
            var fc = {
                type: 'FeatureCollection',
                features: []
            };
            if (self.bufferNodeId() && self.bufferResult()) {
                fc.features.push(self.bufferResult());
            }
            return fc;
        }).extend({ rateLimit: 100 });
        geoJSONLayerData.subscribe(function(data) {
            var map = self.map();
            map.getSource('geojson-editor-data').setData(data);
        });
        this.updateGeoJSON = function() {
            if (self.geoJSONErrors().length === 0) {
                var geoJSON = JSON.parse(this.geoJSONString());
                geoJSON.features.forEach(function(feature) {
                    feature.id = uuid.generate();
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

        var setupDraw = function(map) {
            require(['mapbox-gl-draw'], (MapboxDraw) => {
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
                map.on('draw.update', function() {
                    self.updateTiles();
                    if (self.coordinateEditing()) {
                        var editingFeature = self.draw.getSelected().features[0];
                        if (editingFeature) updateCoordinatesFromFeature(editingFeature);
                    }
                    if (self.bufferNodeId()) self.updateBufferFeature();
                });
                map.on('draw.delete', self.updateTiles);
                map.on('draw.modechange', function(e) {
                    self.updateTiles();
                    self.setSelectLayersVisibility(false);
                    map.draw_mode = e.mode;
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
                    self.setSelectLayersVisibility(false);
                });

                if (self.form) self.form.on('tile-reset', function() {
                    var style = self.map().getStyle();
                    if (style) {
                        self.draw.set({
                            type: 'FeatureCollection',
                            features: getDrawFeatures()
                        });
                    }
                    _.each(self.featureLookup, function(value) {
                        if (value.selectedTool()) value.selectedTool('');
                    });
                });
                if (self.draw) {
                    self.drawAvailable(true);
                }
            });
        };

        if (this.provisionalTileViewModel) {
            this.provisionalTileViewModel.resetAuthoritative();
            this.provisionalTileViewModel.selectedProvisionalEdit.subscribe(function(val){
                if (val) {
                    var displayAll = function(){
                        var featureCollection;
                        for (var k in self.tile.data){
                            if (self.featureLookup[k] && self.draw) {
                                try {
                                    featureCollection = self.draw.getAll();
                                    featureCollection.features = ko.unwrap(self.featureLookup[k].features);
                                    self.draw.set(featureCollection);
                                } catch(e) {
                                    //pass: TypeError in draw seems inconsequential.
                                }
                            }
                        }
                    };
                    setTimeout(displayAll, 100);
                }
            });
        }

        this.map.subscribe(setupDraw);

        self.map.subscribe(function(map) {
            if (self.draw && !params.draw) {
                params.draw = self.draw;
            }
            if (map && !params.map) {
                params.map = map;
            }
        });

        if (!params.additionalDrawOptions) {
            params.additionalDrawOptions = [];
        }

        self.geojsonWidgets.forEach(function(widget) {
            if (widget.config.geometryTypes) {
                widget.drawTools = ko.pureComputed(function() {
                    var options = [{
                        value: '',
                        text: ''
                    }];
                    options = options.concat(
                        ko.unwrap(widget.config.geometryTypes).map(function(type) {
                            var option = {};
                            switch (ko.unwrap(type.id)) {
                            case 'Point':
                                option.value = 'draw_point';
                                option.text = arches.translations.mapAddPoint;
                                break;
                            case 'Line':
                                option.value = 'draw_line_string';
                                option.text = arches.translations.mapAddLine;
                                break;
                            case 'Polygon':
                                option.value = 'draw_polygon';
                                option.text = arches.translations.mapAddPolygon;
                                break;
                            }
                            return option;
                        })
                    );
                    if (self.selectSource()) {
                        options.push({
                            value: "select_feature",
                            text: self.selectText() || arches.translations.mapSelectDrawing
                        });
                    }
                    options = options.concat(params.additionalDrawOptions);
                    return options;
                });
            }
        });

        this.isFeatureClickable = function(feature) {
            var tool = self.selectedTool();
            if (tool && tool !== 'select_feature') return false;
            return feature.properties.resourceinstanceid || self.isSelectable(feature);
        };

        self.isSelectable = function(feature) {
            var selectLayerIds = selectFeatureLayers.map(function(layer) {
                return layer.id;
            });
            return selectLayerIds.indexOf(feature.layer.id) >= 0;
        };

        var addSelectFeatures = function(features) {
            var featureIds = [];
            features.forEach(function(feature) {
                feature.id = uuid.generate();
                feature.properties = {
                    nodeId: self.newNodeId
                };
                self.draw.add(feature);
                featureIds.push(feature.id);
            });
            self.updateTiles();
            if (self.popup) self.popup.remove();
            self.draw.changeMode('simple_select', {
                featureIds: featureIds
            });
            self.selectedFeatureIds(featureIds);
            _.each(self.featureLookup, function(value) {
                value.selectedTool(null);
            });
        };

        self.selectFeature = function(feature) {
            try {
                var geometry = JSON.parse(feature.properties.geojson);
                var newFeature = {
                    "type": "Feature",
                    "properties": {},
                    "geometry": geometry
                };
                addSelectFeatures([newFeature]);
            } catch(e) {
                $.getJSON(feature.properties.geojson, function(data) {
                    addSelectFeatures(data.features);
                });
            }
        };

        var addFromGeoJSON = function(geoJSONString, nodeId) {
            var hint = geojsonhint.hint(geoJSONString);
            var errors = [];
            hint.forEach(function(item) {
                if (item.level !== 'message') {
                    errors.push(item);
                }
            });
            if (errors.length === 0) {
                var geoJSON = JSON.parse(geoJSONString);
                geoJSON.features = geoJSON.features.filter(function(feature) {
                    return feature.geometry;
                });
                if (geoJSON.features.length > 0) {
                    self.map().fitBounds(
                        geojsonExtent(geoJSON),
                        {
                            padding: padding
                        }
                    );
                    geoJSON.features.forEach(function(feature) {
                        feature.id = uuid.generate();
                        if (!feature.properties) feature.properties = {};
                        feature.properties.nodeId = nodeId;
                        self.draw.add(feature);
                    });
                    self.updateTiles();
                }
            }
            return errors;
        };

        self.handleFiles = function(files, nodeId) {
            var errors = [];
            var promises = [];
            for (var i = 0; i < files.length; i++) {
                var extension = files[i].name.split('.').pop();
                if (!['kml', 'json', 'geojson'].includes(extension)) {
                    errors.push({
                        message: 'File unsupported: "' + files[i].name + '"'
                    });
                } else {
                    promises.push(new Promise(function(resolve) {
                        var file = files[i];
                        var extension = file.name.split('.').pop();
                        var reader = new window.FileReader();
                        reader.onload = function(e) {
                            var geoJSON;
                            if (['json', 'geojson'].includes(extension))
                                geoJSON = JSON.parse(e.target.result);
                            else
                                geoJSON = toGeoJSON.kml(
                                    new window.DOMParser()
                                        .parseFromString(e.target.result, "text/xml")
                                );
                            resolve(geoJSON);
                        };
                        reader.readAsText(file);
                    }));
                }
            }
            Promise.all(promises).then(function(results) {
                var geoJSON = {
                    "type": "FeatureCollection",
                    "features": results.reduce(function(features, geoJSON) {
                        features = features.concat(geoJSON.features);
                        return features;
                    }, [])
                };
                errors = errors.concat(
                    addFromGeoJSON(JSON.stringify(geoJSON), nodeId)
                );
                self.featureLookup[nodeId].dropErrors(errors);
            });
        };

        self.dropZoneHandler = function(data, e) {
            var nodeId = data.node.nodeid;
            e.stopPropagation();
            e.preventDefault();
            var files = e.originalEvent.dataTransfer.files;
            self.handleFiles(files, nodeId);
            self.dropZoneLeaveHandler(data, e);
        };

        self.dropZoneOverHandler = function(data, e) {
            e.stopPropagation();
            e.preventDefault();
            e.originalEvent.dataTransfer.dropEffect = 'copy';
        };

        self.dropZoneClickHandler = function(data, e) {
            var fileInput = e.target.parentNode.querySelector('.hidden-file-input input');
            var event = window.document.createEvent("MouseEvents");
            event.initEvent("click", true, false);
            fileInput.dispatchEvent(event);
        };

        self.dropZoneEnterHandler = function(data, e) {
            e.target.classList.add('drag-hover');
        };

        self.dropZoneLeaveHandler = function(data, e) {
            e.target.classList.remove('drag-hover');
        };

        self.dropZoneFileSelected = function(data, e) {
            self.handleFiles(e.target.files, data.node.nodeid);
        };
        self.coordinateReferences = arches.preferredCoordinateSystems;
        self.selectedCoordinateReference = ko.observable(self.coordinateReferences[0].proj4);
        self.coordinates = ko.observableArray();
        var geographic = '+proj=longlat +datum=WGS84 +no_defs", "default';
        self.rawCoordinates = ko.computed(function() {
            return self.coordinates().map(function(coords) {
                var sourceCRS = self.selectedCoordinateReference();
                return proj4(sourceCRS, geographic, [Number(coords[0]()), Number(coords[1]())]);
            });
        }).extend({ throttle: 100 });
        self.rawCoordinates.subscribe(function(rawCoordinates) {
            var selectedFeatureId = self.selectedFeatureIds()[0];
            if (self.coordinateEditing()) {
                if (selectedFeatureId) {
                    var drawFeatures = getDrawFeatures();
                    drawFeatures.forEach(function(feature) {
                        if (feature.id === selectedFeatureId) {
                            if (feature.geometry.type === 'Polygon') {
                                rawCoordinates.push(rawCoordinates[0]);
                                feature.geometry.coordinates[0] = rawCoordinates;
                            } else if (feature.geometry.type === 'Point')
                                feature.geometry.coordinates = rawCoordinates[0];
                            else
                                feature.geometry.coordinates = rawCoordinates;
                        }
                    });
                    self.draw.set({
                        type: 'FeatureCollection',
                        features: drawFeatures
                    });
                    self.updateTiles();
                } else if (rawCoordinates.length >= self.minCoordinates()) {
                    var coordinates = [];
                    var geomType = self.coordinateGeomType();
                    switch (geomType) {
                    case 'Polygon':
                        rawCoordinates.push(rawCoordinates[0]);
                        coordinates = [rawCoordinates];
                        break;
                    case 'Point':
                        coordinates = rawCoordinates[0];
                        break;
                    default:
                        coordinates = rawCoordinates;
                        break;
                    }
                    addSelectFeatures([{
                        type: "Feature",
                        geometry: {
                            type: geomType,
                            coordinates: coordinates
                        }
                    }]);
                }
            }
        });
        self.showCoordinateFeature = function() {
            var selectedFeatureIds = self.selectedFeatureIds();
            var featureId = selectedFeatureIds[0];
            if (featureId) {
                var feature = self.draw.get(featureId);
                self.fitFeatures([feature]);
            }
        };

        self.coordinateEditing = ko.observable(false);
        self.newX = ko.observable();
        self.newY = ko.observable();
        var newCoordinatePair = ko.computed(function() {
            var x = self.newX();
            var y = self.newY();
            return [x, y];
        });
        self.focusLatestY = ko.observable(true);
        var getNewCoordinatePair = function(coords) {
            var newCoords = [
                ko.observable(coords[0]),
                ko.observable(coords[1])
            ];
            newCoords.forEach(function(value) {
                value.subscribe(function(newValue) {
                    if ([undefined, null, ""].includes(newValue)) value(0);
                });
            });
            return newCoords;
        };
        newCoordinatePair.subscribe(function(coords) {
            if (coords[0] && coords[1]) {
                self.coordinates.push(getNewCoordinatePair(coords));
                self.newX(undefined);
                self.newY(undefined);
                self.focusLatestY(true);
            }
        });
        var updateCoordinatesFromFeature = function(feature) {
            var sourceCoordinates = [];
            if (feature.geometry.type === 'Polygon') {
                sourceCoordinates = [];
                for (var i = 0; i < feature.geometry.coordinates[0].length - 1; i++) {
                    sourceCoordinates.push(feature.geometry.coordinates[0][i]);
                }
            } else if (feature.geometry.type === 'Point')
                sourceCoordinates = [feature.geometry.coordinates];
            else sourceCoordinates = feature.geometry.coordinates;
            self.coordinateGeomType(feature.geometry.type);
            self.coordinates(sourceCoordinates.map(function(coords) {
                var newCoords = getNewCoordinatePair(coords);
                transformCoordinatePair(newCoords, geographic);
                return newCoords;
            }));
        };
        var transformCoordinatePair = function(coords, sourceCRS) {
            var targetCRS = self.selectedCoordinateReference();
            var transformedCoordinates = proj4(sourceCRS, targetCRS, [Number(coords[0]()), Number(coords[1]())]);
            coords[0](transformedCoordinates[0]);
            coords[1](transformedCoordinates[1]);
        };
        var previousCRS = self.selectedCoordinateReference();
        var transformCoordinates = function() {
            var targetCRS = self.selectedCoordinateReference();
            self.coordinates().forEach(function(coords) {
                transformCoordinatePair(coords, previousCRS);
            });
            previousCRS = targetCRS;
        };
        self.selectedCoordinateReference.subscribe(transformCoordinates);

        self.coordinateGeomType = ko.observable();
        self.coordinateEditing.subscribe(function(editing) {
            self.coordinateGeomType(null);
            var selectedTool = self.selectedTool();
            switch (selectedTool) {
            case 'draw_point':
                self.coordinateGeomType('Point');
                break;
            case 'draw_line_string':
                self.coordinateGeomType('LineString');
                break;
            case 'draw_polygon':
                self.coordinateGeomType('Polygon');
                break;
            default:
                break;
            }
            var selectedFeatureIds = self.selectedFeatureIds();
            var featureId = selectedFeatureIds[0];
            self.focusLatestY(false);
            self.coordinates([]);
            self.newX(undefined);
            self.newY(undefined);
            if (editing) {
                var selectConfig;
                if (selectedFeatureIds.length > 0) {
                    selectConfig = {
                        featureIds: [featureId]
                    };
                    self.selectedFeatureIds([featureId]);
                    var feature = self.draw.get(featureId);
                    updateCoordinatesFromFeature(feature);
                }
                if (selectedTool) {
                    self.draw.trash();
                }
                self.draw.changeMode('simple_select', selectConfig);
                _.each(self.featureLookup, function(value) {
                    value.selectedTool(null);
                });
            }
        });
        self.hideNewCoordinates = ko.computed(function() {
            var geomType = self.coordinateGeomType();
            var coordCount = self.coordinates().length;
            return geomType === 'Point' && coordCount > 0;
        });

        self.minCoordinates = ko.computed(function() {
            var geomType = self.coordinateGeomType();
            var minCoordinates;
            switch (geomType) {
            case 'Point':
                minCoordinates = 1;
                break;
            case 'LineString':
                minCoordinates = 2;
                break;
            case 'Polygon':
                minCoordinates = 3;
                break;
            default:
                break;
            }
            return minCoordinates;
        });

        self.allowDeleteCoordinates = ko.computed(function() {
            return self.coordinates().length > self.minCoordinates();
        });

        self.editCoordinates = function() {
            self.coordinateEditing(true);
        };

        self.canEditCoordinates = ko.computed(function() {
            var featureId = self.selectedFeatureIds()[0];
            if (featureId) {
                var feature = self.draw.get(featureId);
                return ['Point', 'LineString', 'Polygon'].includes(feature.geometry.type);
            } else {
                var selectedTool = self.selectedTool();
                return ['draw_point', 'draw_line_string', 'draw_polygon'].includes(selectedTool);
            }
        });

        self.selectedFeatureIds.subscribe(function(ids) {
            if (ids.length === 0) self.coordinateEditing(false);
            else if (self.canEditCoordinates()) {
                var feature = self.draw.get(ids[0]);
                updateCoordinatesFromFeature(feature);
            }
        });

        self.bufferFeature = ko.computed(function() {
            return self.selectedFeatureIds()[0];
        });
        var getBufferFeature = function() {
            var featureId = self.bufferFeature();
            if (featureId) {
                return self.draw.get(featureId);
            }
        };
        self.bufferParams = ko.computed(function() {
            var bufferFeature = getBufferFeature();
            if (bufferFeature && self.bufferNodeId()) return {
                "geometry": bufferFeature.geometry,
                "buffer": {
                    "width": parseFloat(self.bufferDistance()),
                    "unit": self.bufferUnits()
                }
            };
        });

        self.bufferFeature.subscribe(function(bufferFeature) {
            if (!bufferFeature) self.bufferNodeId(false);
        });
        self.updateBufferFeature = function() {
            var bufferParams = self.bufferParams();
            var bufferFeature = getBufferFeature();
            if (bufferParams && bufferFeature) {
                bufferParams.geometry = bufferFeature.geometry;
                window.fetch(
                    arches.urls.buffer +
                    '?filter=' +
                    JSON.stringify(bufferParams)
                ).then(function(response) {
                    if (response.ok) {
                        return response.json();
                    }
                }).then(function(json) {
                    var bufferFeature = getBufferFeature();
                    self.bufferResult({
                        type: 'Feature',
                        id: uuid.generate(),
                        geometry: json,
                        properties: {
                            nodeId: bufferFeature.properties.nodeId
                        }
                    });
                });
            } else self.bufferResult(undefined);

        };
        self.bufferParams.subscribe(self.updateBufferFeature);


        if (self.card) {
            self.card.map = self.map;
        }

        self.addBufferResult = function() {
            var bufferResult = self.bufferResult();
            if (self.bufferAddNew()) {
                var dirty = ko.unwrap(self.tile.dirty);
                var nodeId = self.bufferNodeId();
                var addBufferResultAsNew = function() {
                    var updateNewTile = self.card.selected.subscribe(function() {
                        var fc = {
                            "type": "FeatureCollection",
                            "features": [bufferResult]
                        };
                        self.card.getNewTile().data[nodeId](fc);
                        self.card.map.subscribe(function(map) {
                            map.fitBounds(
                                geojsonExtent(fc),
                                {
                                    duration: 0,
                                    padding: padding
                                }
                            );
                        });
                        updateNewTile.dispose();
                    });
                    self.card.selected(true);
                };
                if (dirty) self.saveTile(addBufferResultAsNew);
                else addBufferResultAsNew();
            } else {
                self.draw.add(bufferResult);
                self.bufferNodeId(false);
                self.updateTiles();
                self.editFeature(bufferResult);
                self.fitFeatures([bufferResult]);
            }
        };
    };
    return viewModel;
});
