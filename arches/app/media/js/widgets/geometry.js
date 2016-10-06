define([
    'jquery',
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'mapbox-gl',
    'plugins/mapbox-gl-draw',
    'map/mapbox-style',
    'bindings/fadeVisible',
    'bindings/mapbox-gl',
    'bindings/chosen',
    'bindings/ajax-chosen'
], function($, ko, _, WidgetViewModel, arches, mapboxgl, Draw, mapStyle) {
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
     * @param {string} params.config.pitch - the bearing of the map in degrees with north at 0
     */
    return ko.components.register('geometry-widget', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['zoom', 'centerX', 'centerY', 'geocoder', 'basemap', 'geometryTypes', 'pitch', 'bearing'];
            WidgetViewModel.apply(this, [params]);
            this.selectedBasemap = this.basemap;

            this.mapToolsExpanded = ko.observable(false);
            this.geocodeShimAdded = ko.observable(false);
            this.mapToolsExpanded.subscribe(function(expanded) {
                self.geocodeShimAdded(expanded);
            });

            this.geocoderOptions = ko.observableArray([{
                'id': 'BingGeocoder',
                'name': 'Bing'
            }, {
                'id': 'MapzenGeocoder',
                'name': 'Mapzen'
            }]);

            this.geocodeUrl = arches.urls.geocoder;
            this.geocodePoint = ko.observable();
            this.geocodeResponseOptions = ko.observable();
            this.mapControlPanels = {
                basemaps: ko.observable(false),
                overlays: ko.observable(true),
                maptools: ko.observable(true),
                legend: ko.observable(true)
            };

            this.addInitialLayers = function() {
                var initialLayers = [];
                var overlayLayers = _.sortBy(_.where(arches.mapLayers, {
                    isoverlay: true
                }), 'sortorder').reverse();

                arches.mapLayers.forEach(function(mapLayer) {
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
                this.map.addControl(draw);
                this.redrawGeocodeLayer = function() {
                    var cacheLayer = map.getLayer('geocode-point');
                    map.removeLayer('geocode-point');
                    map.addLayer(cacheLayer, 'gl-draw-active-line.hot');
                }

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

                var overlays =
                    _.each(_.where(arches.mapLayers, {
                        isoverlay: true
                    }), function(overlay) {
                        _.extend(overlay, {
                            opacity: ko.observable(100),
                            color: _.filter(overlay.layer_definitions[0].paint, function(prop, key) {if (key.includes('-color')) {return prop};})[0],
                            showingTools: ko.observable(false),
                            invisible: ko.observable(false),
                            toggleOverlayTools: function(e) {
                                this.showingTools(!this.showingTools());
                            },
                            toggleOverlayVisibility: function(e) {
                                this.opacity() > 0.0 ? this.opacity(0.0) : this.opacity(100.0);
                            },
                            updateOpacity: function(val) {
                                var shift = val > 0.0 ? 0.0001 : -0.0001;
                                var unsetMap = setTimeout(function(val){map.setBearing(map.getBearing() + shift)}, 200); //Layers do not always redraw when toggled
                                var refreshMap = setTimeout(function(val){map.setBearing(map.getBearing() + shift * -1)}, 100); // Shifting the map back and forth forces the map to refresh and draw the toggled layers
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

                this.overlays = ko.observableArray(overlays)

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

                this.updateConfigs = function(theViewModel) {
                    //using a closure because the viewModel was not avaliable within the event
                    return function() {
                        var self = theViewModel;
                        var mapCenter = this.getCenter()
                        var zoom = self.map.getZoom()
                        if (self.zoom() !== zoom) {
                            self.zoom(zoom);
                        };
                        self.centerX(mapCenter.lng);
                        self.centerY(mapCenter.lat);
                        if (Math.abs(this.getBearing()) > 0.01) {
                          self.bearing(this.getBearing());
                        }
                    }
                }

                this.map.on('moveend', this.updateConfigs(this));

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

                this.geocodePoint.subscribe(function(val){
                   var coords = this.geocodeResponseOptions()[val].geometry.coordinates;
                   var point = {
                       "type": "Feature",
                       "properties": {},
                       "geometry": {
                           "type": "Point",
                           "coordinates": coords
                       }
                   }
                   this.map.getSource('geocode-point').setData(point);
                   this.redrawGeocodeLayer();
                   var centerPoint = new mapboxgl.LngLat(coords[0], coords[1])
                   this.map.flyTo({
                       center: centerPoint
                   });
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
                var target = (direction==='up') ? source - 1 : source + 1;

                if (target >= 0 && target < overlays.length) {
                    self.overlays.valueWillMutate();

                    overlays.splice(source, 1);
                    overlays.splice(target, 0, overlay);

                    self.overlays.valueHasMutated();
                }
            };

            this.mapStyle = mapStyle;
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
