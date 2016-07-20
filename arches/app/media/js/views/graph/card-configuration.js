require([
    'jquery',
    'underscore',
    'knockout',
    'views/graph/graph-page-view',
    'views/graph/graph-manager/graph',
    'views/graph/graph-manager/node-list',
    'views/graph/graph-manager/permissions-list',
    'views/graph/graph-manager/node-form',
    'views/graph/graph-manager/permissions-form',
    'models/node',
    'models/graph',
    'viewmodels/alert',
    'arches',
    'card-configuration-data'
], function($, _, ko, PageView, GraphView, NodeListView, PermissionsListView, NodeFormView, PermissionsFormView, NodeModel, GraphModel, AlertViewModel, arches, data) {
    /**
    * create graph model
    */
    // var graphModel = new GraphModel({
    //     data: data.graph,
    //     datatypes: data.datatypes
    // });

    // graphModel.on('changed', function(model, options){
    //     viewModel.graphView.redraw(true);
    // });
    // graphModel.on('select-node', function(model, options){
    //     viewModel.nodeForm.closeClicked(true);
    // });

    /**
    * set up the page view model with the graph model and related sub views
    */
    var loading = ko.observable(false);
    var viewModel = {
        //graphModel: graphModel,
        loading: loading
    };

    // viewModel.graphView = new GraphView({
    //     el: $('#graph'),
    //     graphModel: graphModel,
    //     nodeSize: 15,
    //     nodeSizeOver: 20,
    //     labelOffset: 10,
    //     loading: loading
    // });

    // viewModel.nodeForm = new NodeFormView({
    //     el: $('#node-crud'),
    //     graphModel: graphModel,
    //     validations: data.validations,
    //     branches: data.branches,
    //     loading: loading
    // });

    // viewModel.dirty = ko.computed(function () {
    //     var node = viewModel.nodeForm.node();
    //     return node ? viewModel.nodeForm.node().dirty() : false;
    // });

    // viewModel.nodeList = new NodeListView({
    //     el: $('#node-listing'),
    //     graphModel: graphModel
    // });

    // viewModel.nodeList.on('node-selected', function(node) {
    //     viewModel.graphView.zoomTo(node);
    // });

    // viewModel.permissionsList = new PermissionsListView({
    //     el: $('#node-permissions')
    // });

    // viewModel.permissionsForm = new PermissionsFormView({
    //     el: $('#permissions-panel')
    // });

    /**
    * a GraphPageView representing the card configuration page
    */
    var pageView = new PageView({
        viewModel: viewModel
    });

    // viewModel.nodeForm.failed.subscribe(function(failed) {
    //     if (failed) {
    //         pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
    //     } else {
    //         pageView.viewModel.alert(null);
    //     }
    // });

    // viewModel.nodeForm.closeClicked.subscribe(function(closeClicked) {
    //     var node = viewModel.nodeForm.node();
    //     if (closeClicked && node && node.dirty()) {
    //         pageView.viewModel.alert(new AlertViewModel('ep-alert-blue', arches.confirmNav.title, arches.confirmNav.text, function () {
    //             viewModel.nodeForm.cancel();
    //         }, function () {
    //             viewModel.nodeForm.save();
    //         }));
    //     } else {
    //         pageView.viewModel.alert(null);
    //     }
    // });

    // graphModel.selectNode(graphModel.get('root'));

    // /**
    // * update the sizing of elements on window resize
    // */
    var resize = function(){
        $('#graph').height($(window).height()-100);
        $('.tab-content').height($(window).height()-191);
        $('.grid-container').height($(window).height()-260);
        //viewModel.graphView.resize();
    }

    // viewModel.nodeForm.node.subscribe(resize)

    $( window ).resize(resize);

    resize();
});
