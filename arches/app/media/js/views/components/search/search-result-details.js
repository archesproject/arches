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
                this.ready = ko.observable(false);
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

                this.setupReport = function(id) {
                    self.loading(true);
                    $.getJSON(arches.urls.resource_report + id + '?json=True', function(data) {
                        data.graph = JSON.parse(data.graph);
                        data.cards = JSON.parse(data.cards);
                        data.tiles = JSON.parse(data.tiles);
                        data.cardwidgets = JSON.parse(data.cardwidgets);
                        var graphModel = new GraphModel({
                            data: data.graph,
                            datatypes: data.datatypes,
                            'ontology_namespaces': data['ontology_namespaces']
                        });

                        var cards = _.filter(data.cards, function(card) {
                            var nodegroup = _.find(data.graph.nodegroups, function(group) {
                                return group.nodegroupid === card.nodegroup_id;
                            });
                            return !nodegroup || !nodegroup.parentnodegroup_id;
                        }).map(function(card) {
                            return new CardViewModel({
                                card: card,
                                graphModel: graphModel,
                                resourceId: data.resourceid,
                                displayname: data.displayname,
                                cards: data.cards,
                                tiles: data.tiles,
                                cardwidgets: data.cardwidgets
                            });
                        });

                        self.reportLookup = reportLookup;
                        self.graph = data.graph;

                        var createLookup = function(list, idKey) {
                            return _.reduce(list, function(lookup, item) {
                                lookup[item[idKey]] = item;
                                return lookup;
                            }, {});
                        };
                        self.widgetLookup = createLookup(data.widgets, 'widgetid');
                        self.cardComponentLookup = createLookup(data.cardComponents, 'componentid');
                        self.nodeLookup = createLookup(graphModel.get('nodes')(), 'nodeid');

                        self.report = new ReportModel(_.extend(data, {graphModel: graphModel, cards: cards}));
                        self.ready(true);
                        self.loading(false);
                    });
                };
            }
        }),
        template: { require: 'text!templates/views/components/search/search-result-details.htm'}
    });
});
