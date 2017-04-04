define([
    'knockout',
    'underscore',
    'turf',
    'views/base-manager',
    'models/node',
    'viewmodels/alert',
    'map-layer-manager-data',
    'arches',
    'bindings/mapbox-gl',
    'bindings/codemirror',
    'codemirror/mode/javascript/javascript',
    'datatype-config-components'
], function(ko, _, turf, BaseManagerView, NodeModel, AlertViewModel, data, arches) {
    var vm = {
        map: null,
        geomNodes: [],
        loading: ko.observable(false),
        zoom: ko.observable(arches.mapDefaultZoom),
        minZoom: ko.observable(arches.mapDefaultMinZoom),
        maxZoom: ko.observable(arches.mapDefaultMaxZoom),
        centerX: ko.observable(arches.mapDefaultX),
        centerY: ko.observable(arches.mapDefaultY),
        pitch: ko.observable(0),
        bearing: ko.observable(0),
        iconFilter: ko.observable(''),
        selectedList: ko.observable()
    };

    vm.icons = ko.computed(function () {
        return _.filter(data.icons, function (icon) {
            return icon.name.indexOf(vm.iconFilter()) >= 0;
        });
    });
    var mapLayers = ko.observableArray($.extend(true, [], arches.mapLayers));
    _.each(mapLayers(), function(layer) {
        layer._layer = ko.observable(JSON.stringify(layer));
        layer.layerJSON = ko.observable(JSON.stringify(layer.layer_definitions, null, '\t'))
        layer.activated = ko.observable(layer.activated);
        layer.addtomap = ko.observable(layer.addtomap);
        layer.name = ko.observable(layer.name);
        layer.icon = ko.observable(layer.icon);
        layer.toJSON = ko.computed(function () {
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
                "activated": layer.activated(),
                "addtomap": layer.addtomap(),
                "is_resource_layer": false
            })
        });
        layer.dirty = ko.computed(function() {
            return layer.toJSON() !== layer._layer();
        })
        layer.save = function () {
            vm.loading(true);
            $.ajax({
                type: "POST",
                url: window.location.pathname + '/' + layer.maplayerid,
                data: layer.toJSON(),
                success: function(response) {
                    layer._layer(layer.toJSON());
                    pageView.viewModel.loading(false);
                    var mapLayer = _.find(arches.mapLayers, function(mapLayer) {
                        return mapLayer.maplayerid === layer.maplayerid
                    });
                    _.extend(mapLayer, JSON.parse(layer._layer()));
                    if (!mapLayer.isoverlay && mapLayer.addtomap) {
                        _.each(vm.basemaps(), function (basemap) {
                            if (basemap.maplayerid !== layer.maplayerid) {
                                basemap.addtomap(false);
                            }
                        });
                        _.each(arches.mapLayers, function (mapLayer) {
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
        layer.reset = function () {
            var _layer = JSON.parse(layer._layer());
            layer.layerJSON(JSON.stringify(_layer.layer_definitions, null, '\t'))
            layer.activated(_layer.activated);
            layer.addtomap(_layer.addtomap),
            layer.name(_layer.name);
            layer.icon(_layer.icon);
        };
        layer.delete = function () {
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmMaplayerDelete.title, arches.confirmMaplayerDelete.text, function() {
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
            }));
        };
    });

    vm.selectedBasemapName = ko.observable('');
    vm.basemaps = ko.computed(function() {
        return _.filter(mapLayers(), function(layer) {
            return !layer.isoverlay;
        })
    });
    vm.basemaps().forEach(function (basemap) {
        basemap.select = function () {
            vm.selectedBasemapName(basemap.name());
        }
    });
    var defaultBasemap = _.find(vm.basemaps(), function (basemap) {
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
        })
    });

    var getBasemapLayers = function () {
        return _.filter(vm.basemaps(), function(layer) {
            return layer.name() === vm.selectedBasemapName();
        }).reduce(function(layers, layer) {
            return layers.concat(layer.layer_definitions);
        }, []);
    };
    var sources = $.extend(true, {}, arches.mapSources);

    var cellWidth = arches.hexBinSize;
    var units = 'kilometers';
    var hexGrid = turf.hexGrid(arches.hexBinBounds, cellWidth, units);
    var pointsFC = turf.random('points', 200, {
        bbox: arches.hexBinBounds
    });
    _.each(pointsFC.features, function (feature) {
        feature.properties.doc_count = Math.round(Math.random()*1000);
    });

    var aggregated = turf.collect(hexGrid, pointsFC, 'doc_count', 'doc_count');
    _.each(aggregated.features, function(feature) {
        feature.properties.doc_count = _.reduce(feature.properties.doc_count, function(i,ii) {
            return i+ii;
        }, 0);
    });

    var resultsPoints = pointsFC.features.slice(0, 5);
    resultsPoints[0].properties.highlight = true
    var pointsFC = turf.featureCollection(resultsPoints);

    sources["search-results-hex"] = {
        "type": "geojson",
        "data": aggregated
    };
    sources["search-results-points"] = {
        "type": "geojson",
        "data": pointsFC
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
                loading: vm.loading,
                permissions: data.node_permissions[node.nodeid],
                source: node,
                datatypelookup: datatypelookup,
                icons: data.icons,
                graph: undefined,
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

    vm.selection = ko.observable(vm.geomNodes[0] || null);
    vm.selectedLayerJSON = ko.computed({
        read: function () {
            if (!vm.selection() || !vm.selection().maplayerid) {
                return '[]';
            }
            return vm.selection().layerJSON();
        },
        write: function (value) {
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

    vm.setupMap = function(map) {
        vm.map = map;
    }

    var updateMapStyle = function () {
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
        }
    };

    vm.selectedBasemapName.subscribe(updateMapStyle);
    vm.selection.subscribe(updateMapStyle);
    vm.selectedLayerJSON.subscribe(updateMapStyle);
    vm.selectedList(vm.geomNodes);
    vm.selectedList.subscribe(function (selectedList) {
        var selection = null;
        var layerList = ko.unwrap(vm.selectedList());
        if (layerList && layerList.length > 0) {
            selection = layerList[0];
        }
        vm.selection(selection);
    });
    vm.listFilter = ko.observable('');
    vm.listItems = ko.computed(function () {
        var listFilter = vm.listFilter().toLowerCase();
        var layerList = ko.unwrap(vm.selectedList());
        return _.filter(layerList, function(item) {
            var name = item.nodeid ?
                (item.config.layerName() ? item.config.layerName() : item.layer.name) :
                item.name();
            name = name.toLowerCase()
            return name.indexOf(listFilter) > -1;
        })
    });

    var pageView = new BaseManagerView({
        viewModel: vm
    });

    return pageView;
});
