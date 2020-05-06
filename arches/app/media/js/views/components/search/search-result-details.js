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
], function($, _, ko, arches, ReportModel, GraphModel, CardModel, CardViewModel, reportLookup, BaseFilter) {
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

                var graphCache = {};
                this.setupReport = function(resId, graphId) {
                    var qs = '?json=True';
                    var graph = graphCache[graphId];
                    if (graph) qs += '&exclude_graph=True';
                    self.loading(true);
                    $.getJSON(arches.urls.resource_report + resId + qs, function(data) {
                        if (!graph) {
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
                        }

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
                        self.report = new ReportModel(_.extend(data, {
                            graphModel: graph.graphModel,
                            graph: graph.graph,
                            datatypes: graph.datatypes
                        }));
                        self.loading(false);
                    });
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
