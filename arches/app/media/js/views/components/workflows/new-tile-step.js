define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'models/graph',
    'viewmodels/card',
    'viewmodels/provisional-tile'
], function(_, $, arches, ko, GraphModel, CardViewModel, ProvisionalTileViewModel) {
    function viewModel(params) {
        var self = this;
        var url = arches.urls.api_card + (params.resourceid || params.graphid);

        this.card = ko.observable();
        this.tile = ko.observable();
        this.loading = ko.observable();
        this.resourceId = ko.observable(params.resourceid);
        this.complete = params.complete || ko.observable();
        this.complete(!!params.tileid);

        // TODO: show/hide loading mask before/after request/response
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

            topCards.forEach(function(topCard) {
                topCard.topCards = topCards;
            });

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

            flattenTree(topCards, []).forEach(function(item) {
                if (item.constructor.name === 'CardViewModel' && item.nodegroupid === params.nodegroupid) {
                    if (params.parenttileid && item.parent && params.parenttileid !== item.parent.tileid) {
                        return;
                    }
                    self.card(item);
                    if (params.tileid) {
                        ko.unwrap(item.tiles).forEach(function(tile) {
                            if (tile.tileid === params.tileid) {
                                self.tile(tile);
                            }
                        });
                    } else {
                        self.tile(item.getNewTile());
                    }
                }
            });
        });

        self.saveTile = function(tile, callback) {
            tile.save(function(response) {
                // TODO handle failure with alert...
                throw response;
            }, function(tile) {
                params.resourceid = tile.resourceinstance_id;
                params.tileid = tile.tileid;
                self.resourceId(tile.resourceinstance_id);
                self.complete(true);
                if (typeof callback === 'function') {
                    callback.apply(null, arguments);
                }
            });
        };
    }
    ko.components.register('new-tile-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/new-tile-step.htm'
        }
    });
    return viewModel;
});
