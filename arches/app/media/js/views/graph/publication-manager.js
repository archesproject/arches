require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view',
], function($, _, ko, arches, GraphPageView) {
    /**
    * set up the page view model with the graph model and related sub views
    */
    var viewModel = {
        loading: ko.observable(false),
    };

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });
});
