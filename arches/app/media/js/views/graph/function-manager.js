require([
    'jquery',
    'underscore',
    'knockout',
    'views/graph/graph-page-view',
    'views/graph/function-manager/function-list',
    'graph-functions-data'
], function($, _, ko, GraphPageView, FunctionList, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */
    var loading = ko.observable(false);
    var viewModel = {
        loading: loading
    };

    viewModel.functionList = new FunctionList({
        functions: ko.observableArray(data.functions)
    })

    viewModel.functionList.on('item-selected', function(form){
        // pageView.viewModel.loading(true);
        // formView.loadForm(form.formid, function(){
        //     pageView.viewModel.loading(false);
        // });
    });

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });

});
