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
    'bootstrap-nifty'
], function($, _, ko, PageView, GraphView, BranchListView, NodeListView, PermissionsListView, NodeFormView, PermissionsFormView, BranchInfoView) {
    var graphData = JSON.parse($('#graph-data').val());
    var datatypes = JSON.parse($('#datatypes').val());
    var datatypelookup = {}
    _.each(datatypes, function(datatype){
        datatypelookup[datatype.datatype] = datatype.iconclass;
    }, this)

    var resetNode = function(source, target) {
        target._node = JSON.stringify(source)
        target.selected = ko.observable(false);
        target.filtered = ko.observable(false);
        target.editing = ko.observable(false);
        target.name = ko.observable(source.name);
        target.iconclass = datatypelookup[source.datatype];
        target.reset = function () {
            resetNode(JSON.parse(target._node), target);
        };
        target.json = ko.computed(function() {
            return JSON.stringify(_.extend(JSON.parse(target._node), {
                name: target.name()
            }))
        });
        target.dirty = ko.computed(function() {
            return target.json() !== target._node;
        });
    }
    graphData.nodes.forEach(function (node) {
        resetNode(node, node);
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
