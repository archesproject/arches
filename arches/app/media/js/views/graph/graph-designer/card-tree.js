define([
    'jquery',
    'underscore',
    'knockout',
    'viewmodels/card',
    'arches',
    'graph-designer-data',
    'bindings/sortable',
    'widgets',
    'card-components'
], function($, _, ko, CardViewModel, arches, data) {
    var CardTreeViewModel = function(params) {
        var self = this;
        var filter = ko.observable('');
        var loading = ko.observable(false);
        var selection = ko.observable();

        this.flattenTree = function(parents, flatList) {
            _.each(ko.unwrap(parents), function(parent) {
                flatList.push(parent);
                self.flattenTree(
                    ko.unwrap(parent.cards),
                    flatList
                );
            }, this);
            return flatList;
        };

        var toggleAll = function(state) {
            var nodes = self.flattenTree(self.topCards, []).concat([{
                expanded: self.rootExpanded
            }]);
            _.each(nodes, function(node) {
                node.expanded(state);
            });
        };

        var createLookup = function(list, idKey) {
            return _.reduce(list, function(lookup, item) {
                lookup[ko.unwrap(item[idKey])] = item;
                return lookup;
            }, {});
        };
        _.extend(this, {
            loading: loading,
            widgetLookup: createLookup(data.widgets, 'widgetid'),
            cardComponentLookup: createLookup(data.cardComponents, 'componentid'),
            nodeLookup: createLookup(params.graphModel.get('nodes')(), 'nodeid'),
            graphid: params.graph.graphid,
            graphname: params.graph.name,
            graphiconclass: params.graph.iconclass,
            graph: params.graph,
            expandAll: function() {
                toggleAll(true);
            },
            collapseAll: function() {
                toggleAll(false);
            },
            rootExpanded: ko.observable(true),
            on: function() {
                return;
            },
            topCards: _.filter(data.cards, function(card) {
                var nodegroup = _.find(ko.unwrap(params.graph.nodegroups), function(group) {
                    return ko.unwrap(group.nodegroupid) === card.nodegroup_id;
                });
                return !nodegroup || !ko.unwrap(nodegroup.parentnodegroup_id);
            }).map(function(card) {
                return new CardViewModel({
                    card: card,
                    graphModel: params.graphModel,
                    tile: null,
                    resourceId: ko.observable(),
                    displayname: ko.observable(),
                    handlers: {},
                    cards: data.cards,
                    tiles: [],
                    selection: selection,
                    loading: loading,
                    filter: filter,
                    provisionalTileViewModel: null,
                    cardwidgets: data.cardwidgets,
                    userisreviewer: true,
                    perms: ko.observableArray(),
                    permsLiteral: ko.observableArray()
                });
            }),
            selection: selection,
            filter: filter
        });
        var topCard = self.topCards[0];
        if (topCard != null) {
            selection(topCard.tiles().length > 0 ? topCard.tiles()[0] : topCard);
        }
    };
    return CardTreeViewModel;
});
