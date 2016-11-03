define([
    'jquery',
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'mapbox-gl',
    'mapbox-gl-draw',
    'knockout-mapping',
    'geojson-extent',
    'select2',
    'bindings/select2v4',
    'bindings/fadeVisible',
    'bindings/mapbox-gl',
    'bindings/chosen',
    'bindings/color-picker'
], function($, ko, _, WidgetViewModel, arches, mapboxgl, Draw, koMapping, geojsonExtent) {
    /**
     * knockout components namespace used in arches
     * @external "ko.components"
     * @see http://knockoutjs.com/documentation/component-binding.html
     */

    /**
     * registers a map-widget component for use in forms
     * @function external:"ko.components".map-widget
     * @param {object} params
     * @param {boolean} params.value - the value being managed
     * @param {object} params.config -
     * @param {string} params.config.zoom - map zoom level
     * @param {string} params.config.centerX - map center longitude
     * @param {string} params.config.centerY - map center latitude
     * @param {string} params.config.geocoder - the text string id of the geocoder api (currently MapzenGeocoder or BingGeocoder).
     * @param {string} params.config.basemap - the layer name of the selected basemap to be shown in the map
     * @param {string} params.config.geometryTypes - the geometry types available for a user to edit
     * @param {string} params.config.pitch - the pitch of the map in degrees
     * @param {string} params.config.bearing - the bearing of the map in degrees with north at 0
     */
    return ko.components.register('map-widget', {
        viewModel: function(params) {
            var self = this;
            this.reportHeader = params.type === 'report-header' ? true : false;
            this.resourceEditor = params.type === 'resource-editor' ? true : false;
            this.configType = params.reportHeader || 'header';
            params.configKeys = [
                'zoom',
                'centerX',
                'centerY',
                'geocoder',
                'basemap',
                'geometryTypes',
                'pitch',
                'bearing',
                'geocodePlaceholder',
                'geocoderVisible',
                'minZoom',
                'maxZoom',
                'resourceColor',
                'resourcePointSize',
                'resourceLineWidth',
                'featureEditingDisabled',
                'overlayList'
            ];

            WidgetViewModel.apply(this, [params]);

            if (params.graph !== undefined) {
                this.resourceIcon = params.graph.get('iconclass');
                this.resourceName = params.graph.get('name');
                if (this.resourceColor() === null) {
                    this.resourceColor(params.graph.get('mapfeaturecolor'));
                }
                if (this.resourcePointSize() === null) {
                    this.resourcePointSize(params.graph.get('mappointsize'));
                } else {
                    this.resourcePointSize(Number(this.resourcePointSize()))
                }
                if (this.resourceLineWidth() === null) {
                    this.resourceLineWidth(params.graph.get('maplinewidth'));
                } else {
                    this.resourceLineWidth(Number(this.resourceLineWidth()))
                }
            }

            this.selectedBasemap = this.basemap;
            this.drawMode = ko.observable();
            this.selectedFeatureType = ko.observable();
            this.mapToolsExpanded = ko.observable(false);
            this.overlaySelectorClosed = ko.observable(true);
            this.geocodeShimAdded = ko.observable(false);
            this.mapToolsExpanded.subscribe(function(expanded) {
                self.geocodeShimAdded(expanded);
            });

            this.toggleOverlaySelector = function(e){
              this.overlaySelectorClosed(!this.overlaySelectorClosed());
            };

            this.anchorLayerId = 'gl-draw-point.cold'; //Layers are added below this drawing layer
            this.layers = _.clone(arches.mapLayers);

            this.geocoderOptions = ko.observableArray([{
                'id': 'BingGeocoder',
                'name': 'Bing'
            }, {
                'id': 'MapzenGeocoder',
                'name': 'Mapzen'
            }]);

            this.geometryTypeDetails = {
                Point: {
                    name: 'Point',
                    icon: 'ion-location',
                    drawMode: 'draw_point',
                    active: ko.observable(false)
                },
                Line: {
                    name: 'Line',
                    icon: 'ion-steam',
                    drawMode: 'draw_line_string',
                    active: ko.observable(false)
                },
                Polygon: {
                    name: 'Polygon',
                    icon: 'fa fa-pencil-square-o',
                    drawMode: 'draw_polygon',
                    active: ko.observable(false)
                }
            }

            this.geocodeUrl = arches.urls.geocoder;
            this.geocodeResponseOption = ko.observable();
            this.selectedGeocodeItems = ko.observableArray()
            this.mapControlPanels = {
                basemaps: ko.observable(false),
                overlays: ko.observable(true),
                maptools: ko.observable(true),
                legend: ko.observable(true)
            };

            this.defineResourceLayer = function() {
                var resourceLayer = {
                    name: this.resourceName,
                    layer_definitions: [{
                        "id": "resource-poly",
                        "source": "resource",
                        "type": "fill",
                        "layout": {},
                        "filter": ["!in", "$type", "LineString"],
                        "paint": {
                            "fill-color": this.resourceColor(),
                            "fill-opacity": 0.8
                        }
                    }, {
                        "id": "resource-point",
                        "source": "resource",
                        "type": "circle",
                        "layout": {},
                        "filter": ["!in", "$type", "LineString", "Polygon"],
                        "paint": {
                            "circle-radius": this.resourcePointSize(),
                            "circle-color": this.resourceColor(),
                            "circle-opacity": 0.8
                        }
                    }, {
                        "id": "resource-line",
                        "source": "resource",
                        "type": "line",
                        "layout": {},
                        "paint": {
                            "line-color": this.resourceColor(),
                            "line-opacity": 0.8,
                            "line-width": this.resourceLineWidth()
                        }
                    }],
                    isoverlay: true,
                    sortorder: 4,
                    icon: this.resourceIcon
                };
                return resourceLayer;
            }

            this.addInitialLayers = function() {
                var initialLayers = [];
                if (this.reportHeader) {
                  this.layers.unshift(this.defineResourceLayer());
                }
                var overlayLayers = _.sortBy(_.where(this.layers, {
                    isoverlay: true
                }), 'sortorder').reverse();

                this.layers.forEach(function(mapLayer) {
                    if (mapLayer.name === this.basemap()) {
                        _.each(mapLayer.layer_definitions, function(layer) {
                            initialLayers.push(layer);
                        });
                    }
                }, this);

                overlayLayers.forEach(function(overlayLayer) {
                    _.each(overlayLayer.layer_definitions, function(layer) {
                        initialLayers.push(layer);
                    });
                })

                initialLayers.push({
                    "id": "geocode-point",
                    "source": "geocode-point",
                    "type": "circle",
                    "paint": {
                        "circle-radius": 5,
                        "circle-color": "red"
                    }
                });

                return initialLayers;
            }

            this.toggleGeocoder = function(self, evt) {
                if (self.geocoderVisible() === true) {
                    self.geocoderVisible(false)
                } else {
                    self.geocoderVisible(true)
                }
            }

            this.geomTypeSelectSetup = {
                minimumInputLength: 0,
                multiple: true,
                placeholder: "Available Geometry Types",
                data: [{
                    text: 'Point',
                    id: 'Point'
                }, {
                    text: 'Line',
                    id: 'Line'
                }, {
                    text: 'Polygon',
                    id: 'Polygon'
                }]
            };

            this.setupMap = function(map) {
                var self = this;
                var draw = Draw({
                    controls: {
                        trash: false //if true, the backspace key is inactivated in the geocoder input
                    },
                    styles: [{
                        "id": "gl-draw-point-active",
                        "type": "circle",
                        "filter": ["all", ["!=", "meta", "vertex"],
                            ["==", "$type", "Point"],
                            ["!=", "mode", "static"]
                        ],
                        "paint": {
                            "circle-radius": 5,
                            "circle-color": "#FFF"
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-point",
                        "type": "circle",
                        "layout": {},
                        "filter": ["all", ["!in", "$type", "LineString", "Polygon"],
                            ["!=", "mode", "static"]
                        ],
                        "paint": {
                            "circle-radius": this.resourcePointSize(),
                            "circle-color": this.resourceColor(),
                            "circle-opacity": 0.8
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-line",
                        "type": "line",
                        "filter": ["all", ["==", "$type", "LineString"],
                            ["!=", "mode", "static"]
                        ],
                        "layout": {
                            "line-cap": "round",
                            "line-join": "round"
                        },
                        "paint": {
                            "line-color": this.resourceColor(),
                            // "line-dasharray": [0.2, 2],
                            "line-width": this.resourceLineWidth()
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-polygon-fill",
                        "type": "fill",
                        "filter": ["all", ["==", "$type", "Polygon"],
                            ["!=", "mode", "static"]
                        ],
                        "paint": {
                            "fill-color": this.resourceColor(),
                            "fill-outline-color": this.resourceColor(),
                            "fill-opacity": 0.1
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-polygon-stroke-active",
                        "type": "line",
                        "filter": ["all", ["==", "$type", "Polygon"],
                            ["!=", "mode", "static"]
                        ],
                        "layout": {
                            "line-cap": "round",
                            "line-join": "round"
                        },
                        "paint": {
                            "line-color": this.resourceColor(),
                            // "line-dasharray": [0.2, 2],
                            "line-width": this.resourceLineWidth()
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-polygon-and-line-vertex-halo-active",
                        "type": "circle",
                        "filter": ["all", ["==", "meta", "vertex"],
                            ["==", "$type", "Point"],
                            ["!=", "mode", "static"]
                        ],
                        "paint": {
                            "circle-radius": 5,
                            "circle-color": "#FFF"
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-polygon-and-line-vertex-active",
                        "type": "circle",
                        "filter": ["all", ["==", "meta", "vertex"],
                            ["==", "$type", "Point"],
                            ["!=", "mode", "static"]
                        ],
                        "paint": {
                            "circle-radius": 3,
                            "circle-color": this.resourceColor(),
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-polygon-and-line-midpoint-halo-active",
                        "type": "circle",
                        "filter": ["all", ["==", "meta", "midpoint"],
                            ["==", "$type", "Point"],
                            ["!=", "mode", "static"]
                        ],
                        "paint": {
                            "circle-radius": 4,
                            "circle-color": "#FFF"
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-polygon-and-line-midpoint-active",
                        "type": "circle",
                        "filter": ["all", ["==", "meta", "midpoint"],
                            ["==", "$type", "Point"],
                            ["!=", "mode", "static"]
                        ],
                        "paint": {
                            "circle-radius": 2,
                            "circle-color": this.resourceColor(),
                        },
                        "interactive": true
                    }, {
                        "id": "gl-draw-line-static",
                        "type": "line",
                        "filter": ["all", ["==", "$type", "LineString"],
                            ["==", "mode", "active"]
                        ],
                        "layout": {
                            "line-cap": "round",
                            "line-join": "round"
                        },
                        "paint": {
                            "line-color": "#000",
                            "line-width": this.resourceLineWidth()
                        },
                        "interactive": true
                    }]
                });

                this.map = map;
                this.draw = draw;
                this.map.addControl(draw);
                this.redrawGeocodeLayer = function() {
                    var cacheLayer = map.getLayer('geocode-point');
                    map.removeLayer('geocode-point');
                    map.addLayer(cacheLayer, this.anchorLayerId);
                }

                this.map.on('load', function() {
                    if (!self.configForm) {
                        var source = self.map.getSource('resource')
                        var features = [];
                        var result = {
                            "type": "FeatureCollection",
                            "features": []
                        };
                        var data = null;
                        if (self.reportHeader === true && !ko.isObservable(self.value)) {
                            self.value.forEach(function(tile) {
                                _.each(tile.data, function(val, key) {
                                    if (_.contains(val, 'FeatureCollection')) {
                                        result.features = _.union(result.features, val.features)
                                    }
                                }, self);
                            }, self)
                            data = result;
                            source.setData(data)
                            _.each(['resource-poly', 'resource-line', 'resource-point'], function(layerId) { //clear and add resource layers so that they are on top of map
                                    var cacheLayer = self.map.getLayer(layerId);
                                    self.map.removeLayer(layerId);
                                    self.map.addLayer(cacheLayer, self.anchorLayerId)
                                }, self)

                        } else if (self.reportHeader === false && !ko.isObservable(self.value)) {
                            data = koMapping.toJS(self.value);
                            self.loadGeometriesIntoDrawLayer()
                        } else { //if values are for a form widget...
                            if (_.isObject(self.value())) { //confirm value is not "", null, or undefined
                                data = koMapping.toJS(self.value);
                            }
                        };
                        if (data) {
                            var bounds = new mapboxgl.LngLatBounds(geojsonExtent(data));
                            var tr = this.transform;
                            var nw = tr.project(bounds.getNorthWest());
                            var se = tr.project(bounds.getSouthEast());
                            var size = se.sub(nw);
                            var scaleX = (tr.width - 80) / size.x;
                            var scaleY = (tr.height - 80) / size.y;

                            var options = {
                                center: tr.unproject(nw.add(se).div(2)),
                                zoom: Math.min(tr.scaleZoom(tr.scale * Math.min(scaleX, scaleY)), Infinity)
                            };
                            self.map.jumpTo(options);
                        }
                    }
                });

                this.loadGeometriesIntoDrawLayer = function() {
                    this.draw.add(koMapping.toJS(self.value));
                };

                this.updateDrawLayerPaintProperties = function(paintProperties, val, isNumber) {
                    var val = isNumber ? Number(val) : val; //point size and line width must be number types
                    _.each(this.draw.options.styles, function(style) {
                        var paint = this.map.getLayer(style.id).paint
                        var self = this;
                        paintProperties.forEach(function(prop) {
                            if (paint.hasOwnProperty(prop)) {
                                self.map.setPaintProperty(style.id, prop, val)
                            }
                        })
                    }, this)
                }

                this.resourceColor.subscribe(function(e) {
                    this.updateDrawLayerPaintProperties(['fill-outline-color', 'fill-color', 'circle-color', 'line-color'], e)
                }, this);

                this.resourcePointSize.subscribe(function(e) {
                    this.updateDrawLayerPaintProperties(['circle-radius'], e, true)
                }, this);

                this.resourceLineWidth.subscribe(function(e) {
                    this.updateDrawLayerPaintProperties(['line-width'], e, true)
                }, this);

                this.selectedGeocodeItems.subscribe(function(e) {
                    var coords = e.geometry.coordinates;
                    this.map.getSource('geocode-point').setData(e.geometry);
                    this.redrawGeocodeLayer();
                    var centerPoint = new mapboxgl.LngLat(coords[0], coords[1])
                    this.map.flyTo({
                        center: centerPoint
                    });
                }, this);

                this.selectEditingTool = function(self, val) {

                    _.each(self.geometryTypeDetails, function(geomtype) {
                        if (geomtype.name === val) {
                            self.geometryTypeDetails[val].active(!self.geometryTypeDetails[val].active())
                        } else {
                            self.geometryTypeDetails[geomtype.name].active(false)
                        }
                    });

                    if (self.geometryTypeDetails[val] === undefined) { //it has no geom type, so must be trash
                        self.draw.trash();
                        self.drawMode(null);
                    } else {
                        if (!self.drawMode()) {
                            self.draw.changeMode(self.geometryTypeDetails[val].drawMode);
                            self.drawMode(self.geometryTypeDetails[val].drawMode);
                        } else if (self.geometryTypeDetails[val].drawMode === self.drawMode()) {
                            self.draw.changeMode('simple_select')
                            self.drawMode(undefined);
                        } else {
                            self.draw.changeMode(self.geometryTypeDetails[val].drawMode);
                            self.drawMode(self.geometryTypeDetails[val].drawMode);
                        }
                    }

                }

                this.geocodeQueryPayload =
                    function(term, page) {
                        return {
                            q: term,
                            geocoder: self.geocoder()
                        };
                    }

                this.geocodeSelectSetup = {
                    ajax: {
                        url: arches.urls.geocoder,
                        dataType: 'json',
                        quietMillis: 250,
                        data: this.geocodeQueryPayload,
                        results: function(data, page) {
                            return {
                                results: data.results
                            };
                        },
                        cache: true
                    },
                    minimumInputLength: 4,
                    multiple: false,
                    maximumSelectionSize: 1,
                    placeholder: this.geocodePlaceholder()
                };

                this.createOverlays = function() {
                    var overlays =
                        _.each(_.where(this.layers, {
                            isoverlay: true
                        }), function(overlay) {
                            _.extend(overlay, {
                                opacity: ko.observable(100),
                                color: _.filter(overlay.layer_definitions[0].paint, function(prop, key) {
                                    if (key.includes('-color')) {
                                        return prop
                                    };
                                })[0],
                                showingTools: ko.observable(false),
                                invisible: ko.observable(false),
                                checkedOutOfLibrary: ko.observable(false),
                                toggleOverlayTools: function(e) {
                                    this.showingTools(!this.showingTools());
                                },
                                toggleOverlayVisibility: function(e) {
                                    this.opacity() > 0.0 ? this.opacity(0.0) : this.opacity(100.0);
                                },
                                updateOpacity: function(val) {
                                    val > 0.0 ? this.invisible(false) : this.invisible(true);
                                    this.layer_definitions.forEach(function(layer) {
                                        this.setPaintProperty(layer.id, layer.type + '-opacity', Number(val) / 100.0);
                                    }, map)
                                }
                            });
                            overlay.opacity.subscribe(function(value) {
                                overlay.updateOpacity(value);
                            });
                        });

                    return overlays;
                }

                this.overlayLibrary = ko.observableArray(this.createOverlays())
                this.overlays = ko.observableArray()

                this.exchangeOverlay = function(e) {
                  if (this.checkedOutOfLibrary() === true) {
                    self.overlays.remove(this)
                  } else {
                    self.overlays.push(this);
                  }
                  this.checkedOutOfLibrary(!this.checkedOutOfLibrary())
                }

                this.basemaps = _.filter(arches.mapLayers, function(baselayer) {
                    return baselayer.isoverlay === false
                });

                this.setBasemap = function(basemapType) {
                    var lowestOverlay = _.first(_.last(this.overlays()).layer_definitions);
                    this.basemaps.forEach(function(basemap) {
                        var self = this;
                        if (basemap.name === basemapType.name) {
                            basemap.layer_definitions.forEach(function(layer) {
                                self.map.addLayer(layer, lowestOverlay.id)
                            })
                        } else {
                            basemap.layer_definitions.forEach(function(layer) {
                                if (self.map.getLayer(layer.id) !== undefined) {
                                    self.map.removeLayer(layer.id);
                                }
                            })
                        }
                    }, this)
                };

                this.updateConfigs = function() {
                    var self = this;
                    return function() {
                        var mapCenter = this.getCenter()
                        var zoom = self.map.getZoom()
                        if (self.zoom() !== zoom) {
                            self.zoom(zoom);
                        };
                        self.centerX(mapCenter.lng);
                        self.centerY(mapCenter.lat);
                        self.bearing(this.getBearing());
                        self.pitch(this.getPitch());
                    }
                }

                this.saveGeometries = function() {
                    var self = this;
                    return function() {
                        var currentDrawing = self.draw.getAll()
                        if (self.value.features !== undefined) {
                            _.each(self.value.features(), function(feature) {
                                self.value.features.pop()
                            });
                            currentDrawing.features.forEach(function(feature) {
                                self.value.features.push(feature)
                            })
                        } else {
                            self.value(currentDrawing)
                        }
                    }
                }

                this.updateDrawMode = function(e) {
                    var self = this;
                    return function(e) {
                        var selectedFeatureType;
                        if (_.contains(['draw_point', 'draw_line_string', 'draw_polygon'], self.drawMode()) && self.drawMode() !== self.draw.getMode()) {
                            self.draw.changeMode(self.drawMode())
                        } else {
                            self.drawMode(self.draw.getMode());
                            if (self.draw.getSelectedIds().length > 0) {
                                selectedFeatureType = self.draw.get(self.draw.getSelectedIds()[0]).geometry.type;
                                self.selectedFeatureType(selectedFeatureType === 'LineString' ? 'line' : selectedFeatureType.toLowerCase());
                            } else {
                                if (self.draw.getMode().endsWith("select")) {
                                    self.drawMode(undefined);
                                };
                            }
                        }
                    }
                }

                this.map.on('moveend', this.updateConfigs());
                this.map.on('draw.create', this.saveGeometries())
                this.map.on('draw.update', this.saveGeometries())
                this.map.on('draw.delete', this.saveGeometries())
                this.map.on('click', this.updateDrawMode())

                this.overlays.subscribe(function(overlays) {
                    for (var i = overlays.length; i-- > 0;) { //Using a conventional loop because we want to go backwards over the array
                        overlays[i].layer_definitions.forEach(function(layer) {
                            map.removeLayer(layer.id)
                        })
                    }
                    for (var i = overlays.length; i-- > 0;) {
                        overlays[i].layer_definitions.forEach(function(layer) {
                            map.addLayer(layer, this.anchorLayerId);
                            map.setPaintProperty(layer.id, layer.type + '-opacity', overlays[i].opacity() / 100.0);
                        }, this)
                    }
                    this.redrawGeocodeLayer();
                }, this)
            }

            this.onGeocodeSelection = function(val, e) {
                this.geocoder(e.currentTarget.value)
            }

            this.toggleMapTools = function(data, event) {
                data.mapToolsExpanded(!data.mapToolsExpanded());
            }

            this.toggleMapControlPanels = function(data, event) {
                var panel = data;
                _.each(self.mapControlPanels, function(panelValue, panelName) {
                    panelName === panel ? panelValue(false) : panelValue(true);
                });
            }

            this.moveOverlay = function(overlay, direction) {
                var overlays = ko.utils.unwrapObservable(self.overlays);
                var source = ko.utils.arrayIndexOf(overlays, overlay);
                var target = (direction === 'up') ? source - 1 : source + 1;

                if (target >= 0 && target < overlays.length) {
                    self.overlays.valueWillMutate();

                    overlays.splice(source, 1);
                    overlays.splice(target, 0, overlay);

                    self.overlays.valueHasMutated();
                }
            };

            this.sources = _.clone(arches.mapSources);
            this.sources["resource"] = {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            };

            this.mapStyle = {
                "version": 8,
                "name": "Basic",
                "metadata": {
                    "mapbox:autocomposite": true,
                    "mapbox:type": "template"
                },
                "sources": this.sources,
                "sprite": "mapbox://sprites/mapbox/basic-v9",
                "glyphs": "mapbox://fonts/mapbox/{fontstack}/{range}.pbf",
                "layers": []
            };

            this.mapStyle.layers = this.addInitialLayers();

            this.selectBasemap = function(val) {
                self.basemap(val.name)
                self.setBasemap(val);
            }
        },
        template: {
            require: 'text!widget-templates/map'
        }
    });
});
