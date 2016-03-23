require([
    'jquery',
    'knockout',
    'views/page-view',
    'views/graph-manager/graph',
    'views/graph-manager/branch-list',
    'views/graph-manager/node-list',
    'views/graph-manager/permissions-list',
    'views/graph-manager/node-form',
    'views/graph-manager/permissions-form',
    'views/graph-manager/branch-info',
    'bootstrap-nifty'
], function($, ko, PageView, GraphView, BranchListView, NodeListView, PermissionsListView, NodeFormView, PermissionsFormView, BranchInfoView) {
    var viewModel = {
        nodes: ko.observableArray([]),
        edges: ko.observableArray([])
    };

    viewModel.selectNode = function (node) {
        viewModel.nodes().forEach(function(node) {
            node.selected(false);
        })
        node.selected(true);
    };

    viewModel.selectedNode = ko.computed(function() {
        var selection = null;
        viewModel.nodes().forEach(function(node) {
            if (node.selected()) {
                selection = node;
            }
        })
        return selection;
    });

    viewModel.graph = new GraphView({
        el: $('#graph'),
        nodes: viewModel.nodes,
        edges: viewModel.edges
    });

    viewModel.branchList = new BranchListView({
        el: $('#branch-library')
    });

    viewModel.nodeList = new NodeListView({
        el: $('#node-listing')
    });

    viewModel.permissionsList = new PermissionsListView({
        el: $('#node-permissions')
    });

    viewModel.nodeForm = new NodeFormView({
        el: $('#nodeCrud')
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
});
