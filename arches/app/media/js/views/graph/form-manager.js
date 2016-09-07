require([
    'models/graph',
    'views/graph/graph-page-view',
    'graph-forms-data',
], function(GraphModel, PageView, data) {

    /**
    * a PageView representing the graph forms page
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
