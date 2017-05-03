define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/search/base-filter',
    'arches',
    'datatype-config-components',
    'bindings/let'
], function(_, ko, koMapping, BaseFilter, arches) {
	return BaseFilter.extend({
		initialize: function(options) {
			var self = this;
			this.searchableGraphs = [];
			this.cards = options.cards;
			this.datatypelookup = {};
			this.facetFilterText = ko.observable('');
			_.each(options.datatypes, function(datatype) {
				self.datatypelookup[datatype.datatype] = datatype;
			});
			_.each(options.cards, function(card) {
				card.nodes = _.filter(options.nodes, function(node) {
					return node.nodegroup_id === card.nodegroup_id;
				});
				card.addFacet = function() {
					self.newFacet(card);
				};
			});
			_.each(options.graphs, function(graph) {
				if (graph.isresource && graph.isactive) {
					var graphCards = _.filter(options.cards, function(card) {
						return card.graph_id === graph.graphid && card.nodes.length > 0;
					});
					if (graphCards.length > 0) {
						_.each(graphCards, function(card) {
							card.getGraph = function() {
								return graph;
							};
						});
						graph.cards = ko.computed(function() {
							var facetFilterText = self.facetFilterText().toLowerCase();
							if (facetFilterText) {
								return _.filter(graphCards, function(card) {
									return card.name.toLowerCase().indexOf(facetFilterText) > -1;
								});
							} else {
								return graphCards;
							}
						});
						self.searchableGraphs.push(graph);
					}
				}
			});
			this.filter = {
				facets: ko.observableArray()
			};

			BaseFilter.prototype.initialize.call(this, options);
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

		appendFilters: function(filterParams) {
			var filtersApplied = this.filter.facets().length > 0;
			if (filtersApplied) {
				var facets = this.filter.facets();
				var advanced = [];
				_.each(facets, function(facet) {
					var value = koMapping.toJS(facet.value);

					advanced.push(value);
				});
				filterParams.advanced = JSON.stringify(advanced);
			}
			return filtersApplied;
		},

		restoreState: function(query) {
			var self = this;
			var doQuery = false;
			if ('advanced' in query) {
				var facets = JSON.parse(query.advanced);
				_.each(facets, function(facet) {
					var nodeIds = _.filter(Object.keys(facet), function(key) {
						return key !== 'op';
					});
					var card = _.find(self.cards, function(card) {
						var cardNodeIds = _.map(card.nodes, function(node) {
							return node.nodeid;
						});
						return _.contains(cardNodeIds, nodeIds[0]);
					});
					if (card) {
						_.each(card.nodes, function(node) {
							facet[node.nodeid] = ko.observable(facet[node.nodeid]);
						});
						facet.op = ko.observable(facet.op);
						self.filter.facets.push({
							card: card,
							value: facet
						});
						doQuery = true;
					}
				});
			}
			return doQuery;
		},

		clear: function() {
			this.filter.facets([]);
			return;
		}
	});
});
