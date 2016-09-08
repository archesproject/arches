require([
    'models/graph',
    'views/graph/graph-page-view',
    'arches',
    'graph-forms-data',
], function(GraphModel, PageView, arches, data) {

    /**
    * a PageView representing the graph forms page
    */
    var self = this;
    var viewModel = {
        graphModel: new GraphModel({
            data: data.graph
        }),
        forms: data.forms,
        openForm: function (formId) {
            pageView.viewModel.navigate(arches.urls.form_configuration + formId);
        },
        addForm: function () {
            pageView.viewModel.loading(true);
            $.ajax({
                type: "POST",
                url: 'add_form',
                success: function(response) {
                    pageView.viewModel.openForm(response.formid);
                },
                error: function(response) {
                    pageView.viewModel.loading(false);
                }
            });
        }
    };

    var pageView = new PageView({
        viewModel: viewModel
    });
});
