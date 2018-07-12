define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'models/card',
    'models/card-widget',
    'arches',
    'require',
    'viewmodels/tile'
], function($, _, ko, koMapping, CardModel, CardWidgetModel, arches, require) {
    /**
    * A viewmodel used for generic cards
    *
    * @constructor
    * @name CardViewModel
    *
    * @param  {string} params - a configuration object
    */
    var isChildSelected = function(parent) {
        var childSelected = false;
        var childrenKey = parent.tiles ? 'tiles' : 'cards';
        ko.unwrap(parent[childrenKey]).forEach(function(child) {
            if (child.selected() || isChildSelected(child)) {
                childSelected = true;
            }
        });
        return childSelected;
    };

    var doesChildHaveProvisionalEdits = function(parent) {
        var hasEdits = false;
        var childrenKey = parent.tiles ? 'tiles' : 'cards';
        ko.unwrap(parent[childrenKey]).forEach(function(child) {
            if (child.hasprovisionaledits() || doesChildHaveProvisionalEdits(child)) {
                hasEdits = true;
            }
        });
        return hasEdits;
    };

    var updateDisplayName = function(resourceId, displayname) {
        $.get(
            arches.urls.resource_descriptors + resourceId(),
            function(descriptors) {
                displayname(descriptors.displayname);
            }
        );
    };

    var CardViewModel = function(params) {
        var TileViewModel = require('viewmodels/tile');
        var self = this;
        var selection = params.selection || ko.observable();
        var filter = params.filter || ko.observable();
        var loading = params.loading || ko.observable();
        var nodes = _.filter(ko.unwrap(params.graphModel.get('nodes')), function(node) {
            return ko.unwrap(node.nodegroup_id) === ko.unwrap(params.card.nodegroup_id);
        });
        // .map(function(node) {
        //     node.configKeys = ko.observableArray(
        //         _.map(node.config, function(val, key) {
        //             return key;
        //         })
        //     );
        //     node.config = koMapping.fromJS(node.config);
        //     return node;
        // });
        var widgets = ko.observableArray(_.filter(params.cardwidgets, function(widget) {
            return widget.card_id === params.card.cardid;
        }));
        // var widgets = ko.observableArray();

        // cardwidgets().forEach(function(widgetdata){
        //     widgets.push(new CardWidgetModel(widgetdata, {
        //         //node: nodeModel,
        //         //card: self,
        //         //datatype: datatype,
        //         //disabled: attributes.data.disabled
        //     }));
        // }, this);

        _.each(ko.unwrap(nodes), function(node) {
            var widget = _.find(widgets(), function(widget) {
                return widget.node_id === ko.unwrap(node.nodeid);
            });
            // if (!widget) {
            //     var datatype = _.find(params.datatypes, function(datatype) {
            //         return datatype.datatype === ko.unwrap(node.datatype);
            //     });
            //     if (datatype.defaultwidget_id) {
            //         var widgetData = _.find(params.widgets, function(widget) {
            //             return widget.widgetid === datatype.defaultwidget_id;
            //         });
            //         widget = {
            //             widget_id: ko.observable(datatype.defaultwidget_id),
            //             config: _.extend({
            //                 label: ko.unwrap(node.name)
            //             }, widgetData.defaultconfig),
            //             label: ko.unwrap(node.name),
            //             node_id: ko.unwrap(node.nodeid),
            //             card_id: params.card.cardid,
            //             id: '',
            //             sortorder: ''
            //         };
            //         widgets.push(widget);
            //     }
            // }
            // if (widget) {
            //     widget.selected = ko.pureComputed({
            //         read: function() {
            //             return selection() === this;
            //         },
            //         write: function(value) {
            //             if (value) {
            //                 selection(this);
            //             }
            //         },
            //         owner: widget
            //     });
            // }
        });

        var nodegroups = params.graphModel.get('nodegroups');

        var cardModel = new CardModel({
            data: _.extend({
                widgets: params.cardwidgets,
                nodes: params.graphModel.get('nodes'),
                widgetList: params.widgets
            }, params.card),
            datatypes: params.datatypes,
        });

        cardModel.widgets().forEach(function(widget){
            widget.selected = ko.pureComputed({
                read: function() {
                    return selection() === this;
                },
                write: function(value) {
                    if (value) {
                        selection(this);
                    }
                },
                owner: widget
            });
        });

        var nodegroup = _.find(ko.unwrap(nodegroups), function(group) {
            return ko.unwrap(group.nodegroupid) === ko.unwrap(params.card.nodegroup_id);
        });

        _.extend(this, nodegroup, {
            model: cardModel,
            widgets: cardModel.widgets,
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
            tiles: ko.observableArray(
                _.filter(params.tiles, function(tile) {
                    return (
                        params.tile ? (tile.parenttile_id === params.tile.tileid) : true
                    ) && ko.unwrap(tile.nodegroup_id) === ko.unwrap(params.card.nodegroup_id);
                }).map(function(tile) {
                    return new TileViewModel({
                        tile: tile,
                        card: self,
                        resourceId: params.resourceId,
                        displayname: params.displayname,
                        handlers: params.handlers,
                        userisreviewer: params.userisreviewer,
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
                        nodegroups: ko.unwrap(nodegroups)
                    });
                })
            ),
            cards: _.filter(params.cards, function(card) {
                var nodegroup = _.find(ko.unwrap(nodegroups), function(group) {
                    return ko.unwrap(group.nodegroupid) === ko.unwrap(card.nodegroup_id);
                });
                return ko.unwrap(nodegroup.parentnodegroup_id) === ko.unwrap(params.card.nodegroup_id);
            }).map(function(card) {
                return new CardViewModel({
                    card: _.clone(card),
                    graphModel: params.graphModel,
                    tile: null,
                    resourceId: params.resourceId,
                    displayname: params.displayname,
                    handlers: params.handlers,
                    cards: params.cards,
                    tiles: params.tiles,
                    selection: selection,
                    loading: loading,
                    filter: filter,
                    provisionalTileViewModel: params.provisionalTileViewModel,
                    //nodes: params.nodes,
                    cardwidgets: params.cardwidgets,
                    datatypes: params.datatypes,
                    widgets: params.widgets,
                    //nodegroups: ko.unwrap(nodegroups)
                });
            }),
            hasprovisionaledits: ko.computed(function() {
                return _.filter(params.tiles, function(tile) {
                    return (
                        params.tile ? (tile.parenttile_id === params.tile.tileid) : true
                    ) && ko.unwrap(tile.nodegroup_id) === ko.unwrap(params.card.nodegroup_id) && ko.unwrap(tile.provisionaledits);
                }).length;
            }),
            selected: ko.pureComputed({
                read: function() {
                    return selection() === this;
                },
                write: function(value) {
                    if (value) {
                        selection(this);
                    }
                },
                owner: this
            }),
            canAdd: ko.pureComputed({
                read: function() {
                    return this.cardinality === 'n' || this.tiles().length === 0;
                },
                owner: this
            }),
            reorderTiles: function(e) {
                loading(true);
                var tiles = _.map(self.tiles(), function(tile) {
                    return tile.getAttributes();
                });
                $.ajax({
                    type: 'POST',
                    data: JSON.stringify({
                        tiles: tiles
                    }),
                    url: arches.urls.reorder_tiles,
                    complete: function(response) {
                        loading(false);
                        updateDisplayName(params.resourceId, params.displayname);
                    }
                });
            },
            getNewTile: function() {
                return new TileViewModel({
                    tile: {
                        tileid: '',
                        resourceinstance_id: params.resourceId(),
                        nodegroup_id: ko.unwrap(self.model.nodegroup_id),
                        parenttile_id: self.parent ? self.parent.tileid : null,
                        data: _.reduce(self.widgets, function(data, widget) {
                            data[widget.node_id] = null;
                            return data;
                        }, {})
                    },
                    card: self,
                    resourceId: params.resourceId,
                    displayname: params.displayname,
                    handlers: params.handlers,
                    userisreviewer: params.userisreviewer,
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
                    nodegroups: ko.unwrap(nodegroups)
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
