define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'models/report',
    'models/graph',
    'viewmodels/card',
    'report-templates',
    'views/components/search/base-filter',
    'card-components',
    'bindings/chosen'
], function($, _, ko, arches, ReportModel, GraphModel, CardViewModel, reportLookup, BaseFilter, cardComponents) {
    var componentName = 'search-result-details';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                var self = this;
                options.name = 'Search Result Details';
                this.requiredFilters = ['search-results'];
                BaseFilter.prototype.initialize.call(this, options);
                this.loading = ko.observable(false);
                this.options = options;
                this.report = null;
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
                var processReportData = function(data, graph) {
                    data.cards = _.filter(graph.cards, function(card) {
                        var nodegroup = _.find(graph.graph.nodegroups, function(group) {
                            return group.nodegroupid === card.nodegroup_id;
                        });
                        return !nodegroup || !nodegroup.parentnodegroup_id;
                    }).map(function(card) {
                        return new CardViewModel({
                            card: card,
                            graphModel: graph.graphModel,
                            resourceId: data.resourceid,
                            displayname: data.displayname,
                            cards: graph.cards,
                            tiles: data.tiles,
                            cardwidgets: graph.cardwidgets
                        });
                    });

                    self.reportLookup = reportLookup;
                    data.templates = reportLookup;
                    data.cardComponents = cardComponents;
                    self.report = new ReportModel(_.extend(data, {
                        graphModel: graph.graphModel,
                        graph: graph.graph,
                        datatypes: graph.datatypes
                    }));
                    self.loading(false);
                };
                this.setupReport = function(graphId, source) {
                    var graph = graphCache[graphId];
                    var tileData = {
                        "tiles": source.tiles,
                        "related_resources": [],
                        "displayname": source.displayname,
                        "resourceid": source.resourceinstanceid
                    };
                    self.loading(true);
                    if (graph) processReportData(
                        tileData,
                        graph
                    );
                    else {
                        $.getJSON(arches.urls.graphs_api + graphId, function(data) {
                            var graphModel = new GraphModel({
                                data: data.graph,
                                datatypes: data.datatypes
                            });

                            graph = {
                                graphModel: graphModel,
                                cards: data.cards,
                                graph: data.graph,
                                datatypes: data.datatypes,
                                cardwidgets: data.cardwidgets
                            };
                            graphCache[graphId] = graph;
                            processReportData(tileData, graph);
                        });
                    }
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
