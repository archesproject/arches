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
    var pageView = new PageView({
        viewModel: viewModel,
        graphs: data.graphs
    });
});
