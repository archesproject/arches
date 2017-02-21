define([
    'knockout',
    'underscore',
    'views/base-manager',
    'models/node',
    'map-layer-manager-data',
    'datatype-config-components'
], function(ko, _, BaseManagerView, NodeModel, data) {
    var vm = {
        geomNodes: []
    };

    var datatypelookup = {};
    _.each(data.datatypes, function(datatype){
        datatypelookup[datatype.datatype] = datatype;
    }, this);

    _.each(data.geom_nodes, function(node) {
        vm.geomNodes.push(
            new NodeModel({
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
