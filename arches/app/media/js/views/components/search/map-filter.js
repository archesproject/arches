define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'views/components/search/base-filter',
    'views/components/map',
    'views/components/widgets/map/bin-feature-collection',
    'views/components/widgets/map/map-styles',
    'turf',
    'geohash',
    'mapbox-gl',
    'mapbox-gl-draw',
    'geojson-extent',
    'mathjs',
    'uuid'
], function($, _, arches, ko, BaseFilter, MapComponentViewModel, binFeatureCollection, mapStyles, turf, geohash, mapboxgl, MapboxDraw, geojsonExtent, mathjs, uuid) {
    var componentName = 'map-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                var self = this;

                options.sources = {
                    "geojson-search-buffer-data": {
                        "type": "geojson",
                        "generateId": true,
                        "data": {
                            "type": "FeatureCollection",
                            "features": []
                        }
                    }
                };

                options.layers = ko.observable([{
                    "id": "geojson-search-buffer",
                    "type": "fill",
                    "layout": {
                        "visibility": "visible"
                    },
                    "paint": {
                        "fill-color": "#3bb2d0",
                        "fill-outline-color": "#3bb2d0",
                        "fill-opacity": 0.2
                    },
                    "source": "geojson-search-buffer-data"
                }]);

                MapComponentViewModel.apply(this, [options]);

                options.name = "Map Filter";
                BaseFilter.prototype.initialize.call(this, options);

                this.searchGeometries = ko.observableArray(null);
                this.extentSearch = ko.observable(false);
                this.searchAggregations = ko.observable();
                this.searchBuffer = ko.observable();
                this.hoverData = ko.observable(null);
                this.clickData = ko.observable(null);
                this.drawMode = ko.observable();
                this.pageLoaded = false;

                this.bufferUnits = [{
                    name: 'meters',
                    val: 'm'
                },{
                    name: 'feet',
                    val: 'ft'
                }];
                this.buffer = ko.observable('10');
                this.bufferUnit = ko.observable('m');
                this.buffLayer =  [{
                    "id": "geojson-search-buffer",
                    "type": "fill",
                    "filter": ["==", "$type", "Polygon"],
                    "paint": {
                        "fill-color": "#3bb2d0",
                        "fill-outline-color": "#3bb2d0",
                        "fill-opacity": 0.1
                    },
                    "source": "geojson-editor-data"
                }];

                // this.geometryTypes = [
                //     {'id':'Point','text':'Point'},
                //     {'id':'Line','text':'Line'},{'id':'Polygon','text':'Polygon'}];
                this.spatialFilterTypes = [{
                    name: 'Point',
                    title: 'Draw a Marker',
                    class: 'leaflet-draw-draw-marker',
                    icon: 'ion-location',
                    drawMode: 'draw_point',
                    active: ko.observable(false)
                }, {
                    name: 'Line',
                    title: 'Draw a Polyline',
                    icon: 'ion-steam',
                    class: 'leaflet-draw-draw-polyline',
                    drawMode: 'draw_line_string',
                    active: ko.observable(false)
                }, {
                    name: 'Polygon',
                    title: 'Draw a Polygon',
                    icon: 'fa fa-pencil-square-o',
                    class: 'leaflet-draw-draw-polygon',
                    drawMode: 'draw_polygon',
                    active: ko.observable(false)
                }, {
                    name: 'Extent',
                    title: 'Search by Map Extent',
                    icon: 'fa fa-pencil-square-o',
                    class: 'leaflet-draw-draw-polygon',
                    drawMode: 'extent',
                    active: ko.observable(false)
                }];

                this.drawModes = _.pluck(this.spatialFilterTypes, 'drawMode');

                this.drawMode.subscribe(function(selectedDrawTool){
                    if(!!selectedDrawTool){
                        if(selectedDrawTool === 'extent'){
                            this.searchByExtent();
                        } else {
                            this.draw.changeMode(selectedDrawTool);
                        }
                    }
                }, this);


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
                    this.draw = new MapboxDraw({
                        displayControlsDefault: false,
                        modes: modes
                    });
                    map.addControl(this.draw);
                    // this.draw.set({
                    //     type: 'FeatureCollection',
                    //     features: []
                    // });
                    map.on('draw.create', function(e) {
                        console.log('in draw create');
                        console.log(e);

                        //self.draw.deleteAll();
                        self.searchGeometries().forEach(function(feature){
                            self.draw.delete(feature.id);
                        });
                        //self.clearBuffer();
                        self.searchGeometries(e.features);
                        self.updateFilterGeom();
                        self.drawMode(undefined);
                        // self.filter.feature_collection({
                        //     "type": "FeatureCollection",
                        //     "features": e.features,
                        //     "properties": {
                        //         "buffer": {
                        //             "width": self.buffer(),
                        //             "unit": self.bufferUnit()
                        //         }
                        //     }
                        // });
                        // e.features.forEach(function(feature) {
                        //     self.draw.setFeatureProperty(feature.id, 'nodeId', self.newNodeId);
                        // });
                        // self.updateTiles();
                    });
                    // map.on('draw.update', self.updateTiles);
                    // map.on('draw.delete', self.updateTiles);
                    map.on('draw.update', function(e) {
                        self.searchGeometries(e.features);
                        self.updateFilterGeom();
                        // console.log('render');
                        // console.log(e)
                        // self.updateTiles();
                        // self.setSelectLayersVisibility(false);
                    });
                    // map.on('draw.selectionchange', function(e) {
                    //     self.selectedFeatureIds(e.features.map(function(feature) {
                    //         return feature.id;
                    //     }));
                    //     if (e.features.length > 0) {
                    //         _.each(self.featureLookup, function(value) {
                    //             value.selectedTool(null);
                    //         });
                    //     }
                    //     self.setSelectLayersVisibility(false);
                    // });

                    // self.form.on('tile-reset', function() {
                    //     self.draw.set({
                    //         type: 'FeatureCollection',
                    //         features: getDrawFeatures()
                    //     });
                    //     _.each(self.featureLookup, function(value) {
                    //         if (value.selectedTool()) value.selectedTool('');
                    //     });
                    // });
                };

                this.map.subscribe(setupDraw, this);

                this.searchResults.timestamp.subscribe(function(timestamp) {
                    //this.map.subscribe(this.updateResults, this);
                    console.log('timestamp updated');
                    if(this.pageLoaded) {
                        this.updateResults();
                    }
                }, this);

                this.resizeOnChange = ko.computed(function() {
                    return ko.unwrap(options.resizeOnChange);
                });
                this.filter.feature_collection = ko.observable({
                    "type": "FeatureCollection",
                    "features": []
                });
                this.filter.inverted = ko.observable(false);
                // var basemaps = _.filter(arches.mapLayers, function(layer) {
                //     return !layer.isoverlay;
                // });

                // if (!this.defaultBasemap) {
                //     this.defaultBasemap = _.find(basemaps, function (basemap) {
                //         return basemap.addtomap;
                //     });
                // }
                // if (!this.defaultBasemap) {
                //     this.defaultBasemap = basemaps[0];
                // }

                this.geocoderDefault = arches.geocoderDefault;

                this.overlays = _.filter(arches.mapLayers, function(layer) {
                    return layer.isoverlay && layer.addtomap;
                }).map(function(layer) {
                    return {
                        'maplayerid': layer.maplayerid,
                        'name': layer.name,
                        'opacity': 100
                    };
                });

                this.defaultZoom = arches.mapDefaultZoom;
                this.minZoom = arches.mapDefaultMinZoom;
                this.maxZoom = arches.mapDefaultMaxZoom;
                this.defaultCenter = [arches.mapDefaultX, arches.mapDefaultY];


                this.clearSearch = ko.observable();
                this.clearSearch.subscribe(function(val) {
                    if (!val) {
                        this.clear(false);
                    }
                }, this);

                this.filters[componentName](this);

                this.map.subscribe(function(){
                    this.restoreState();
                    
                    var filterUpdated = ko.computed(function() {
                        return JSON.stringify(ko.toJS(this.filter.feature_collection())) + this.filter.inverted();
                    }, this);
                    filterUpdated.subscribe(function() {
                        this.updateQuery();
                    }, this);

                    this.buffer.subscribe(function(val) {
                        this.updateFilterGeom();
                    }, this);

                    this.bufferUnit.subscribe(function(val) {
                        this.updateFilterGeom();
                    }, this);
                }, this);

                this.mouseoverInstanceId = options.mouseoverInstanceId;
                this.mapLinkData = options.mapLinkData;

                var bins = binFeatureCollection(this.searchAggregations);

                var getSearchAggregationGeoJSON = function() {
                    var agg = ko.unwrap(self.searchAggregations);
                    if (!agg || !agg.geo_aggs.grid.buckets) {
                        return {
                            "type": "FeatureCollection",
                            "features": []
                        };
                    }

                    if (self.filter.feature_collection() && self.filter.feature_collection()['features'].length > 0 && self.extentSearch() === false) {
                        var geojsonFC = self.filter.feature_collection();
                        var extent = geojsonExtent(geojsonFC);
                        var bounds = new mapboxgl.LngLatBounds(extent);
                        self.map().fitBounds(bounds, {
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
                    var pointSource = self.map().getSource('search-results-points');
                    var agg = ko.unwrap(self.searchAggregations);
                    if (!agg || !agg.results) {
                        return {
                            "type": "FeatureCollection",
                            "features": []
                        };
                    }

                    var features = [];
                    var mouseoverInstanceId = self.mouseoverInstanceId();
                    var hoverData = self.hoverData();
                    var clickData = self.clickData();
                    _.each(agg.results, function(result) {
                        _.each(result._source.points, function(point) {
                            var feature = turf.point([point.point.lon, point.point.lat], _.extend(result._source, {
                                resourceinstanceid: result._id,
                                // highlight: result._id === mouseoverInstanceId ||
                                //      (clickData ? (ko.unwrap(clickData.resourceinstanceid) === result._id) : false) ||
                                //      (hoverData ? (ko.unwrap(hoverData.resourceinstanceid) === result._id) : false)
                            }));
                            features.push(feature);
                        });
                    });

                    var pointsFC = turf.featureCollection(features);
                    pointSource.setData(pointsFC);
                };

                this.updateSearchResultsLayer = function() {
                    var aggSource = self.map().getSource('search-results-hex');
                    var hashSource = self.map().getSource('search-results-hashes');
                    var aggData = getSearchAggregationGeoJSON();
                    aggSource.setData(aggData.agg);
                    hashSource.setData(aggData.points);
                    updateSearchPointsGeoJSON();
                };

                this.map.subscribe(function(){
                    this.searchAggregations.subscribe(this.updateSearchResultsLayer, this);
                    if (ko.isObservable(bins)) {
                        bins.subscribe(this.updateSearchResultsLayer, this);
                    }
                    if (this.searchAggregations()) {
                        this.updateSearchResultsLayer();
                    }
                    this.mouseoverInstanceId.subscribe(updateSearchPointsGeoJSON);
                }, this);

                // this.clickData.subscribe(updateSearchPointsGeoJSON);
                // this.hoverData.subscribe(function(val) {
                //     var resultsHoverLayer = this.map.getLayer('search-results-hex-outline-highlighted');
                //     var filter = ['==', 'id', ''];
                //     if (val && val.doc_count) {
                //         filter[2] = val.id;
                //     }
                //     if (resultsHoverLayer) {
                //         this.map.setFilter(resultsHoverLayer.id, filter);
                //     }
                //     updateSearchPointsGeoJSON();
                // }, this);

                this.mapLinkData.subscribe(function(data) {
                    this.zoomToGeoJSON(data, true);
                },this);

            },

            searchByExtent: function() {
                if (_.contains(this.drawModes, this.drawMode())) {
                    this.draw.deleteAll();
                }
                var bounds = this.map().getBounds();
                var ll = bounds.getSouthWest().toArray();
                var ul = bounds.getNorthWest().toArray();
                var ur = bounds.getNorthEast().toArray();
                var lr = bounds.getSouthEast().toArray();
                var coordinates = [ll, ul, ur, lr, ll];
                var boundsFeature = {
                    "type": "Feature",
                    "properties": {
                    //     "buffer": {
                    //         "width": 0,
                    //         "unit": this.bufferUnit()
                    //     }
                    },
                    "id": uuid.generate(),
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [coordinates]
                    }
                };
                this.draw.set({
                    "type": "FeatureCollection",
                    "features": [boundsFeature]
                });
                this.searchGeometries([boundsFeature]);
                this.updateFilterGeom();
                this.drawMode(undefined);
                // this.filter.feature_collection({
                //     "type": "FeatureCollection",
                //     "features": [boundsFeature]
                // });
            },

            updateFilterGeom: function(){
                var maxBuffer = 100000;
                var maxBufferUnits = 'm';
                var maxBufferUnit = mathjs.unit(maxBuffer, maxBufferUnits);
                var unit = mathjs.unit(this.buffer() + this.bufferUnit());
                unit.equalBase(maxBufferUnit);
                if (this.buffer() < 0) {
                    this.buffer(0);
                } else if (unit.value > maxBufferUnit.value) {
                    this.buffer(maxBuffer);
                    this.bufferUnit(maxBufferUnits);
                }
                this.searchGeometries().forEach(function(feature){
                    if(!feature.properties){
                        feature.properties = {};
                    }
                    feature.properties.buffer = {
                        "width": this.buffer(),
                        "unit": this.bufferUnit()
                    };
                }, this);
                this.filter.feature_collection({
                    "type": "FeatureCollection",
                    "features": this.searchGeometries()
                });
            },

            editGeoJSON: function() {
                // var geoJSONString = JSON.stringify({
                //     type: 'FeatureCollection',
                //     features: features
                // }, null, '   ');
                // this.geoJSONString(geoJSONString);
            },

            /**
              * Updates the draw mode of the draw layer when a user selects a draw tool in the map controls
              * @param  {string} selectedDrawTool the draw tool name selected in the map controls
              * @return {null}
              */
            selectEditingTool: function(drawMode) {
                self = self || this;
                // this.setDrawTool = function(tool) {
                //     var showSelectLayers = (tool === 'select_feature');
                //     self.setSelectLayersVisibility(showSelectLayers);
                //     if (showSelectLayers) {
                //         self.draw.changeMode('simple_select');
                //         self.selectedFeatureIds([]);
                //     } else if (tool) self.draw.changeMode(tool);
                // };

                // this.draw.deleteAll();
                // this.clearBuffer();

                // if (selectedDrawTool === 'end' || this.geometryTypeDetails[selectedDrawTool].drawMode === this.drawMode() || this.geometryTypeDetails[selectedDrawTool].drawMode !== this.drawMode()) {
                //     this.draw.deleteAll();
    
                // if (this.form) {
                //     this.featureColor(this.featureColorCache);
                // }
                // _.each(this.geometryTypeDetails, function(geomtype) {
                //     if (geomtype.name === selectedDrawTool) {
                //         this.geometryTypeDetails[selectedDrawTool].active(!this.geometryTypeDetails[selectedDrawTool].active());
                //     } else {
                //         this.geometryTypeDetails[geomtype.name].active(false);
                //     }
                // }, this);

                this.draw.changeMode(drawMode);
                this.drawMode(drawMode);

            },

            zoomToGeoJSON: function(data, fly) {
                var method = fly ? 'flyTo' : 'jumpTo';
                var bounds = new mapboxgl.LngLatBounds(geojsonExtent(data));
                var tr = self.map().transform;
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
                self.map()[method](options);
            },

            updateQuery: function() {
                var self = this;
                var queryObj = this.query();
                if (this.filter.feature_collection().features.length > 0) {
                    if (this.getFilter('term-filter').hasTag(this.type) === false) {
                        this.getFilter('term-filter').addTag('Map Filter Enabled', this.name, this.filter.inverted);
                    }
                    this.filter.feature_collection().features[0].properties['inverted'] = this.filter.inverted();
                    queryObj[componentName] = ko.toJSON(this.filter.feature_collection());
                } else {
                    //this.clear();
                    delete queryObj[componentName];
                }
                this.query(queryObj);
            },

            restoreState: function() {
                var query = this.query();
                if (componentName in query) {
                    var mapQuery = JSON.parse(query[componentName]);
                    if (mapQuery.features.length > 0) {
                        var properties = mapQuery.features[0].properties;
                        this.filter.inverted(properties.inverted);
                        this.getFilter('term-filter').addTag('Map Filter Enabled', this.name, this.filter.inverted);
                        this.filter.feature_collection(mapQuery);
                        this.buffer(properties.buffer.width);
                        this.bufferUnit(properties.buffer.unit);
                        this.draw.set({
                            "type": "FeatureCollection",
                            "features": mapQuery.features
                        });
                    }
                }
                console.log('from restoreState')
                this.updateResults();
                this.pageLoaded = true;
            },

            updateResults: function() {
                if (!!this.searchResults.results){
                    this.searchAggregations({
                        results: this.searchResults.results.hits.hits,
                        geo_aggs: this.searchResults.results.aggregations.geo_aggs.inner.buckets[0]
                    });
                    this.fitToAggregationBounds();
                }
                if(!!this.searchResults[componentName]) {
                    // var buffer = {
                    //     "type": "FeatureCollection",
                    //     "features": [{
                    //         "type": "Feature",
                    //         "geometry": this.searchResults[componentName].search_buffer
                    //     }]
                    // };
                    var buffer = this.searchResults[componentName].search_buffer;
                    console.log(buffer);
                    this.map().getSource('geojson-search-buffer-data').setData(buffer);
                    //this.searchBuffer(this.searchResults[componentName].search_buffer);
                }
            },

            clear: function(reset_features) {
                if (reset_features !== false){
                    if (this.filter.feature_collection().features.length > 0) {
                        this.filter.feature_collection({
                            "type": "FeatureCollection",
                            "features": []
                        });
                    }
                }
                this.getFilter('term-filter').removeTag('Map Filter Enabled');
                this.draw.deleteAll();
                this.clearBuffer();
                this.searchGeometries([]);
            },

            clearBuffer: function() {
                this.map().getSource('geojson-search-buffer-data').setData({
                    "type": "FeatureCollection",
                    "features": []
                });
            },

            fitToAggregationBounds: function() {
                var agg = this.searchAggregations();
                var aggBounds;
                if (agg && agg.geo_aggs.bounds.bounds && this.map()) {
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
                    var maxZoom = ko.unwrap(this.maxZoom);
                    maxZoom = maxZoom > 17 ? 17 : maxZoom;
                    this.map().fitBounds(bounds, {
                        padding: 45,
                        maxZoom: maxZoom
                    });
                }
            }
        }),
        template: { require: 'text!templates/views/components/search/map-filter.htm' }
    });
    // var viewModel = function(params) {
    // // ko.components.register(componentName, {
    // //     viewModel: BaseFilter.extend(viewModel),
    // //     template: {
    // //         require: 'text!templates/views/components/search/map-filter.htm'
    // //     }
    // // });
    // return viewModel;
});
