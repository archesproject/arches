define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches'
], function($, _, ko, koMapping, arches) {
    /**
    * A viewmodel used for generic cards
    *
    * @constructor
    * @name CardViewModel
    *
    * @param  {string} params - a configuration object
    */
    var isChildSelected = function (parent) {
        var childSelected = false;
        var childrenKey = parent.tiles ? 'tiles' : 'cards';
        ko.unwrap(parent[childrenKey]).forEach(function(child) {
            if (child.selected() || isChildSelected(child)){
                childSelected = true;
            }
        });
        return childSelected;
    };

    var doesChildHaveProvisionalEdits = function(parent) {
        var hasEdits = false;
        var childrenKey = parent.tiles ? 'tiles' : 'cards';
        ko.unwrap(parent[childrenKey]).forEach(function(child) {
            if (child.hasprovisionaledits() || doesChildHaveProvisionalEdits(child)){
                hasEdits = true;
            }
        });
        return hasEdits;
    };

    var TileViewModel = function(params) {
        var self = this;
        var selection = params.selection || ko.observable();
        var filter = params.filter || ko.observable();
        var loading = params.loading || ko.observable();

        _.extend(this, params.tile)

        this._tileData = ko.observable(
            koMapping.toJSON(params.tile.data)
        );

        this.data = koMapping.fromJS(params.tile.data);
        this.provisionaledits = ko.observable(params.tile.provisionaledits);

        _.extend(this, {
            parent: params.card,
            cards: _.filter(params.cards, function(card) {
                var nodegroup = _.find(params.nodegroups, function(group) {
                    return group.nodegroupid === card.nodegroup_id;
                })
                return nodegroup.parentnodegroup_id === self.nodegroup_id;
            }).map(function(card) {
                var cardVM = new CardViewModel({
                    card: _.clone(card),
                    tile: self,
                    resourceId: params.resourceId,
                    handlers: params.handlers,
                    cards: params.cards,
                    tiles: params.tiles,
                    selection: selection,
                    loading: loading,
                    filter: filter,
                    provisionalTileViewModel: params.provisionalTileViewModel,
                    nodes: params.nodes,
                    cardwidgets: params.cardwidgets,
                    datatypes: params.datatypes,
                    widgets: params.widgets,
                    nodegroups: params.nodegroups
                });
                return cardVM;
            }),
            expanded: ko.observable(true),
            hasprovisionaledits: ko.computed(function () {
                return !!self.provisionaledits();
            }, this),
            selected: ko.pureComputed({
                read: function () {
                    return selection() === this;
                },
                write: function (value) {
                    if (value) {
                        selection(this);
                    }
                },
                owner: this
            }),
            formData: new FormData(),
            dirty: ko.computed(function () {
                return this._tileData() !== koMapping.toJSON(this.data);
            }, this),
            reset: function () {
                ko.mapping.fromJS(
                    JSON.parse(self._tileData()),
                    self.data
                );
                _.each(params.handlers['tile-reset'], function (handler) {
                    handler(self);
                });
                params.provisionalTileViewModel.selectedProvisionalEdit(undefined);
            },
            getAttributes: function () {
                var tileData = self.data ? koMapping.toJS(self.data) : {};
                var tileProvisionalEdits = self.provisionaledits ? koMapping.toJS(self.provisionaledits) : {};
                return {
                    "tileid": self.tileid,
                    "data": tileData,
                    "nodegroup_id": self.nodegroup_id,
                    "parenttile_id": self.parenttile_id,
                    "resourceinstance_id": self.resourceinstance_id,
                    "provisionaledits": tileProvisionalEdits
                }
            },
            getData: function () {
                var children = {};
                if (self.cards) {
                    children = _.reduce(self.cards, function (tiles, card) {
                        return tiles.concat(card.tiles());
                    }, []).reduce(function (tileLookup, child) {
                        tileLookup[child.tileid] = child.getData();
                        return tileLookup;
                    }, {});
                }
                return _.extend(self.getAttributes(), {
                    "tiles": children
                });
            },
            save: function () {
                loading(true);
                delete self.formData.data;
                if (params.provisionalTileViewModel.selectedProvisionalEdit()) {
                    params.provisionalTileViewModel.acceptProvisionalEdit();
                };
                self.formData.append(
                    'data',
                    JSON.stringify(
                        self.getData()
                    )
                );

                $.ajax({
                    type: "POST",
                    url: arches.urls.tile,
                    processData: false,
                    contentType: false,
                    data: self.formData
                }).done(function(tileData, status, req) {
                    if (self.tileid) {
                        koMapping.fromJS(tileData.data,tile.data);
                        koMapping.fromJS(tileData.provisionaledits,tile.provisionaledits);
                    } else {
                        self.data = koMapping.fromJS(tileData.data);
                    }
                    self._tileData(koMapping.toJSON(self.data));
                    if (!self.tileid) {
                        self.tileid = tileData.tileid;
                        self.parent.tiles.unshift(self);
                        self.parent.expanded(true);
                        selection(self);
                    }
                    if (data.userisreviewer === false && !self.provisionaledits()) {
                        //If the user is provisional ensure their edits are provisional
                        self.provisionaledits(self.data);
                    };
                    if (data.userisreviewer === true && params.provisionalTileViewModel.selectedProvisionalEdit()) {
                        if (JSON.stringify(params.provisionalTileViewModel.selectedProvisionalEdit().value) === koMapping.toJSON(self.data)) {
                            params.provisionalTileViewModel.removeSelectedProvisionalEdit();
                        };
                    };
                    if (!params.resourceId()) {
                        self.resourceinstance_id = tileData.resourceinstance_id;
                        params.resourceId(self.resourceinstance_id);
                    }
                    _.each(params.handlers['after-update'], function (handler) {
                        handler(req, self);
                    });
                    updateDisplayName();
                }).fail(function(response) {
                }).always(function(){
                    loading(false);
                });
            },
            deleteTile: function(onFail) {
                loading(true);
                $.ajax({
                    type: "DELETE",
                    url: arches.urls.tile,
                    data: JSON.stringify(self.getData())
                }).done(function(response) {
                    params.card.tiles.remove(self);
                    selection(params.card);
                }).fail(function(response) {
                    if (typeof onFail === 'function') {
                        onFail(response);
                    }
                    // vm.alert(new AlertViewModel('ep-alert-red', response.responseJSON.message[0], response.responseJSON.message[1], null, function(){}));
                }).always(function(){
                    loading(false);
                });
            }
        });
        this.isChildSelected = ko.computed(function() {
            return isChildSelected(this);
        }, this);
        this.doesChildHaveProvisionalEdits = ko.computed(function() {
            return doesChildHaveProvisionalEdits(this);
        }, this);
    };

    var CardViewModel = function(params) {
        var self = this;
        var selection = params.selection || ko.observable();
        var filter = params.filter || ko.observable();
        var loading = params.loading || ko.observable();
        var nodes = _.filter(params.nodes, function (node) {
            return node.nodegroup_id === params.card.nodegroup_id;
        }).map(function (node) {
            node.configKeys = ko.observableArray(
                _.map(node.config, function (val, key) {
                    return key
                })
            );
            node.config = koMapping.fromJS(node.config);
            return node;
        });
        var widgets = _.filter(params.cardwidgets, function (widget) {
            return widget.card_id === params.card.cardid;
        });
        _.each(nodes, function (node) {
            var widget = _.find(widgets, function (widget) {
                return widget.node_id === node.nodeid
            });
            if (!widget) {
                var datatype = _.find(params.datatypes, function (datatype) {
                    return datatype.datatype === node.datatype;
                });
                if (datatype.defaultwidget_id) {
                    var widgetData = _.find(params.widgets, function (widget) {
                        return widget.widgetid === datatype.defaultwidget_id;
                    });
                    widgets.push({
                        widget_id: datatype.defaultwidget_id,
                        config: _.extend({
                            label: node.name
                        }, widgetData.defaultconfig),
                        label: node.name,
                        node_id: node.nodeid,
                        card_id: params.card.cardid,
                        id: '',
                        sortorder: ''
                    });
                }
            }
        });
        var nodegroup = _.find(params.nodegroups, function(group) {
            return group.nodegroupid === params.card.nodegroup_id;
        });

        var tiles = ko.observableArray(
            _.filter(params.tiles, function(tile) {
                return (
                    params.tile ? (tile.parenttile_id === params.tile.tileid) : true
                ) && tile.nodegroup_id === params.card.nodegroup_id;
            }).map(function (tile) {
                var tileVM = new TileViewModel({
                    tile: tile,
                    card: self,
                    resourceId: params.resourceId,
                    handlers: params.handlers,
                    cards: params.cards,
                    tiles: params.tiles,
                    provisionalTileViewModel: params.provisionalTileViewModel,
                    selection: selection,
                    loading: loading,
                    filter: filter,
                    nodes: params.nodes,
                    cardwidgets: params.cardwidgets,
                    datatypes: params.datatypes,
                    widgets: params.widgets,
                    nodegroups: params.nodegroups
                });
                return tileVM;
            })
        );

        _.extend(this, params.card, nodegroup, {
            widgets: widgets,
            nodes: nodes,
            parent: params.tile,
            expanded: ko.observable(true),
            highlight: ko.computed(function() {
                var filterText = filter();
                if (!filterText) {
                    return false;
                }
                filterText = filterText.toLowerCase();
                if (params.card.name.toLowerCase().indexOf(filterText) > -1) {
                    return true;
                }
            }, this),
            // tiles: ko.observableArray(),
            tiles: tiles,
            hasprovisionaledits: ko.computed(function(){
                return _.filter(params.tiles, function(tile){
                    return (
                        params.tile ? (tile.parenttile_id === params.tile.tileid) : true
                    ) && tile.nodegroup_id === params.card.nodegroup_id && ko.unwrap(tile.provisionaledits);
                }).length
            }),
            selected: ko.pureComputed({
                read: function () {
                    return selection() === this;
                },
                write: function (value) {
                    if (value) {
                        selection(this);
                    }
                },
                owner: this
            }),
            canAdd: ko.pureComputed({
                read: function () {
                    return this.cardinality === 'n' || this.tiles().length === 0
                },
                owner: this
            }),
            reorderTiles: function (e) {
                loading(true);
                var tiles = _.map(self.tiles(), function(tile) {
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
            getNewTile: function () {
                return new TileViewModel({
                    tile: {
                        tileid: '',
                        resourceinstance_id: params.resourceId(),
                        nodegroup_id: self.nodegroup_id,
                        parenttile_id: self.parent ? self.parent.tileid : null,
                        data: _.reduce(self.widgets, function (data, widget) {
                            data[widget.node_id] = null;
                            return data;
                        }, {})
                    },
                    card: self,
                    handlers: params.handlers,
                    cards: params.cards,
                    tiles: params.tiles,
                    selection: selection,
                    filter: filter,
                    provisionalTileViewModel: params.provisionalTileViewModel,
                    loading: loading,
                    nodes: params.nodes,
                    cardwidgets: params.cardwidgets,
                    datatypes: params.datatypes,
                    widgets: params.widgets,
                    nodegroups: params.nodegroups
                });
            }
        });
        this.isChildSelected = ko.computed(function() {
            return isChildSelected(this);
        }, this);
        this.doesChildHaveProvisionalEdits = ko.computed(function() {
            return doesChildHaveProvisionalEdits(this);
        }, this);
    };
    return CardViewModel;
});
