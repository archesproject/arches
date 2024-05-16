require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'views/graph/graph-page-view',
    'views/graph/graph-publication-data',
    'bindings/hover',
], function($, _, ko, arches, AlertViewModel, GraphPageView, data) {
    var viewModel = {
        loading: ko.observable(false),
        publishedUserData: ko.observable(data['user_ids_to_user_data']),
        graphPublicationIdFromDatabase: ko.observable(data['graph_publication_id']),
        graphPublicationId: ko.observable(data['graph_publication_id']),
        publishedGraphs: ko.observable(data['graphs_x_published_graphs']),
        graphPublicationResourceInstanceCount: ko.observable(data['graph_publication_id_to_resource_instance_count']),
        selectPublication: function(data) {viewModel.graphPublicationId(data['publicationid']);},
        showUpdatePublicationAlert: showUpdatePublicationAlert,
        showDeletePublicationAlert: showDeletePublicationAlert,
    };

    function showUpdatePublicationAlert() {
        viewModel.alert(new AlertViewModel(
            'ep-alert-blue',
            arches.translations.confirmGraphPublicationUpdate['title'],
            arches.translations.confirmGraphPublicationUpdate['text'],
            function(){/* cancel */},
            function(){
                viewModel.loading(true);

                $.ajax({
                    type: "POST",
                    url: arches.urls.update_published_graph.replace('//', '/' + viewModel.graphid() + '/'),
                    data: JSON.stringify(viewModel.graphPublicationId()),
                    success: function(_response) {
                        window.location.assign(arches.urls.graph_designer(viewModel.graphid()));
                    },
                    error: function(_response) {
                        viewModel.loading(false);

                        viewModel.alert(new AlertViewModel(
                            'ep-alert-red',
                            arches.translations.graphPublicationUpdateFailure['title'],
                            arches.translations.graphPublicationUpdateFailure['text'],
                            null,
                            function() {/* OK */}
                        ));
                    },
                });
            },
        ));
    }

    function showDeletePublicationAlert() {
        viewModel.alert(new AlertViewModel(
            'ep-alert-red',
            arches.translations.confirmGraphPublicationDelete['title'],
            arches.translations.confirmGraphPublicationDelete['text'],
            function(){/* cancel */},
            function(){
                $.ajax({
                    type: "DELETE",
                    url: arches.urls.delete_published_graph.replace('//', '/' + viewModel.graphid() + '/'),
                    data: JSON.stringify(viewModel.graphPublicationId()),
                    success: function(_response) {
                        const alert = new AlertViewModel(
                            'ep-alert-blue',
                            arches.translations.graphPublicationDeleteSuccess['title'],
                            arches.translations.graphPublicationDeleteSuccess['text'],
                            null,
                            function(){/* OK */},
                        );

                        viewModel.alert(alert);

                        alert.active.subscribe(function() {
                            viewModel.publishedGraphs(_response);
                        });
                    },
                    error: function(_response) {
                        viewModel.alert(new AlertViewModel(
                            'ep-alert-red',
                            arches.translations.graphPublicationDeleteFailure['title'],
                            arches.translations.graphPublicationDeleteFailure['text'],
                            null,
                            function() {/* OK */}
                        ));
                    },
                });
            },
        ));
    }
    
    return new GraphPageView({
        viewModel: viewModel
    });
});
