require([
    'jquery',
    'underscore',
    'knockout',
    'views/graph/graph-page-view',
    'views/graph/graph-manager/graph',
    'views/graph/graph-manager/node-list',
    'views/graph/graph-manager/node-form',
    'models/node',
    'models/graph',
    'viewmodels/alert',
    'arches',
    'graph-manager-data',
    'datatype-config-components'
], function($, _, ko, PageView, GraphView, NodeListView, NodeFormView, NodeModel, GraphModel, AlertViewModel, arches, data) {
    /**
    * create graph model
    */
    var graphModel = new GraphModel({
        data: data.graph,
        datatypes: data.datatypes,
        ontology_namespaces: data.ontology_namespaces
    });

    var nextSelection = null;
    graphModel.on('changed', function(model, response){
        viewModel.graphView.redraw(true);
        viewModel.alert(null);
        loading(false);
        if(response.status != 200){
            var errorMessageTitle = arches.requestFailed.title
            var errorMessageText = arches.requestFailed.text
            viewModel.alert(null);
            if (response.responseJSON) {
              errorMessageTitle = response.responseJSON.title
              errorMessageText = response.responseJSON.message
            }
            viewModel.alert(new AlertViewModel('ep-alert-red', errorMessageTitle, errorMessageText));
        }
    });
    graphModel.on('select-node', function(node){
        nextSelection = node;
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
        nodeSize: 15,
        nodeSizeOver: 20,
        labelOffset: 10,
        loading: loading
    });

    viewModel.nodeForm = new NodeFormView({
        el: $('#node-crud'),
        graphModel: graphModel,
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

    viewModel.nodeList.on('node-selected', function(node) {
        viewModel.graphView.zoomTo(node);
    });

    /**
    * a GraphPageView representing the graph manager page
    */
    var pageView = new PageView({
        viewModel: viewModel
    });


    viewModel.nodeForm.closeClicked.subscribe(function(closeClicked) {
        var node = viewModel.nodeForm.node();
        if (closeClicked && node && node.dirty()) {
            pageView.viewModel.alert(new AlertViewModel('ep-alert-blue', arches.confirmNav.title, arches.confirmNav.text, function () {
                viewModel.nodeForm.closeClicked(false);
                nextSelection = null;
            }, function () {
                viewModel.nodeForm.cancel();
                viewModel.nodeForm.closeClicked(false);
                if (nextSelection) {
                    graphModel.selectNode(nextSelection);
                }
                nextSelection = null;
            }));
        } else {
            pageView.viewModel.alert(null);
        }
    });

    graphModel.selectNode(graphModel.get('root'));

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
