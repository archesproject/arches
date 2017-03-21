define([
    'jquery',
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'mapbox-gl',
    'mapbox-gl-draw',
    'jsts',
    'proj4',
    'turf',
    'geohash',
    'knockout-mapping',
    'geojson-extent',
    'views/list',
    'views/components/widgets/map/map-styles',
    'viewmodels/geocoder',
    'viewmodels/map-controls',
    'select2',
    'bindings/select2v4',
    'bindings/fadeVisible',
    'bindings/mapbox-gl',
    'bindings/chosen',
    'bindings/color-picker'
], function($, ko, _, WidgetViewModel, arches, mapboxgl, Draw, jsts, proj4, turf, geohash, koMapping, geojsonExtent, ListView, mapStyles, GeocoderViewModel, MapControlsViewModel) {
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

            this.configType = params.reportHeader || 'header';
            this.resizeOnChange = ko.pureComputed(function() {
                return {
                    param: ko.unwrap(params.resizeOnChange),
                    expanded: this.expanded()
                }
            }, this);
            this.resizeDuration = params.resizeDuration || 500;
            this.context = params.type;
            this.getContextCss = ko.pureComputed(function() {
                var result;
                var lookup = {
                    'report-header': 'map-report-header-container',
                    'search-filter': 'map-search-container',
                    'resource-editor': 'map-crud-container'
                };
                result = lookup[this.context] || 'map-crud-container';
                if (this.expanded()) {
                    result += ' expanded-edit-map';
                }
                return result;
            }, this)
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

            this.toolType = this.context === 'search-filter' ? 'Query Tools' : 'Map Tools'
            if (this.context === 'search-filter') {
                this.results = params.results;
                this.query = params.query;
            }

            this.buffer = ko.observable(100.0);
            this.queryFeature;
            this.extentSearch = ko.observable(false);
            this.geojsonString = ko.observable();
            this.anchorLayerId = 'gl-draw-point.cold'; //Layers are added below this drawing layer

            this.summaryDetails = []

            if (ko.unwrap(this.value) !== null) {
                this.summaryDetails = koMapping.toJS(this.value).features || [];
            }

            this.geocoder = new GeocoderViewModel({
                provider: this.geocodeProvider,
                placeholder: this.geocodePlaceholder,
                anchorLayerId: this.anchorLayerId
            });

            this.hoverData = ko.observable(null);
            this.clickData = ko.observable(null);
            this.popupData = ko.computed(function () {
                var hoverData = self.hoverData();
                return hoverData ? hoverData : self.clickData();
            });

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
                } else if (val.features.length === 0 && self.context === 'search-filter') {
                        self.updateSearchQueryLayer([]);
                        if (self.extentSearch() === true) {
                            self.toggleExtentSearch();
                        }
                    }
                };

            if (ko.isObservable(this.value)) {
                this.value.subscribe(this.clearGeometries)
            }

            if (this.form) {
                var dc = '';
                var resourceSourceId = 'resources';
                this.form.on('after-update', function(req, tile) {
                    // if (self.map) {
                    //     var style = self.map.getStyle();
                    //     var oldDc = dc;
                    //     dc = '-' + new Date().getTime();
                    //     style.sources[resourceSourceId + dc] = style.sources[resourceSourceId + oldDc];
                    //     delete style.sources[resourceSourceId + oldDc];
                    //     _.each(style.layers, function(layer) {
                    //         if (layer.source === resourceSourceId + oldDc) {
                    //             layer.source = resourceSourceId + dc;
                    //         }
                    //     });
                    //     style.sources = _.defaults(self.sources, style.sources);
                    //     self.map.setStyle(style);
                    // }

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

            if (!this.configForm && this.context === 'report-header') {
                _.each(arches.mapLayers, function(layer) {
                    _.each(layer.layer_definitions, function(def) {
                        def.id += '-' + layer.name;
                        if (def.ref) {
                            def.ref += '-' + layer.name;
                        }
                    });
                });
            }

            this.layers = $.extend(true, [], _.filter(arches.mapLayers, function (layer) {
                return layer.activated;
            })); //deep copy of layers

            this.defineSearchQueryLayer = function() {
                var searchQueryLayer = {
                    name: 'Map Query',
                    maplayerid: 'search-query',
                    isResource: false,
                    layer_definitions: mapStyles.getSearchQueryStyles(),
                    isoverlay: false,
                    icon: 'ion-map'
                }
                return searchQueryLayer
            }

            this.updateSearchQueryLayer = function(geojson_features) {
                var style = self.getMapStyle();
                style.sources['search-query'].data = {
                    "type": "FeatureCollection",
                    "features": geojson_features
                };
                self.map.setStyle(style);
            }

            this.restoreSearchState = function() {
                var features = this.query.features;
                var drawMode;
                var geojsonToDrawMode = {
                    'Point': {'drawMode': 'draw_point', 'name':'Point'},
                    'LineString': {'drawMode':'draw_line_string', 'name':'Line'},
                    'Polygon': {'drawMode': 'draw_polygon', 'name': 'Polygon'}
                }
                if (features.length > 0) {
                    this.queryFeature = features[0];
                    if (this.queryFeature.properties.extent_search === true) {
                        var bounds = new mapboxgl.LngLatBounds(geojsonExtent(this.queryFeature));
                        this.toggleExtentSearch()
                        this.map.fitBounds(bounds);
                    } else {
                        drawMode = geojsonToDrawMode[this.queryFeature.geometry.type]
                        this.draw.changeMode(drawMode.drawMode)
                        this.drawMode(drawMode.drawMode)
                        this.geometryTypeDetails[drawMode.name].active(true);
                        this.updateSearchQueryLayer([this.queryFeature]);
                        if (this.queryFeature.properties.buffer) {
                            this.buffer(this.queryFeature.properties.buffer.width)
                        }
                    }
                }
            }

            this.updateDrawLayerWithJson = function(val){
                    try {
                        var data = JSON.parse(val)
                        try {
                            self.draw.add(data)
                            self.saveGeometries()()
                        } catch(err) {
                            console.log(err)
                            console.log('invalid geometry')
                        }
                    } catch(err) {
                        console.log(err)
                        console.log('invalid json')
                    }
            }


            this.geojsonString.subscribe(this.updateDrawLayerWithJson, self)
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
                        "id": "resource-poly" + this.graphId,
                        "source": "resource",
                        "type": "fill",
                        "layout": {},
                        "filter": ["!in", "$type", "LineString"],
                        "paint": {
                            "fill-color": this.featureColor(),
                            "fill-opacity": 0.8
                        }
                    }, {
                        "id": "resource-point" + this.graphId,
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
                        "id": "resource-line" + this.graphId,
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

                if (this.context === 'search-filter') {
                    this.searchQueryLayer = this.defineSearchQueryLayer();
                    this.layers.unshift(this.searchQueryLayer);
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
                if (this.resizeOnChange && this.resizeOnChange.subscribe) {
                    this.resizeOnChange.subscribe(function() {
                        var duration = self.resizeDuration;

                        var resize = function () {
                            map.resize();
                            duration -= 1;
                            if (duration >= 0) {
                                _.defer(resize, 1);
                            }
                        }
                        _.defer(resize, 1);
                    });
                }
                this.geocoder.setMap(map);
                this.draw = draw;
                this.map.addControl(draw);

                this.map.on('load', function() {
                    if (!self.configForm) {
                        var zoomToGeoJSON = function (data, fly) {
                            var method = fly ? 'flyTo' : 'jumpTo';
                            var bounds = new mapboxgl.LngLatBounds(geojsonExtent(data));
                            var tr = self.map.transform;
                            var nw = tr.project(bounds.getNorthWest());
                            var se = tr.project(bounds.getSouthEast());
                            var size = se.sub(nw);
                            var scaleX = (tr.width - 80) / size.x;
                            var scaleY = (tr.height - 80) / size.y;

                            var options = {
                                center: tr.unproject(nw.add(se).div(2)),
                                zoom: Math.min(tr.scaleZoom(tr.scale * Math.min(scaleX, scaleY)), ko.unwrap(self.maxZoom))
                            };
                            self.map[method](options);
                        };
                        var source = self.map.getSource('resource')
                        var features = [];
                        var result = {
                            "type": "FeatureCollection",
                            "features": []
                        };
                        var data = null;

                        self.getMapStyle = function() {
                            var style = map.getStyle();
                            style.sources = _.defaults(self.sources, style.sources);
                            var updateGeoJsonSource = function(){
                                return function(source, key) {
                                    if (source.type === 'geojson') {
                                        style.sources[key].data = self.map.getSource(key)._data
                                    }
                                }
                            }
                            _.each(style.sources, updateGeoJsonSource(), this)
                            return style
                        };

                        self.overlayLibrary(self.createOverlays())
                        if (self.resourceLayer !== undefined && self.context === 'report-header') {
                            self.overlays.unshift(self.createOverlay(self.resourceLayer));
                        }

                        if (self.context === 'search-filter') {
                            self.searchAggregations = params.searchAggregations;
                            var cellWidth = arches.hexBinSize;
                            var units = 'kilometers';
                            var hexGrid = turf.hexGrid(arches.hexBinBounds, cellWidth, units);
                            var getSearchAggregationGeoJSON = function () {
                                var agg = ko.unwrap(self.searchAggregations);
                                if (!agg || !agg.grid.buckets) {
                                    return {
                                        "type": "FeatureCollection",
                                        "features": []
                                    };
                                }
                                if (agg.bounds.bounds && self.map && !self.extentSearch()) {
                                    var bounds = [
                                        [
                                            agg.bounds.bounds.top_left.lon,
                                            agg.bounds.bounds.bottom_right.lat
                                        ],
                                        [
                                            agg.bounds.bounds.bottom_right.lon,
                                            agg.bounds.bounds.top_left.lat
                                        ]
                                    ];
                                    map.fitBounds(bounds);
                                }
                                var features = [];
                                _.each(agg.grid.buckets, function (cell) {
                                    var pt = geohash.decode(cell.key);
                                    var feature = turf.point([pt.lon, pt.lat], {
                                        doc_count: cell.doc_count
                                    });
                                    features.push(feature);
                                });
                                var pointsFC = turf.featureCollection(features);

                                var aggregated = turf.collect(hexGrid, pointsFC, 'doc_count', 'doc_count');
                                _.each(aggregated.features, function(feature) {
                                    feature.properties.doc_count = _.reduce(feature.properties.doc_count, function(i,ii) {
                                        return i+ii;
                                    }, 0);
                                });

                                return aggregated;
                            }
                            var getSearchPointsGeoJSON = function () {
                                var agg = ko.unwrap(self.searchAggregations);
                                if (!agg || !agg.results) {
                                    return {
                                        "type": "FeatureCollection",
                                        "features": []
                                    };
                                }

                                var features = [];
                                _.each(agg.results, function (result) {
                                    _.each(result._source.points, function (pt) {
                                        var feature = turf.point([pt.lon, pt.lat], _.extend(result._source, {
                                            resourceinstanceid: result._id,
                                            highlight: false
                                        }));
                                        features.push(feature);
                                    });
                                });

                                var mouseoverInstanceId = self.results.mouseoverInstanceId();
                                if (mouseoverInstanceId) {
                                    var highlightFeature = _.find(features, function(feature) {
                                        return feature.properties.resourceinstanceid === mouseoverInstanceId;
                                    });
                                    if (highlightFeature) {
                                        highlightFeature.properties.highlight = true;
                                    }
                                }

                                var pointsFC = turf.featureCollection(features);
                                return pointsFC;
                            }
                            self.overlays.unshift(self.createOverlay(self.searchQueryLayer))
                            self.updateSearchResultsLayer = function() {
                                var aggSource = self.map.getSource('search-results-hex')
                                var aggData = getSearchAggregationGeoJSON();
                                aggSource.setData(aggData)
                                var pointSource = self.map.getSource('search-results-points')
                                var pointData = getSearchPointsGeoJSON();
                                pointSource.setData(pointData)
                            }
                            self.searchAggregations.subscribe(self.updateSearchResultsLayer);
                            if (self.searchAggregations) {
                                self.updateSearchResultsLayer()
                            }
                            self.results.mouseoverInstanceId.subscribe(function () {
                                var pointSource = self.map.getSource('search-results-points')
                                var pointData = getSearchPointsGeoJSON();
                                pointSource.setData(pointData)
                            });
                            self.results.mapLinkData.subscribe(function(data) {
                                zoomToGeoJSON(data, true);
                            });
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
                            _.each(['resource-poly' + self.graphId, 'resource-line' + self.graphId, 'resource-point' + self.graphId], function(layerId) { //clear and add resource layers so that they are on top of map
                                var cacheLayer = self.map.getLayer(layerId);
                                self.map.moveLayer(layerId, self.anchorLayerId)
                            }, self);

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
                                zoomToGeoJSON(data);
                            }
                        }
                    }
                    window.setTimeout(function() {
                        window.dispatchEvent(new Event('resize'))
                        if (self.query !== undefined && self.context === 'search-filter') {
                            self.restoreSearchState();
                        }
                    }, 30)
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

                this.switchToEditMode = function() {
                    self.draw.changeMode('simple_select')
                    self.drawMode(undefined);
                }

                /**
                 * Updates the draw mode of the draw layer when a user selects a draw tool in the map controls
                 * @param  {string} selectedDrawTool the draw tool name selected in the map controls
                 * @return {null}
                 */
                this.selectEditingTool = function(self, selectedDrawTool) {
                    self = self || this;
                    if (this.context === 'search-filter') {
                        this.extentSearch(false);
                        this.draw.deleteAll();
                        this.queryFeature = undefined;
                        this.updateSearchQueryLayer([]);
                        this.value({
                          "type": "FeatureCollection",
                          "features": []
                        });
                    }
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
                    if (selectedDrawTool === 'delete') {
                        self.draw.trash();
                        self.drawMode('simple_select');
                    }
                    else if (selectedDrawTool === 'end') {
                        self.draw.changeMode('simple_select')
                        self.drawMode(undefined);
                    }
                    else {
                        if (!self.drawMode()) {
                            self.draw.changeMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                            self.drawMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                        } else if (self.geometryTypeDetails[selectedDrawTool].drawMode === self.drawMode()) {
                            self.draw.changeMode('simple_select')
                            if (self.mapControls.mapControlsExpanded()) {
                                self.drawMode(undefined);
                            } else {
                                self.drawMode('simple_select')
                            }
                        } else {
                            self.draw.changeMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                            self.drawMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                        }
                    }

                }

                this.removeMaplayer = function(maplayer) {
                    if (maplayer !== undefined) {
                        var style = this.getMapStyle();
                        maplayer.layer_definitions.forEach(function(def) {
                            var layer = _.find(style.layers, function(layer) {
                                return layer.id === def.id;
                            });
                            style.layers = _.without(style.layers, layer);
                        })
                        this.map.setStyle(style);
                    }
                }

                this.addMaplayer = function(maplayer) {
                    if (maplayer !== undefined) {
                        var style = this.getMapStyle();
                        var anchorIndex = _.findIndex(style.layers, function(layer) {
                            return layer.id === self.anchorLayerId;
                        });
                        var l1 = style.layers.slice(0, anchorIndex);
                        var l2 = style.layers.slice(anchorIndex);
                        style.layers = l1.concat(maplayer.layer_definitions, l2);
                        this.map.setStyle(style);
                        maplayer.updateOpacity(maplayer.opacity());
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

                var opacityTypes = [
                    'background',
                    'fill',
                    'line',
                    'text',
                    'icon',
                    'raster',
                    'circle',
                    'fill-extrusion'
                ];
                var multiplyStopValues = function(stops, multiplier) {
                    _.each(stops, function(stop) {
                        if (Array.isArray(stop[1])) {
                            multiplyStopValues(stop[1], multiplier);
                        } else {
                            stop[1] = stop[1] * multiplier;
                        }
                    });
                };
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
                            var opacityVal = Number(val) / 100.0;
                            var style = self.getMapStyle();
                            this.layer_definitions.forEach(function(def) {
                                var layer = _.find(style.layers, function(layer) {
                                    return layer.id === def.id;
                                });

                                if (layer) {
                                    if (layer.paint === undefined) {
                                        layer.paint = {};
                                    }
                                    _.each(opacityTypes, function(opacityType) {
                                        var startVal = def.paint ? def.paint[opacityType + '-opacity'] : null;

                                        if (startVal) {
                                            if (parseFloat(startVal)) {
                                                layer.paint[opacityType + '-opacity'] = startVal * opacityVal;
                                            } else {
                                                layer.paint[opacityType + '-opacity'] = JSON.parse(JSON.stringify(startVal));
                                                if (startVal.base) {
                                                    layer.paint[opacityType + '-opacity'].base = startVal.base * opacityVal;
                                                }
                                                if (startVal.stops) {
                                                    multiplyStopValues(layer.paint[opacityType + '-opacity'].stops, opacityVal);
                                                }
                                            }
                                        } else if (layer.type === opacityType ||
                                            (layer.type === 'symbol' && (opacityType === 'text' || opacityType === 'icon'))) {
                                            layer.paint[opacityType + '-opacity'] = opacityVal;
                                        }
                                    });
                                }
                            }, this)

                            map.setStyle(style);
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
                                    overlayConfig.opacity = value
                                }
                            }, self)
                        maplayer.updateOpacity(value);
                    }, self);
                    return maplayer
                };

                this.createOverlays = function() {
                    var overlays = [];
                    this.layers.forEach(function(layer){
                        if (layer.isoverlay === true) {
                            overlay = self.createOverlay(layer)
                            overlays.push(overlay);
                        }
                    })
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
                    return baselayer.isoverlay === false && baselayer.activated;
                });

                this.setBasemap = function(basemapType) {
                    var style = this.getMapStyle();
                    var basemapToAdd = _.find(this.basemaps, function(basemap) {
                        return basemap.name === basemapType.name;
                    });
                    var basemapIds = _.map(this.basemaps, function(basemap) {
                        return _.map(basemap.layer_definitions, function(layer) {
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
                        self.queryFeature = currentDrawing.features[currentDrawing.features.length - 1];
                        if (self.context === 'search-filter') {
                            self.updateSearchQueryLayer([self.queryFeature])
                        }
                    }
                }

                this.updateDrawMode = function(e) {
                    var self = this;
                    var context = this.context
                    return function(e) {
                        var selectedFeatureType;
                        var featureCount = self.draw.getAll().features.length;
                        if (context === 'search-filter' && featureCount > 1) {
                            _.each(self.draw.getAll().features.slice(0, featureCount - 1), function(feature) {
                                self.draw.delete(feature.id)
                            }, self)
                        }
                        if (_.contains(['draw_point', 'draw_line_string', 'draw_polygon'], self.drawMode()) && self.drawMode() !== self.draw.getMode()) {
                            self.draw.changeMode(self.drawMode())
                            if (context === 'search-filter') {
                                if (self.buffer() > 0) {
                                    self.applySearchBuffer(self.buffer())
                                }
                            }
                        } else {
                            self.drawMode(self.draw.getMode());
                            if (context !== 'search-filter') {
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
                }

                this.updateFeatureStyles = function() {
                    var self = this;
                    return function() {
                        if (self.form) {
                            self.featureColor() === self.featureColorCache || self.featureColor(self.featureColorCache);
                            self.featurePointSize() === self.featurePointSizeCache || self.featurePointSize(self.featurePointSizeCache);
                            self.featureLineWidth() === self.featureLineWidthCache || self.featureLineWidth(self.featureLineWidthCache);
                        }
                    };
                };

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

                this.applySearchBuffer = function(val) {
                    var buffer;
                    var coords3857;
                    var coords4326;
                    var coords;
                    if (self.value().features.length > 0 && self.queryFeature !== undefined) {
                        if (val >= 0) {
                            var transformer = proj4('EPSG:4326','EPSG:3857');
                            coords = self.queryFeature.geometry.coordinates;
                            switch (self.queryFeature.geometry.type) {
                                case 'Point': coords3857 = transformer.forward(coords); break;
                                case 'LineString': coords3857 = _.map(coords, function(coord){ return transformer.forward(coord);}); break;
                                case 'Polygon': coords3857 = [_.map(coords[0], function(coord){ return transformer.forward(coord);})];
                            }

                            var prebufferFeature = $.extend(true, {}, self.queryFeature);
                            prebufferFeature.geometry.coordinates = coords3857;
                            var reader = new jsts.io.GeoJSONReader();
                            var writer = new jsts.io.GeoJSONWriter();
                            var jstsFeature = reader.read(prebufferFeature)
                            var buffer = writer.write(jstsFeature.geometry.buffer(val/3.28084));
                            var coords4326 = [_.map(buffer.coordinates[0], function(coords){ return transformer.inverse(coords);})];
                            var bufferFeature = turf.polygon(coords4326);


                            bufferFeature.id = 'buffer-layer';
                            self.queryFeature.properties.buffer = {
                                width: val,
                                unit: 'ft'
                            }
                            self.value().features[0] = self.queryFeature
                            self.updateSearchQueryLayer([bufferFeature, self.queryFeature])
                        } else {
                            self.queryFeature.properties.buffer = {
                                width: 0,
                                unit: 'ft'
                            }
                            self.value().features = [self.queryFeature]
                        }
                        self.value(self.value())
                        self.draw.changeMode(self.drawMode())
                    }
                }

                this.toggleExtentSearch = function(val) {
                    this.extentSearch(!this.extentSearch())
                    if (this.extentSearch() === true) {
                        self.draw.deleteAll();
                        self.draw.changeMode('simple_select');
                        self.drawMode(undefined);
                        _.each(self.geometryTypeDetails, function(geomtype) {
                            geomtype.active(false);
                        })
                    } else {
                        this.value({
                          "type": "FeatureCollection",
                          "features": []
                        });
                    }
                }

                this.searchByExtent = function() {
                    if (self.extentSearch() === true) {
                        self.queryFeature = undefined;
                        self.updateSearchQueryLayer([])
                        var bounds = self.map.getBounds();
                        var ll = bounds.getSouthWest().toArray();
                        var ul = bounds.getNorthWest().toArray();
                        var ur = bounds.getNorthEast().toArray();
                        var lr = bounds.getSouthEast().toArray();
                        var coordinates = [ll, ul, ur, lr, ll]
                        var boundsFeature = {
                            "type": "Feature",
                            "properties": {
                                "buffer": {
                                    "width": 0,
                                    "unit": "ft"
                                },
                                "extent_search": true
                            },
                            "geometry": {
                                "type": "Polygon",
                                "coordinates": [coordinates]
                            }
                        }
                        self.value().features = [boundsFeature];
                        self.value(self.value());
                    }
                }

                this.extentSearch.subscribe(function() {
                    self.searchByExtent();
                })

                this.buffer.subscribe(function(val) {
                    var maxBuffer = 100000;
                    if(val < 0){
                        this.buffer(0)
                    }else if(val > maxBuffer){
                        this.buffer(maxBuffer)
                    }else{
                        this.applySearchBuffer(val)
                    }
                }, this);

                var resourceLookup = {};
                var lookupResourceData = function (resourceData) {
                    var resourceId = resourceData.resourceinstanceid;
                    if (resourceLookup[resourceId]) {
                        return resourceLookup[resourceId];
                    }
                    resourceData.loading = true;
                    resourceData.displaydescription = '';
                    resourceData.map_popup = '';
                    resourceData.displayname = '';
                    resourceData.graphid = '';
                    resourceData.graph_name = '';
                    resourceData = ko.mapping.fromJS(resourceData);
                    resourceLookup[resourceId] = resourceData;
                    $.get(arches.urls.resource_descriptors + resourceId, function (data) {
                        resourceLookup[resourceId].displaydescription(data.displaydescription);
                        resourceLookup[resourceId].map_popup(data.map_popup);
                        resourceLookup[resourceId].displayname(data.displayname);
                        resourceLookup[resourceId].graphid(data.graphid);
                        resourceLookup[resourceId].graph_name(data.graph_name);
                        resourceLookup[resourceId].loading(false);
                    });
                    return resourceLookup[resourceId];
                }
                var isFeatureVisible = function (feature) {
                    var overlay = _.find(self.overlays(), function(overlay) {
                        return _.find(overlay.layer_definitions, function (layer) {
                            return layer.id === feature.layer.id;
                        });
                    });
                    return !overlay.invisible();
                }
                self.map.on('mousemove', function(e) {
                    var features = self.map.queryRenderedFeatures(e.point);
                    var hoverData = null;
                    var clickable = false;
                    var hoverFeature = _.find(features, function(feature) {
                        if (feature.properties.resourceinstanceid) {
                            return isFeatureVisible(feature);
                        }
                    }) || _.find(features, function(feature) {
                        if (feature.layer.id === 'search-results-hex') {
                            return isFeatureVisible(feature);
                        }
                    }) || null;

                    if (hoverFeature && hoverFeature.properties) {
                        hoverData = hoverFeature.properties;
                        if (hoverFeature.properties.resourceinstanceid) {
                            hoverData = lookupResourceData(hoverData);
                            clickable = true;
                        }
                    }

                    if (self.hoverData() !== hoverData) {
                        self.hoverData(hoverData);
                    }
                    self.map.getCanvas().style.cursor = clickable ? 'pointer' : '';
                }, this);

                map.on('click', function (e) {
                    var features = self.map.queryRenderedFeatures(e.point);
                    var clickData = null;
                    var clickFeature = _.find(features, function(feature) {
                        if (feature.properties.resourceinstanceid) {
                            return isFeatureVisible(feature);
                        }
                    }) || _.find(features, function(feature) {
                        if (feature.properties.total > 1) {
                            return isFeatureVisible(feature);
                        }
                    }) || null;
                    if (clickFeature) {
                        if (clickFeature.properties.resourceinstanceid) {
                            clickData = lookupResourceData(clickFeature.properties);
                        } else if (clickFeature.properties.total > 1) {
                            var coordinates = JSON.parse(clickFeature.properties.extent).coordinates;
                            if (Array.isArray(coordinates[0])) {
                                coordinates = coordinates[0];
                            } else {
                                coordinates = [coordinates];
                            }

                            var bounds = coordinates.reduce(function(bounds, coord) {
                                return bounds.extend(coord);
                            }, new mapboxgl.LngLatBounds(coordinates[0], coordinates[0]));

                            map.fitBounds(bounds, {
                                padding: 20
                            });
                        }
                    }

                    if (self.clickData() !== clickData) {
                        self.clickData(clickData);
                    }
                });

                ['draw.create', 'draw.update', 'draw.delete'].forEach(function(event) {
                    self.map.on(event, self.saveGeometries())
                });
                self.map.on('click', this.updateDrawMode())
                self.map.on('draw.selectionchange', self.updateFeatureStyles());

                if (this.context === 'search-filter') {
                    self.map.on('dragend', this.searchByExtent);
                    self.map.on('zoomend', this.searchByExtent);
                    self.map.on('rotateend', this.searchByExtent);
                    self.map.on('pitch', this.searchByExtent);
                    this.resizeOnChange.subscribe(function(){
                        setTimeout(this.searchByExtent, 600);
                    }, self);
                    $(window).on("resize", this.searchByExtent);
                } else {
                    self.map.on('moveend', this.updateConfigs());
                }

            }; //end setup map

            // preprocess relative paths for app tileserver
            // see: https://github.com/mapbox/mapbox-gl-js/issues/3636#issuecomment-261119004
            _.each(arches.mapSources, function(sourceConfig, name) {
                if (sourceConfig.tiles) {
                    sourceConfig.tiles.forEach(function(url, i) {
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
            this.sources["search-results-hex"] = {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            };
            this.sources["search-results-points"] = {
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
                "sprite": arches.mapboxSprites,
                "glyphs": arches.mapboxGlyphs,
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
