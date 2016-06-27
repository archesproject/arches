require([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'viewmodels/alert',
    'arches',
    'view-data',
    'bootstrap-nifty',
    'bindings/hover'
], function($, _, ko, PageView, AlertViewModel, arches, data) {
    var graphs = ko.observableArray(data.graphs);

    /**
    * creates a request to add a new graph; redirects to the graph settings
    * page for the new graph on success
    *
    * @param  {string} url - the url to be used in the request
    * @param  {object} data (optional) - data to be included in request
    */
    var newGraph = function(url, data) {
        data = data || {};
        pageView.viewModel.loading(true);
        $.ajax({
            type: "POST",
            url: url,
            data: JSON.stringify(data),
            success: function(response) {
                window.location = response.metadata.graphid + '/settings';
            },
            failure: function(response) {
                pageView.viewModel.loading(false);
            }
        });
    }


    /**
    * sets up the graphs for the page's view model
    */
    graphs().forEach(function(graph) {
        graph.hover = ko.observable(false);
        graph.open = function(page) {
            page = page || '';
            pageView.viewModel.loading(true);
            window.location = graph.graphid + page;
        };
        graph.clone = function() {
            newGraph('clone/' + graph.graphid);
        };
        graph.deleteGraph = function () {
            pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmGraphDelete.title, arches.confirmGraphDelete.text, function() {
                return;
            }, function(){
                pageView.viewModel.loading(true);
                $.ajax({
                    complete: function (request, status) {
                        pageView.viewModel.loading(false);
                        if (status === 'success') {
                            graphs.remove(graph);
                        }
                    },
                    type: "DELETE",
                    url: graph.graphid
                });
            }));
        };
    });


    /**
    * a PageView representing the graph list page
    */
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
                newGraph('new', {isresource: true});
            },
            newGraph: function () {
                newGraph('new', {isresource: false});
            }
        }
    });

    $('.dropdown').dropdown();
});
