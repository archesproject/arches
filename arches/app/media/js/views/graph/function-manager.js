require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view',
    'views/graph/function-manager/function-list',
    'views/graph/function-manager/applied-function-list',
    'models/function',
    'models/function-x-graph',
    'graph-base-data',
    'graph-functions-data',
    'function-templates',
], function($, _, ko, arches, GraphPageView, FunctionList, AppliedFunctionList, FunctionModel, FunctionXGraphModel, baseData, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */
    var functionModels = [];
    var functionXGraphModels = [];
    var viewModel = {
        loading: ko.observable(false),
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


    viewModel.appliedFunctionList = new AppliedFunctionList({
        functions: ko.observableArray()
    })
    data.applied_functions.forEach(function(func){
        func.function = _.find(functionModels, function(fn){
            return fn.functionid === func.function_id;
        });
        viewModel.appliedFunctionList.items.push(new FunctionXGraphModel(func));
    }, this);


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

    viewModel.dirty = ko.computed(function(){
        return !!(_.find(viewModel.appliedFunctionList.items(), function(fn){
            return fn.dirty();
        }));
    });

    viewModel.save = function(){
        var functionsToSave = [];
        viewModel.loading(true);
        viewModel.appliedFunctionList.items().forEach(function(fn){
            if(fn.dirty()){
                functionsToSave.push(fn.toJSON());
            }
        });

        $.ajax({
            type: "POST",
            url: arches.urls.apply_functions.replace('//', '/' + baseData.graphid + '/'),
            data: JSON.stringify(functionsToSave),
            success: function(response) {
                //jsonCache(jsonData());
                viewModel.loading(false);
            },
            failure: function(response) {
                viewModel.loading(false);
            }
        });
    }

    viewModel.cancel = function(){
        viewModel.appliedFunctionList.items().forEach(function(fn){
            if(fn.dirty()){
                fn.reset();
            }
        });
    }

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });

    // graphPageView.viewModel.dirty = ko.computed(function(){
    //     return !!(_.find(viewModel.appliedFunctionList.items(), function(fn){
    //         return fn.dirty();
    //     }));
    // });

});
