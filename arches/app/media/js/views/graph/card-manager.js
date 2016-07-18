require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'models/graph',
    'views/graph/graph-page-view',
    'views/list',
    'viewmodels/alert',
    'graph-cards-data',
    'arches',
    'bindings/dragDrop'
], function($, _, ko, koMapping, GraphModel, PageView, ListView, AlertViewModel, data, arches) {

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
        }
    };
    viewModel.cardLibraryStatus = ko.pureComputed(function() {
        return showCardLibrary() ? 'show-card-library' : 'hide-card-library';
    }, viewModel);
    viewModel.appliedGraphs = ko.observableArray();
    viewModel.availableGraphs = ko.observableArray();

    var findCard = function(branch, nodegroupid){
        return _.find(branch.cards, function(card){
            return card.nodegroup_id === nodegroupid;
        })
    };
    data.branches.forEach(function(branch){
        branch.nodegroups.forEach(function(nodegroup){
            if (!(nodegroup.parentnodegroup_id)){
                branch.card = findCard(branch, nodegroup.nodegroupid);;
                viewModel.availableGraphs.push(branch);
            }
        })
    });

    viewModel.cardList = new ListView({
        el: $('#card-listing'),
        items: viewModel.availableGraphs
    });

    var alertFailure = function () {
        pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
    };

    viewModel.appendBranch = function(item){
        var self = this;
        this.loading(true);
        var branch_graph = new GraphModel({
            data: item
        });
        this.graphModel.appendBranch(this.graphModel.get('root').nodeid, null, branch_graph, function(response, status){
            var success = (status === 'success');
            this.loading(false);
            if (!success) alertFailure();
        }, this)
    };

    viewModel.deleteCard = function (card) {
        var self = this
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
    };


    viewModel.graphCards = ko.computed(function(){
        var parentCards = [];
        var allCards = this.graphModel.get('cards')();
        this.graphModel.get('nodegroups').filter(function(nodegroup){
            return !!nodegroup.parentnodegroup_id === false;
        }, this).forEach(function(nodegroup){
            parentCards = parentCards.concat(allCards.filter(function(card){
                return card.nodegroup_id === nodegroup.nodegroupid;
            }, this))
        }, this);
        return parentCards;
    }, viewModel);

    viewModel.newCard = ko.computed({
        read: function() {
            return viewModel.graphCards().length ? viewModel.graphCards()[0] : null;
        },
        write: function(value) {
            viewModel.appendBranch(value);
        }
    });

    var pageView = new PageView({
        viewModel: viewModel
    });
});
