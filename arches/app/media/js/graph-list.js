require([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'models/node',
    'bootstrap-nifty'
], function($, _, ko, PageView, NodeModel) {
    var graphs = ko.observableArray(JSON.parse($('#graphs').val()));

    var cloneGraph = function(graphid, data) {
        data = data || {};
        pageView.viewModel.loading(true);
        $.ajax({
            type: "POST",
            url: 'clone/' + graphid,
            data: JSON.stringify(data),
            success: function(response) {
                window.location = response.metadata.graphid + '/settings';
            },
            failure: function(response) {
                pageView.viewModel.loading(false);
            }
        });
    }

    graphs().forEach(function(graph) {
        graph.open = function(page) {
            page = page || '';
            pageView.viewModel.loading(true);
            window.location = graph.graphid + page;
        };
        graph.clone = function() {
            cloneGraph(graph.graphid);
        };
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

    var newGraph = function (isResource) {
        var graphId = '22000000-0000-0000-0000-000000000000';
        cloneGraph(graphId, {
            isresource: !!isResource
        });
    };

    var pageView = new PageView({
        viewModel: {
            graphs: ko.computed(function() {
                return ko.utils.arrayFilter(graphs(), function(graph) {
                    return !graph.isresource;
                });
            }),
            resources: ko.computed(function() {
                return ko.utils.arrayFilter(graphs(), function(graph) {
                    return graph.isresource;
                });
            }),
            newResource: function () {
                newGraph(true);
            },
            newGraph: function () {
                newGraph(false);
            }
        }
    });

    $('.dropdown').dropdown();
});
