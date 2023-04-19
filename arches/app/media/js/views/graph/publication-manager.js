require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view',
    'views/graph/graph-publication-data',
    'bindings/hover',
], function($, _, ko, arches, GraphPageView, data) {
    console.log(data)
    var viewModel = {
        loading: ko.observable(false),
        publishedUserData: ko.observable(data['user_ids_to_user_data']),
        graphPublicationIdFromDatabase: ko.observable(data['graph_publication_id']),
        graphPublicationId: ko.observable(data['graph_publication_id']),
        publishedGraphs: ko.observable(data['graphs_x_published_graphs']),
        selectPublication: function(data) {viewModel.graphPublicationId(data['publicationid']);},
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
