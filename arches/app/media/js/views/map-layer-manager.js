define([
    'jquery',
    'knockout',
    'underscore',
    'arches',
    'turf',
    'geohash',
    'views/base-manager',
    'models/node',
    'viewmodels/alert',
    'views/components/widgets/map/bin-feature-collection',
    'views/map-layer-manager-data',
    'bindings/mapbox-gl',
    'bindings/codemirror',
    'codemirror/mode/javascript/javascript',
    'datatype-config-components',
    'views/components/icon-selector',
    'views/components/datatypes/geojson-feature-collection',
    'views/components/widgets/number',
], function($, ko, _, arches, turf, geohash, BaseManagerView, NodeModel, AlertViewModel, binFeatureCollection, data) {
    var vm = {
        map: null,
        geomNodes: [],
        loading: ko.observable(false),
        minZoom: ko.observable(arches.mapDefaultMinZoom),
        maxZoom: ko.observable(arches.mapDefaultMaxZoom),
        pitch: ko.observable(0),
        bearing: ko.observable(0),
        iconFilter: ko.observable(''),
        selectedList: ko.observable()
    };

    vm.icons = ko.computed(function() {
        return _.filter(data.icons, function(icon) {
            return icon.name.indexOf(vm.iconFilter()) >= 0;
        });
    });
    var mapLayers = ko.observableArray($.extend(true, [], arches.mapLayers));
    _.each(mapLayers(), function(layer) {
        layer._layer = ko.observable(JSON.stringify(layer));
        layer.layerJSON = ko.observable(JSON.stringify(layer.layer_definitions, null, '\t'));
        layer.activated = ko.observable(layer.activated);
        layer.addtomap = ko.observable(layer.addtomap);
        layer.name = ko.observable(layer.name);
        layer.icon = ko.observable(layer.icon);
        layer.legend = ko.observable(layer.legend);
        layer.searchonly = ko.observable(layer.searchonly);
        layer.centerX = ko.observable(layer.centerx);
        layer.centerY = ko.observable(layer.centery);
        layer.zoom = ko.observable(layer.zoom);
        layer.sortOrder = ko.observable(layer.sortorder);
        layer.isPublic = ko.observable(layer.ispublic);
        layer.toJSON = ko.computed(function() {
            var layers;
            try {
                layers = JSON.parse(layer.layerJSON());
            }
            catch (e) {
                layers = [];
            }
            return JSON.stringify({
                "maplayerid": layer.maplayerid,
                "name": layer.name(),
                "layer_definitions": layers,
                "isoverlay": layer.isoverlay,
                "icon": layer.icon(),
                "legend": layer.legend(),
                "searchonly": layer.searchonly(),
                "activated": layer.activated(),
                "addtomap": layer.addtomap(),
                "is_resource_layer": false,
                "centerx": layer.centerX(),
                "centery": layer.centerY(),
                "zoom": layer.zoom(),
                "sortorder": layer.sortOrder(),
                "ispublic": layer.isPublic()
            });
        });
        layer.dirty = ko.computed(function() {
            return layer.toJSON() !== layer._layer();
        });
        layer.save = function() {
            vm.loading(true);
            $.ajax({
                type: "POST",
                url: window.location.pathname + '/' + layer.maplayerid,
                data: layer.toJSON(),
                success: function(response) {
                    layer._layer(layer.toJSON());
                    pageView.viewModel.loading(false);
                    var mapLayer = _.find(arches.mapLayers, function(mapLayer) {
                        return mapLayer.maplayerid === layer.maplayerid;
                    });
                    _.extend(mapLayer, JSON.parse(layer._layer()));
                    if (!mapLayer.isoverlay && mapLayer.addtomap) {
                        _.each(vm.basemaps(), function(basemap) {
                            if (basemap.maplayerid !== layer.maplayerid) {
                                basemap.addtomap(false);
                            }
                        });
                        _.each(arches.mapLayers, function(mapLayer) {
                            if (!mapLayer.isoverlay && mapLayer.maplayerid !== layer.maplayerid) {
                                mapLayer.addtomap = false;
                            }
                        });
                    }
                },
                error: function(response) {
                    pageView.viewModel.loading(false);
                }
            });
        };
        layer.reset = function() {
            var _layer = JSON.parse(layer._layer());
            layer.layerJSON(JSON.stringify(_layer.layer_definitions, null, '\t'));
            layer.activated(_layer.activated);
            layer.addtomap(_layer.addtomap),
            layer.name(_layer.name);
            layer.icon(_layer.icon);
            layer.centerX(_layer.centerx);
            layer.centerY(_layer.centery);
            layer.zoom(_layer.zoom);
            layer.sortOrder(_layer.sortorder);
            layer.isPublic(_layer.ispublic);
            layer.legend(_layer.legend);
            layer.searchonly(_layer.searchonly);
        };
        layer.delete = function() {
            pageView.viewModel.alert(new AlertViewModel(
                'ep-alert-red',
                arches.translations.confirmMaplayerDelete.title,
                arches.translations.confirmMaplayerDelete.text,
                function() {
                    return;
                }, function(){
                    vm.loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: window.location.pathname + '/' + layer.maplayerid,
                        success: function(response) {
                            mapLayers.remove(layer);
                            arches.mapLayers = _.without(arches.mapLayers, _.findWhere(arches.mapLayers, {
                                maplayerid: layer.maplayerid
                            }));
                            var selection = null;
                            var layerList = ko.unwrap(vm.selectedList());
                            if (layerList && layerList.length > 0) {
                                selection = layerList[0];
                            }
                            vm.selection(selection);
                            pageView.viewModel.loading(false);
                        },
                        error: function(response) {
                            pageView.viewModel.loading(false);
                        }
                    });
                }
            ));
        };
    });

    vm.selectedBasemapName = ko.observable('');
    vm.basemaps = ko.computed(function() {
        return _.filter(mapLayers(), function(layer) {
            return !layer.isoverlay;
        });
    });
    vm.basemaps().forEach(function(basemap) {
        basemap.select = function() {
            vm.selectedBasemapName(basemap.name());
        };
    });
    var defaultBasemap = _.find(vm.basemaps(), function(basemap) {
        return basemap.addtomap();
    });
    if (!defaultBasemap) {
        defaultBasemap = vm.basemaps()[0];
    }
    if (defaultBasemap) {
        vm.selectedBasemapName(defaultBasemap.name());
    }
    vm.overlays = ko.computed(function() {
        return _.filter(mapLayers(), function(layer) {
            return layer.isoverlay && !layer.is_resource_layer;
        });
    });

    var getBasemapLayers = function() {
        return _.filter(vm.basemaps(), function(layer) {
            return layer.name() === vm.selectedBasemapName();
        }).reduce(function(layers, layer) {
            return layers.concat(layer.layer_definitions);
        }, []);
    };
    var sources = $.extend(true, {}, arches.mapSources);


    sources["search-results-hex"] = {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features": []
        }
    };
    sources["search-results-points"] = {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features": []
        }
    };
    sources["search-results-hashes"] = {
        "type": "geojson",
        "data": {
            "type": "FeatureCollection",
            "features": []
        }
    };

    _.each(sources, function(sourceConfig, name) {
        if (sourceConfig.tiles) {
            sourceConfig.tiles.forEach(function(url, i) {
                if (url.startsWith('/')) {
                    sourceConfig.tiles[i] = window.location.origin + url;
                }
            });
        }
    });

    var datatypelookup = {};
    _.each(data.datatypes, function(datatype){
        datatypelookup[datatype.datatype] = datatype;
    }, this);

    _.each(data.geom_nodes, function(node) {
        vm.geomNodes.push(
            new NodeModel({
                url: arches.urls.node_layer,
                loading: vm.loading,
                permissions: data.node_permissions[node.nodeid],
                source: node,
                datatypelookup: datatypelookup,
                icons: data.icons,
                layer: _.find(data.resource_map_layers, function(layer) {
                    return layer.nodeid === node.nodeid;
                }),
                mapSource: _.find(data.resource_map_sources, function(source) {
                    return source.nodeid === node.nodeid;
                }),
                graph: _.find(data.graphs, function(graph) {
                    return graph.graphid === node.graph_id;
                })
            })
        );
    });
    var selectedList;
    switch (window.location.hash) {
    case "#basemaps":
        selectedList = vm.basemaps;
        break;
    case "#overlays":
        selectedList = vm.overlays;
        break;
    default:
        selectedList = vm.geomNodes;
    }
    vm.selectedList(selectedList);
    vm.selection = ko.observable(ko.unwrap(selectedList)[0] || null);
    vm.selectedLayerJSON = ko.computed({
        read: function() {
            if (!vm.selection() || !vm.selection().maplayerid) {
                return '[]';
            }
            return vm.selection().layerJSON();
        },
        write: function(value) {
            if (vm.selection() && vm.selection().maplayerid) {
                vm.selection().layerJSON(value);
            }
        }
    });

    var displayLayers = JSON.parse(vm.selectedLayerJSON());
    var basemapLayers = getBasemapLayers();

    vm.mapStyle = {
        "version": 8,
        "name": "Basic",
        "metadata": {
            "mapbox:autocomposite": true,
            "mapbox:type": "template"
        },
        "sources": sources,
        "sprite": arches.mapboxSprites,
        "glyphs": arches.mapboxGlyphs,
        "layers": basemapLayers.concat(displayLayers)
    };

    var searchAggregations = ko.observable(null);
    var searchResults = ko.observable(null);
    var bins = binFeatureCollection(searchAggregations);

    var getSearchAggregationGeoJSON = function() {
        var agg = ko.unwrap(searchAggregations);
        if (!agg || !agg.geo_aggs.grid.buckets) {
            return {
                "type": "FeatureCollection",
                "features": []
            };
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
        var pointSource = vm.map.getSource('search-results-points');
        if (vm.map && pointSource) {
            var aggResults = ko.unwrap(searchResults);
            if (!aggResults || !aggResults.results) {
                return {
                    "type": "FeatureCollection",
                    "features": []
                };
            }

            var features = [];
            _.each(aggResults.results.hits.hits, function(result) {
                _.each(result._source.points, function(point) {
                    var feature = turf.point([point.point.lon, point.point.lat], _.extend(result._source, {
                        resourceinstanceid: result._id,
                        highlight: false
                    }));
                    features.push(feature);
                });
            });

            var pointsFC = turf.featureCollection(features);
            pointSource.setData(pointsFC);
        }
    };

    var updateSearchResultsLayer = function() {
        if (vm.map && searchAggregations()) {
            var aggSource = vm.map.getSource('search-results-hex');
            var hashSource = vm.map.getSource('search-results-hashes');
            if (aggSource && hashSource) {
                var aggData = getSearchAggregationGeoJSON();
                aggSource.setData(aggData.agg);
                hashSource.setData(aggData.points);
            }
            updateSearchPointsGeoJSON();
        }
    };

    vm.setupMap = function(map) {
        vm.map = map;
        map.on('moveend', function(e) {
            if (e.originalEvent) {
                var center = map.getCenter();
                var zoom = map.getZoom();
                if (vm.zoom() !== zoom) {
                    vm.zoom(zoom);
                }
                vm.centerX(center.lng);
                vm.centerY(center.lat);
            }
        });

        searchAggregations.subscribe(updateSearchResultsLayer);
        if (ko.isObservable(bins)) {
            bins.subscribe(updateSearchResultsLayer);
        }
        updateSearchResultsLayer();
    };

    $.ajax({
        dataType: "json",
        url: arches.urls.search_results,
        data: {
            'paging-filter': 1
        },
        success: function(results) {
            results.results.aggregations['geo_aggs'] = results.results.aggregations['geo_aggs'].inner.buckets[0];
            searchAggregations(results.results.aggregations);
            searchResults(results);
        }
    });

    var updateMapStyle = function() {
        var displayLayers;
        try {
            displayLayers = JSON.parse(vm.selectedLayerJSON());
        }
        catch (e) {
            displayLayers = [];
        }
        var basemapLayers = getBasemapLayers();
        if (vm.selection() && vm.selection().isoverlay) {
            vm.mapStyle.layers = basemapLayers.concat(displayLayers);
        } else {
            vm.mapStyle.layers = displayLayers;
        }
        if (vm.map) {
            vm.map.setStyle(vm.mapStyle);
            updateSearchResultsLayer();
        }
    };

    vm.selectedBasemapName.subscribe(updateMapStyle);
    vm.selection.subscribe(updateMapStyle);
    vm.selectedLayerJSON.subscribe(updateMapStyle);
    vm.selectedList.subscribe(function(selectedList) {
        var selection = null;
        var layerList = ko.unwrap(selectedList);
        if (layerList && layerList.length > 0) {
            selection = layerList[0];
        }
        vm.selection(selection);
    });
    vm.listFilter = ko.observable('');
    vm.listItems = ko.computed(function() {
        var listFilter = vm.listFilter().toLowerCase();
        var layerList = ko.unwrap(vm.selectedList());
        return _.filter(layerList, function(item) {
            var name = item.nodeid ?
                (item.config.layerName() ? item.config.layerName() : item.layer.name) :
                item.name();
            name = name.toLowerCase();
            return name.indexOf(listFilter) > -1;
        });
    });
    var addMapConfig = function(key, defaultValue) {
        vm[key] = ko.computed({
            read: function() {
                var val;
                var selection = vm.selection();
                if (selection && selection[key]) {
                    val = selection[key]();
                }
                return val || defaultValue;
            },
            write: function(val) {
                var selection = vm.selection();
                val = val===defaultValue ? null : val;
                if (selection && selection[key]) {
                    selection[key](val);
                }
            }
        });
    };
    addMapConfig('centerX', arches.mapDefaultX);
    addMapConfig('centerY', arches.mapDefaultY);
    addMapConfig('zoom', arches.mapDefaultZoom);

    var pageView = new BaseManagerView({
        viewModel: vm
    });

    return pageView;
});
