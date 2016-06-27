require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/graph-page-view',
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
    data.graphs.forEach(function(graph){
        if(graph.isactive && !graph.isresource){
            viewModel.availableGraphs.push(graph);
        }
    })
    var pageView = new PageView({
        viewModel: viewModel
    });
});
