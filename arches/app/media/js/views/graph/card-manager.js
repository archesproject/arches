require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'models/graph',
    'views/graph/graph-page-view',
    'graph-cards-data',
    'bindings/dragDrop'
], function($, _, ko, koMapping, GraphModel, PageView, data) {

    /**
    * a PageView representing the graph cards page
    */
    var self = this;
    var viewModel = {
        graphModel: new GraphModel({
            data: data.graph
        }),
        showCardLibrary: ko.observable(false),
        toggleCardLibrary: function(){
            this.showCardLibrary(!this.showCardLibrary());
        }
    };
    viewModel.cardLibraryStatus = ko.pureComputed(function() {
        return this.showCardLibrary() ? 'show-card-library' : 'hide-card-library';
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

    viewModel.appendBranch = function(item){
        var self = this;
        this.loading(true);
        var branch_graph = new GraphModel({
            data: item
        });
        this.graphModel.appendBranch(this.graphModel.get('root').nodeid, null, branch_graph, function(response, status){
            this.loading(false);
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
                self.loading(false);
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
    // data.graph.cards.forEach(function(card){

    //     viewModel.appliedGraphs.push(branch);
    // });
    var pageView = new PageView({
        viewModel: viewModel
    });
});
