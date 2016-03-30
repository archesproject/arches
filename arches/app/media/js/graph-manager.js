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
    var branches = JSON.parse($('#branches').val());
    var datatypes = JSON.parse($('#datatypes').val());
    var datatypelookup = {}
    _.each(datatypes, function(datatype){
        datatypelookup[datatype.datatype] = datatype.iconclass;
    }, this)

    graphData.nodes.forEach(function (node, i) {
        graphData.nodes[i] = new NodeModel({
            source: node,
            datatypelookup: datatypelookup
        });
    });

    branches.forEach(function(branch){
        branch.selected = ko.observable(false);
        branch.filtered = ko.observable(false);
    }, this);

    var viewModel = {
        nodes: ko.observableArray(graphData.nodes),
        edges: ko.observableArray(graphData.edges),
        branches: ko.observableArray(branches)
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

    viewModel.nodeForm = new NodeFormView({
        el: $('#nodeCrud'),
        node: viewModel.editNode
    });

    var getEdges = function (node) {
        var edges = viewModel.edges()
            .filter(function (edge) {
                return edge.domainnode_id === node.nodeid;
            });
        var nodes = edges.map(function (edge) {
            return viewModel.nodes().find(function (node) {
                return edge.rangenode_id === node.nodeid;
            });
        });
        nodes.forEach(function (node) {
            edges = edges.concat(getEdges(node));
        });
        return edges
    };

    viewModel.nodeForm.on('node-deleted', function (node) {
        var edges = getEdges(node);
        var nodes = edges.map(function (edge) {
            return viewModel.nodes().find(function (node) {
                return edge.rangenode_id === node.nodeid;
            });
        });
        var edge = viewModel.edges()
            .find(function (edge) {
                return edge.rangenode_id === node.nodeid;
            });
        nodes.push(node);
        edges.push(edge);
        viewModel.edges.remove(function (edge) {
            return _.contains(edges, edge);
        });
        viewModel.nodes.remove(function (node) {
            return _.contains(nodes, node);
        });
    });

    viewModel.graph.on('node-clicked', function (node) {
        if (viewModel.editNode() && viewModel.editNode().dirty()) {
            viewModel.nodeForm.closeClicked(true);
            return;
        }
        viewModel.nodes().forEach(function (node) {
            node.editing(false);
        });
        node.editing(true);
    });

    viewModel.branchList = new BranchListView({
        el: $('#branch-library'),
        branches: viewModel.branches
    });

    viewModel.nodeList = new NodeListView({
        el: $('#node-listing'),
        nodes: viewModel.nodes
    });

    viewModel.permissionsList = new PermissionsListView({
        el: $('#node-permissions')
    });

    viewModel.permissionsForm = new PermissionsFormView({
        el: $('#permissions-panel')
    });

    new PageView({
        viewModel: viewModel
    });

    var resize = function(){
        $('#graph').height($(window).height()-200);
        $('.tab-content').height($(window).height()-259);
        $('.grid-container').height($(window).height()-360);
        viewModel.graph.resize();
    }

    $( window ).resize(resize);

    resize();
});
