require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view',
    'views/graph/graph-publication-data',
    'bindings/hover',
], function($, _, ko, arches, GraphPageView, data) {
    var viewModel = {
        loading: ko.observable(false),
        graphPublicationIdFromDatabase: ko.observable(data['graph_publication_id']),
        graphPublicationId: ko.observable(data['graph_publication_id']),
        publishedGraphs: ko.observable(data['graphs_x_published_graphs']),
        foo: function(data) {viewModel.graphPublicationId(data['publicationid']);},
        cancel: function(){},
        save: function(){},
        dirty: ko.observable(false),
    };

    viewModel.graphPublicationId.subscribe((graphPublicationId) => {
        viewModel.dirty(graphPublicationId !== viewModel.graphPublicationIdFromDatabase());
    });
    
    return new GraphPageView({
        viewModel: viewModel
    });
});
