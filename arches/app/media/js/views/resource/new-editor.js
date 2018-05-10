define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/base-manager',
    'resource-editor-data',
    'bindings/resizable-sidepanel',
    'widgets',
    'card-components'
], function(_, ko, koMapping, BaseManagerView, data) {
    var tiles = data.tiles;
    var filter = ko.observable('');
    var selection = ko.observable();
    var cards = _.map(data.cards, function(card) {
        return _.extend(
            card,
            _.find(data.nodegroups, function(group) {
                return group.nodegroupid === card.nodegroup_id;
            }), {
                widgets: _.filter(data.cardwidgets, function (widget) {
                    return widget.card_id === card.cardid;
                }),
                nodes: _.filter(data.nodes, function (node) {
                    return node.nodegroup_id === card.nodegroup_id;
                }).map(function (node) {
                    node.configKeys = ko.observableArray(
                        _.map(node.config, function (val, key) {
                            return key
                        })
                    );
                    node.config = koMapping.fromJS(node.config);
                    return node;
                })
            }
        );
    });

    var setupCard = function (card, parent) {
        return _.extend(card, {
            parent: parent,
            expanded: ko.observable(true),
            highlight: ko.computed(function() {
                var filterText = filter();
                if (!filterText) {
                    return false;
                }
                filterText = filterText.toLowerCase();
                if (card.name.toLowerCase().indexOf(filterText) > -1) {
                    return true;
                }
            }, this),
            tiles: ko.observableArray(
                _.filter(tiles, function(tile) {
                    return (
                        parent ? (tile.parenttile_id === parent.tileid) : true
                    ) && tile.nodegroup_id === card.nodegroup_id;
                }).map(function (tile) {
                    return setupTile(tile, card);
                })
            ),
            selected: ko.computed(function () {
                return selection() === card;
            }, this)
        });
    };

    var setupTile = function(tile, parent) {
        return _.extend(tile, {
            parent: parent,
            cards: _.filter(cards, function(card) {
                return card.parentnodegroup_id === tile.nodegroup_id;
            }).map(function(card) {
                return setupCard(_.clone(card), tile);
            }),
            expanded: ko.observable(true),
            selected: ko.computed(function () {
                return selection() === tile;
            }, this),
            data: koMapping.fromJS(tile.data),
            formData: new FormData()
        });
    };

    var toggleAll = function(state) {
        var nodes = _.reduce(
            tiles,
            function(nodeList, tile) {
                nodeList.push(tile);
                return nodeList.concat(tile.cards);
            }, [{
                expanded: vm.rootExpanded
            }].concat(vm.topCards)
        );
        _.each(nodes, function(node) {
            node.expanded(state);
        });
    };
    var createLookup = function (list, idKey) {
        return _.reduce(list, function (lookup, item) {
            lookup[item[idKey]] = item;
            return lookup
        }, {});
    };
    var vm = {
        widgetLookup: createLookup(data.widgets, 'widgetid'),
        cardComponentLookup: createLookup(data.cardComponents, 'componentid'),
        nodeLookup: createLookup(data.nodes, 'nodeid'),
        graphid: data.graphid,
        graphname: data.graphname,
        graphiconclass: data.graphiconclass,
        graph: {
            graphid: data.graphid,
            name: data.graphname,
            iconclass: data.graphiconclass,
        },
        displayname: ko.observable(data.displayname),
        expandAll: function() {
            toggleAll(true);
        },
        collapseAll: function() {
            toggleAll(false);
        },
        rootExpanded: ko.observable(true),
        topCards: _.filter(cards, function(card) {
            return !card.parentnodegroup_id
        }).map(function (card) {
            return setupCard(card, null);
        }),
        selection: selection,
        selectedTile: ko.computed(function () {
            var item = selection();
            if (item && item.tileid) {
                return item;
            }
        }),
        selectedCard: ko.computed(function () {
            var item = selection();
            if (item) {
                if (item.tileid) {
                    return item.parent;
                }
                return item;
            }
        }),
        filter: filter
    };

    return new BaseManagerView({
        viewModel: vm
    });
});
