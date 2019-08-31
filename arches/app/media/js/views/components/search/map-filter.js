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
], function($, _, arches, ko, BaseFilter, MapComponentViewModel, binFeatureCollection, mapStyles, turf, geohash) {
    var componentName = 'map-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                var self = this;
                MapComponentViewModel.apply(this, [options]);

                options.name = "Map Filter";
                BaseFilter.prototype.initialize.call(this, options);

                this.extentSearch = ko.observable(false);
                this.searchAggregations = ko.observable();
                this.searchBuffer = ko.observable();
                this.hoverData = ko.observable(null);
                this.clickData = ko.observable(null);

                this.searchResults.timestamp.subscribe(function(timestamp) {
                    this.updateResults();
                }, this);

                this.resizeOnChange = ko.computed(function() {
                    return ko.unwrap(options.resizeOnChange);
                });
                this.filter.feature_collection = ko.observable({
                    "type": "FeatureCollection",
                    "features": []
                });
                this.filter.inverted = ko.observable(false);
                var basemaps = _.filter(arches.mapLayers, function(layer) {
                    return !layer.isoverlay;
                });

                if (!this.defaultBasemap) {
                    this.defaultBasemap = _.find(basemaps, function (basemap) {
                        return basemap.addtomap;
                    });
                }
                if (!this.defaultBasemap) {
                    this.defaultBasemap = basemaps[0];
                }

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
                this.restoreState();
                
                var filterUpdated = ko.computed(function() {
                    return JSON.stringify(ko.toJS(this.filter.feature_collection())) + this.filter.inverted();
                }, this);
                filterUpdated.subscribe(function() {
                    this.updateQuery();
                }, this);




                this.searchQueryLayer = {
                    name: 'Map Query',
                    maplayerid: 'search-query',
                    isResource: false,
                    layer_definitions: mapStyles.getSearchQueryStyles(),
                    isoverlay: false,
                    icon: 'ion-map'
                };

                // this.addInitialLayers = function() {
                //     var initialLayers = [];
                //     this.layers.unshift(this.searchQueryLayer);
                //     this.layers.forEach(function(mapLayer) {
                //         if (mapLayer.name === this.basemap()) {
                //             _.each(mapLayer.layer_definitions, function(layer) {
                //                 initialLayers.push(layer);
                //             });
                //         }
                //     }, this);
                //     return initialLayers;
                // };

                // this.mapStyle = {
                //     "version": 8,
                //     "name": "Basic",
                //     "metadata": {
                //         "mapbox:autocomposite": true,
                //         "mapbox:type": "template"
                //     },
                //     "sources": this.sources,
                //     "sprite": arches.mapboxSprites,
                //     "glyphs": arches.mapboxGlyphs,
                //     "layers": this.addInitialLayers()
                // };



                var zoomToGeoJSON = function(data, fly) {
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
                };

                this.mouseoverInstanceId = options.mouseoverInstanceId;
                this.mapLinkData = options.mapLinkData;

                var bins = binFeatureCollection(this.searchAggregations);
                this.searchBuffer.subscribe(function(val){
                    this.updateSearchQueryLayer([{geometry: JSON.parse(this.searchBuffer())}, this.queryFeature]);
                }, this);
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
                    var i = 1;
                    _.each(agg.results, function(result) {
                        _.each(result._source.points, function(point) {
                            var feature = turf.point([point.point.lon, point.point.lat], _.extend(result._source, {
                                resourceinstanceid: result._id,
                                // highlight: result._id === mouseoverInstanceId ||
                                //      (clickData ? (ko.unwrap(clickData.resourceinstanceid) === result._id) : false) ||
                                //      (hoverData ? (ko.unwrap(hoverData.resourceinstanceid) === result._id) : false)
                            }));
                            feature.id = i++;
                            features.push(feature);
                        });
                    });

                    var pointsFC = turf.featureCollection(features);
                    pointSource.setData(pointsFC);
                };
                this.overlays.unshift(this.createOverlay(this.searchQueryLayer));
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
                // this.mapLinkData.subscribe(function(data) {
                //     zoomToGeoJSON(data, true);
                // },this);

            },

            updateQuery: function(filterParams) {
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
                        this.filter.inverted(mapQuery.features[0].properties.inverted);
                        this.getFilter('term-filter').addTag('Map Filter Enabled', this.name, this.filter.inverted);
                        this.filter.feature_collection(mapQuery);
                    }
                }
                this.updateResults();
            },

            updateResults: function() {
                if (!!this.searchResults.results){
                    this.searchAggregations({
                        results: this.searchResults.results.hits.hits,
                        geo_aggs: this.searchResults.results.aggregations.geo_aggs.inner.buckets[0]
                    });
                }
                if(!!this.searchResults[componentName]) {
                    this.searchBuffer(this.searchResults[componentName].search_buffer);
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
            },

            fitToAggregationBounds: function() {
                var agg = this.searchAggregations();
                var aggBounds;
                if (agg && agg.geo_aggs.bounds.bounds && this.map() && !this.extentSearch()) {
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
            },

            createOverlay: function(maplayer) {
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
                // configMaplayer = _.findWhere(this.overlayConfigs(), {
                //     "maplayerid": maplayer.maplayerid
                // });
                // if (configMaplayer !== undefined) {
                //     maplayer.checkedOutOfLibrary(configMaplayer !== undefined);
                //     maplayer.opacity(configMaplayer.opacity);
                // }
                // maplayer.opacity.subscribe(function(value) {
                //     self.overlayOpacity(value);
                //     this.overlayConfigs().forEach(
                //         function(overlayConfig) {
                //             if (maplayer.maplayerid === overlayConfig.maplayerid) {
                //                 overlayConfig.opacity = value;
                //             }
                //         }, self);
                //     maplayer.updateOpacity(value);
                // }, self);
                return maplayer;
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
