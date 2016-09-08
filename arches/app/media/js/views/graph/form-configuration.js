require([
    'models/graph',
    'views/graph/graph-page-view',
    'form-configuration-data'
], function(GraphModel, PageView, data) {
    /**
    * a PageView representing the form configuration page
    */
    var self = this;
    var viewModel = {
        graphModel: new GraphModel({
            data: data.graph
        })
    };

    var pageView = new PageView({
        viewModel: viewModel
    });
});
