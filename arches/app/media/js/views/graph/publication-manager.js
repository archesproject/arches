require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view',
    'views/graph/graph-publication-data',
], function($, _, ko, arches, GraphPageView, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */
    var viewModel = {
        loading: ko.observable(false),
    };

    console.log(data);

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });
});
