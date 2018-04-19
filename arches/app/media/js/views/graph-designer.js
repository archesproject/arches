define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/base-manager',
    'viewmodels/alert',
    'models/graph',
    'views/graph/graph-tree',
    'graph-designer-data',
    'arches',
    'viewmodels/graph-settings',
    'bindings/resizable-sidepanel'
], function($, _, ko, koMapping, BaseManagerView, AlertViewModel, GraphModel, GraphTree, data, arches, GraphSettingsViewModel) {

    var viewModel = {
        dataFilter: ko.observable(''),
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design'),
        graphSettingsVisible: ko.observable(false),
        contentLoading: ko.observable(false),
        graph: koMapping.fromJS(data['graph']),
        ontologies: ko.observableArray([]),
        ontologyClasses: ko.observable(data['ontologyClasses']),
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
    });

    viewModel.graphSettingsViewModel = new GraphSettingsViewModel({
        graph: viewModel.graph,
        ontologyClasses: viewModel.ontologyClasses,
        ontologies: viewModel.ontologies,
        ontologyClass: ko.observable(''),
        iconFilter: ko.observable(''),
        node: viewModel.graph.root,
        rootNodeColor: ko.observable(''),
        ontology_namespaces: []
    });

    viewModel.loadGraphSettings = function(){
        var self = this;
        self.contentLoading(true);
        $.ajax({
            type: "GET",
            url: arches.urls.new_graph_settings(data.graphid),
            data: {'search': true, 'csrfmiddlewaretoken': '{{ csrf_token }}'}})
        .done(function(data){
            self.graphSettingsViewModel.resource_data(data.resources);
            self.graphSettingsViewModel.icon_data(data.icons);
            self.graphSettingsViewModel.jsonCache(self.graphSettingsViewModel.jsonData());
            self.graphSettingsViewModel.contentLoading = self.contentLoading;
            self.graphSettingsVisible(true);
            self.contentLoading(false);
        })
        .fail(function() {
          console.log( "error" );
      });
    };

    if (viewModel.activeTab() === 'graph') {
        viewModel.loadGraphSettings();
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
