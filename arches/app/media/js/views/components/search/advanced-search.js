define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/components/search/base-filter',
    'arches',
    'datatype-config-components',
    'bindings/let'
], function($, _, ko, koMapping, BaseFilter, arches) {
    var componentName = 'advanced-search';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({
            initialize: function(options) {
                var self = this;
                options.name = 'Advanced Search Filter';
                BaseFilter.prototype.initialize.call(this, options);
                this.tagId = "Advanced Search";
                this.searchableGraphs = ko.observableArray();
                this.datatypelookup = {};
                this.facetFilterText = ko.observable('');
                this.filter = {
                    facets: ko.observableArray()
                };
                this.cardNameDict = {};
                var createLookup = function(list, idKey) {
                    return _.reduce(list, function(lookup, item) {
                        lookup[item[idKey]] = item;
                        return lookup;
                    }, {});
                };
                self.widgetLookup = null;

                $.ajax({
                    type: "GET",
                    url: arches.urls.api_search_component_data + componentName,
                    context: this
                }).done(function(response) {
                    this.cards = response.cards;
                    _.each(response.datatypes, function(datatype) {
                        this.datatypelookup[datatype.datatype] = datatype;
                    }, this);
                    self.widgetLookup = createLookup(
                        response.cardwidgets,
                        'node_id'
                    );
                    _.each(response.cards, function(card) {
                        self.cardNameDict[card.nodegroup_id] = card.name;
                        card.nodes = _.filter(response.nodes, function(node) {
                            return node.nodegroup_id === card.nodegroup_id;
                        });
                        card.addFacet = function() {
                            _.each(card.nodes, function(node) {
                                if (self.cardNameDict[node.nodegroup_id] && node.nodeid === node.nodegroup_id) {
                                    node.label = self.cardNameDict[node.nodegroup_id];
                                } else if (node.nodeid !== node.nodegroup_id && self.widgetLookup[node.nodeid]) {
                                    const widget = self.widgetLookup[node.nodeid];
                                    node.label = widget.label;
                                    node.sortorder = widget.sortorder;
                                } else {
                                    node.label = node.name;
                                }
                            }).sort((a, b) => a.sortorder - b.sortorder);
                            self.newFacet(card);
                        };
                    }, this);
                    var graphs = response.graphs.sort(function(a,b) {
                        return a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1;});
                    _.each(graphs, function(graph) {
                        if (graph.isresource && graph.isactive) {
                            var graphCards = _.filter(response.cards, function(card) {
                                return card.graph_id === graph.graphid && card.nodes.length > 0;
                            });
                            graphCards.sort(function(a,b) {
                                return a.name.toLowerCase() > b.name.toLowerCase() ? 1 : -1;});
                            if (graphCards.length > 0) {
                                _.each(graphCards, function(card) {
                                    card.getGraph = function() {
                                        return graph;
                                    };
                                });
                                graph.collapsed = ko.observable(true);
                                graph.cards = ko.computed(function() {
                                    var facetFilterText = this.facetFilterText().toLowerCase();
                                    if (facetFilterText) {
                                        graph.collapsed(false);
                                        return _.filter(graphCards, function(card) {
                                            return card.name.toLowerCase().indexOf(facetFilterText) > -1;
                                        });
                                    } else {
                                        return graphCards;
                                    }
                                }, this);
                                this.searchableGraphs.push(graph);
                            }
                        }
                    }, this);
                    this.restoreState();

                    var filterUpdated = ko.computed(function() {
                        return JSON.stringify(ko.toJS(this.filter.facets()));
                    }, this);
                    filterUpdated.subscribe(function() {
                        this.updateQuery();
                    }, this);

                    options.loading(false);
                });

                this.filters[componentName](this);
            },

            updateQuery: function() {
                var queryObj = this.query();
                var filtersApplied = this.filter.facets().length > 0;
                if (filtersApplied) {
                    var facets = this.filter.facets();
                    var advanced = [];
                    _.each(facets, function(facet) {
                        var value = koMapping.toJS(facet.value);
                        advanced.push(value);
                    });
                    queryObj[componentName] = JSON.stringify(advanced);

                    if (this.getFilter('term-filter').hasTag(this.tagId) === false) {
                        this.getFilter('term-filter').addTag(this.tagId, this.name, ko.observable(false));
                    }
                } else {
                    delete queryObj[componentName];
                    this.getFilter('term-filter').removeTag(this.tagId);
                }
                this.query(queryObj);
            },

            newFacet: function(card) {
                var facet = {
                    card: card,
                    value: {
                        op: ko.observable('and')
                    }
                };
                _.each(facet.card.nodes, function(node) {
                    facet.value[node.nodeid] = ko.observable({});
                });
                this.filter.facets.push(facet);
            },

            restoreState: function() {
                var query = this.query();
                if (componentName in query) {
                    var facets = JSON.parse(query[componentName]);

                    if (facets.length > 0) {
                        this.getFilter('term-filter').addTag("Advanced Search", this.name, ko.observable(false));    
                    }
                    _.each(facets, function(facet) {
                        var nodeIds = _.filter(Object.keys(facet), function(key) {
                            return key !== 'op';
                        });
                        var card = _.find(this.cards, function(card) {
                            var cardNodeIds = _.map(card.nodes, function(node) {
                                return node.nodeid;
                            });
                            return _.contains(cardNodeIds, nodeIds[0]);
                        }, this);
                        if (card) {
                            _.each(card.nodes, function(node) {
                                facet[node.nodeid] = ko.observable(facet[node.nodeid]);
                            });
                            facet.op = ko.observable(facet.op);
                            this.filter.facets.push({
                                card: card,
                                value: facet
                            });
                        }
                    }, this);
                }
            },

            clear: function() {
                this.filter.facets.removeAll();
            }
        }),
        template: { require: 'text!templates/views/components/search/advanced-search.htm' }
    });
});
