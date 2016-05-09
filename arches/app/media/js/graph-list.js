require([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'models/node',
    'bootstrap-nifty'
], function($, _, ko, PageView, NodeModel) {
    var graphs = ko.observableArray(JSON.parse($('#graphs').val()));
    var selectedGraph = ko.observable(null);
    var newGraphName = ko.observable('');

    graphs().forEach(function(graph) {
        graph.open = function() {
            pageView.viewModel.loading(true);
            window.location = graph.nodeid + '/settings';
        };
        graph.clone = function() {
            if (newGraphName() === '') {
                graph.select();
                $('#graph-name-modal').modal('show');
            } else {
                pageView.viewModel.loading(true);
                $.ajax({
                    type: "POST",
                    url: 'clone/' + selectedGraph(),
                    data: JSON.stringify({name: newGraphName()}),
                    success: function(response) {
                        window.location = response.root.nodeid + '/settings';
                    },
                    failure: function(response) {
                        pageView.viewModel.loading(false);
                    }
                });
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
            pageView.viewModel.loading(true);
            node['delete'](function (request, status) {
                var success = (status === 'success');
                pageView.viewModel.loading(false);
                if (success) {
                    if (graph.selected()) {
                        selectedGraph(null);
                    }
                    graphs.remove(graph);
                }
            }, node);
        };
    });

    var pageView = new PageView({
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
