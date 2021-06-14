define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/components/search/base-filter',
    'report-templates',
    'card-components',
    'models/report',
    'viewmodels/card',
    'views/components/foo',
    'bindings/chosen'
], function($, _, ko, arches, BaseFilter, reportLookup, cardComponents, ReportModel, CardViewModel) {
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
                // this.resourceInstanceId.subscribe(function(resourceid) {
                //     var url = arches.urls.api_specific_resource_report_data(resourceid) + '?graph_data=false';

                //     $.getJSON(url, function(resp) {
                //         console.log("AAAxcxAAA", resp)
                //     })
                // });

                this.report = ko.observable();

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

                console.log("search result details load", self, options, arches)

                this.genericResourceReportData = ko.observable()

                $.getJSON(arches.urls.api_generic_resource_report_data, function(resp) {
                    self.genericResourceReportData(resp)
                })

                
                this.setupReport = function(source, bulkFooCache) {    
                    var sourceData = {
                        "tiles": source.tiles,
                        "displayname": source.displayname,
                        "resourceid": source.resourceinstanceid
                    };

                    var graphId = source['graph_id'];

                    if (bulkFooCache()[graphId]) {
                        self.createReport(sourceData, bulkFooCache()[graphId]);
                    }
                    else {
                        self.loading(true);

                        var bulkFooSubscription = bulkFooCache.subscribe(function(cache) {
                            if (cache[graphId]) {
                                self.createReport(sourceData, cache[graphId]);

                                bulkFooSubscription.dispose(); /* terminates subscription */
                                self.loading(false);
                            }
                        });
                    }
                };

                this.createReport = function(sourceData, bulkFooCacheData) {
                    console.log('in create report', sourceData, bulkFooCacheData)

                    var data = { ...sourceData };

                    data.cards = _.filter(bulkFooCacheData.cards, function(card) {
                        var nodegroup = _.find(bulkFooCacheData.graph.nodegroups, function(group) {
                            return group.nodegroupid === card.nodegroup_id;
                        });
                        return !nodegroup || !nodegroup.parentnodegroup_id;
                    }).map(function(card) {
                        return new CardViewModel({
                            card: card,
                            graphModel: bulkFooCacheData.graphModel,
                            resourceId: data.resourceid,
                            displayname: data.displayname,
                            cards: bulkFooCacheData.cards,
                            tiles: data.tiles,
                            cardwidgets: bulkFooCacheData.cardwidgets
                        });
                    });

                    data.templates = reportLookup;
                    data.cardComponents = cardComponents;

                    self.report(new ReportModel(_.extend(data, {
                        graphModel: bulkFooCacheData.graphModel,
                        graph: bulkFooCacheData.graph,
                        datatypes: bulkFooCacheData.datatypes
                    })));
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
