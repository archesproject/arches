require([
    'jquery',
    'underscore',
    'knockout',
    'views/page-view',
    'views/graph-manager/graph',
    'views/graph-manager/branch-list',
    'views/graph-manager/node-list',
    'views/graph-manager/permissions-list',
    'views/graph-manager/node-form',
    'views/graph-manager/permissions-form',
    'views/graph-manager/branch-info',
    'models/node',
    'bootstrap-nifty'
], function($, _, ko, PageView, GraphView, BranchListView, NodeListView, PermissionsListView, NodeFormView, PermissionsFormView, BranchInfoView, NodeModel) {
    var graphData = JSON.parse($('#graph-data').val());
    var datatypes = JSON.parse($('#datatypes').val());
    var datatypelookup = {}
    _.each(datatypes, function(datatype){
        datatypelookup[datatype.datatype] = datatype.iconclass;
    }, this)

    graphData.nodes.forEach(function (node, i) {
        graphData.nodes[i] = new NodeModel(node, datatypelookup);
    });

    var viewModel = {
        nodes: ko.observableArray(graphData.nodes),
        edges: ko.observableArray(graphData.edges)
    };

    viewModel.editNode = ko.computed(function() {
        var editNode = _.find(viewModel.nodes(), function(node){
            return node.editing();
        }, this);
        return editNode;
    });

    viewModel.selectedNodes = ko.computed(function() {
        var selectedNodes = _.filter(viewModel.nodes(), function(node){
            return node.selected();
        }, this);
        return selectedNodes;
    });

    viewModel.graph = new GraphView({
        el: $('#graph'),
        nodes: viewModel.nodes,
        edges: viewModel.edges
    });

    ko.computed(function() {
        viewModel.editNode();
        viewModel.selectedNodes();
        viewModel.graph.render();
    });

    viewModel.branchList = new BranchListView({
        el: $('#branch-library')
    });

    viewModel.nodeList = new NodeListView({
        el: $('#node-listing'),
        nodes: viewModel.nodes
    });

    viewModel.permissionsList = new PermissionsListView({
        el: $('#node-permissions')
    });

    viewModel.nodeForm = new NodeFormView({
        el: $('#nodeCrud'),
        node: viewModel.editNode
    });

    viewModel.permissionsForm = new PermissionsFormView({
        el: $('#permissions-panel')
    });

    viewModel.branchInfo = new BranchInfoView({
        el: $('#branch-panel')
    });

    new PageView({
        viewModel: viewModel
    });

    var resize = function(){
        $('#graph').height($(window).height()-200);
        $('svg').height($(window).height()-200);
        $('.tab-content').height($(window).height()-259);
        $('.grid-container').height($(window).height()-360);
    }

    $( window ).resize(resize);

    resize();
});
