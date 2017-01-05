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
    'views/list',
    'widgets/map/map-styles',
    'viewmodels/geocoder',
    'viewmodels/map-controls',
    'select2',
    'bindings/select2v4',
    'bindings/fadeVisible',
    'bindings/mapbox-gl',
    'bindings/chosen',
    'bindings/color-picker'
], function($, ko, _, WidgetViewModel, arches, mapboxgl, Draw, koMapping, geojsonExtent, ListView, mapStyles, GeocoderViewModel, MapControlsViewModel) {
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
     * @param {number} params.config.zoom - map zoom level
     * @param {number} params.config.centerX - map center longitude
     * @param {number} params.config.centerY - map center latitude
     * @param {string} params.config.geocodeProvider - the text string id of the geocoder api (currently MapzenGeocoder or BingGeocoder).
     * @param {string} params.config.basemap - the layer name of the selected basemap to be shown in the map
     * @param {object} params.config.geometryTypes - the geometry types available for a user to edit
     * @param {number} params.config.pitch - the pitch of the map in degrees
     * @param {number} params.config.bearing - the bearing of the map in degrees with north at 0
     * @param {string} params.config.geocodePlaceholder - the placehoder of the geocoder input
     * @param {boolean} params.config.geocoderVisible - whether the geocoder is available on the map
     * @param {number} params.config.minZoom - the min zoom of the map
     * @param {number} params.config.maxZoom - the max zoom of the map
     * @param {string} params.config.resourceColor - the color of resource geometries
     * @param {number} params.config.resourcePointSize - the point size of resource geometries
     * @param {number} params.config.resourceLineWidth - the line width of resource geometries
     * @param {boolean} params.config.featureEditingDisabled - a config for reports that hides the draw tools
     * @param {object} params.config.overlayConfigs - an array of overlays saved to the widget
     */
    return ko.components.register('map-widget', {
        viewModel: function(params) {
            var self = this;
            var result;
            this.context = params.type
            this.getContextCss = ko.pureComputed(function(){
                lookup = {'report-header':'map-report-header-container',
                          'search-filter':'map-search-container',
                          'resource-editor':'map-crud-container'
                        };
                result = lookup[this.context] || 'map-crud-container';
                return result;
            }, this)
            this.configType = params.reportHeader || 'header';
            params.configKeys = [
                'zoom',
                'centerX',
                'centerY',
                'geocodeProvider',
                'basemap',
                'geometryTypes',
                'pitch',
                'bearing',
                'geocodePlaceholder',
                'geocoderVisible',
                'minZoom',
                'maxZoom',
                'featureColor',
                'featurePointSize',
                'featureLineWidth',
                'featureEditingDisabled',
                'overlayConfigs',
                'overlayOpacity',
                'mapControlsHidden'
            ];

            WidgetViewModel.apply(this, [params]);
            this.overlaySelectorClosed = ko.observable(true);
            this.geocodeShimAdded = ko.observable(false);
            this.selectedBasemap = this.basemap;
            this.drawMode = ko.observable();
            this.selectedFeatureType = ko.observable();
            this.overlays = ko.observableArray();
            this.overlayLibrary = ko.observableArray();
            this.overlayLibraryList = new ListView({
                items: self.overlayLibrary
            });
            this.anchorLayerId = 'gl-draw-point.cold'; //Layers are added below this drawing layer

            this.summaryDetails = []
            if (ko.unwrap(this.value) !== null) {
                this.summaryDetails =  koMapping.toJS(this.value).features || [];
            }

            this.geocoder = new GeocoderViewModel({
                provider: this.geocodeProvider,
                placeholder: this.geocodePlaceholder,
                anchorLayerId: this.anchorLayerId
            });
            this.hoverFeature = ko.observable(null);


            // TODO: This should be a system config rather than hard-coded here
            this.geocoderProviders = ko.observableArray([{
                'id': 'BingGeocoder',
                'name': 'Bing'
            }, {
                'id': 'MapzenGeocoder',
                'name': 'Mapzen'
            }]);

            this.loadGeometriesIntoDrawLayer = function() {
                if (self.draw) {
                    var val = koMapping.toJS(self.value);
                    self.draw.deleteAll()
                    if (val) {
                        self.draw.add(val);
                    }
                }
            };

            this.clearGeometries = function(val, key) {
                if (self.draw !== undefined && val === null) {
                    self.draw.deleteAll()
                }
            };

            if (ko.isObservable(this.value)) {
              this.value.subscribe(this.clearGeometries)
            }

            if (this.form) {
                var dc = '';
                var resourceSourceId = 'resources';
                this.form.on('after-update', function(req, tile) {
                   if (self.map) {
                       var style = self.map.getStyle();
                       var oldDc = dc;
                       dc = '-' + new Date().getTime();
                       style.sources[resourceSourceId + dc] = style.sources[resourceSourceId + oldDc];
                       delete style.sources[resourceSourceId + oldDc];
                       _.each(style.layers, function(layer) {
                          if (layer.source === resourceSourceId + oldDc) {
                              layer.source = resourceSourceId + dc;
                          }
                       });
                       style.sources = _.defaults(self.sources, style.sources);
                       self.map.setStyle(style);
                   }

                   if (self.draw !== undefined) {
                     self.draw.changeMode('simple_select')
                     self.featureColor(self.resourceColor)
                     self.loadGeometriesIntoDrawLayer();
                   }

                });
                this.form.on('tile-reset', self.loadGeometriesIntoDrawLayer);
            }


            this.mapControls = new MapControlsViewModel({
                mapControlsHidden: this.mapControlsHidden,
                overlaySelectorClosed: this.overlaySelectorClosed,
                overlays: this.overlays
            });

            if (params.graph !== undefined) {
                this.resourceIcon = params.graph.get('iconclass');
                this.resourceName = params.graph.get('name');
                this.graphId = params.graph.get('graphid')
                this.resourceColor = params.graph.get('mapfeaturecolor')
                this.resourcePointSize = params.graph.get('mappointsize')
                this.resourceLineWidth = params.graph.get('maplinewidth')
                if (!this.featureColor()) {
                    this.featureColor(this.resourceColor);
                }
                if (!this.featurePointSize()) {
                    this.featurePointSize(this.resourcePointSize);
                } else {
                    this.featurePointSize(Number(this.featurePointSize()))
                }
                if (!this.featureLineWidth()) {
                    this.featureLineWidth(this.resourceLineWidth);
                } else {
                    this.featureLineWidth(Number(this.featureLineWidth()));
                }
                this.featureColorCache = this.featureColor()
                this.featurePointSizeCache = this.featurePointSize()
                this.featureLineWidthCache = this.featureLineWidth()
            }

            this.toggleOverlaySelector = function(e) {
                this.overlaySelectorClosed(!this.overlaySelectorClosed());
            };

            this.mapControls.mapControlsExpanded.subscribe(function(expanded) {
                self.geocodeShimAdded(expanded);
            });

            this.createResouceModelOverlays = function(resources) {
              var resourceLayers = [];
              function MapLayer(resource) {
                var maplayer = {
                    icon: resource.icon,
                    layer_definitions: mapStyles.getResourceModelStyles(resource),
                    maplayerid: resource.maplayerid,
                    name: resource.name,
                    isoverlay: true
                }
                return maplayer
              }
              resources.forEach(function(resource){
                resourceLayers.push(MapLayer(resource))
              })
              return resourceLayers;
            }

            this.resourceModelOverlays = this.createResouceModelOverlays(arches.resources)
            this.allLayers = _.union(this.resourceModelOverlays, arches.mapLayers)
            this.layers = $.extend(true, [], this.allLayers); //deep copy of layers

            /**
             * Creates the map layer for the resource with widget configs
             * @return {object}
             */
            this.defineResourceLayer = function() {
                var resourceLayer = {
                    name: this.resourceName,
                    maplayerid: this.graphId,
                    isResource: true,
                    layer_definitions: [{
                        "id": "resource-poly",
                        "source": "resource",
                        "type": "fill",
                        "layout": {},
                        "filter": ["!in", "$type", "LineString"],
                        "paint": {
                            "fill-color": this.featureColor(),
                            "fill-opacity": 0.8
                        }
                    }, {
                        "id": "resource-point",
                        "source": "resource",
                        "type": "circle",
                        "layout": {},
                        "filter": ["!in", "$type", "LineString", "Polygon"],
                        "paint": {
                            "circle-radius": this.featurePointSize(),
                            "circle-color": this.featureColor(),
                            "circle-opacity": 0.8
                        }
                    }, {
                        "id": "resource-line",
                        "source": "resource",
                        "type": "line",
                        "layout": {},
                        "paint": {
                            "line-color": this.featureColor(),
                            "line-opacity": 0.8,
                            "line-width": this.featureLineWidth()
                        }
                    }],
                    isoverlay: false,
                    icon: this.resourceIcon
                };
                return resourceLayer;
            }

            /**
             * creates an array of map layers available to the map when the map object is instantiated
             * @return {object}
             */
            this.addInitialLayers = function() {
                var initialLayers = [];
                if (this.context === 'report-header') {
                    this.resourceLayer = this.defineResourceLayer();
                    this.layers.unshift(this.resourceLayer);
                }

                this.layers.forEach(function(mapLayer) {
                    if (mapLayer.name === this.basemap()) {
                        _.each(mapLayer.layer_definitions, function(layer) {
                            initialLayers.push(layer);
                        });
                    }
                }, this);

                initialLayers.push(this.geocoder.pointstyle);
                return initialLayers;
            }

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

            /**
             * prepares the map for the widget after the mapbox bindingHandler has instantiated a map object
             * @param  {object} map map object created in ko.bindingHandler
             * @return {null}
             */
            this.setupMap = function(map) {
                var draw = Draw({
                    controls: {
                        trash: false //if true, the backspace key is inactivated in the geocoder input
                    },
                    styles: mapStyles.getDrawStyles({
                        linewidth: this.featureLineWidth,
                        color: this.featureColor,
                        pointsize: this.featurePointSize
                    }),
                    displayControlsDefault: false
                });

                this.map = map;
                this.geocoder.setMap(map);
                this.draw = draw;
                this.map.addControl(draw);

                this.map.on('load', function() {
                    if (!self.configForm) {
                        var source = self.map.getSource('resource')
                        var features = [];
                        var result = {
                            "type": "FeatureCollection",
                            "features": []
                        };
                        var data = null;
                        self.overlayLibrary(self.createOverlays())
                        if (self.resourceLayer !== undefined) {
                            self.overlays.unshift(self.createOverlay(self.resourceLayer));
                            self.addMaplayer(self.resourceLayer);
                        }
                        if (self.context === 'report-header' && !ko.isObservable(self.value)) {
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
                                self.map.moveLayer(layerId, self.anchorLayerId)
                            }, self)

                        } else if (self.context !== 'report-header' && !ko.isObservable(self.value)) {
                            data = koMapping.toJS(self.value);
                            self.loadGeometriesIntoDrawLayer()
                        } else { //if values are for a form widget...
                            if (_.isObject(self.value())) { //confirm value is not "", null, or undefined
                                data = koMapping.toJS(self.value);
                            }
                        };

                        if (data) {
                            if (data.features.length > 0) {
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
                    }
                    window.setTimeout(function(){window.dispatchEvent(new Event('resize'))}, 30)
                });

                /**
                 * Updates the appearance of the draw layer when feature appearance configs change
                 * @return {null}
                 */
                this.updateDrawLayerPaintProperties = function(paintProperties, val, isNumber) {
                    var val = isNumber ? Number(val) : val; //point size and line width must be number types
                    _.each(this.draw.options.styles, function(style) {
                        var paint = this.map.getLayer(style.id).paint
                        var self = this;
                        paintProperties.forEach(function(prop) {
                          if (paint.hasOwnProperty(prop)) {
                            if (!style.id.includes('halo')) {
                                  self.map.setPaintProperty(style.id, prop, val)
                              }
                            if (style.id.includes('halo') && !prop.includes('color')) {
                                self.map.setPaintProperty(style.id, prop, val * 1.25)
                              }
                          }
                        })
                    }, this)
                }

                this.featureColor.subscribe(function(e) {
                    this.updateDrawLayerPaintProperties(['fill-outline-color', 'fill-color', 'circle-color', 'line-color'], e)
                }, this);

                this.featurePointSize.subscribe(function(e) {
                    this.updateDrawLayerPaintProperties(['circle-radius'], e, true)
                }, this);

                this.featureLineWidth.subscribe(function(e) {
                    this.updateDrawLayerPaintProperties(['line-width'], e, true)
                }, this);

                /**
                 * Updates the draw mode of the draw layer when a user selects a draw tool in the map controls
                 * @param  {string} selectedDrawTool the draw tool name selected in the map controls
                 * @return {null}
                 */
                this.selectEditingTool = function(self, selectedDrawTool) {
                    if (this.form) {
                      this.featureColor(this.featureColorCache);
                    }
                    _.each(self.geometryTypeDetails, function(geomtype) {
                        if (geomtype.name === selectedDrawTool) {
                            self.geometryTypeDetails[selectedDrawTool].active(!self.geometryTypeDetails[selectedDrawTool].active())
                        } else {
                            self.geometryTypeDetails[geomtype.name].active(false)
                        }
                    });

                    if (self.geometryTypeDetails[selectedDrawTool] === undefined) { //it has no geom type, so must be trash
                        self.draw.trash();
                        self.drawMode(null);
                    } else {
                        if (!self.drawMode()) {
                            self.draw.changeMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                            self.drawMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                        } else if (self.geometryTypeDetails[selectedDrawTool].drawMode === self.drawMode()) {
                            self.draw.changeMode('simple_select')
                            self.drawMode(undefined);
                        } else {
                            self.draw.changeMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                            self.drawMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                        }
                    }

                }

                this.removeMaplayer = function(maplayer) {
                    if (maplayer !== undefined) {
                        maplayer.layer_definitions.forEach(function(layer) {
                            if (map.getLayer(layer.id) !== undefined) {
                                map.removeLayer(layer.id)
                            }
                        })
                    }
                }

                this.addMaplayer = function(maplayer) {
                    if (maplayer !== undefined) {
                        maplayer.layer_definitions.forEach(function(layer) {
                            if (map.getLayer(layer.id) === undefined) {
                                map.addLayer(layer, this.anchorLayerId);
                                map.setPaintProperty(layer.id, layer.type + '-opacity', maplayer.opacity() / 100.0);
                            }
                        }, this)
                    }
                }

                this.overlayLibrary.subscribe(function(overlays) {
                    var initialConfigs = self.overlayConfigs();
                    for (var i = initialConfigs.length; i-- > 0;) {
                        var overlay = _.findWhere(overlays, {
                            "maplayerid": initialConfigs[i].maplayerid
                        });
                        if (overlay === undefined) {
                            var overlay = _.findWhere(overlays, {
                                "maplayerid": self.graphId
                            });
                        };
                        if (overlay !== undefined) {
                            self.addMaplayer(overlay)
                            self.overlays.push(overlay)
                        }
                    }
                });

                this.createOverlay = function(maplayer) {
                    var self = this;
                    var configMaplayer;
                    _.extend(maplayer, {
                        opacity: ko.observable(100),
                        color: _.filter(maplayer.layer_definitions[0].paint, function(prop, key) {
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
                    configMaplayer = _.findWhere(this.overlayConfigs(), {
                        "maplayerid": maplayer.maplayerid
                    })
                    if (configMaplayer !== undefined) {
                        maplayer.checkedOutOfLibrary(configMaplayer !== undefined)
                        maplayer.opacity(configMaplayer.opacity)
                    }
                    maplayer.opacity.subscribe(function(value) {
                        self.overlayOpacity(value);
                        this.overlayConfigs().forEach(
                            function(overlayConfig) {
                                if (maplayer.maplayerid === overlayConfig.maplayerid) {
                                    // self.overlayConfigs.valueWillMutate();
                                    overlayConfig.opacity = value
                                        // self.overlayConfigs.valueHasMutated();
                                }
                            }, self)
                        maplayer.updateOpacity(value);
                    }, self);
                    return maplayer
                };

                this.createOverlays = function() {
                    var overlays =
                        _.each(_.where(this.layers, {
                            isoverlay: true
                        }), self.createOverlay, self);
                    return overlays;
                }

                this.exchangeOverlay = function(e) {
                    if (this.checkedOutOfLibrary() === true) {
                        self.overlays.remove(this)
                        self.removeMaplayer(this)
                    } else {
                        self.overlays.push(this);
                    }
                    this.checkedOutOfLibrary(!this.checkedOutOfLibrary())
                }

                this.basemaps = _.filter(arches.mapLayers, function(baselayer) {
                    return baselayer.isoverlay === false
                });

                this.setBasemap = function(basemapType) {
                    var style = this.map.getStyle();
                    style.sources = _.defaults(self.sources, style.sources);
                    var basemapToAdd = _.find(this.basemaps, function(basemap) {
                        return basemap.name === basemapType.name;
                    });
                    var basemapIds = _.map(this.basemaps, function(basemap) {
                        return _.map(basemap.layer_definitions, function (layer) {
                            return layer.id;
                        });
                    }).reduce(function(ids1, ids2) {
                        return ids1.concat(ids2);
                    });
                    style.layers = basemapToAdd.layer_definitions.concat(_.filter(style.layers, function(layer) {
                        return !_.contains(basemapIds, layer.id);
                    }));
                    self.map.setStyle(style);
                };

                this.updateConfigs = function() {
                    var self = this;
                    if (this.form === null && this.context !== 'report-header') {
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
                    } else {
                      return function() {}
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

                this.updateFeatureStyles = function(){
                  var self = this;
                  return function(){
                    if (self.form) {
                      self.featureColor() === self.featureColorCache || self.featureColor(self.featureColorCache);
                      self.featurePointSize() === self.featurePointSizeCache || self.featurePointSize(self.featurePointSizeCache);
                      self.featureLineWidth() === self.featureLineWidthCache || self.featureLineWidth(self.featureLineWidthCache);
                    }
                  };
                };

                this.map.on('moveend', this.updateConfigs());
                ['draw.create', 'draw.update', 'draw.delete'].forEach(function(event) {
                    self.map.on(event, self.saveGeometries())
                });
                this.map.on('click', this.updateDrawMode())
                this.map.on('draw.selectionchange', self.updateFeatureStyles());

                this.overlays.subscribe(function(overlays) {
                    this.overlayConfigs([]);
                    for (var i = overlays.length; i-- > 0;) { //Using a conventional loop because we want to go backwards over the array
                        this.removeMaplayer(overlays[i])
                    }
                    for (var i = overlays.length; i-- > 0;) {
                        if (overlays[i].isResource !== true) {
                            this.overlayConfigs().push({
                                'maplayerid': overlays[i].maplayerid,
                                'name': overlays[i].name,
                                'opacity': overlays[i].opacity()
                            });
                        }
                        this.addMaplayer(overlays[i])
                    }
                    this.geocoder.redrawLayer();
                }, this)

                self.map.on('mousemove', function (e) {
                    var features = self.map.queryRenderedFeatures(e.point);
                    var hoverFeature = _.find(features, function (feature) {
                        return feature.layer.id.indexOf('resources') === 0;
                    }) || null;
                    if (self.hoverFeature() !== hoverFeature) {
                        self.hoverFeature(hoverFeature);
                    }
                });
            }; //end setup map

            // preprocess relative paths for app tileserver
            // see: https://github.com/mapbox/mapbox-gl-js/issues/3636#issuecomment-261119004
            _.each(arches.mapSources, function (sourceConfig, name) {
                if (sourceConfig.tiles) {
                    sourceConfig.tiles.forEach(function (url, i) {
                        if (url.startsWith('/')) {
                            sourceConfig.tiles[i] = window.location.origin + url;
                        }
                    });
                }
            });

            this.sources = $.extend(true, {}, arches.mapSources); //deep copy of sources
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

            this.selectBasemap = function(val) {
                self.basemap(val.name)
                self.setBasemap(val);
            }

            this.mapStyle.layers = this.addInitialLayers();
        },
        template: {
            require: 'text!widget-templates/map'
        }
    });
});
