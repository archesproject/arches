define([
    'jquery',
    'underscore',
    'knockout',
    'viewmodels/card',
    'arches',
    'graph-designer-data',
    'bindings/sortable',
    'bindings/scrollTo',
    'widgets',
    'card-components'
], function($, _, ko, CardViewModel, arches, data) {
    var CardTreeViewModel = function(params) {
        var self = this;
        var filter = ko.observable('');
        var loading = ko.observable(false);
        self.multiselect = params.multiselect || false;
        var selection;
        if (params.multiselect) {
            selection = ko.observableArray([]);
        } else {
            selection = ko.observable();
        }
        var hover = ko.observable();
        var scrollTo = ko.observable();

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
            var nodes = self.flattenTree(self.topCards(), []);
            _.each(nodes, function(node) {
                node.expanded(state);
            });
            if (state) {
                self.rootExpanded(true);
            }
        };

        var selectAll = function(state) {
            var nodes = self.flattenTree(self.topCards(), []);
            _.each(nodes, function(node) {
                if (node.selected() !== state) {
                    node.selected(true);
                }
            });
        };

        var expandToRoot = function(node) {
            //expands all nodes up to the root, but does not expand the root.
            var nodes = self.flattenTree(self.topCards(), []);
            if (node.parent) {
                node.parent.expanded(true);
                expandToRoot(node.parent);
            } else {
                node.expanded(true);
                _.each(nodes, function(n) {
                    if (node.parentnodegroup_id !== null && node.parentnodegroup_id === n.nodegroupid) {
                        expandToRoot(n);
                    }
                });
            }
        };

        var createLookup = function(list, idKey) {
            return _.reduce(list, function(lookup, item) {
                lookup[ko.unwrap(item[idKey])] = item;
                return lookup;
            }, {});
        };

        _.extend(this, {
            filterEnterKeyHandler: function(context, e) {
                if (e.keyCode === 13) {
                    var highlightedItems = _.filter(self.flattenTree(self.topCards(), []), function(item) {
                        return item.highlight && item.highlight();
                    });
                    var previousItem = scrollTo();
                    scrollTo(null);
                    if (highlightedItems.length > 0) {
                        var scrollIndex = 0;
                        var previousIndex = highlightedItems.indexOf(previousItem);
                        if (previousItem && highlightedItems[previousIndex+1]) {
                            scrollIndex = previousIndex + 1;
                        }
                        scrollTo(highlightedItems[scrollIndex]);
                    }
                    return false;
                }
                return true;
            },
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
            selectAllCards: function() {
                selectAll(true);
            },
            clearSelection: function() {
                selectAll(false);
            },
            expandToRoot: expandToRoot,
            rootExpanded: ko.observable(true),
            on: function() {
                return;
            },
            topCards: ko.observableArray(_.filter(data.cards, function(card) {
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
                    hover: hover,
                    scrollTo: scrollTo,
                    multiselect: self.multiselect,
                    loading: loading,
                    filter: filter,
                    provisionalTileViewModel: null,
                    cardwidgets: data.cardwidgets,
                    userisreviewer: true,
                    perms: ko.observableArray(),
                    permsLiteral: ko.observableArray()
                });
            })),
            beforeMove: function(e) {
                e.cancelDrop = (e.sourceParent!==e.targetParent);
            },
            updateCards: function(data) {
                self.topCards.removeAll();
                self.topCards(_.filter(data.cards, function(card) {
                    var nodegroup = _.find(ko.unwrap(params.graph.nodegroups), function(group) {
                        return ko.unwrap(group.nodegroupid) === card.nodegroup_id;
                    });
                    if (nodegroup) {
                        return !nodegroup || !ko.unwrap(nodegroup.parentnodegroup_id);
                    } else {
                        return true;
                    }
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
                        hover: hover,
                        scrollTo: scrollTo,
                        multiselect: self.multiselect,
                        loading: loading,
                        filter: filter,
                        provisionalTileViewModel: null,
                        cardwidgets: data.cardwidgets,
                        userisreviewer: true,
                        perms: ko.observableArray(),
                        permsLiteral: ko.observableArray()
                    });
                }));
            },
            reorderCards: function() {
                loading(true);
                var cards = _.map(self.topCards(), function(card, i) {
                    card.model.get('sortorder')(i);
                    return {
                        id: card.model.id,
                        name: card.model.get('name')(),
                        sortorder: i
                    };
                });
                $.ajax({
                    type: 'POST',
                    data: JSON.stringify({
                        cards: cards
                    }),
                    url: arches.urls.reorder_cards,
                    complete: function() {
                        loading(false);
                    }
                });
            },
            selection: selection,
            filter: filter
        });
        var topCard = self.topCards()[0];
        if (topCard != null) {
            if (self.multiselect === true) {
                selection.push(topCard.tiles().length > 0 ? topCard.tiles()[0] : topCard);
            } else {
                selection(topCard.tiles().length > 0 ? topCard.tiles()[0] : topCard);
            }
        }
    };
    return CardTreeViewModel;
});
