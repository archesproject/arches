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

    var findCard = function(branch, nodegroupid){
        return _.find(branch.cards, function(card){
            return card.nodegroup_id === nodegroupid;
        })
    }
    data.branches.forEach(function(branch){
        branch.nodegroups.forEach(function(nodegroup){
            var card = findCard(branch, nodegroup.nodegroupid);
            if (!(nodegroup.parentnodegroup_id)){
                branch.card = card;
            }
        })
        
        viewModel.availableGraphs.push(branch);
    });

    // data.graph.cards.forEach(function(card){
        
    //     viewModel.appliedGraphs.push(branch);
    // });
    var pageView = new PageView({
        viewModel: viewModel
    });
});
