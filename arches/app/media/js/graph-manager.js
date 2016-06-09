require([
    'jquery',
    'underscore',
    'knockout',
    'views/graph-page-view',
    'views/graph-manager/graph',
    'views/graph-manager/node-list',
    'views/graph-manager/permissions-list',
    'views/graph-manager/node-form',
    'views/graph-manager/permissions-form',
    'models/node',
    'models/graph',
    'graph-manager-data'
], function($, _, ko, PageView, GraphView, NodeListView, PermissionsListView, NodeFormView, PermissionsFormView, NodeModel, GraphModel, data) {
    /**
    * prep data for model
    */
    data.branches.forEach(function(branch){
        branch.selected = ko.observable(false);
        branch.filtered = ko.observable(false);
    }, this);

    /**
    * create graph model
    */
    var graphModel = new GraphModel({
        data: data.graph,
        datatypes: data.datatypes
    });

    graphModel.on('changed', function(model, options){
        viewModel.graphView.redraw(true);
    });
    graphModel.on('select-node', function(model, options){
        viewModel.nodeForm.closeClicked(true);
    });

    /**
    * set up the page view model with the graph model and related sub views
    */
    var loading = ko.observable(false);
    var viewModel = {
        graphModel: graphModel,
        loading: loading
    };

    viewModel.graphView = new GraphView({
        el: $('#graph'),
        graphModel: graphModel,
        nodeSize: 20,
        nodeSizeOver: 20,
        labelOffset: 10
    });

    viewModel.nodeForm = new NodeFormView({
        el: $('#node-crud'),
        graphModel: graphModel,
        validations: data.validations,
        branches: data.branches,
        loading: loading
    });

    viewModel.dirty = ko.computed(function () {
        var node = viewModel.nodeForm.node();
        return node ? viewModel.nodeForm.node().dirty() : false;
    });

    viewModel.nodeList = new NodeListView({
        el: $('#node-listing'),
        graphModel: graphModel
    });

    viewModel.permissionsList = new PermissionsListView({
        el: $('#node-permissions')
    });

    viewModel.permissionsForm = new PermissionsFormView({
        el: $('#permissions-panel')
    });

    /**
    * a GraphPageView representing the graph manager page
    */
    new PageView({
        viewModel: viewModel
    });


    /**
    * update the sizing of elements on window resize
    */
    var resize = function(){
        $('#graph').height($(window).height()-100);
        $('.tab-content').height($(window).height()-191);
        $('.grid-container').height($(window).height()-260);
        viewModel.graphView.resize();
    }

    viewModel.nodeForm.node.subscribe(resize)

    $( window ).resize(resize);

    resize();
});
