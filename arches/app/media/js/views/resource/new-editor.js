define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/base-manager',
    'viewmodels/alert',
    'arches',
    'resource-editor-data',
    'bindings/resizable-sidepanel',
    'bindings/sortable',
    'widgets',
    'card-components'
], function($, _, ko, koMapping, BaseManagerView, AlertViewModel, arches, data) {
    var handlers = {
        'after-update': [],
        'tile-reset': []
    };
    var tiles = data.tiles;
    var filter = ko.observable('');
    var loading = ko.observable(false);
    var selection = ko.observable();
    var resourceId = ko.observable(data.resourceid);

    var updateDisplayName = function () {
        $.get(
            arches.urls.resource_descriptors + resourceId(),
            function (descriptors) {
                vm.displayname(descriptors.displayname);
            }
        );
    };

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

    var isChildSelected = function (parent) {
        var childSelected = false;
        var childKey = parent.tiles ? 'tiles' : 'cards';
        ko.unwrap(parent[childKey]).forEach(function(child) {
            if (child.selected() || isChildSelected(child)){
                childSelected = true;
            }
        });
        return childSelected;
    };

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
            }, this),
            isChildSelected: ko.computed(function() {
                return isChildSelected(card);
            }, this)
        });
    };

    var setupTile = function(tile, parent) {
        tile._tileData = ko.observable(
            koMapping.toJSON(tile.data)
        );
        tile.data = koMapping.fromJS(tile.data);

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
            isChildSelected: ko.computed(function() {
                return isChildSelected(tile);
            }, this),
            formData: new FormData(),
            dirty: ko.computed(function () {
                return tile._tileData() !== koMapping.toJSON(tile.data);
            }, this),
            reset: function () {
                ko.mapping.fromJS(
                    JSON.parse(tile._tileData()),
                    tile.data
                );
                _.each(handlers['tile-reset'], function (handler) {
                    handler(tile);
                });
            },
            getAttributes: function () {
                var tileData = tile.data ? koMapping.toJS(tile.data) : {};
                return {
                    "tileid": tile.tileid,
                    "data": tileData,
                    "nodegroup_id": tile.nodegroup_id,
                    "parenttile_id": tile.parenttile_id,
                    "resourceinstance_id": tile.resourceinstance_id
                }
            },
            getData: function () {
                var children = {};
                if (tile.cards) {
                    children = _.reduce(tile.cards, function (tiles, card) {
                        return tiles.concat(card.tiles());
                    }, []).reduce(function (tileLookup, child) {
                        tileLookup[child.tileid] = child.getData();
                        return tileLookup;
                    }, {});
                }
                return _.extend(tile.getAttributes(), {
                    "tiles": children
                });
            },
            save: function () {
                loading(true);
                delete tile.formData.data;
                tile.formData.append(
                    'data',
                    JSON.stringify(
                        tile.getData()
                    )
                );

                $.ajax({
                    type: "POST",
                    url: arches.urls.tile,
                    processData: false,
                    contentType: false,
                    data: tile.formData
                }).done(function(tileData, status, req) {
                    ko.mapping.fromJS(tileData.data,tile.data);
                    tile._tileData(koMapping.toJSON(tile.data));
                    if (!tile.tileid) {
                        tile.tileid = tileData.tileid;
                        tile.parent.tiles.unshift(tile);
                        vm.selection(tile);
                    }
                    if (!resourceId()) {
                        tile.resourceinstance_id = tileData.resourceinstance_id;
                        resourceId(tile.resourceinstance_id);
                    }
                    _.each(handlers['after-update'], function (handler) {
                        handler(req, tile);
                    });
                    updateDisplayName();
                }).fail(function(response) {
                    console.log('there was an error ', response);
                }).always(function(){
                    loading(false);
                });
            },
            deleteTile: function() {
                loading(true);
                $.ajax({
                    type: "DELETE",
                    url: arches.urls.tile,
                    data: JSON.stringify(tile.getData())
                }).done(function(response) {
                    parent.tiles.remove(tile);
                    selection(parent);
                }).fail(function(response) {
                    console.log('there was an error ', response);
                }).always(function(){
                    loading(false);
                });
            }
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
        loading: loading,
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
            if (item) {
                if (item.tileid) {
                    return item;
                }
                return setupTile({
                    tileid: '',
                    resourceinstance_id: resourceId(),
                    nodegroup_id: item.nodegroup_id,
                    parenttile_id: item.parent ? item.parent.tileid : null,
                    data: _.reduce(item.widgets, function (data, widget) {
                        data[widget.node_id] = null;
                        return data;
                    }, {})
                }, item);
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
        filter: filter,
        on: function (eventName, handler) {
            if (handlers[eventName]) {
                handlers[eventName].push(handler);
            }
        },
        beforeMove: function (e) {
            e.cancelDrop = (e.sourceParent!==e.targetParent);
        },
        reorderTiles: function (e) {
            loading(true);
            var tiles = _.map(e.sourceParent(), function(tile) {
                return tile.getAttributes();
            });
            $.ajax({
                type: "POST",
                data: JSON.stringify({
                    tiles: tiles
                }),
                url: arches.urls.reorder_tiles,
                complete: function(response) {
                    loading(false);
                    updateDisplayName();
                }
            });
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
