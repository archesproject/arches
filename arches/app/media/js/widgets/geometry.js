define([
    'jquery',
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'mapbox-gl',
    'mapbox-gl-draw',
    'knockout-mapping',
    'select2v4',
    'bindings/select2v4',
    'bindings/fadeVisible',
    'bindings/mapbox-gl',
    'bindings/chosen'
], function($, ko, _, WidgetViewModel, arches, mapboxgl, Draw, koMapping) {
    /**
     * knockout components namespace used in arches
     * @external "ko.components"
     * @see http://knockoutjs.com/documentation/component-binding.html
     */

    /**
     * registers a geometry-widget component for use in forms
     * @function external:"ko.components".geometry-widget
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
    return ko.components.register('geometry-widget', {
        viewModel: function(params) {
            var self = this;
            var resourceIcon = 'fa fa-map-marker';
            var resourceName = 'resource';
            this.reportHeader = params.type === 'report-header' ? true : false;
            this.configType = params.reportHeader || 'header';
            params.configKeys = ['zoom', 'centerX', 'centerY', 'geocoder', 'basemap', 'geometryTypes', 'pitch', 'bearing', 'geocodePlaceholder'];
            WidgetViewModel.apply(this, [params]);

            if (!this.configForm && params.graph !== undefined) {
                resourceIcon = params.graph.iconclass;
                resourceName = params.graph.name;
            }

            this.selectedBasemap = this.basemap;

            this.mapToolsExpanded = ko.observable(false);
            this.geocodeShimAdded = ko.observable(false);
            this.mapToolsExpanded.subscribe(function(expanded) {
                self.geocodeShimAdded(expanded);
            });
            this.layers = _.clone(arches.mapLayers);
            this.geocoderOptions = ko.observableArray([{
                'id': 'BingGeocoder',
                'name': 'Bing'
            }, {
                'id': 'MapzenGeocoder',
                'name': 'Mapzen'
            }]);

            this.geocodeUrl = arches.urls.geocoder;
            this.geocodeResponseOption = ko.observable();
            this.selectedItems = ko.observableArray()
            this.mapControlPanels = {
                basemaps: ko.observable(false),
                overlays: ko.observable(true),
                maptools: ko.observable(true),
                legend: ko.observable(true)
            };


            this.defineResourceLayer = function(resource) {
                var resourceLayer = {
                    name: resourceName,
                    layer_definitions: [{
                        "id": "resource-poly",
                        "source": "resource",
                        "type": "fill",
                        "layout": {},
                        "filter": ["!in", "$type", "LineString"],
                        "paint": {
                            "fill-color": "#fb6017",
                            "fill-opacity": 0.8
                        }
                    }, {
                        "id": "resource-point",
                        "source": "resource",
                        "type": "circle",
                        "layout": {},
                        "filter": ["!in", "$type", "LineString", "Polygon"],
                        "paint": {
                            "circle-radius": 5,
                            "circle-color": "#fb6017",
                            "circle-opacity": 0.8
                        }
                    }, {
                        "id": "resource-line",
                        "source": "resource",
                        "type": "line",
                        "layout": {},
                        "paint": {
                            "line-color": "#fb6017",
                            "line-opacity": 0.8,
                            "line-width": 2.5
                        }
                    }],
                    isoverlay: true,
                    sortorder: 4,
                    icon: resourceIcon
                };
                return resourceLayer;
            }


            this.addInitialLayers = function() {
                this.layers.push(this.defineResourceLayer());
                var initialLayers = [];
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

            this.editingToolIcons = {
                Point: 'ion-location',
                Line: 'ion-steam',
                Polygon: 'fa fa-pencil-square-o',
                Delete: 'ion-trash-a'
            }

            this.setupMap = function(map) {

                var self = this;
                var draw = Draw();
                this.map = map;
                this.draw = draw;
                this.map.addControl(draw);
                this.redrawGeocodeLayer = function() {
                    var cacheLayer = map.getLayer('geocode-point');
                    map.removeLayer('geocode-point');
                    map.addLayer(cacheLayer, 'gl-draw-active-line.hot');
                }

                this.map.on('load', function() {
                    if (!self.configForm) {
                        var source = self.map.getSource('resource')
                        var features = [];
                        var result = {
                            "type": "FeatureCollection",
                            "features": []
                        };
                        if (self.reportHeader === true && !ko.isObservable(self.value)) {
                            self.value.forEach(function(tile) {
                                _.each(tile.data, function(val, key) {
                                    if (_.contains(val, 'FeatureCollection')) {
                                        result.features = _.union(result.features, val.features)
                                    }
                                }, self);
                            }, self)
                            source.setData(result);
                        } else if (self.reportHeader === false && !ko.isObservable(self.value)) {
                            source.setData(koMapping.toJS(self.value))
                        } else { //if values are for a form widget...
                            if (_.isObject(self.value())) { //confirm value is not "", null, or undefined
                                source.setData(koMapping.toJS(self.value))
                            }
                        };
                    }
                });

                this.selectedItems.subscribe(function(e) {
                    var coords = e.geometry.coordinates;
                    this.map.getSource('geocode-point').setData(e.geometry);
                    this.redrawGeocodeLayer();
                    var centerPoint = new mapboxgl.LngLat(coords[0], coords[1])
                    this.map.flyTo({
                        center: centerPoint
                    });
                }, this);

                this.selectEditingTool = function(val, e) {
                    switch (val) {
                        case 'Point':
                            draw.changeMode('draw_point');
                            break;
                        case 'Line':
                            draw.changeMode('draw_line_string');
                            break;
                        case 'Polygon':
                            draw.changeMode('draw_polygon');
                            break;
                        default:
                            draw.trash();
                    }
                }

                this.dataReturn =
                    function(term, page) {
                        return {
                            q: term,
                            geocoder: self.geocoder()
                        };
                    }

                this.selectSetup = {
                    ajax: {
                        url: arches.urls.geocoder,
                        dataType: 'json',
                        quietMillis: 250,
                        data: this.dataReturn,
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

                this.overlays = ko.observableArray(this.createOverlays())

                this.basemaps = _.filter(arches.mapLayers, function(baselayer) {
                    return baselayer.isoverlay === false
                });

                this.setBasemap = function(basemapType) {
                    var lowestOverlay = _.last(_.last(overlays).layer_definitions);
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
                            currentDrawing.features.forEach(function(feature) {
                                self.value.features.push(feature)
                            })
                        } else {
                            self.value(currentDrawing)
                        }
                    }
                }

                this.map.on('moveend', this.updateConfigs());
                this.map.on('draw.create', this.saveGeometries())
                this.map.on('draw.delete', this.saveGeometries())

                this.overlays.subscribe(function(overlays) {
                    var anchorLayer = 'gl-draw-active-line.hot';
                    for (var i = overlays.length; i-- > 0;) { //Using a conventional loop because we want to go backwards over the array without creating a copy
                        overlays[i].layer_definitions.forEach(function(layer) {
                            map.removeLayer(layer.id)
                        })
                    }
                    for (var i = overlays.length; i-- > 0;) {
                        overlays[i].layer_definitions.forEach(function(layer) {
                            map.addLayer(layer, anchorLayer);
                            map.setPaintProperty(layer.id, layer.type + '-opacity', overlays[i].opacity() / 100.0);
                        })
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
            require: 'text!widget-templates/geometry'
        }
    });
});
