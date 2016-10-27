require([
    'jquery',
    'underscore',
    'knockout',
    'views/graph/graph-page-view',
    'graph-functions-data'
], function($, _, ko, GraphPageView, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */
    var loading = ko.observable(false);
    var viewModel = {
        loading: loading
    };

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });

});
