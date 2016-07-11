require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/graph/graph-page-view',
    'graph-cards-data'
], function($, _, ko, koMapping, PageView, data) {

    /**
    * a GraphPageView representing the graph cards page
    */
    var self = this;
    var viewModel = {
        showCardLibrary: ko.observable(false),
        toggleCardLibrary: function(){
            this.showCardLibrary(!this.showCardLibrary());
        }
    }
    viewModel.cardLibraryStatus = ko.pureComputed(function() {
        return this.showCardLibrary() ? 'show-card-library' : 'hide-card-library';
    }, viewModel);
    viewModel.appliedGraphs = ko.observableArray();
    viewModel.availableGraphs = ko.observableArray();

    var findCardOrNode = function(branch, nodegroupid){
        var cardOrNode = _.find(branch.cards, function(card){
            return card.nodegroup_id === nodegroupid;
        })
        if(!cardOrNode){
            cardOrNode = _.find(branch.nodes, function(node){
                return node.nodeid === nodegroupid;
            })
        }
        return cardOrNode;
    }
    data.branches.forEach(function(branch){
        branch.card = {'name':'', 'subcards': []}
        branch.nodegroups.forEach(function(nodegroup){
            var cardOrNode = findCardOrNode(branch, nodegroup.nodegroupid);
            if(nodegroup.parentnodegroup_id){
                branch.card.subcards.push({'name':cardOrNode.name});
            }else{
                branch.card.name = cardOrNode.name;
            }
        })
        
        viewModel.availableGraphs.push(branch);
    })
    var pageView = new PageView({
        viewModel: viewModel
    });
});
