require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'models/graph',
    'views/graph/graph-page-view',
    'views/list',
    'viewmodels/alert-json',
    'graph-cards-data',
    'arches',
    'bindings/dragDrop'
], function($, _, ko, koMapping, GraphModel, PageView, ListView, JsonErrorAlertViewModel, data, arches) {

    /**
    * a PageView representing the graph cards page
    */
    var self = this;
    var showCardLibrary = ko.observable(false);
    var viewModel = {
        graphModel: new GraphModel({
            data: data.graph
        }),
        showCardLibrary: showCardLibrary,
        toggleCardLibrary: function(){
            showCardLibrary(!showCardLibrary());
        },
        selectedCardId: ko.observable(null)
    };
    viewModel.cardLibraryStatus = ko.pureComputed(function() {
        return showCardLibrary() ? 'show-card-library' : 'hide-card-library';
    }, viewModel);
    viewModel.appliedGraphs = ko.observableArray();
    viewModel.availableGraphs = ko.observableArray();

    var findCard = function(branch, nodegroupid){
        return _.find(branch.cards, function(card){
            return card.nodegroup_id === nodegroupid;
        });
    };
    data.branches.forEach(function(branch){
        branch.nodegroups.forEach(function(nodegroup){
            if (!(nodegroup.parentnodegroup_id)){
                branch.card = findCard(branch, nodegroup.nodegroupid);
                viewModel.availableGraphs.push(branch);
            }
        });
    });

    viewModel.cardList = new ListView({
        items: viewModel.availableGraphs
    });

    var alertFailure = function(responseJSON) {
        pageView.viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', responseJSON));
    };

    viewModel.addCard = function(data){
        var self = this;
        this.loading(true);
        var cardGraph = new GraphModel({
            data: data
        });
        this.graphModel.appendBranch(this.graphModel.get('root'), null, cardGraph, function(response, status){
            var success = (status === 'success');
            this.loading(false);
            if (!success) alertFailure();
        }, this);
    };

    viewModel.deleteCard = function(card) {
        if (card.is_editable === true) {
            var self = this;
            var node = _.find(this.graphModel.get('nodes')(), function(node) {
                return node.nodeid === card.nodegroup_id;
            });
            if (node) {
                this.loading(true);
                this.graphModel.deleteNode(node, function(response, status){
                    var success = (status === 'success');
                    self.loading(false);
                    if (!success) alertFailure();
                });
            }
        }
    };

    viewModel.openCard = function(cardId) {
        pageView.viewModel.navigate(arches.urls.card + cardId);
    };

    viewModel.selectedCardId.subscribe(function(cardId) {
        if (cardId) {
            viewModel.openCard(cardId);
        }
    });

    viewModel.graphCardOptions = ko.computed(function() {
        var options = [{
            name: null,
            graphId: null,
            disabled: true
        }];
        return options.concat(viewModel.graphModel.graphCards());
    });

    viewModel.newCard = ko.computed({
        read: function() {
            return viewModel.graphModel.graphCards().length ? viewModel.graphModel.graphCards()[0] : null;
        },
        write: function(value) {
            viewModel.addCard(value);
        }
    });

    var pageView = new PageView({
        viewModel: viewModel
    });
});
