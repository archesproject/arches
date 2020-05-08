define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'models/report',
    'models/graph',
    'models/card',
    'viewmodels/card',
    'report-templates',
    'views/components/search/base-filter',
    'card-components',
    'bindings/chosen'
], function($, _, ko, arches, ReportModel, GraphModel, CardModel, CardViewModel, reportLookup, BaseFilter, cardComponents) {
    var componentName = 'search-result-details';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                var self = this;
                options.name = 'Search Result Details';
                BaseFilter.prototype.initialize.call(this, options);
                this.loading = ko.observable(false);
                this.options = options;
                this.report = null;

                var loaded = ko.computed(function(){
                    return this.getFilter('search-results');
                }, this);
                loaded.subscribe(function(loaded) {
                    if (loaded) {
                        options.searchResultsVm = this.getFilter('search-results');
                        options.filters[componentName](this);
                    }
                }, this);

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
                this.setupReport = function(resId, graphId, source) {
                    var qs = '?json=True';
                    var graph = graphCache[graphId];
                    self.loading(true);
                    if (graph) processReportData(
                        {
                            "tiles": source.tiles,
                            "related_resources": [],
                            "displayname": source.displayname,
                            "resourceid": source.resourceinstanceid
                        },
                        graph
                    );
                    else {
                        $.getJSON(arches.urls.resource_report + resId + qs, function(data) {
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
                            processReportData(data, graph);
                        });
                    }
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
