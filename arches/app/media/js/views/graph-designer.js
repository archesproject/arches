define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/base-manager',
    'viewmodels/alert',
    'models/graph',
    'views/graph/graph-designer/graph-tree',
    'views/graph/graph-designer/node-form',
    'views/graph/graph-manager/branch-list',
    'graph-designer-data',
    'arches',
    'viewmodels/graph-settings',
    'bindings/resizable-sidepanel',
    'datatype-config-components'
], function($, _, ko, koMapping, BaseManagerView, AlertViewModel, GraphModel, GraphTree, NodeFormView, BranchListView, data, arches, GraphSettingsViewModel) {
    var viewModel = {
        placeholder: ko.observable(''),
        graphid: ko.observable(data.graphid),
        activeTab: ko.observable('graph'),
        viewState: ko.observable('design'),
        graphSettingsVisible: ko.observable(false),
        contentLoading: ko.observable(false),
        graph: koMapping.fromJS(data['graph']),
        ontologies: ko.observable(data['ontologies']),
        ontologyClasses: ko.observable(data['ontologyClasses']),
    }

    viewModel.graphModel = new GraphModel({
        data: data.graph,
        datatypes: data.datatypes,
        ontology_namespaces: data.ontology_namespaces
    });

    viewModel.graphModel.on('error', function(response){
        viewModel.alert(new AlertViewModel('ep-alert-red', response.responseJSON.title, response.responseJSON.message));
    });

    viewModel.selectedNode = viewModel.graphModel.get('selectedNode');

    viewModel.nodeForm = new NodeFormView({
        graph: viewModel.graph,
        graphModel: viewModel.graphModel,
        loading: viewModel.contentLoading,
        node: viewModel.selectedNode
    });

    viewModel.branchListView = new BranchListView({
        el: $('#branch-library'),
        branches: data.branches,
        graphModel: viewModel.graphModel,
        loading: viewModel.loading,
        disableAppendButton: ko.computed(function () {
            return //self.node() && self.node().dirty();
        })
    });

    viewModel.graphSettingsViewModel = new GraphSettingsViewModel({
        graph: viewModel.graph,
        graphModel: viewModel.graphModel,
        ontologyClasses: viewModel.ontologyClasses,
        ontologies: viewModel.ontologies,
        ontologyClass: ko.observable(''),
        iconFilter: ko.observable(''),
        node: viewModel.selectedNode,
        rootNodeColor: ko.observable(''),
        ontology_namespaces: data.ontology_namespaces
    });

    viewModel.graphTree = new GraphTree({
        graphModel: viewModel.graphModel,
        graphSettings: viewModel.graphSettingsViewModel
    });

    viewModel.graphTree.branchListVisible.subscribe(function(visible){
        if(visible){
            viewModel.branchListView.loadDomainConnections();
        }
    }, this);

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

    /**
    * update the sizing of elements on window resize
    */
    var resize = function(){
        $('.grid').height($(window).height()-208);
    }

    $( window ).resize(resize);

    resize();

    return new BaseManagerView({
        viewModel: viewModel
    });
});
