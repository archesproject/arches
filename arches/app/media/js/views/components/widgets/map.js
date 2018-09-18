define([
    'jquery',
    'knockout',
    'knockout-mapping',
    'underscore',
    'viewmodels/widget',
    'arches',
    'mapbox-gl',
    'mapbox-gl-draw',
    'turf',
    'geohash',
    'geojson-extent',
    'views/list',
    'views/components/widgets/map/map-styles',
    'views/components/widgets/map/bin-feature-collection',
    'viewmodels/map-controls',
    'viewmodels/xy-input',
    'mathjs',
    'select2',
    'bindings/select2v4',
    'bindings/fadeVisible',
    'bindings/mapbox-gl',
    'bindings/chosen',
    'bindings/color-picker',
    'geocoder-templates'
], function($, ko, koMapping, _, WidgetViewModel, arches, mapboxgl, Draw, turf, geohash, geojsonExtent, ListView, mapStyles, binFeatureCollection, MapControlsViewModel, XYInputViewModel, mathjs) {
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
     * @param {string} params.config.geocodeProvider - the geocoderid of the selected geocoder.
     * @param {string} params.config.basemap - the layer name of the selected basemap to be shown in the map
     * @param {object} params.config.geometryTypes - the geometry types available for a user to edit
     * @param {number} params.config.pitch - the pitch of the map in degrees
     * @param {number} params.config.bearing - the bearing of the map in degrees with north at 0
     * @param {string} params.config.geocodePlaceholder - the placehoder of the geocoder input
     * @param {boolean} params.config.geocoderVisible - whether the geocoder is available on the map
     * @param {number} params.config.minZoom - the min zoom of the map
     * @param {number} params.config.maxZoom - the max zoom of the map
     * @param {string} params.config.featureColor - the color of resource geometries
     * @param {number} params.config.featurePointSize - the point size of resource geometries
     * @param {number} params.config.featureLineWidth - the line width of resource geometries
     * @param {boolean} params.config.featureEditingDisabled - a config for reports that hides the draw tools
     * @param {object} params.config.overlayConfigs - an array of overlays saved to the widget
     */
    var viewModel = function(params) {
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
            'mapControlsHidden',
            'defaultValueType',
            'defaultValue'
        ];

        WidgetViewModel.apply(this, [params]);

        this.mapImage = ko.observable(null);
        this.configType = params.reportHeader || 'header';
        this.resizeOnChange = ko.pureComputed(function() {
            return {
                param: ko.unwrap(params.resizeOnChange),
                expanded: this.expanded()
            };
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
        }, this);
        this.overlaySelectorClosed = ko.observable(true);
        this.geocodeShimAdded = ko.observable(false);
        this.selectedBasemap = this.basemap;
        this.drawMode = ko.observable();
        this.selectedFeatureType = ko.observable();
        this.overlays = ko.observableArray();
        this.overlayLibrary = ko.observableArray();
        this.geoJsonStringValid = ko.observable(true);
        this.overlayLibraryList = new ListView({
            items: self.overlayLibrary
        });
        this.minimizeNotifications = ko.observable(false);
        this.drawFeaturesOnMap = ko.observable(true);

        if (this.centerX() == 0 && this.centerY() == 0 && this.zoom() == 0) {
            //Infering that the default widget config settings are used and switching to system_settings for map position.
            this.centerX(arches.mapDefaultX);
            this.centerY(arches.mapDefaultY);
            this.zoom(arches.mapDefaultZoom);
            this.maxZoom(arches.mapDefaultMaxZoom);
            this.minZoom(arches.mapDefaultMinZoom);
        }

        this.zoomConfigOpen = ko.observable(false);
        this.positionConfigOpen = ko.observable(false);
        this.geocoderConfigOpen = ko.observable(false);
        this.resourcePropertiesConfigOpen = ko.observable(false);
        this.defaultValueConfigOpen = ko.observable(false);
        this.clickSourceLayerCache;

        if (this.context === 'search-filter') {
            this.query = params.query;
            this.clearSearch = params.clearSearch;
            this.searchBuffer = params.searchBuffer;
        }

        this.bufferUnits = [{
            name: 'meters',
            val: 'm'
        },
        {
            name: 'feet',
            val: 'ft'
        }
        ];
        this.buffer = ko.observable('100');
        this.bufferUnit = ko.observable('m');
        this.queryFeature;
        this.extentSearch = ko.observable(false);
        this.geojsonString = ko.observable();
        this.geojsonInput = ko.observable(false);
        this.pitchAndZoomEnabled = ko.observable(true);
        this.atMaxZoom = ko.observable(false);
        this.atMinZoom = ko.observable(true);

        this.anchorLayerId = 'gl-draw-point.cold'; //Layers are added below this drawing layer

        this.summaryDetails = [];

        if (ko.unwrap(this.value) !== null) {
            this.summaryDetails = koMapping.toJS(this.value).features || [];
        }

        this.hoverData = ko.observable(null);
        this.clickData = ko.observable(null);
        this.getMarkup = function(val){
            if (val().feature_info_content) {
                var popupdata = val();
                var expression = /[-a-zA-Z0-9@:%_\+.~#?&//=]{2,256}\.[a-z]{2,4}\b(\/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?/gi;
                var regex = new RegExp(expression);
                var match = popupdata.feature_info_content.match(regex);
                if (match) {
                    if (popupdata.feature_info_content === match[0]) {
                        $.ajax({
                            url: arches.urls.feature_popup_content,
                            data: {url:popupdata.feature_info_content},
                            method: 'POST'
                        }).done(function(data){
                            popupdata.feature_info_content = data;
                            val(popupdata);
                        }, this);
                    }
                }
            }
        };
        this.popupData = ko.computed(function() {
            if (self.hoverData()) {
                self.getMarkup(self.hoverData);
            }
            if (self.clickData()) {
                self.getMarkup(self.clickData);
            }
            var clickData = self.clickData();
            return clickData ? clickData : self.hoverData();
        });

        this.geocodingProviders = arches.geocodingProviders;
        if (!this.geocodeProvider()) {
            this.geocodeProvider(arches.geocoderDefault);
        }

        this.geocodeProviderDetails = ko.mapping.fromJS(_.findWhere(this.geocodingProviders, {
            'geocoderid': this.geocodeProvider()
        }));

        this.geocodeProvider.subscribe(function(geocoderid) {
            var provider = _.findWhere(this.geocodingProviders, {
                'geocoderid': geocoderid
            });
            this.geocodeProviderDetails.api_key(provider.api_key);
            this.geocodeProviderDetails.component(provider.component);
        }, this);

        this.loadGeometriesIntoDrawLayer = function() {
            self.geojsonInput(false);
            self.xyInput.active(false);
            if (self.draw) {
                var val = koMapping.toJS(self.value);
                self.draw.deleteAll();
                if (val) {
                    self.draw.add(val);
                }
                self.drawFeaturesOnMap(self.draw.getAll().features.length > 0);
            }
        };

        this.zoomToDrawLayer = function(){
            var allFeatures = this.context === 'report-header' ?
                this.value() : self.draw.getAll();
            if (allFeatures.features.length > 0) {
                this.map.fitBounds(geojsonExtent(allFeatures), {padding:20});
            }
        };

        this.clearGeometries = function(val) {
            if (self.draw !== undefined && !val) {
                self.draw.deleteAll();
            } else if (val && val.features) {
                if (val.features.length === 0 && self.context === 'search-filter') {
                    self.searchBuffer(null);
                    self.updateSearchQueryLayer([]);
                }
            }
        };

        if (ko.isObservable(this.value)) {
            this.value.subscribe(this.clearGeometries);
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
                //        if (layer.source === resourceSourceId + oldDc) {
                //             layer.source = resourceSourceId + dc;
                //        }
                //     });
                //     style.sources = _.defaults(self.sources, style.sources);
                //    self.map.setStyle(style);
                // }

                if (self.draw !== undefined) {
                    self.draw.changeMode('simple_select');
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

        this.xyInput = new XYInputViewModel({
            mapWidget: self
        });

        if (params.graph !== undefined) {
            if (params.graph.get) {
                this.resourceIcon = params.graph.get('iconclass');
                this.resourceName = params.graph.get('name');
                this.graphId = params.graph.get('graphid');
            } else {
                this.resourceIcon = params.graph.iconclass;
                this.resourceName = params.graph.name;
                this.graphId = params.graph.graphid;
            }
            this.featurePointSize(Number(this.featurePointSize()));
            this.featureLineWidth(Number(this.featureLineWidth()));
            this.featureColorCache = this.featureColor();
            this.featurePointSizeCache = this.featurePointSize();
            this.featureLineWidthCache = this.featureLineWidth();
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

        this.layers = $.extend(true, [], _.filter(arches.mapLayers, function(layer) {
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
            };
            return searchQueryLayer;
        };

        this.updateSearchQueryLayer = function(geojson_features) {
            if ('getMapStyle' in self) {
                var style = self.getMapStyle();
                style.sources['search-query'].data = {
                    "type": "FeatureCollection",
                    "features": geojson_features
                };
                self.map.setStyle(style);
                if (geojson_features.length === 0) {
                    self.clearSearch(true);
                    self.clearSearch(false);
                    if (self.draw.getAll().features.length > 0) {
                        _.each(self.geometryTypeDetails, function(type) {
                            if (type.active() === true) {
                                type.active(false);
                            }
                        });
                        self.switchToEditMode();
                        self.draw.deleteAll();
                    }
                }
            }
        };

        this.restoreSearchState = function() {
            if (this.query) {
                var features = this.query.features;
                var drawMode;
                var geojsonToDrawMode = {
                    'Point': {
                        'drawMode': 'draw_point',
                        'name': 'Point'
                    },
                    'LineString': {
                        'drawMode': 'draw_line_string',
                        'name': 'Line'
                    },
                    'Polygon': {
                        'drawMode': 'draw_polygon',
                        'name': 'Polygon'
                    }
                };
                if (features.length > 0) {
                    this.queryFeature = features[0];
                    if (this.queryFeature.properties.extent_search === true) {
                        var bounds = new mapboxgl.LngLatBounds(geojsonExtent(this.queryFeature));
                        this.toggleExtentSearch();
                        this.map.fitBounds(bounds);
                    } else {
                        drawMode = geojsonToDrawMode[this.queryFeature.geometry.type];
                        this.draw.changeMode(drawMode.drawMode);
                        this.drawMode(drawMode.drawMode);
                        this.geometryTypeDetails[drawMode.name].active(true);
                        this.updateSearchQueryLayer([self.queryFeature]);
                        if (this.queryFeature.properties.buffer) {
                            if (this.buffer() === this.queryFeature.properties.buffer.width && this.bufferUnit() === this.queryFeature.properties.buffer.unit) {
                                this.updateBuffer(this.queryFeature.properties.buffer.width, this.queryFeature.properties.buffer.unit);
                            } else {
                                this.buffer(this.queryFeature.properties.buffer.width);
                                this.bufferUnit(this.queryFeature.properties.buffer.unit);
                            }
                        }
                    }
                }
            } else {
                this.fitToAggregationBounds();
            }
        };

        this.updateDrawLayerWithJson = function(val) {
            var zoomExtent = 500;
            if (val !== '') {
                try {
                    var data = JSON.parse(val);
                    try {
                        if (self.context === 'search-filter') {
                            self.clearGeometries(null);
                        }
                        self.draw.add(data);
                        self.saveGeometries();
                        if (data['type'] === 'Point') {
                            data = turf.buffer(data, zoomExtent, 'meters');
                        }
                        var bbox = turf.bbox(data);
                        var ll = new mapboxgl.LngLat(bbox[0], bbox[1]);
                        var ur = new mapboxgl.LngLat(bbox[2], bbox[3]);
                        var bounds = new mapboxgl.LngLatBounds(ll, ur);
                        self.map.fitBounds(bounds, {
                            padding: 200
                        });
                        window.setTimeout(function() {
                            self.geojsonString('');
                        }, 500);
                        self.geoJsonStringValid(true);
                        if (self.context === 'search-filter') {
                            self.applySearchBuffer(self.buffer());
                        }
                    } catch (err) {
                        self.geoJsonStringValid(false);
                    }
                } catch (err) {
                    self.geoJsonStringValid(false);
                }
            }
        };


        this.geojsonString.subscribe(this.updateDrawLayerWithJson, self);
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
        };

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

            if (this.context === 'survey-bounds') {
                window.setTimeout(self.loadGeometriesIntoDrawLayer, 1500);
            }

            this.layers.forEach(function(mapLayer) {
                if (mapLayer.name === this.basemap()) {
                    _.each(mapLayer.layer_definitions, function(layer) {
                        initialLayers.push(layer);
                    });
                }
            }, this);
            return initialLayers;
        };

        this.geometryTypeDetails = {
            Point: {
                name: 'Point',
                title: 'Draw a Marker',
                class: 'leaflet-draw-draw-marker',
                icon: 'ion-location',
                drawMode: 'draw_point',
                active: ko.observable(false)
            },
            Line: {
                name: 'Line',
                title: 'Draw a Polyline',
                icon: 'ion-steam',
                class: 'leaflet-draw-draw-polyline',
                drawMode: 'draw_line_string',
                active: ko.observable(false)
            },
            Polygon: {
                name: 'Polygon',
                title: 'Draw a Polygon',
                icon: 'fa fa-pencil-square-o',
                class: 'leaflet-draw-draw-polygon',
                drawMode: 'draw_polygon',
                active: ko.observable(false)
            }
        };

        this.drawModes = _.pluck(this.geometryTypeDetails, 'drawMode');

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

            var draw = new Draw({
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

                    var resize = function() {
                        map.resize();
                        duration -= 1;
                        if (duration >= 0) {
                            _.defer(resize, 1);
                        }
                    };
                    _.defer(resize, 1);
                });
            }
            this.xyInput.setMap(map);
            this.draw = draw;
            this.map.addControl(draw);

            var devicePixelRatio = window.devicePixelRatio;
            var generatePrintMap = function() {
                Object.defineProperty(window, 'devicePixelRatio', {
                    get: function() {
                        return 3.125;
                    }
                });

                var hidden = document.createElement('div');
                var container = document.createElement('div');
                hidden.className = 'hidden-map';
                document.body.appendChild(hidden);
                container.className = 'print-map-container';
                hidden.appendChild(container);

                var printMap = new mapboxgl.Map({
                    container: container,
                    center: self.map.getCenter(),
                    zoom: self.map.getZoom(),
                    style: self.map.getStyle(),
                    bearing: self.map.getBearing(),
                    pitch: self.map.getPitch(),
                    interactive: false,
                    attributionControl: false
                });
                printMap.once('load', function() {
                    self.mapImage(printMap.getCanvas().toDataURL());
                    printMap.remove();
                    hidden.parentNode.removeChild(hidden);
                    Object.defineProperty(window, 'devicePixelRatio', {
                        get: function() {
                            return devicePixelRatio;
                        }
                    });
                    self.map.resize();
                });
            };

            this.map.on('load', function() {
                if (!self.configForm) {
                    if (self.context === 'report-header') {
                        map.on('moveend', _.throttle(generatePrintMap, 3000));
                    }
                    var zoomToGeoJSON = function(data, fly) {
                        var method = fly ? 'flyTo' : 'jumpTo';
                        var bounds = new mapboxgl.LngLatBounds(geojsonExtent(data));
                        var tr = self.map.transform;
                        var nw = tr.project(bounds.getNorthWest());
                        var se = tr.project(bounds.getSouthEast());
                        var size = se.sub(nw);
                        var scaleX = (tr.width - 80) / size.x;
                        var scaleY = (tr.height - 80) / size.y;
                        var maxZoom = ko.unwrap(self.maxZoom);
                        maxZoom = maxZoom > 17 ? 17 : maxZoom;
                        var options = {
                            center: tr.unproject(nw.add(se).div(2)),
                            zoom: Math.min(tr.scaleZoom(tr.scale * Math.min(scaleX, scaleY)), maxZoom)
                        };
                        self.map[method](options);
                    };
                    self.zoomToPopupData = function() {
                        var fcs;
                        var fc = {
                            "type": "FeatureCollection",
                            "features": []
                        };
                        fcs = ko.unwrap(self.popupData().featureCollections);
                        _.each(fcs, function(currentFC) {
                            fc.features = fc.features.concat(currentFC.geom.features);
                        });
                        zoomToGeoJSON(fc, true);
                    };
                    var source = self.map.getSource('resource');
                    var features = [];
                    var result = {
                        "type": "FeatureCollection",
                        "features": []
                    };
                    var data = null;

                    self.fitToAggregationBounds = function(agg) {
                        var agg = self.searchAggregations();
                        var aggBounds;
                        if (agg && agg.geo_aggs.bounds.bounds && self.map && !self.extentSearch()) {
                            aggBounds = agg.geo_aggs.bounds.bounds;
                            var bounds = [
                                [
                                    aggBounds.top_left.lon,
                                    aggBounds.bottom_right.lat
                                ],
                                [
                                    aggBounds.bottom_right.lon,
                                    aggBounds.top_left.lat
                                ]
                            ];
                            var maxZoom = ko.unwrap(self.maxZoom);
                            maxZoom = maxZoom > 17 ? 17 : maxZoom;
                            map.fitBounds(bounds, {
                                padding: 45,
                                maxZoom: maxZoom
                            });
                        }
                    };

                    self.getMapStyle = function() {
                        var style = map.getStyle();
                        style.sources = _.defaults(self.sources, style.sources);
                        var updateGeoJsonSource = function() {
                            return function(source, key) {
                                if (source.type === 'geojson') {
                                    style.sources[key].data = self.map.getSource(key)._data;
                                }
                            };
                        };
                        _.each(style.sources, updateGeoJsonSource(), this);
                        return style;
                    };

                    self.overlayLibrary(self.createOverlays());
                    if (self.resourceLayer !== undefined && self.context === 'report-header') {
                        self.overlays.unshift(self.createOverlay(self.resourceLayer));
                    }

                    if (self.context === 'search-filter') {
                        self.searchAggregations = params.searchAggregations;
                        var bins = binFeatureCollection(self.searchAggregations);
                        self.searchBuffer.subscribe(function(val){
                            self.updateSearchQueryLayer([{geometry: JSON.parse(self.searchBuffer())}, self.queryFeature]);
                        });
                        var getSearchAggregationGeoJSON = function() {
                            var agg = ko.unwrap(self.searchAggregations);
                            if (!agg || !agg.geo_aggs.grid.buckets) {
                                return {
                                    "type": "FeatureCollection",
                                    "features": []
                                };
                            }

                            if (self.value() && self.value()['features'].length > 0 && self.extentSearch() === false) {
                                var geojsonFC = self.value();
                                var extent = geojsonExtent(geojsonFC);
                                var bounds = new mapboxgl.LngLatBounds(extent);
                                self.map.fitBounds(bounds, {
                                    padding: self.buffer()
                                });
                            } else {
                                self.fitToAggregationBounds();
                            }
                            var features = [];
                            _.each(agg.geo_aggs.grid.buckets, function(cell) {
                                var pt = geohash.decode(cell.key);
                                var feature = turf.point([pt.lon, pt.lat], {
                                    doc_count: cell.doc_count
                                });
                                features.push(feature);
                            });
                            var pointsFC = turf.featureCollection(features);

                            var aggregated = turf.collect(ko.unwrap(bins), pointsFC, 'doc_count', 'doc_count');
                            _.each(aggregated.features, function(feature) {
                                feature.properties.doc_count = _.reduce(feature.properties.doc_count, function(i, ii) {
                                    return i + ii;
                                }, 0);
                            });

                            return {
                                points: pointsFC,
                                agg: aggregated
                            };
                        };
                        var updateSearchPointsGeoJSON = function() {
                            var pointSource = self.map.getSource('search-results-points');
                            var agg = ko.unwrap(self.searchAggregations);
                            if (!agg || !agg.results) {
                                return {
                                    "type": "FeatureCollection",
                                    "features": []
                                };
                            }

                            var features = [];
                            var mouseoverInstanceId = self.results.mouseoverInstanceId();
                            var hoverData = self.hoverData();
                            var clickData = self.clickData();
                            _.each(agg.results, function(result) {
                                _.each(result._source.points, function(point) {
                                    var feature = turf.point([point.point.lon, point.point.lat], _.extend(result._source, {
                                        resourceinstanceid: result._id,
                                        highlight: result._id === mouseoverInstanceId ||
                                             (clickData ? (ko.unwrap(clickData.resourceinstanceid) === result._id) : false) ||
                                             (hoverData ? (ko.unwrap(hoverData.resourceinstanceid) === result._id) : false)
                                    }));
                                    features.push(feature);
                                });
                            });

                            var pointsFC = turf.featureCollection(features);
                            pointSource.setData(pointsFC);
                        };
                        self.overlays.unshift(self.createOverlay(self.searchQueryLayer));
                        self.updateSearchResultsLayer = function() {
                            var aggSource = self.map.getSource('search-results-hex');
                            var hashSource = self.map.getSource('search-results-hashes');
                            var aggData = getSearchAggregationGeoJSON();
                            aggSource.setData(aggData.agg);
                            hashSource.setData(aggData.points);
                            updateSearchPointsGeoJSON();
                        };
                        self.searchAggregations.subscribe(self.updateSearchResultsLayer);
                        if (ko.isObservable(bins)) {
                            bins.subscribe(self.updateSearchResultsLayer);
                        }
                        if (self.searchAggregations()) {
                            self.updateSearchResultsLayer();
                        }
                        self.results.mouseoverInstanceId.subscribe(updateSearchPointsGeoJSON);
                        self.clickData.subscribe(updateSearchPointsGeoJSON);
                        self.hoverData.subscribe(function(val) {
                            var resultsHoverLayer = self.map.getLayer('search-results-hex-outline-highlighted');
                            var filter = ['==', 'id', ''];
                            if (val && val.doc_count) {
                                filter[2] = val.id;
                            }
                            if (resultsHoverLayer) {
                                self.map.setFilter(resultsHoverLayer.id, filter);
                            }
                            updateSearchPointsGeoJSON();
                        });
                        self.results.mapLinkData.subscribe(function(data) {
                            zoomToGeoJSON(data, true);
                        });
                    }


                    if (self.context === 'report-header') {
                        data = self.value();
                        source.setData(data);
                        self.value.subscribe(function(value) {
                            source.setData(value);
                            if (value.features.length > 0){
                                zoomToGeoJSON(value);
                            }
                        });
                        _.each(['resource-poly' + self.graphId, 'resource-line' + self.graphId, 'resource-point' + self.graphId], function(layerId) { //clear and add resource layers so that they are on top of map
                            var cacheLayer = self.map.getLayer(layerId);
                            self.map.moveLayer(layerId, self.anchorLayerId);
                        }, self);

                    } else if (self.context !== 'report-header' && !ko.isObservable(self.value)) {
                        data = koMapping.toJS(self.value);
                        self.loadGeometriesIntoDrawLayer();
                    } else { //if values are for a form widget...
                        if (_.isObject(self.value())) { //confirm value is not "", null, or undefined
                            data = koMapping.toJS(self.value);
                            self.loadGeometriesIntoDrawLayer();
                        }
                    }

                    if (data) {
                        if (data.features.length > 0) {
                            zoomToGeoJSON(data);
                        }
                    }
                }
                window.setTimeout(function() {
                    window.dispatchEvent(new Event('resize'));
                    if (self.context === 'search-filter') {
                        self.restoreSearchState();
                    }
                }, 30);
            });

            /**
              * Updates the appearance of the draw layer when feature appearance configs change
              * @return {null}
              */
            this.updateDrawLayerPaintProperties = function(paintProperties, val, isNumber) {
                var val = isNumber ? Number(val) : val; //point size and line width must be number types
                _.each(this.draw.options.styles, function(style) {
                    var paint = this.map.getLayer(style.id).paint;
                    var self = this;
                    paintProperties.forEach(function(prop) {
                        if (paint.hasOwnProperty(prop)) {
                            if (!style.id.includes('halo')) {
                                self.map.setPaintProperty(style.id, prop, val);
                            }
                            if (style.id.includes('halo') && !prop.includes('color')) {
                                self.map.setPaintProperty(style.id, prop, val * 1.25);
                            }
                        }
                    });
                }, this);
            };

            this.featureColor.subscribe(function(e) {
                this.updateDrawLayerPaintProperties(['fill-outline-color', 'fill-color', 'circle-color', 'line-color'], e);
            }, this);

            this.featurePointSize.subscribe(function(e) {
                this.updateDrawLayerPaintProperties(['circle-radius'], e, true);
            }, this);

            this.featureLineWidth.subscribe(function(e) {
                this.updateDrawLayerPaintProperties(['line-width'], e, true);
            }, this);

            this.switchToEditMode = function() {
                self.draw.changeMode('simple_select');
                self.drawMode(undefined);
            };

            if (this.context === 'resource-editor') {
                self.drawMode.subscribe(function(val) {
                    if (val !== undefined) {
                        self.geojsonInput(false);
                        if (!self.xyInput.selectedPoint() || val !== 'simple_select') {
                            self.xyInput.active(false);
                        }
                    }
                });
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
                    this.xyInput.active(false);
                    this.draw.deleteAll();
                    this.queryFeature = undefined;
                    if (selectedDrawTool === 'end' || this.geometryTypeDetails[selectedDrawTool].drawMode === this.drawMode() || this.geometryTypeDetails[selectedDrawTool].drawMode !== this.drawMode()) {
                        this.updateSearchQueryLayer([]);
                    }
                } else if (this.context === 'resource-editor') {
                    if (this.geojsonInput()) {
                        this.geojsonInput(false);
                    }
                }
                if (this.form) {
                    this.featureColor(this.featureColorCache);
                }
                _.each(self.geometryTypeDetails, function(geomtype) {
                    if (geomtype.name === selectedDrawTool) {
                        self.geometryTypeDetails[selectedDrawTool].active(!self.geometryTypeDetails[selectedDrawTool].active());
                    } else {
                        self.geometryTypeDetails[geomtype.name].active(false);
                    }
                });
                if (selectedDrawTool === 'delete') {
                    self.draw.trash();
                    self.drawMode('simple_select');
                } else if (selectedDrawTool === 'end') {
                    self.switchToEditMode();
                } else {
                    if (!self.drawMode()) {
                        self.draw.changeMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                        self.drawMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                    } else if (self.geometryTypeDetails[selectedDrawTool].drawMode === self.drawMode()) {
                        self.draw.changeMode('simple_select');
                        if (self.mapControls.mapControlsExpanded()) {
                            self.drawMode(undefined);
                        } else {
                            self.drawMode('simple_select');
                        }
                    } else {
                        self.draw.changeMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                        self.drawMode(self.geometryTypeDetails[selectedDrawTool].drawMode);
                    }
                }

            };

            this.removeMaplayer = function(maplayer) {
                if (maplayer !== undefined) {
                    var style = this.getMapStyle();
                    maplayer.layer_definitions.forEach(function(def) {
                        var layer = _.find(style.layers, function(layer) {
                            return layer.id === def.id;
                        });
                        style.layers = _.without(style.layers, layer);
                    });
                    this.map.setStyle(style);
                }
            };

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
            };

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
                    }
                    if (overlay !== undefined) {
                        self.addMaplayer(overlay);
                        self.overlays.push(overlay);
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
                'fill-extrusion',
                'heatmap'
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
                            return prop;
                        }
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
                        var setStyle = false;
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
                                            this.map.setPaintProperty(layer.id, opacityType + '-opacity', startVal * opacityVal);
                                        } else {
                                            setStyle = true;
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
                                        this.map.setPaintProperty(layer.id, opacityType + '-opacity', opacityVal);
                                    }
                                }, self);
                            }
                        }, this);
                        if (setStyle) {
                            map.setStyle(style);
                        }
                    }
                });
                configMaplayer = _.findWhere(this.overlayConfigs(), {
                    "maplayerid": maplayer.maplayerid
                });
                if (configMaplayer !== undefined) {
                    maplayer.checkedOutOfLibrary(configMaplayer !== undefined);
                    maplayer.opacity(configMaplayer.opacity);
                }
                maplayer.opacity.subscribe(function(value) {
                    self.overlayOpacity(value);
                    this.overlayConfigs().forEach(
                        function(overlayConfig) {
                            if (maplayer.maplayerid === overlayConfig.maplayerid) {
                                overlayConfig.opacity = value;
                            }
                        }, self);
                    maplayer.updateOpacity(value);
                }, self);
                return maplayer;
            };

            this.createOverlays = function() {
                var overlays = [];
                this.layers.forEach(function(layer) {
                    if (layer.isoverlay === true) {
                        overlay = self.createOverlay(layer);
                        overlays.push(overlay);
                    }
                });
                return overlays;
            };

            this.exchangeOverlay = function(e) {
                if (this.checkedOutOfLibrary() === true) {
                    self.overlays.remove(this);
                    self.removeMaplayer(this);
                } else {
                    self.overlays.push(this);
                }
                this.checkedOutOfLibrary(!this.checkedOutOfLibrary());
            };

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
                if (!this.form) {
                    var mapCenter = this.getCenter();
                    var zoom = self.map.getZoom();
                    if (self.zoom() !== zoom) {
                        self.zoom(zoom);
                    }
                    self.centerX(mapCenter.lng);
                    self.centerY(mapCenter.lat);
                    self.bearing(this.getBearing());
                    self.pitch(this.getPitch());
                }
            };

            this.saveGeometries = function() {
                self.drawFeaturesOnMap(self.draw.getAll().features.length > 0);
                var currentDrawing = self.draw.getAll();
                if (self.value.features !== undefined) {
                    _.each(self.value.features(), function(feature) {
                        self.value.features.pop();
                    });
                    currentDrawing.features.forEach(function(feature) {
                        self.value.features.push(feature);
                    });
                } else {
                    self.value(currentDrawing);
                }
                self.queryFeature = currentDrawing.features[currentDrawing.features.length - 1];
                if (self.context === 'search-filter') {
                    self.updateSearchQueryLayer([self.queryFeature]);
                }
            };

            this.updateDrawMode = function(e) {
                var selectedFeatureType;
                var featureCount = self.draw.getAll().features.length;
                if (self.context === 'search-filter' && featureCount > 1) {
                    _.each(self.draw.getAll().features.slice(0, featureCount - 1), function(feature) {
                        self.draw.delete(feature.id);
                    }, self);
                }
                if (_.contains(['draw_point', 'draw_line_string', 'draw_polygon'], self.drawMode()) && self.drawMode() !== self.draw.getMode()) {
                    self.draw.changeMode(self.drawMode());
                    if (self.context === 'search-filter') {
                        if (self.buffer() > 0) {
                            self.applySearchBuffer(self.buffer());
                        }
                    }
                } else {
                    self.drawMode(self.draw.getMode());
                    if (self.context !== 'search-filter') {
                        if (self.draw.getSelectedIds().length > 0) {
                            selectedFeatureType = self.draw.get(self.draw.getSelectedIds()[0]).geometry.type;
                            if (selectedFeatureType === 'Point') {
                                self.xyInput.updateSelectedPoint();
                            }
                            self.selectedFeatureType(selectedFeatureType === 'LineString' ? 'line' : selectedFeatureType.toLowerCase());
                        } else {
                            if (self.draw.getMode().endsWith("select")) {
                                self.drawMode(undefined);
                            }
                        }
                    }
                }
            };

            this.updateFeatureStyles = function() {
                if (self.form) {
                    self.featureColor() === self.featureColorCache || self.featureColor(self.featureColorCache);
                    self.featurePointSize() === self.featurePointSizeCache || self.featurePointSize(self.featurePointSizeCache);
                    self.featureLineWidth() === self.featureLineWidthCache || self.featureLineWidth(self.featureLineWidthCache);
                }
            };

            this.deactivateDrawTools = function() {
                _.each(self.geometryTypeDetails, function(geomtype) {
                    if (geomtype.active()) {
                        geomtype.active(false);
                    }
                });
                self.switchToEditMode();
            };

            this.geojsonInput.subscribe(function(val) {
                if (!val) {
                    this.geoJsonStringValid(true);
                    this.geojsonString('');
                } else {
                    self.deactivateDrawTools();
                    self.xyInput.active(false);
                }
            }, this);

            this.xyInput.active.subscribe(function(val){
                if (val) {
                    self.deactivateDrawTools();
                    self.geojsonInput(false);
                }
            });

            this.overlays.subscribe(function(overlays) {
                this.overlayConfigs([]);
                for (var i = overlays.length; i-- > 0;) { //Using a conventional loop because we want to go backwards over the array
                    this.removeMaplayer(overlays[i]);
                }
                for (var i = overlays.length; i-- > 0;) {
                    if (overlays[i].isResource !== true) {
                        this.overlayConfigs().push({
                            'maplayerid': overlays[i].maplayerid,
                            'name': overlays[i].name,
                            'opacity': overlays[i].opacity()
                        });
                    }
                    this.addMaplayer(overlays[i]);
                }
                // this.geocoder.redrawLayer();
            }, this);

            this.pitchAndZoomEnabled.subscribe(function(val) {
                if (!val) {
                    this.map.setPitch(0);
                    this.map.setBearing(0);
                    this.map.dragRotate.disable();
                } else {
                    this.map.setPitch(this.pitch() > 0 ? this.pitch() : 50);
                    this.map.dragRotate.enable();
                }
            }, this);

            this.applySearchBuffer = function(val) {
                var buffer;
                var coords3857;
                var coords4326;
                var coords;
                if (self.value().features.length > 0 && self.queryFeature !== undefined) {
                    if (val > 0) {
                        self.queryFeature.properties.buffer = {
                            width: self.buffer(),
                            unit: self.bufferUnit()
                        };
                        self.value().features[0] = self.queryFeature;
                        self.updateSearchQueryLayer([{geometry: JSON.parse(self.searchBuffer())},self.queryFeature]);
                    } else {
                        self.queryFeature.properties.buffer = {
                            width: 0,
                            unit: self.bufferUnit()
                        };
                        self.value().features = [self.queryFeature];
                    }
                    self.value(self.value());
                    self.draw.changeMode(self.drawMode());
                }
            };

            this.toggleExtentSearch = function(val) {
                self.extentSearch(!self.extentSearch());
                if (self.extentSearch() === true) {
                    self.draw.deleteAll();
                    self.xyInput.active(false);
                    self.deactivateDrawTools();
                } else {
                    self.value({
                        "type": "FeatureCollection",
                        "features": []
                    });
                }
            };

            this.searchByExtent = function() {
                if (self.extentSearch() === true) {
                    self.queryFeature = undefined;
                    if (_.contains(self.drawModes, self.drawMode())) {
                        self.updateSearchQueryLayer([]);
                    }
                    var bounds = self.map.getBounds();
                    var ll = bounds.getSouthWest().toArray();
                    var ul = bounds.getNorthWest().toArray();
                    var ur = bounds.getNorthEast().toArray();
                    var lr = bounds.getSouthEast().toArray();
                    var coordinates = [ll, ul, ur, lr, ll];
                    var boundsFeature = {
                        "type": "Feature",
                        "properties": {
                            "buffer": {
                                "width": 0,
                                "unit": self.bufferUnit()
                            },
                            "extent_search": true
                        },
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [coordinates]
                        }
                    };
                    self.value().features = [boundsFeature];
                    self.value(self.value());
                }
            };

            this.extentSearch.subscribe(function(val) {
                self.searchByExtent();
            });

            this.updateBuffer = function(val, units) {
                var maxBuffer = 100000;
                var maxBufferUnits = 'm';
                var maxBufferUnit = mathjs.unit(maxBuffer, maxBufferUnits);
                var unit = mathjs.unit(val + units);
                unit.equalBase(maxBufferUnit);
                if (val < 0) {
                    this.buffer(0);
                } else if (unit.value > maxBufferUnit.value) {
                    this.buffer(maxBuffer);
                    this.bufferUnit(maxBufferUnits);
                } else {
                    this.applySearchBuffer(unit.value);
                }
            };

            this.buffer.subscribe(function(val) {
                this.updateBuffer(val, this.bufferUnit());
            }, this);

            this.bufferUnit.subscribe(function(val) {
                this.updateBuffer(this.buffer(), val);
            }, this);

            var resourceLookup = {};
            var lookupResourceData = function(resourceData) {
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
                resourceData.featureCollections = [];
                resourceData = ko.mapping.fromJS(resourceData);
                resourceLookup[resourceId] = resourceData;
                $.get(arches.urls.resource_descriptors + resourceId, function(data) {
                    resourceLookup[resourceId].displaydescription(data.displaydescription);
                    resourceLookup[resourceId].map_popup(data.map_popup);
                    resourceLookup[resourceId].displayname(data.displayname);
                    resourceLookup[resourceId].graphid(data.graphid);
                    resourceLookup[resourceId].graph_name(data.graph_name);
                    resourceLookup[resourceId].featureCollections(data.geometries);
                    resourceLookup[resourceId].loading(false);
                });
                return resourceLookup[resourceId];
            };

            var isFeatureVisible = function(feature) {
                var overlay = _.find(self.overlays(), function(overlay) {
                    return _.find(overlay.layer_definitions, function(layer) {
                        return layer.id === feature.layer.id;
                    });
                });
                return !overlay.invisible();
            };

            var highlightFeature = function(feature, layerIdSuffix, filterProperty, style) {
                var featureId = feature && feature.properties[filterProperty] ? feature.properties[filterProperty] : '';
                _.each(style.layers, function(layer) {
                    if (layer.id.endsWith(layerIdSuffix)) {
                        var filter = self.map.getFilter(layer.id);
                        if (filter) {
                            _.each(filter, function(query) {
                                if (Array.isArray(query) && query[1] === filterProperty) {
                                    query[2] = featureId;
                                }
                            });
                            map.setFilter(layer.id, filter);
                        } else {
                            map.setFilter(layer.layer.id, ["all", ["==", filterProperty, featureId]]);
                        }
                    }
                });
            };

            self.clearHighlight = function(layerIdSuffix, currentFeature) {
                var style = self.getMapStyle();
                _.each(style.layers, function(layer) {
                    if (layer.id.endsWith(layerIdSuffix)) {
                        var filter = self.map.getFilter(layer.id);
                        var sourceLayerId = layer.id.startsWith('resources-') ? 'resources-fill-' + layer['source-layer'] : layer['source-layer'];
                        var sourceLayer = _.findWhere(style.layers, {'id': sourceLayerId});
                        if (filter) {
                            _.each(filter, function(item) {
                                if (Array.isArray(item) && (item[1] === '_featureid' || item[1] === 'resourceinstanceid') && item[2] != currentFeature) {
                                    item[2] = '';
                                    map.setFilter(layer.id, filter);
                                }
                            });
                        }
                        if (sourceLayer.filter) {
                            var clickCacheFeatureId;
                            var clickCacheFilterProperty;
                            if (self.clickSourceLayerCache && self.clickData()) {
                                clickCacheFeatureId = self.clickSourceLayerCache.featureid;
                                clickCacheFilterProperty = self.clickSourceLayerCache.filterProperty;
                            }
                            _.each(sourceLayer.filter, function(query){
                                if (Array.isArray(query) && query.length === 3) {
                                    if ((query[1] === '_featureid' || query[1] === 'resourceinstanceid') && (query[2] != clickCacheFeatureId && query[1] != clickCacheFilterProperty) && query[2] != currentFeature) {
                                        sourceLayer.filter = self.removeLayerFilterQuery(sourceLayer.filter, query);
                                    }
                                }
                            });
                            map.setFilter(sourceLayer.id, sourceLayer.filter);
                        }
                    }
                });
            };

            self.layerFilterHasQuery = function(filter, query) {
                var matchingQueries = _.find(filter, function(q) {
                    return _.difference(q, query).length === 0;
                });
                if (matchingQueries) {
                    return true;
                } else {
                    return false;
                }
            };

            self.removeLayerFilterQuery = function(filter, query) {
                filter = _.without(filter, query);
                return filter;
            };

            self.filterSourceFeature = function(layer, filterProperty, featureId) {
                var filtersCurrentFeature;
                var filtersClickedFeature;
                var clickSourceCacheFilter;
                var sourceFilterCopy = null;
                var clickSourceCacheFilterCopy = null;
                var hideSourceQuery;
                var hideClickCacheQuery;
                if (!layer.filter) {
                    sourceFilterCopy = ["all", ["!=", filterProperty, featureId]];
                } else {
                    sourceFilterCopy = $.extend(true, [], layer.filter);
                    filtersCurrentFeature = self.layerFilterHasQuery(sourceFilterCopy, ["!=", filterProperty, featureId]);
                    if (filtersCurrentFeature === false) {
                        sourceFilterCopy.push(["!=", filterProperty, featureId]);
                    }
                }
                if (self.clickSourceLayerCache) {
                    clickSourceCacheFilter = ["!=", self.clickSourceLayerCache.filterproperty, self.clickSourceLayerCache.featureid];
                    filtersClickedFeature = self.layerFilterHasQuery(sourceFilterCopy, clickSourceCacheFilter);
                    if (filtersClickedFeature === false) {
                        sourceFilterCopy.push(clickSourceCacheFilter);
                    }
                }
                map.setFilter(layer.id, sourceFilterCopy); //filters the source feature
            };

            self.map.hoverFeatures = [];
            self.map.on('mousemove', function(e) {
                var features = self.map.queryRenderedFeatures(e.point);
                var updateFeatures = features.length !== self.map.hoverFeatures.length;
                if (!updateFeatures && features.length > 0 && self.map.hoverFeatures.length > 0) {
                    updateFeatures = features[0].id !== self.map.hoverFeatures[0].id;
                }
                if (updateFeatures) {
                    var hoverData = null;
                    var clickable = false;
                    var hoverFeature = _.find(features, function(feature) {
                        if (feature.properties.feature_info_content) {
                            hoverData = feature.properties;
                        }
                        if (feature.properties.resourceinstanceid || feature.properties._featureid) {
                            return isFeatureVisible(feature);
                        }
                    }) || _.find(features, function(feature) {
                        if (feature.layer.id === 'search-results-hex') {
                            return isFeatureVisible(feature);
                        }
                    }) || (
                        self.context === 'resource-editor' && _.find(features, function(feature) {
                            if (feature.properties.geojson) {
                                return isFeatureVisible(feature);
                            }
                        })
                    ) || null;

                    if (hoverFeature && hoverFeature.properties) {
                        hoverData = hoverFeature.properties;
                        if (hoverFeature.properties.resourceinstanceid) {
                            hoverData = lookupResourceData(hoverData);
                            clickable = true;
                        }
                        if (hoverFeature.properties.geojson) {
                            clickable = true;
                        }
                    }

                    if (self.hoverData() !== hoverData) {
                        self.hoverData(hoverData, hoverFeature);
                        var filterProperty = '';
                        var style;
                        var featureId;
                        var sourceLayer;
                        if (hoverFeature && (hoverFeature.layer.id.endsWith('hover') === false) && (hoverFeature.layer.id.endsWith('click') === false)){
                            if (hoverFeature && hoverFeature.properties.resourceinstanceid) {
                                filterProperty = 'resourceinstanceid';
                            } else if (hoverFeature && hoverFeature.properties._featureid) {
                                filterProperty = '_featureid';
                            }
                            featureId = hoverFeature && hoverFeature.properties[filterProperty] ? hoverFeature.properties[filterProperty] : '';
                            style = self.getMapStyle();

                            highlightFeature(hoverFeature, 'hover', filterProperty, style);
                            var sourceLayerId = filterProperty === '_featureid' ? hoverFeature.layer['source-layer'] : 'resources-fill-' + hoverFeature.layer['source-layer'];
                            sourceLayer = map.getLayer(sourceLayerId);
                            if (sourceLayer && sourceLayer.type === 'fill') {
                                self.filterSourceFeature(sourceLayer, filterProperty, featureId);
                            }
                        }
                        if (hoverFeature === null) {
                            self.clearHighlight('hover');
                        } else if (hoverFeature && hoverFeature.id === featureId) {
                            self.clearHighlight('hover', featureId);
                        }

                    }

                    self.map.getCanvas().style.cursor = clickable ? 'pointer' : '';
                    self.map.hoverFeatures = features;
                }
            });

            map.on('click', function(e) {
                if (self.context === 'resource-editor') {
                    self.xyInput.updateSelectedPoint();
                }
                var features = self.map.queryRenderedFeatures(e.point);
                var clickData = null;
                var clickFeature = _.find(features, function(feature) {
                    if (feature.properties.feature_info_content) {
                        clickData = feature.properties;
                    }
                    if (feature.properties.resourceinstanceid || feature.properties._featureid) {
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

                    var style = self.getMapStyle();
                    self.clearHighlight('click');

                    var clickFeatureId = clickFeature.properties && clickFeature.properties.resourceinstanceid ? ko.unwrap(clickFeature.properties.resourceinstanceid) : '';
                    var filterProperty = null;
                    self.clickSourceLayerCache = null;
                    if (clickFeatureId) {
                        filterProperty = 'resourceinstanceid';
                    } else if (clickFeature.properties && clickFeature.properties._featureid) {
                        filterProperty = '_featureid';
                        clickFeatureId = clickFeature.properties._featureid;
                    }
                    if (filterProperty !== null) {
                        highlightFeature(clickFeature, 'click', filterProperty, style);
                        var sourceLayer = filterProperty === '_featureid' ? self.map.getLayer(clickFeature.layer['source-layer']) : self.map.getLayer('resources-fill-' + clickFeature.layer['source-layer']);
                        if (!sourceLayer && (clickFeature.layer.source === 'search-results-points')) {

                        }
                        if (sourceLayer && clickFeature.layer.type === 'fill') {
                            self.filterSourceFeature(sourceLayer, filterProperty, clickFeatureId);
                            self.clickSourceLayerCache = {sourcelayer: sourceLayer, filterproperty: filterProperty, featureid: clickFeatureId};
                        }
                    }
                }

                if (self.clickData() !== clickData) {
                    self.clickData(clickData);
                    self.clearHighlight('hover');
                }
            });

            self.drawingAdded = ko.observable(null);
            var addDrawingFromGeojsonGeom = function(geojsonGeom) {
                var feature = {
                    "type": "Feature",
                    "geometry": geojsonGeom,
                    "properties": {}
                };
                _.delay(function() {
                    self.map.doubleClickZoom.enable();
                    self.drawingAdded(null);
                }, 1500);
                self.draw.add(feature);
                self.saveGeometries();
                self.drawingAdded(true);
            };
            var findDrawableFeature = function(point) {
                var features = self.map.queryRenderedFeatures(point);
                return (
                    self.context === 'resource-editor' && _.find(features, function(feature) {
                        if (feature.properties.geojson) {
                            return isFeatureVisible(feature);
                        }
                    })
                ) || null;
            };
            map.on('mousedown', function(e) {
                var clickFeature = findDrawableFeature(e.point);
                if (clickFeature) {
                    self.map.doubleClickZoom.disable();
                }
            });
            map.on('dblclick', function(e) {
                var clickFeature = findDrawableFeature(e.point);
                if (clickFeature) {
                    self.drawingAdded(false);
                    try {
                        var geojsonGeom = JSON.parse(clickFeature.properties.geojson);
                        addDrawingFromGeojsonGeom(geojsonGeom);
                    } catch (e) {
                        $.getJSON(clickFeature.properties.geojson, addDrawingFromGeojsonGeom);
                    }
                }
            });

            self.clickData.subscribe(function(val) {
                if (val === null){
                    self.clearHighlight('click');
                    self.clickSourceLayerCache = null;
                }
            });

            ['draw.create', 'draw.update', 'draw.delete'].forEach(function(event) {
                self.map.on(event, self.saveGeometries);
            });
            self.map.on('click', this.updateDrawMode);
            self.map.on('draw.selectionchange', self.updateFeatureStyles);

            self.map.on('zoom', function(e) {
                self.map.getMaxZoom() <= self.map.getZoom() ? self.atMaxZoom(true) : self.atMaxZoom(false);
                self.map.getMinZoom() >= self.map.getZoom() ? self.atMinZoom(true) : self.atMinZoom(false);
            });

            if (this.context === 'search-filter') {
                self.map.on('dragend', this.searchByExtent);
                self.map.on('zoomend', this.searchByExtent);
                self.map.on('rotateend', this.searchByExtent);
                self.map.on('pitch', this.searchByExtent);
                this.resizeOnChange.subscribe(function() {
                    setTimeout(this.searchByExtent, 600);
                }, self);
                $(window).on("resize", this.searchByExtent);
            } else {
                self.map.on('moveend', self.updateConfigs);
            }

            if (self.defaultValueType() && self.defaultValueType() != '' || self.defaultValueType() > 0) {
                if (self.defaultValueType() == 1){
                    self.value(self.defaultValue());
                }
                this.loadDefaultValue(self.defaultValueType(), true);
            }

            if (typeof self.onInit === 'function') {
                self.onInit(self.map);
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
        this.sources["search-results-hashes"] = {
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
            self.basemap(val.name);
            self.setBasemap(val);
        };

        this.defaultValueOptions = [
            {
                "name": "",
                "defaultOptionid": 0,
                "value": ""
            },
            {
                "name": "Drawn Location",
                "defaultOptionid": 1,
                "value": "Drawn Location"
            },
            {
                "name": "Current Device Location",
                "defaultOptionid": 2,
                "value": "Current Device Location"
            }
        ];

        if (this.configForm || this.state === 'form') {

            this.loadDefaultValue = function(val, load) {
                if (val === 0 || val === null) {
                    self.clearGeometries(null);
                    self.defaultValue("");
                }
                else if (val === 1 && self.draw) {
                    if (!load) {
                        self.defaultValue(self.draw.getAll());
                    }
                    if (self.defaultValue()) {
                        setTimeout(self.loadGeometriesIntoDrawLayer, 1500);
                    }
                }
                else if (val === 2 && self.draw) {
                    self.clearGeometries(null);
                    navigator.geolocation.getCurrentPosition(function(location) {
                        self.defaultValue(
                            {
                                type: "FeatureCollection",
                                features: [
                                    {
                                        geometry: {
                                            type: 'Point',
                                            coordinates: [location.coords.longitude, location.coords.latitude]
                                        },
                                        type: 'Feature',
                                        properties: {
                                            timestamp: location.timestamp,
                                            accuracy: location.coords.accuracy,
                                            altitude: location.coords.altitude,
                                            altitudeAccuracy: location.coords.altitudeAccuracy,
                                            heading: location.coords.heading,
                                            speed: location.coords.speed
                                        }
                                    }
                                ]
                            }
                        );
                        if (self.defaultValue()) {
                            self.loadGeometriesIntoDrawLayer();
                            self.zoomToDrawLayer();
                        }
                    });
                }
            };
            this.defaultValueType.subscribe(this.loadDefaultValue);
        }

        this.mapStyle.layers = this.addInitialLayers();

        this.reportURL = arches.urls.resource_report;

        this.editURL = arches.urls.resource_editor;

        this.displayValue = ko.computed(function() {
            var value = koMapping.toJS(this.value);
            if (!value || !value.features) {
                return 0;
            }
            return value.features.length;
        }, this);
    };
    ko.components.register('map-widget', {
        viewModel: viewModel,
        template: {
            require: 'text!widget-templates/map'
        }
    });
    return viewModel;
});
