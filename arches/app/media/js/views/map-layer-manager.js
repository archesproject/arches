define([
    'knockout',
    'underscore',
    'views/base-manager',
    'models/node',
    'map-layer-manager-data',
    'arches',
    'bindings/mapbox-gl',
    'bindings/codemirror',
    'codemirror/mode/javascript/javascript',
    'datatype-config-components'
], function(ko, _, BaseManagerView, NodeModel, data, arches) {
    var vm = {
        map: null,
        geomNodes: [],
        loading: ko.observable(false),
        zoom: ko.observable(0),
        minZoom: ko.observable(0),
        maxZoom: ko.observable(20),
        centerX: ko.observable(-80),
        centerY: ko.observable(0),
        pitch: ko.observable(0),
        bearing: ko.observable(0),
        iconFilter: ko.observable(''),
    };
    vm.icons = ko.computed(function () {
        return _.filter(data.icons, function (icon) {
            return icon.name.indexOf(vm.iconFilter()) >= 0;
        });
    });
    var mapLayers = $.extend(true, {}, arches.mapLayers);
    _.each(mapLayers, function(layer) {
        layer.layerJSON = ko.observable(JSON.stringify(layer.layer_definitions, null, '\t'))
        layer.activated = ko.observable(layer.activated);
        layer.name = ko.observable(layer.name);
        layer.icon = ko.observable(layer.icon);
    });
    vm.selectedBasemapName = ko.observable('');
    vm.basemaps = _.filter(mapLayers, function(layer) {
        return !layer.isoverlay;
    });
    vm.basemaps.forEach(function (basemap) {
        if (vm.selectedBasemapName() === '') {
            vm.selectedBasemapName(basemap.name());
        }
        if (basemap.name() === 'streets') {
            vm.selectedBasemapName('streets');
        }
        basemap.select = function () {
            vm.selectedBasemapName(basemap.name());
        }
    });
    vm.overlays = _.filter(mapLayers, function(layer) {
        return layer.isoverlay && !layer.is_resource_layer;
    });

    var getBasemapLayers = function () {
        return _.filter(vm.basemaps, function(layer) {
            return layer.name() === vm.selectedBasemapName();
        }).reduce(function(layers, layer) {
            return layers.concat(layer.layer_definitions);
        }, []);
    };
    var sources = $.extend(true, {}, arches.mapSources);
    _.each(sources, function(sourceConfig, name) {
        if (sourceConfig.tiles) {
            sourceConfig.tiles.forEach(function(url, i) {
                if (url.startsWith('/')) {
                    sourceConfig.tiles[i] = window.location.origin + url;
                }
            });
        }
    });

    var getSelectionLayers = function () {
        return [];
    }

    var displayLayers = getSelectionLayers();
    var basemapLayers = getBasemapLayers();

    vm.mapStyle = {
        "version": 8,
        "name": "Basic",
        "metadata": {
            "mapbox:autocomposite": true,
            "mapbox:type": "template"
        },
        "sources": sources,
        "sprite": "mapbox://sprites/mapbox/basic-v9",
        "glyphs": "mapbox://fonts/mapbox/{fontstack}/{range}.pbf",
        "layers": basemapLayers.concat(displayLayers)
    };

    vm.setupMap = function(map) {
        vm.map = map;
    }

    var updateMapStyle = function () {
        var displayLayers = getSelectionLayers();
        var basemapLayers = getBasemapLayers();
        vm.mapStyle.layers = basemapLayers.concat(displayLayers);
        vm.map.setStyle(vm.mapStyle);
    };

    vm.selectedBasemapName.subscribe(updateMapStyle);

    var datatypelookup = {};
    _.each(data.datatypes, function(datatype){
        datatypelookup[datatype.datatype] = datatype;
    }, this);

    _.each(data.geom_nodes, function(node) {
        vm.geomNodes.push(
            new NodeModel({
                loading: vm.loading,
                source: node,
                datatypelookup: datatypelookup,
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

    vm.selection = ko.observable(vm.geomNodes[0]);

    return new BaseManagerView({
        viewModel: vm
    });
});
