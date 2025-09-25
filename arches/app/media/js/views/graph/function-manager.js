import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import arches from 'arches';
import GraphPageView from 'views/graph/graph-page-view';
import AlertViewModel from 'viewmodels/alert';
import JsonErrorAlertViewModel from 'viewmodels/alert-json';
import FunctionList from 'views/graph/function-manager/function-list';
import AppliedFunctionList from 'views/graph/function-manager/applied-function-list';
import FunctionModel from 'models/function-model';
import FunctionXGraphModel from 'models/function-x-graph';
import baseData from 'views/graph/graph-base-data';
import data from 'views/graph/graph-functions-data';
import 'views/components/functions/primary-descriptors';
import 'function-templates';


var functionModels = [];
var savedFunctions = ko.observableArray(_.map(data.applied_functions, function(fn){return fn.function_id;}));

var viewModel = {
    loading: ko.observable(false),
    selectedFunction: ko.observable(),
    shouldShowUpdatePublishedGraphsButton: ko.observable(baseData.graph.has_unpublished_changes),
    shouldShowPublishModal: ko.observable(false),
    graph: koMapping.fromJS(baseData.graph),
};
const url = new URL(window.location);

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


viewModel.showRestoreStateFromSerializedGraphAlert = function() {
    viewModel.alert(new AlertViewModel(
        'ep-alert-red',
        arches.translations.confirmGraphRevert.title,
        arches.translations.confirmGraphRevert.text,
        function() {},
        viewModel.restoreStateFromSerializedGraph,
    ));    viewModel.alert(new AlertViewModel(
        'ep-alert-red',
        arches.translations.confirmGraphRevert.title,
        arches.translations.confirmGraphRevert.text,
        function() {},
        viewModel.restoreStateFromSerializedGraph,
    ));
};

viewModel.restoreStateFromSerializedGraph = function() {
    viewModel.loading(true);

    $.ajax({
        type: "POST",
        url: arches.urls.restore_state_from_serialized_graph(viewModel.graph.graphid()),
        complete: function(response, status) {
            if (status === 'success') { window.location.reload(); }
            else {
                viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
            }
        }
    });
};

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
    viewModel.shouldShowUpdatePublishedGraphsButton(true);
};

viewModel.showUpdatePublishedGraphsAlert = function() {
    viewModel.alert(new AlertViewModel(
        'ep-alert-red',
        arches.translations.confirmGraphPublicationEdit.title,
        arches.translations.confirmGraphPublicationEdit.text,
        function() {},
        viewModel.updatePublishedGraphs
    ));
    viewModel.shouldShowUpdatePublishedGraphsButton(true);
};

viewModel.updatePublishedGraphs = function() {
    viewModel.loading(true);

    $.ajax({
        type: "POST",
        data: JSON.stringify({}),
        url: arches.urls.update_published_graphs(viewModel.graph.graphid()),
        success: function(response) {
            window.location.href = window.location.pathname + '?has_updated_published_graph=true';
        },
        error: function(response) {
            viewModel.shouldShowPublishModal(false);
            viewModel.loading(false);

            viewModel.alert(new JsonErrorAlertViewModel(
                'ep-alert-red',
                response.responseJSON,
                null,
                function(){},
            ));
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

if (url.searchParams.has('has_updated_published_graph')) {
    viewModel.alert(new AlertViewModel(
            'ep-alert-blue',
            arches.translations.graphDesignerPublishedGraphUpdated.title,
            arches.translations.graphDesignerPublishedGraphUpdated.text,
            null,
            function(){
                // removes query args without reloading page
                url.search = '';
                window.history.replaceState({}, document.title, url.toString());
            },
        )
    );
}
