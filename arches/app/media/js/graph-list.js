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
    var selectedGraph = ko.observable(null);
    var newGraphName = ko.observable('');

    graphs().forEach(function(graph) {
        graph.metadata = _.find(metadata, function(metadata) {
            return metadata.graphmetadataid === graph.graphmetadata_id;
        });
        graph.open = function() {
            window.location = graph.nodeid;
        };
        graph.clone = function() {
            if (newGraphName() === '') {
                graph.select();
                $('#graph-name-modal').modal('show');
            } else {
                $.ajax({
                    type: "POST",
                    url: 'clone/' + selectedGraph(),
                    data: {
                        name: newGraphName()
                    },
                    success: function(response) {
                        window.location = response.root.nodeid;
                    },
                    datatype:'JSON'
                });
                console.log('clone the graph...');
            }
        };
        graph.select = function() {
            selectedGraph(graph.nodeid);
        };
        graph.selected = ko.computed(function() {
            return graph.nodeid === selectedGraph();
        });
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
                    if (graph.selected()) {
                        selectedGraph(null);
                    }
                    graphs.remove(graph);
                }
            }, node);
        };
    });

    new PageView({
        viewModel: {
            graphs: graphs,
            selectedGraph: selectedGraph,
            newGraphName: newGraphName,
            cloneSelected: function () {
                if (selectedGraph()) {
                    _.find(graphs(), function (graph) {
                        return graph.selected()
                    }).clone();
                }
            }
        }
    });

    $('.dropdown').dropdown();
});
