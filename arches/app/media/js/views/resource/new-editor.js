define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/base-manager',
    'resource-editor-data',
    'bindings/resizable-sidepanel',
    'widgets'
], function(_, ko, koMapping, BaseManagerView, data) {
    var tiles = data.tiles;
    var filter = ko.observable('');
    var cardData = _.map(data.cards, function(card) {
        return _.extend(
            card,
            _.find(data.nodegroups, function(group) {
                return group.nodegroupid === card.nodegroup_id;
            }), {
                expanded: ko.observable(true),
                highlight: ko.computed(function() {
                    var filterText = filter();
                    if (!filterText) {
                        return false;
                    }
                    filterText = filterText.toLowerCase();
                    if (card.name.toLowerCase().indexOf(filterText) !== -1) {
                        return true;
                    }
                }, this),
                widgets: _.filter(data.cardwidgets, function (widget) {
                    return widget.card_id === card.cardid;
                })
            }
        );
    });
    var vm = {
        widgetLookup: _.reduce(data.widgets, function (lookup, widget) {
            lookup[widget.widgetid] = widget;
            return lookup
        }, {}),
        nodeLookup: _.reduce(data.nodes, function (lookup, node) {
            node.config = koMapping.fromJS(node.config)
            lookup[node.nodeid] = node;
            return lookup
        }, {}),
        graphid: data.graphid,
        graphname: data.graphname,
        graphiconclass: data.graphiconclass,
        displayname: ko.observable(data.displayname),
        expandAll: function() {
            toggleAll(true);
        },
        collapseAll: function() {
            toggleAll(false);
        },
        rootExpanded: ko.observable(true),
        filter: filter
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

    vm.topCards = _.filter(cardData, function(card) {
        if (!card.parentnodegroup_id) {
            card.tiles = ko.observable(
                _.filter(tiles, function(tile) {
                    return tile.nodegroup_id === card.nodegroup_id;
                })
            );
            card.expanded = ko.observable(true);
            return true;
        }
    });

    _.each(tiles, function(tile) {
        tile.cards = _.filter(cardData, function(card) {
            return card.parentnodegroup_id === tile.nodegroup_id;
        }).map(function(card) {
            return _.extend(_.clone(card), {
                expanded: ko.observable(true),
                tiles: ko.observableArray(
                    _.filter(tiles, function(childCandidate) {
                        return childCandidate.parenttile_id === tile.tileid &&
                            childCandidate.nodegroup_id === card.nodegroup_id;
                    })
                )
            });
        });
        tile.expanded = ko.observable(true);
    });

    return new BaseManagerView({
        viewModel: vm
    });
});
