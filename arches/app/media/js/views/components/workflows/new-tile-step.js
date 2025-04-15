import _ from 'underscore';
import $ from 'jquery';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import arches from 'arches';
import GraphModel from 'models/graph';
import CardViewModel from 'viewmodels/card';
import ProvisionalTileViewModel from 'viewmodels/provisional-tile';
import AlertViewModel from 'viewmodels/alert';
import newTileStepTemplate from 'templates/views/components/workflows/new-tile-step.htm';


function viewModel(params) {
    var self = this;

    this.resourceId = ko.observable(ko.unwrap(params.resourceid));
    this.resourceId.subscribe(function(id) {
        params.resourceid(id);
    });

    var cachedValue = ko.unwrap(params.value);
    if (cachedValue) {
        if (cachedValue.tileid) {
            params.tileid(cachedValue.tileid);
        }
        if (cachedValue.resourceid) {
            self.resourceId(cachedValue.resourceid);
        }
    }
    
    if (!self.resourceId() && params.workflow && ko.unwrap(params.workflow.resourceId)) {
        self.resourceId(ko.unwrap(params.workflow.resourceId));
    } 

    this.getCardResourceIdOrGraphId = function() { // override for different cases
        return (ko.unwrap(this.resourceId) || ko.unwrap(params.graphid));
    };

    this.card = ko.observable();
    this.tile = ko.observable();
    params.hasDirtyTile(false);

    this.tile.subscribe(function(tile) {
        if (tile && params.hasDirtyTile) {
            tile.dirty.subscribe(function(val) {
                /* 
                    for proper function, need to interact with card dirty state inside tile subscription 
                */
                ((self.card() && self.card().isDirty()) || val) ? params.hasDirtyTile(true) : params.hasDirtyTile(false);
            });
        }
    });
    
    this.loading = params.loading || ko.observable(false);
    this.alert = params.alert || ko.observable(null);
    
    this.complete = params.complete || ko.observable();
    this.complete.subscribe(function(isComplete) {
        if (isComplete && params.value) {
            params.value(params.defineStateProperties());
        }
    });

    this.completeOnSave = params.completeOnSave === false ? false : true;

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
    self.topCards = [];

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

            self.topCards = _.filter(data.cards, function(card) {
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

            self.card.subscribe(function(card){
                if (card) {
                    card.context = 'workflow';

                    if (params.preSaveCallback) {
                        card.preSaveCallback = params.preSaveCallback;
                    }
                    if (params.postSaveCallback) {
                        card.postSaveCallback = params.postSaveCallback;
                    }
                }
                if (ko.unwrap(card.widgets) && params.hiddenNodes) {
                    card.widgets().forEach(function(widget){
                        if (params.hiddenNodes.indexOf(widget.node_id()) > -1) {
                            widget.visible(false);
                        }
                    });
                }
            });

            self.topCards.forEach(function(topCard) {
                topCard.topCards = self.topCards;
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

            flattenTree(self.topCards, []).forEach(function(item) {
                if (item.constructor.name === 'CardViewModel' && item.nodegroupid === ko.unwrap(params.nodegroupid)) {
                    if (ko.unwrap(params.parenttileid) && item.parent && ko.unwrap(params.parenttileid) !== item.parent.tileid) {
                        return;
                    }
                    if (self.customCardLabel) item.model.name(ko.unwrap(self.customCardLabel));
                    self.card(item);
                    if (ko.unwrap(params.tileid)) {
                        ko.unwrap(item.tiles).forEach(function(tile) {
                            if (tile.tileid === ko.unwrap(params.tileid)) {
                                self.tile(tile);
                            }
                        });
                    } else if (ko.unwrap(params.createTile) !== false) {
                        self.tile(item.getNewTile());
                    }
                }
            });
            self.loading(false);
            // commented the line below because it causes steps to automatically advance on page reload
            // self.complete(!!ko.unwrap(params.tileid));
        });
    };

    self.getTiles = function(nodegroupId, tileId) {
        var tiles = [];
        flattenTree(self.topCards, []).forEach(function(item) {
            if (item.constructor.name === 'CardViewModel' && item.nodegroupid === nodegroupId) {
                tiles = tiles.concat(ko.unwrap(item.tiles));
            }
        });
        if (tileId) {
            tiles = tiles.filter(function(tile) {
                return tile.tileid === tileId;
            });
        }
        return tiles;
    };

    params.tile = self.tile;

    if(ko.unwrap(params.getJSONOnLoad) !== false) {
        this.getJSON();
    }

    params.defineStateProperties = function(){
        // Collects those properties that you want to set to the state.
        /** 
         * Wastebin
         * Note that wastebin as set on the workflow step params is inclusive; only things identified by those keys (e.g. tile, resourceid) will be deleted on quit. Otherwise if no wastebin params given, nothing will be deleted on quit.
         * 
         * -- If the workflow edits/creates one and only one new resource, resourceid need only be named in the first step's params' wastebin like so: wastebin: {resourceid:null}
         * This will automatically cascade/delete all tiles generated from this resource.
         * 
         * -- If not every step's generated tile belongs to the same resource or you want to selectively delete a tile from a step, {tile:null} should be declared in every step's params' wastebin where you want the tile from that step to be deleted on quit.
         * 
         * Overriding this method:
         * Keep in mind that anything extending newTileStep that overrides this method should include similar logic to handle for wastebin if there is a wastebin use case for that particular step in the workflow.
        **/
        var wastebin = !!(ko.unwrap(params.wastebin)) ? koMapping.toJS(params.wastebin) : undefined;
        var resourceId = ko.unwrap(params.resourceid);

        if (resourceId) {
            if (wastebin && 'resources' in wastebin) {
                wastebin.resources.push(resourceId);
            }
            if (wastebin && 'resourceid' in wastebin) {
                wastebin.resourceid = resourceId;
            }
        }
        if (wastebin && 'tile' in wastebin) {
            if (!!ko.unwrap(params.tile)) {
                wastebin.tile = koMapping.toJS(params.tile().data);
                wastebin.tile.tileid = (ko.unwrap(params.tile)).tileid;
                wastebin.tile.resourceinstance_id = (ko.unwrap(params.tile)).resourceinstance_id;
            }
        }
        
        ko.mapping.fromJS(wastebin, {}, params.wastebin);
        
        return {
            resourceid: resourceId,
            tile: !!(ko.unwrap(params.tile)) ? koMapping.toJS(params.tile().data) : undefined,
            tileid: !!(ko.unwrap(params.tile)) ? ko.unwrap(params.tile().tileid): undefined,
            wastebin: wastebin
        };
    };
    /* calling on init to give workflow access to wastebin on load */ 
    params.defineStateProperties();

    self.onSaveSuccess = function(tiles) {
        var tile;
        
        if (tiles.length > 0 || typeof tiles == 'object') {
            tile = tiles[0] || tiles;

            params.tileid(tile.tileid);
            self.resourceId(tile.resourceinstance_id);
        }

        if (params.value) {
            params.value(params.defineStateProperties());
        }
        
        if (self.completeOnSave === true) { self.complete(true); }
    };

}
ko.components.register('new-tile-step', {
    viewModel: viewModel,
    template: newTileStepTemplate,
});
export default viewModel;
