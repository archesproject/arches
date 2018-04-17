define([
    'underscore',
    'knockout',
    'views/base-manager',
    'models/graph',
    'views/graph/graph-tree',
    'graph-designer-data',
    'bindings/resizable-sidepanel',
    'bindings/tree-viewer'
], function(_, ko, BaseManagerView, GraphModel, GraphTree, data) {
    var viewModel = {
        dataFilter: ko.observable(''),
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design'),
        treePlugin: {},
        open_all: function(){
            viewModel.treePlugin.open_all();
        }
    }

    viewModel.graphModel = new GraphModel({
        data: data.graph,
        datatypes: data.datatypes,
        ontology_namespaces: data.ontology_namespaces
    });

    viewModel.graphTree = new GraphTree({
        graphModel: viewModel.graphModel
    });
    console.log(viewModel.graphTree.tree);

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
