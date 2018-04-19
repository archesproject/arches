define([
    'underscore',
    'knockout',
    'views/base-manager',
    'viewmodels/alert',
    'models/graph',
    'views/graph/graph-tree',
    'graph-designer-data',
    'bindings/resizable-sidepanel'
], function(_, ko, BaseManagerView, AlertViewModel, GraphModel, GraphTree, data) {
    var viewModel = {
        dataFilter: ko.observable(''),
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design')
    }

    viewModel.graphModel = new GraphModel({
        data: data.graph,
        datatypes: data.datatypes,
        ontology_namespaces: data.ontology_namespaces
    });

    viewModel.graphTree = new GraphTree({
        graphModel: viewModel.graphModel
    });

    viewModel.graphTree.on('error', function(response){
        viewModel.alert(new AlertViewModel('ep-alert-red', response.title, response.message));
    })



    if (viewModel.activeTab() === 'graph') {
        // here we might load data/views asyncronously
    }else{

    }

    if (viewModel.viewState() === 'design') {
        // here we might load data/views asyncronously
    }else{

    }

    return new BaseManagerView({
        viewModel: viewModel
    });
});
