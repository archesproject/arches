require([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'models/node',
    'bootstrap-nifty'
], function($, _, ko, PageView, NodeModel) {
    var graphs = ko.observableArray(JSON.parse($('#graphs').val()));
    var metadata = JSON.parse($('#metadata').val());
    var loading = ko.observable(false);

    graphs().forEach(function(graph) {
        graph.metadata = _.find(metadata, function(metadata) {
            return metadata.graphmetadataid === graph.graphmetadata_id;
        });
        graph.open = function() {
            window.location = graph.nodeid;
        };
        graph.deleteGraph = function () {
            var node = new NodeModel({
                source: graph,
                datatypelookup: {}
            });
            loading(true);
            node['delete'](function (request, status) {
                var success = (status === 'success');
                loading(false);
                if (success) {
                    graphs.remove(graph);
                }
            }, node);
        };
    });

    new PageView({
        viewModel: {
            graphs: graphs
        }
    });

    $('.dropdown').dropdown();
});
