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

                this.report = ko.observable();
                this.loading = ko.observable(false);

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

                this.setupReport = function(source, bulkFooGraphCache, bulkFooDisambiguatedResourceCache) {    
                    self.loading(true);

                    var sourceData = {
                        "tiles": source.tiles,
                        "displayname": source.displayname,
                        "resourceid": source.resourceinstanceid
                    };

                    var graphId = source['graph_id'];
                    var resourceId = source['resourceinstanceid'];

                    if (bulkFooGraphCache()[graphId]) {
                        self.createReport(sourceData, bulkFooGraphCache()[graphId], bulkFooDisambiguatedResourceCache()[resourceId]);
                        self.loading(false)
                    }
                    else {

                        var bulkFooGraphCacheSubscription = bulkFooGraphCache.subscribe(function(cache) {
                            if (cache[graphId]) {
                                self.createReport(sourceData, cache[graphId], bulkFooDisambiguatedResourceCache()[resourceId]);

                                bulkFooGraphCacheSubscription.dispose(); /* terminates subscription */
                                self.loading(false);
                            }
                        });
                    }
                };

                this.createReport = function(sourceData, bulkFooGraphCacheData, bulkFooDisambiguatedResourceCacheData) {
                    console.log("DFDSFDSFDSFDSFSDFSD", sourceData, bulkFooDisambiguatedResourceCacheData, bulkFooGraphCacheData)
                    var data = { ...sourceData };

                    /* only templates that `preload_resource_data` use/cache the graph */ 
                    if (bulkFooGraphCacheData.graph) {
                        data.cards = _.filter(bulkFooGraphCacheData.cards, function(card) {
                            var nodegroup = _.find(bulkFooGraphCacheData.graph.nodegroups, function(group) {
                                return group.nodegroupid === card.nodegroup_id;
                            });
                            return !nodegroup || !nodegroup.parentnodegroup_id;
                        }).map(function(card) {
                            return new CardViewModel({
                                card: card,
                                graphModel: bulkFooGraphCacheData.graphModel,
                                resourceId: data.resourceid,
                                displayname: data.displayname,
                                cards: bulkFooGraphCacheData.cards,
                                tiles: data.tiles,
                                cardwidgets: bulkFooGraphCacheData.cardwidgets
                            });
                        });
    
                        data.templates = reportLookup;
                        data.cardComponents = cardComponents;

                        var report = new ReportModel(_.extend(data, {
                            graphModel: bulkFooGraphCacheData.graphModel,
                            graph: bulkFooGraphCacheData.graph,
                            datatypes: bulkFooGraphCacheData.datatypes,
                        }));

                        report.disambiguated_resource = bulkFooDisambiguatedResourceCacheData;
    
                        self.report(report);
                    }
                    else {
                        self.report({
                            templateId: ko.observable(bulkFooGraphCacheData.template_id),
                            disambiguated_resource: bulkFooDisambiguatedResourceCacheData,
                        });

                    }
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
