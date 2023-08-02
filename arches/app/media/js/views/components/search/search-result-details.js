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
    'views/components/resource-report-abstract',
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

                this.setupReport = function(source, bulkResourceReportCache, bulkDisambiguatedResourceInstanceCache) {    
                    self.loading(true);

                    var sourceData = {
                        "tiles": source.tiles,
                        "displayname": source.displayname,
                        "resourceid": source.resourceinstanceid
                    };

                    var graphId = source['graph_id'];
                    var resourceId = source['resourceinstanceid'];

                    if (bulkResourceReportCache()[graphId] && bulkDisambiguatedResourceInstanceCache()[resourceId]) {
                        self.createReport(sourceData, bulkResourceReportCache()[graphId], bulkDisambiguatedResourceInstanceCache()[resourceId]);
                        self.loading(false);
                    }
                };

                this.createReport = function(sourceData, bulkResourceReportCacheData, bulkDisambiguatedResourceInstanceCacheData) {
                    var data = { ...sourceData };

                    if (bulkResourceReportCacheData.graph) {
                        data.cards = _.filter(bulkResourceReportCacheData.cards, function(card) {
                            var nodegroup = _.find(bulkResourceReportCacheData.graph.nodegroups, function(group) {
                                return group.nodegroupid === card.nodegroup_id;
                            });
                            return !nodegroup || !nodegroup.parentnodegroup_id;
                        }).map(function(card) {
                            return new CardViewModel({
                                card: card,
                                graphModel: bulkResourceReportCacheData.graphModel,
                                resourceId: data.resourceid,
                                displayname: data.displayname,
                                cards: bulkResourceReportCacheData.cards,
                                tiles: data.tiles,
                                cardwidgets: bulkResourceReportCacheData.cardwidgets
                            });
                        });
    
                        data.templates = reportLookup;
                        data.cardComponents = cardComponents;

                        var report = new ReportModel(_.extend(data, {
                            graphModel: bulkResourceReportCacheData.graphModel,
                            graph: bulkResourceReportCacheData.graph,
                            datatypes: bulkResourceReportCacheData.datatypes,
                        }));

                        report.report_json = bulkDisambiguatedResourceInstanceCacheData;
    
                        self.report(report);
                    }
                    else {
                        self.report({
                            templateId: ko.observable(bulkResourceReportCacheData.template_id),
                            report_json: bulkDisambiguatedResourceInstanceCacheData,
                        });

                    }
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
