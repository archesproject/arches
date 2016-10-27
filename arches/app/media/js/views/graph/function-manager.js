require([
    'jquery',
    'underscore',
    'knockout',
    'views/graph/graph-page-view',
    'views/graph/function-manager/function-list',
    'views/graph/function-manager/applied-function-list',
    'models/function',
    'models/function-x-graph',
    'graph-functions-data'
], function($, _, ko, GraphPageView, FunctionList, AppliedFunctionList, FunctionModel, FunctionXGraphModel, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */
    var functionModels = [];
    var functionXGraphModels = [];
    var loading = ko.observable(false);
    var viewModel = {
        loading: loading,
        selectedFunction: ko.observable()
    };


    data.functions.forEach(function(func){
        functionModels.push(new FunctionModel(func));
    }, this);

    viewModel.functionList = new FunctionList({
        functions: ko.observableArray(functionModels)
    })

    viewModel.functionList.on('item-clicked', function(func){
        // pageView.viewModel.loading(true);
        // formView.loadForm(form.formid, function(){
        //     pageView.viewModel.loading(false);
        // });
    });


    data.applied_functions.forEach(function(func){
        func.function = _.find(functionModels, function(fn){
            return fn.functionid === func.function_id;
        });
        functionXGraphModels.push(new FunctionXGraphModel(func));
    }, this);

    viewModel.appliedFunctionList = new AppliedFunctionList({
        functions: ko.observableArray(functionXGraphModels)
    })

    viewModel.appliedFunctionList.on('item-clicked', function(func){
        if (func.selected()) {
            viewModel.selectedFunction(func);
        }else{
            viewModel.selectedFunction(undefined);
        }
        // pageView.viewModel.loading(true);
        // formView.loadForm(form.formid, function(){
        //     pageView.viewModel.loading(false);
        // });
    });

    viewModel.toggleFunctionLibrary = function(){
        if (!!viewModel.selectedFunction()) {
            viewModel._selectedFunction = viewModel.selectedFunction();
            viewModel._selectedFunction.selected(false);
            viewModel.selectedFunction(undefined);
        }else{
            viewModel.selectedFunction(viewModel._selectedFunction);
            viewModel._selectedFunction.selected(true);
        }
    }

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });

});
