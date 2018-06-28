define([
    'jquery',
    'underscore',
    'knockout',
    'moment',
    'views/base-manager',
    'viewmodels/alert',
    'viewmodels/card',
    'viewmodels/new-provisional-tile',
    'arches',
    'resource-editor-data',
    'bindings/resizable-sidepanel',
    'bindings/sortable',
    'widgets',
    'card-components'
], function($, _, ko, moment, BaseManagerView, AlertViewModel, CardViewModel, ProvisionalTileViewModel, arches, data) {
    var handlers = {
        'after-update': [],
        'tile-reset': []
    };
    var tiles = data.tiles;
    var filter = ko.observable('');
    var loading = ko.observable(false);
    var selection = ko.observable();
    var displayname = ko.observable(data.displayname);
    var resourceId = ko.observable(data.resourceid);
    var selectedTile = ko.computed(function () {
        var item = selection();
        if (item) {
            if (item.tileid) {
                return item;
            }
            return item.getNewTile();
        }
    });
    var provisionalTileViewModel = new ProvisionalTileViewModel({tile: selectedTile, reviewer: data.user_is_reviewer});

    var cards = data.cards;

    var flattenTree = function (parents, flatList) {
        _.each(ko.unwrap(parents), function(parent) {
            flatList.push(parent);
            var childrenKey = parent.tiles ? 'tiles' : 'cards';
            flattenTree(
                ko.unwrap(parent[childrenKey]),
                flatList
            );
        });
        return flatList
    };

    var toggleAll = function(state) {
        var nodes = flattenTree(vm.topCards, []).concat([{
            expanded: vm.rootExpanded
        }]);
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
        loading: loading,
        widgetLookup: createLookup(data.widgets, 'widgetid'),
        cardComponentLookup: createLookup(data.cardComponents, 'componentid'),
        nodeLookup: createLookup(data.nodes, 'nodeid'),
        graphid: data.graphid,
        graphname: data.graphname,
        reviewer: data.userisreviewer,
        graphiconclass: data.graphiconclass,
        graph: {
            graphid: data.graphid,
            name: data.graphname,
            iconclass: data.graphiconclass,
        },
        displayname: displayname,
        expandAll: function() {
            toggleAll(true);
        },
        collapseAll: function() {
            toggleAll(false);
        },
        rootExpanded: ko.observable(true),
        topCards: _.filter(data.cards, function(card) {
            var nodegroup = _.find(data.nodegroups, function(group) {
                return group.nodegroupid === card.nodegroup_id;
            })
            return !nodegroup || !nodegroup.parentnodegroup_id;
        }).map(function (card) {
            return new CardViewModel({
                card: card,
                tile: null,
                resourceId: resourceId,
                displayname: displayname,
                handlers: handlers,
                cards: data.cards,
                tiles: tiles,
                selection: selection,
                loading: loading,
                filter: filter,
                provisionalTileViewModel: provisionalTileViewModel,
                nodes: data.nodes,
                cardwidgets: data.cardwidgets,
                datatypes: data.datatypes,
                widgets: data.widgets,
                nodegroups: data.nodegroups,
                userisreviewer: data.userisreviewer
            });
        }),
        selection: selection,
        selectedTile: selectedTile,
        selectedCard: ko.computed(function () {
            var item = selection();
            if (item) {
                if (item.tileid) {
                    return item.parent;
                }
                return item;
            }
        }),
        provisionalTileViewModel: provisionalTileViewModel,
        filter: filter,
        on: function (eventName, handler) {
            if (handlers[eventName]) {
                handlers[eventName].push(handler);
            }
        },
        resourceId: resourceId,
        copyResource: function () {
            if (resourceId()) {
                vm.menuActive(false);
                loading(true);
                $.ajax({
                    type: "GET",
                    url: arches.urls.resource_copy.replace('//', '/' + resourceId() + '/'),
                    success: function(response) {
                        vm.alert(new AlertViewModel('ep-alert-blue', arches.resourceCopySuccess.title, '', null, function(){}));
                    },
                    error: function(response) {
                        vm.alert(new AlertViewModel('ep-alert-red', arches.resourceCopyFailed.title, arches.resourceCopyFailed.text, null, function(){}));
                    },
                    complete: function (request, status) {
                        loading(false);
                    },
                });
            }
        },
        deleteResource: function () {
            if (resourceId()) {
                vm.menuActive(false);
                vm.alert(new AlertViewModel('ep-alert-red', arches.confirmResourceDelete.title, arches.confirmResourceDelete.text, function() {
                    return;
                }, function(){
                    loading(true);
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.resource_editor + resourceId(),
                        success: function(response) {

                        },
                        error: function(response) {

                        },
                        complete: function (request, status) {
                            loading(false);
                            if (status === 'success') {
                                vm.navigate(arches.urls.resource);
                            }
                        },
                    });
                }));
            }
        },
        deleteTile: function (tile) {
            tile.deleteTile(function (response) {
                vm.alert(new AlertViewModel('ep-alert-red', response.responseJSON.message[0], response.responseJSON.message[1], null, function(){}));
            });
        },
        saveTile: function (tile) {
            tile.save(function (response) {
                vm.alert(new AlertViewModel('ep-alert-red', response.responseJSON.message[0], response.responseJSON.message[1], null, function(){}));
            });
        },
        viewEditHistory: function () {
            if (resourceId()) {
                vm.menuActive(false);
                vm.navigate(arches.urls.get_resource_edit_log(resourceId()));
            }
        },
        viewReport: function () {
            if (resourceId()) {
                vm.menuActive(false);
                vm.navigate(arches.urls.resource_report + resourceId());
            }
        }
    };
    var topCard = vm.topCards[0];
    selection(topCard.tiles().length > 0 ? topCard.tiles()[0] : topCard);

    vm.selectionBreadcrumbs = ko.computed(function () {
        var item = vm.selectedTile()
        var crumbs = [];
        if (item) {
            while (item.parent) {
                item = item.parent;
                crumbs.unshift(item);
            }
        }
        return crumbs;
    });

    return new BaseManagerView({
        viewModel: vm
    });
});
