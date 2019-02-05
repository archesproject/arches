define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'models/card',
    'models/card-widget',
    'arches',
    'require',
    'utils/dispose',
    'viewmodels/tile'
], function($, _, ko, koMapping, CardModel, CardWidgetModel, arches, require, dispose) {
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
        var children = [];
        if ('tileid' in parent) {
            children = ko.unwrap(parent.cards);
        } else if ('model' in parent) {
            children = ko.unwrap(parent.cards).concat(
                ko.unwrap(parent.tiles),
                ko.unwrap(parent.widgets)
            );
        }
        children.forEach(function(child) {
            if (child.selected && child.selected() || isChildSelected(child)) {
                childSelected = true;
            }
        });
        return childSelected;
    };

    var doesChildHaveProvisionalEdits = function(parent) {
        var hasEdits = false;
        var childrenKey = 'tileid' in parent ? 'cards': 'tiles';
        ko.unwrap(parent[childrenKey]).forEach(function(child) {
            if (child.hasprovisionaledits && child.hasprovisionaledits() || doesChildHaveProvisionalEdits(child)) {
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
        var hover = params.hover || ko.observable();
        var scrollTo = params.scrollTo || ko.observable();
        var filter = params.filter || ko.observable();
        var loading = params.loading || ko.observable();
        var perms = ko.observableArray();
        var permsLiteral = ko.observableArray();
        var nodegroups = params.graphModel.get('nodegroups');
        var multiselect = params.multiselect || false;
        var isWritable = params.card.is_writable || false;
        var selection;
        if (params.multiselect) {
            selection = params.selection || ko.observableArray([]);
        } else {
            selection = params.selection || ko.observable();
        }
        var nodegroup = _.find(ko.unwrap(nodegroups), function(group) {
            return ko.unwrap(group.nodegroupid) === ko.unwrap(params.card.nodegroup_id);
        });

        var cardModel = new CardModel({
            data: _.extend(params.card, {
                widgets: params.cardwidgets,
                nodes: params.graphModel.get('nodes'),
                nodegroup: nodegroup
            }),
            datatypelookup: params.graphModel.get('datatypelookup'),
        });

        var applySelectedComputed = function(widgets){
            widgets.forEach(function(widget){
                widget.parent = self;
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
                widget.hovered = ko.pureComputed({
                    read: function() {
                        return hover() === this;
                    },
                    write: function(value) {
                        if (value === true) {
                            hover(this);
                        }
                        if (value === null) {
                            hover(null);
                        }
                    },
                    owner: widget
                });
            });
        };

        applySelectedComputed(cardModel.widgets());

        var widgetsSubscription = cardModel.widgets.subscribe(function(widgets){
            applySelectedComputed(widgets);
        });

        _.extend(this, nodegroup, {
            isWritable: isWritable,
            model: cardModel,
            multiselect: params.multiselect,
            widgets: cardModel.widgets,
            parent: params.tile,
            parentCard: params.parentCard,
            expanded: ko.observable(false),
            perms: perms,
            permsLiteral: permsLiteral,
            scrollTo: ko.pureComputed(function() {
                return scrollTo() === this;
            }, this),
            fullyProvisional: ko.pureComputed(function(){
                var res;
                var provisionalindex;
                var summary = _.map(this.tiles(), function(tile){
                    var dataEmpty = _.keys(koMapping.toJS(tile.data)).length === 0;
                    if (tile.provisionaledits() !== null && dataEmpty) {
                        return 2;
                    } else if (tile.provisionaledits() !== null && !dataEmpty) {
                        return 1;
                    } else {
                        return 0;
                    }
                });
                provisionalindex = _.reduce(summary, function(a, b){return a + b;});
                if (provisionalindex > 0) {
                    if (_.every(summary, function(val){return val === 2;})) {
                        res = 'fullyprovisional';
                    }
                    else {
                        res = 'provisional';
                    }
                }
                return res;
            }, this),
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
                        graphModel: params.graphModel,
                        resourceId: params.resourceId,
                        displayname: params.displayname,
                        handlers: params.handlers,
                        userisreviewer: params.userisreviewer,
                        cards: params.cards,
                        tiles: params.tiles,
                        provisionalTileViewModel: params.provisionalTileViewModel,
                        selection: selection,
                        scrollTo: scrollTo,
                        loading: loading,
                        filter: filter,
                        cardwidgets: params.cardwidgets,
                    });
                })
            ),
            cards: ko.observableArray(_.filter(params.cards, function(card) {
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
                    multiselect: multiselect,
                    scrollTo: scrollTo,
                    loading: loading,
                    filter: filter,
                    provisionalTileViewModel: params.provisionalTileViewModel,
                    cardwidgets: params.cardwidgets,
                    perms: perms,
                    permsLiteral: permsLiteral,
                    parentCard: self
                });
            })),
            hasprovisionaledits: ko.computed(function() {
                return _.filter(params.tiles, function(tile) {
                    return (params.tile ? (tile.parenttile_id === params.tile.tileid) : true)
                        && ko.unwrap(tile.nodegroup_id) === ko.unwrap(params.card.nodegroup_id)
                        && ko.unwrap(tile.provisionaledits)
                        && _.keys(ko.unwrap(tile.provisionaledits)).length !== 0;
                }).length;
            }),
            selected: ko.pureComputed({
                read: function() {
                    if (self.multiselect) {
                        return _.contains(selection(), this);
                    } else {
                        return selection() === this;
                    }
                },
                write: function(value) {
                    if (self.multiselect){
                        if (value === true){
                            if (_.contains(selection(), this) === false){
                                selection.push(this);
                            }
                        } else if (value === false) {
                            if (_.contains(selection(), this) === true) {
                                selection.remove(this);
                            }
                        }
                    } else if (value) {
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
            reorderTiles: function() {
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
                    complete: function() {
                        loading(false);
                        updateDisplayName(params.resourceId, params.displayname);
                    }
                });
            },
            reorderCards: function() {
                loading(true);
                var cards = _.map(self.cards(), function(card, i) {
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
            getNewTile: function() {
                return new TileViewModel({
                    tile: {
                        tileid: '',
                        resourceinstance_id: params.resourceId(),
                        nodegroup_id: ko.unwrap(self.model.nodegroup_id),
                        parenttile_id: self.parent ? self.parent.tileid : null,
                        data: _.reduce(self.widgets(), function(data, widget) {
                            data[widget.node_id()] = null;
                            return data;
                        }, {})
                    },
                    card: self,
                    graphModel: params.graphModel,
                    resourceId: params.resourceId,
                    displayname: params.displayname,
                    handlers: params.handlers,
                    userisreviewer: params.userisreviewer,
                    cards: params.cards,
                    tiles: params.tiles,
                    selection: selection,
                    scrollTo: scrollTo,
                    filter: filter,
                    provisionalTileViewModel: params.provisionalTileViewModel,
                    loading: loading,
                    cardwidgets: params.cardwidgets,
                });
            }
        });

        this.childless = ko.pureComputed(function() {
            return this.cards().length === 0;
        }, this);

        this.selected.subscribe(function(selected) {
            if (selected) this.expanded(true);
        }, this);
        this.expanded.subscribe(function(expanded) {
            if (expanded && this.parent) this.parent.expanded(true);
        }, this);

        this.isChildSelected = ko.computed(function() {
            return isChildSelected(this);
        }, this);
        this.doesChildHaveProvisionalEdits = ko.computed(function() {
            return doesChildHaveProvisionalEdits(this);
        }, this);

        var expandParents = function(item) {
            if (item.parent) {
                item.parent.expanded(true);
                expandParents(item.parent);
            }
        };

        this.selectChildCards = function(value) {
            if (value !== undefined){
                this.selected(value);
            } else {
                if (this.selected() === false) {
                    value = true;
                    this.selected(true);
                } else {
                    value = false;
                    this.selected(false);
                }
            }
            if (this.cards().length > 0) {
                this.expanded(true);

                this.cards().forEach(function(childCard){
                    childCard.selectChildCards(value);
                }, this);
            }
        };

        var higlightSubscription = this.highlight.subscribe(function(highlight) {
            if (highlight) {
                this.expanded(true);
                expandParents(this);
            }
        }, this);

        this.disposables = [];
        this.disposables.push(higlightSubscription);
        this.disposables.push(widgetsSubscription);
        this.disposables.push(this.scrollTo);
        this.disposables.push(this.highlight);
        this.disposables.push(this.hasprovisionaledits);
        this.disposables.push(this.selected);
        this.disposables.push(this.canAdd);
        this.disposables.push(this.isChildSelected);
        this.disposables.push(this.doesChildHaveProvisionalEdits);
        this.disposables.push(
            this.cards.subscribe(function() {
                this.model.parseNodes.call(this.model);
            }, this)
        );
        this.disposables.push(this.model);

        this.dispose = function() {
            dispose(self);
        };

    };
    return CardViewModel;
});
