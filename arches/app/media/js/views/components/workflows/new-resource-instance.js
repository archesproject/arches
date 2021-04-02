define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'models/graph',
    'viewmodels/card',
    'viewmodels/provisional-tile',
    'viewmodels/alert'
], function(_, $, arches, ko, koMapping, GraphModel, CardViewModel, ProvisionalTileViewModel, AlertViewModel) {
    function viewModel(params) {
        var self = this;

        this.resourceId = ko.observable(ko.unwrap(params.resourceid));
        this.resourceId.subscribe(function(id) {
            params.resourceid(id);
        });

        this.getCardResourceIdOrGraphId = function() {
            return (ko.unwrap(this.resourceId) || ko.unwrap(params.graphid));
        };

        this.card = ko.observable();

        this.tile = ko.observable();
        this.tile.subscribe(function(tile) {
            if (tile && params.hasDirtyTile) {
                console.log("line 41 ran");
                tile.dirty.subscribe(function(val) {
                    ((self.card() && self.card().isDirty()) || val) ? params.hasDirtyTile(true) : params.hasDirtyTile(false);
                });
            }
        });
        
        this.loading = params.loading || ko.observable(false);
        this.alert = params.alert || ko.observable(null);
        
        this.complete = params.complete || ko.observable();
        this.graphName = params.graphName;

        this.loading(true);

        this.customCardLabel = params.customCardLabel || false;
        var flattenTree = function(parents, flatList) {
            _.each(ko.unwrap(parents), function(parent) {
                flatList.push(parent);
                var childrenKey = parent.tiles ? 'tiles' : 'cards';
                flattenTree(
                    ko.unwrap(parent[childrenKey]),
                    flatList
                );
            });
            return flatList;
        };

        self.topCards = ko.observableArray();

        this.getJSON = function() {
            var url = arches.urls.api_card + this.getCardResourceIdOrGraphId();

            $.getJSON(url, function(data) {
                var handlers = {
                    'after-update': [],
                    'tile-reset': []
                };
                var displayname = ko.observable(data.displayname);
                var createLookup = function(list, idKey) {
                    return _.reduce(list, function(lookup, item) {
                        lookup[item[idKey]] = item;
                        return lookup;
                    }, {});
                };

                self.reviewer = data.userisreviewer;
                self.provisionalTileViewModel = new ProvisionalTileViewModel({
                    tile: self.tile,
                    reviewer: data.userisreviewer
                });

                var graphModel = new GraphModel({
                    data: {
                        nodes: data.nodes,
                        nodegroups: data.nodegroups,
                        edges: []
                    },
                    datatypes: data.datatypes
                });

                var topCards = _.filter(data.cards, function(card) {
                    var nodegroup = _.find(data.nodegroups, function(group) {
                        return group.nodegroupid === card.nodegroup_id;
                    });
                    return !nodegroup || !nodegroup.parentnodegroup_id;
                }).map(function(card) {
                    params.nodegroupid = params.nodegroupid || card.nodegroup_id;
                    return new CardViewModel({
                        card: card,
                        graphModel: graphModel,
                        tile: null,
                        resourceId: self.resourceId,
                        displayname: displayname,
                        handlers: handlers,
                        cards: data.cards,
                        tiles: data.tiles,
                        provisionalTileViewModel: self.provisionalTileViewModel,
                        cardwidgets: data.cardwidgets,
                        userisreviewer: data.userisreviewer,
                        loading: self.loading
                    });
                });

                self.topCards(topCards);
    
                self.widgetLookup = createLookup(
                    data.widgets,
                    'widgetid'
                );
                self.cardComponentLookup = createLookup(
                    data['card_components'],
                    'componentid'
                );
                self.nodeLookup = createLookup(
                    graphModel.get('nodes')(),
                    'nodeid'
                );
                self.on = function(eventName, handler) {
                    if (handlers[eventName]) {
                        handlers[eventName].push(handler);
                    }
                };
                self.foo();
                self.loading(false);
            });
        };

        self.foo = function() {
            flattenTree(self.topCards, []).forEach(function(item) { //do I need to flatten?
                if (item.constructor.name === 'CardViewModel' && item.nodegroupid === params.nodegroupid) {
                    if (ko.unwrap(params.parenttileid) && item.parent && ko.unwrap(params.parenttileid) !== item.parent.tileid) {
                        return;
                    }
                    if (self.customCardLabel) item.model.name(ko.unwrap(self.customCardLabel));
                    self.card(item);

                    if (ko.unwrap(self.resourceId) && item.tiles().length > 0) {
                        flattenTree(item.tiles(), []).forEach(function(tile) { //do I need to flatten?
                            if (tile.nodegroup_id === params.nodegroupid) {
                                self.tile(tile);
                            }
                        });                        
                    } else if (ko.unwrap(params.createTile) !== false) {
                        self.tile(item.getNewTile());
                    }
                }
            })
        };

        params.tile = self.tile;

        if(ko.unwrap(params.getJSONOnLoad) !== false) {
            this.getJSON();
        }

        self.loadCard = function(card){
            self.card(card);
            params.nodegroupid = self.card().nodegroupid;
            self.foo();
        }

        self.close = function(){
            self.complete(true);
        }

        self.onDeleteSuccess = function(tiles) {
            self.tile(self.card().getNewTile());
        }

        self.onSaveSuccess = function(tiles) {
            var tile;
            if (tiles.length > 0 || typeof tiles == 'object') {
                tile = tiles[0] || tiles;

                self.tile(tile);
                self.resourceId(tile.resourceinstance_id);
            }

            if (self.completeOnSave === true) { self.complete(true); }
        };
    }

    ko.components.register('new-resource-instance', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/new-resource-instance.htm'
        }
    });
    return viewModel;
});
