define([
    'underscore',
    'knockout',
    'views/base-manager',
    'resource-editor-data',
    'bindings/resizable-sidepanel'
], function(_, ko, BaseManagerView, data) {
    var tiles = data.tiles;
    var cardData = _.map(data.cards, function(card) {
        return _.extend(
            card,
            _.find(data.nodegroups, function(group) {
                return group.nodegroupid === card.nodegroup_id;
            }), {
                expanded: ko.observable(true)
            }
        );
        return cards;
    });
    var vm = {
        graphid: data.graphid,
        graphiconclass: data.graphiconclass,
        displayname: ko.observable(data.displayname),
        expandAll: function() {
            toggleAll(true)
        },
        collapseAll: function() {
            toggleAll(false)
        },
        rootExpanded: ko.observable(true)
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
        _.each(
            nodes,
            function(node) {
                node.expanded(state);
            }
        );
    };

    vm.topCards = _.filter(cardData, function(card) {
        card.children = _.filter(cardData, function(candidateChild) {
            return candidateChild.parentnodegroup_id === card.nodegroup_id;
        });
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
