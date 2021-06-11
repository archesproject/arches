define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'models/graph',
    'views/components/search/base-filter',
    'views/components/foo',
    'bindings/chosen'
], function($, _, ko, arches, GraphModel, BaseFilter) {
    var componentName = 'search-result-details';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                var self = this;

                options.name = 'Search Result Details';
                this.requiredFilters = ['search-results'];

                BaseFilter.prototype.initialize.call(this, options);

                this.options = options;

                this.resourceInstanceId = ko.observable();

                this.loading = ko.observable(false);
                this.ready = ko.observable(false);

                var setSearchResults = function(){
                    options.searchResultsVm = self.getFilter('search-results');
                    options.searchResultsVm.details = self;
                    options.filters[componentName](self);           
                };

                if (this.requiredFiltersLoaded() === false) {
                    this.requiredFiltersLoaded.subscribe(setSearchResults, this);
                } else {
                    setSearchResults();
                }

                var query = this.query();
                query['tiles'] = true;
                this.query(query);

                var graphCache = {};

                // var fooCache = {};

                this.foo = function() {
                    console.log(self.searchResults.results)
                };

                // /* roundabout searchResults subscription */ 
                // this.loading.subscribe(function() {
                //     console.log('g', self, options, self.searchResults.results)
                    
                // });

                // this.responseJson = ko.observable();


                console.log("search result details load", self, options, arches)

                this.genericResourceReportData = ko.observable()

                $.getJSON(arches.urls.api_generic_resource_report_data, function(resp) {
                    self.genericResourceReportData(resp)
                })



                
                this.setupReport = function(graphId, resourceInstanceId, source) {
                    // self.foo();
                    // self.responseJson(responseJson);
                    // self.loading(true);
                    self.resourceInstanceId(resourceInstanceId);

                    // var graph = graphCache[graphId];


                    // if (!graph) {
                    //     $.getJSON(arches.urls.graphs_api + graphId + "?context=search-result-details", function(data) {
                    //         var graphModel = new GraphModel({
                    //             data: data.graph,
                    //             datatypes: data.datatypes
                    //         });

                    //         graph = {
                    //             graphModel: graphModel,
                    //             cards: data.cards,
                    //             graph: data.graph,
                    //             datatypes: data.datatypes,
                    //             cardwidgets: data.cardwidgets
                    //         };

                    //         graphCache[graphId] = graph;

                    //         // self.loading(false);
                    //     });
                    // }
                    // else {
                    //     // self.loading(false);
                    // }
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
