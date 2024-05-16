require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view',
    'viewmodels/alert-json',
    'views/graph/function-manager/function-list',
    'views/graph/function-manager/applied-function-list',
    'models/function',
    'models/function-x-graph',
    'views/graph/graph-base-data',
    'views/graph/graph-functions-data',
    'views/components/functions/primary-descriptors',
    'function-templates'
], function($, _, ko, arches, GraphPageView, JsonErrorAlertViewModel, FunctionList, AppliedFunctionList, FunctionModel, FunctionXGraphModel, baseData, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */
    var functionModels = [];
    var savedFunctions = ko.observableArray(_.map(data.applied_functions, function(fn){return fn.function_id;}));

    var viewModel = {
        loading: ko.observable(false),
        selectedFunction: ko.observable()
    };

    data.functions.forEach(function(func){
        functionModels.push(new FunctionModel(func));
    }, this);

    viewModel.functionList = new FunctionList({
        functions: ko.observableArray(functionModels)
    });

    viewModel.functionList.on('item-clicked', function(func){
        var newAppliedFunction = new FunctionXGraphModel({
            id: null,
            graphid: baseData.graphid,
            function: func,
            function_id: func.functionid,
            config: func.defaultconfig
        });
        viewModel.appliedFunctionList.items.push(newAppliedFunction);
        viewModel.appliedFunctionList.selectItem(newAppliedFunction);
    });

    viewModel.appliedFunctionList = new AppliedFunctionList({
        functions: ko.observableArray()
    });

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
    };

    viewModel.dirty = ko.computed(function(){
        if (viewModel.selectedFunction() && _.contains(savedFunctions(), viewModel.selectedFunction().function_id) === false) {
            return true;
        } else {
            return !!(_.find(viewModel.appliedFunctionList.items(), function(fn){
                return fn.dirty();
            }));
        }
    });

    var alertFailure = function(responseJSON) {
        graphPageView.viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', responseJSON));
    };

    viewModel.save = function(){
        var functionsToSave = [];
        viewModel.loading(true);
        viewModel.appliedFunctionList.items().forEach(function(fn){
            if (
                fn.dirty() 
                || !fn.function.component()
                || (viewModel.selectedFunction() && _.contains(savedFunctions(), viewModel.selectedFunction().function_id) === false)
            ) {
                functionsToSave.push(fn.toJSON());
            }
        });

        $.ajax({
            type: "POST",
            url: arches.urls.apply_functions.replace('//', '/' + baseData.graphid + '/'),
            data: JSON.stringify(functionsToSave),
            success: function(response) {
                var functionToUpdate;
                response.forEach(function(fn){
                    savedFunctions.push(fn.function_id);
                    functionToUpdate = _.find(viewModel.appliedFunctionList.items(), function(func){
                        return fn._id === func.toJSON()._id;
                    });
                    functionToUpdate.parse(fn);
                });
                viewModel.loading(false);
            },
            error: function(response) {
                viewModel.loading(false);
                alertFailure(response.responseJSON);
            }
        });
    };

    viewModel.delete = function(functionToDelete){
        if(!functionToDelete.id){
            viewModel.appliedFunctionList.items.remove(functionToDelete);
            viewModel.toggleFunctionLibrary();
        }else{
            $.ajax({
                type: "DELETE",
                url: arches.urls.remove_functions.replace('//', '/' + baseData.graphid + '/'),
                data: JSON.stringify([functionToDelete]),
                success: function() {
                    savedFunctions.remove(functionToDelete.function_id);
                    viewModel.appliedFunctionList.items.remove(functionToDelete);
                    viewModel.toggleFunctionLibrary();
                    viewModel.loading(false);
                },
                error: function(response) {
                    viewModel.loading(false);
                    alertFailure(response.responseJSON);
                }
            });
        }
    };

    viewModel.cancel = function(){
        viewModel.appliedFunctionList.items().forEach(function(fn){
            if(fn.dirty()){
                fn.reset();
            }
            if(!fn.id){
                viewModel.appliedFunctionList.items.remove(fn);
                if(viewModel.selectedFunction() === fn){
                    viewModel.toggleFunctionLibrary();
                }
            }
        });
    };

    viewModel.filterFunctions = function() {
        var vm = this;
        return function(applied) {
            var appliedIds = _.pluck(applied, 'function_id');
            _.each(vm.functionList.items(), function(item){
                if (_.contains(appliedIds, item.functionid)) {
                    item.filtered(true);
                } else if (item.filtered() === true){
                    item.filtered(false);
                }
            }, this);
        };
    };

    viewModel.appliedFunctionList.items.subscribe(viewModel.filterFunctions());
    viewModel.appliedFunctionList.items.valueHasMutated(); //force the filter to updated on page load

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });

});
