define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'uuid',
    'models/graph',
    'viewmodels/card',
    'viewmodels/provisional-tile',
    'viewmodels/alert'
], function(_, $, arches, ko, koMapping, uuid, GraphModel, CardViewModel, ProvisionalTileViewModel) {
    function ComponentFOO(componentConfig, loading, title, previouslyPersistedComponentData) {
        var self = this;

        var params = componentConfig.parameters;  /* CLEAN THIS OUT */

        this.resourceId = ko.observable();

        this.componentName = componentConfig.componentName;
        this.componentParameters = componentConfig.parameters;

        this.manageTile = componentConfig.manageTile || false;
        this.manageMultipleTiles = componentConfig.manageMultipleTiles || false;

        this.addedData = ko.observableArray();
        this.savedData = ko.observableArray();

        // this.loading = ko.observable(loading());  /* MUST NOT be able to set parent loading state */

        this.loading = loading;

        this.hasUnsavedData = ko.computed(function() {
            var isAllSavedDataInAddedData = self.savedData().reduce(function(acc, savedDatum) {
                if (self.addedData.indexOf(savedDatum.data) === -1) { acc = false; }
                return acc;
            }, true);

            /* we can assume that an array of equal length to savedData, containing all values of savedData, is valid */ 
            if (
                !isAllSavedDataInAddedData || !( self.savedData().length === self.addedData().length ) 
            ) {
                return true;
            }

            return false;
        });



        this.initialize = function() {
            loading(true);

            if (ko.unwrap(params.resourceid)) {
                self.resourceId(ko.unwrap(params.resourceid));
            } 
            else if (params.workflow && ko.unwrap(params.workflow.resourceId)) {
                self.resourceId(ko.unwrap(params.workflow.resourceId));
            } 

            if (this.manageTile) {
                self.initializeTileBasedComponent(previouslyPersistedComponentData);
            }
            else if (this.manageMultipleTiles) {
                self.initializeMultipleTileBasedComponent(previouslyPersistedComponentData);
            }
        };

        this.initializeTileBasedComponent = function() {
            self.tile = ko.observable();

            self.fooDirty = ko.pureComputed(function() {
                if (self.tile()) {
                    return self.tile().dirty();
                }

                return false;
            })

            self.card = ko.observable();
            self.topCards = ko.observable();

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
    
                self.flattenTree(self.topCards, []).forEach(function(item) {
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
    
                
                componentConfig.parameters.card = self.card();
                componentConfig.parameters.tile = self.tile();
                componentConfig.parameters.loading = loading;
                componentConfig.parameters.provisionalTileViewModel = self.provisionalTileViewModel;
                componentConfig.parameters.reviewer = data.userisreviewer;
                
                loading(false)
            });
        };

        this.initializeMultipleTileBasedComponent = function(previouslyPersistedData) {
            this.manageTile = true;

            if (previouslyPersistedData) {
                previouslyPersistedData.forEach(function(previouslyPersistedDatum) {
                    if (previouslyPersistedDatum.tileid) {
                        /* add tileid to nodeData for reference. */ 
                        previouslyPersistedDatum.data.tileid = previouslyPersistedDatum.tileid;
                    }

                    self.addedData.push(previouslyPersistedDatum.data);
                    self.savedData.push(previouslyPersistedDatum);
                });
            }


            this.editingData = ko.observable(false);

            this.itemName = ko.observable(ko.unwrap(title) ? ko.unwrap(title) : 'Items');

            this.bar = function() {
                loading(true)
                var tileData = koMapping.toJS(self.tile().data);

                var ccc = self.editingData();

                tileData.tileid = ccc.tileid;

                if (ccc) {
                    self.addedData.replace(ccc, tileData);
                    self.editingData(false);
                }
                else {
                    this.addedData.unshift(tileData);
                }

                self.tile().reset();
                loading(false)
            }

            this.foo = function(data) {
                loading(true)

                self.editingData(data);

                var tile = self.tile();

                /* force the value of current tile data observables */ 
                Object.keys(tile.data).forEach(function(key) {
                    if (ko.isObservable(tile.data[key])) {
                        tile.data[key](data[key]);
                    }
                });

                loading(false)
            }

            this.save = function() {
                /* save new tiles */ 
                self.addedData().forEach(function(data) {
                    var tile = self.tile();

                    /* force the value of current tile data observables */ 
                    Object.keys(tile.data).forEach(function(key) {
                        if (ko.isObservable(tile.data[key])) {
                            tile.data[key](data[key]);
                        }
                    });
                    
                    /* if it already has a tileid here, it's a previously saved tile */ 
                    if (!data.tileid) {
                        tile.save(
                            function(){/* onFail */}, 
                            function(savedTileData) {
                                self.savedData.unshift(savedTileData);
                            },
                        );
                    }
                    self.tile(self.card().getNewTile());
                });

                var removedTiles = [];

                self.savedData().forEach(function(data) {
                    var tile = self.tile();
                    tile.tileid = data.tileid;

                    var editedData = ko.utils.arrayFirst(self.addedData(), function(addedDatum) {
                        return addedDatum.tileid === data.tileid;
                    });

                    if (!editedData) {
                        /* means we removed the tile from the list */
                        removedTiles.push(data)
                    }
                    else {
                        /* force the value of current tile data observables */ 
                        Object.keys(tile.data).forEach(function(key) {
                            if (ko.isObservable(tile.data[key])) {
                                tile.data[key](editedData[key]);
                            }
                        });

                        tile.save(
                            function(){},
                            function(savedTileData) {
                                var foo = ko.utils.arrayFirst(self.savedData(), function(savedDatum) {
                                    return savedDatum.tileid === savedTileData.tileid;
                                });

                                self.savedData.replace(foo, savedTileData);
                                self.addedData.replace(foo.data, savedTileData.data);
                            },
                        )

                        self.tile(self.card().getNewTile());
                    }
                });

                removedTiles.forEach(function(data) {
                    var tile = self.tile();
                    tile.tileid = data.tileid;

                    tile.deleteTile();
                });

                self.savedData.removeAll(removedTiles);
            };

            this.reset = function() {
                self.editingData(false);
                self.tile().reset();
            }

            self.initializeTileBasedComponent();
        };

        this.getCardResourceIdOrGraphId = function() { // override for different cases
            return (ko.unwrap(this.resourceId) || ko.unwrap(componentConfig.parameters.graphid));
        };

        this.flattenTree = function(parents, flatList) {
            _.each(ko.unwrap(parents), function(parent) {
                flatList.push(parent);
                var childrenKey = parent.tiles ? 'tiles' : 'cards';
                self.flattenTree(
                    ko.unwrap(parent[childrenKey]),
                    flatList
                );
            });
            return flatList;
        };

        this.initialize();
    }

    function viewModel(params) {
        var self = this;

        this.clearCallback = params.clearCallback;
        this.clearCallback(function() {
            self.reset();
        });

        this.dataToPersist = ko.observable({});
        self.dataToPersist.subscribe(function(foo) {
            params.value(foo);
        })

        this.hasUnsavedData = ko.observable(false);
        this.hasUnsavedData.subscribe(function(hasUnsavedData) {
            params.hasDirtyTile(hasUnsavedData);
        })

        // REFACTOR TO INCLUDE ALL COMPONENTS
        this.loading = params.loading || ko.observable();
        this.complete = params.complete || ko.observable(false);

        /* BEGIN source-of-truth for page data */

        /* 
            `pageLayout` is an observableArray of arrays representing section Information ( `sectionInfo` ).

            `sectionInfo` is an array where the first item is the `sectionTitle` parameter, and the second 
            item is an array of `uniqueInstanceName`.
        */ 
        this.pageLayout = ko.observableArray();
        
        /*
            `componentFOOLookup` is an object where we pair a `uniqueInstanceName` key to `ComponentFOO`
            class objects.
        */ 
        this.componentFOOLookup = ko.observable({});

        /* END source-of-truth for page data */
        

        this.reset = function() {
            self.loading(true);

            Object.values(self.componentFOOLookup()).forEach(function(componentFOO) {
                componentFOO.addedData.removeAll();
                componentFOO.reset();
            });
            
            self.loading(false);
        };

        params.preSaveCallback(function() {
            self.loading(true);

            Object.values(self.componentFOOLookup()).forEach(function(componentFOOBAR) {
                if (componentFOOBAR.hasUnsavedData()) {
                    componentFOOBAR.save();
                } 
            });
        });

        params.postSaveCallback(function() {
            self.hasUnsavedData(false);
            self.loading(false);
        });

        this.initialize = function() {
            self.loading(true);

            var previouslyPersistedData = ko.unwrap(params.value);

            ko.toJS(params.layoutSections).forEach(function(layoutSection) {
                var componentFOONames = [];

                layoutSection.componentConfigs.forEach(function(componentFOOData) {
                    componentFOONames.push(componentFOOData.uniqueInstanceName);

                    var componentFOOLookup = self.componentFOOLookup();

                    var previouslyPersistedComponentData;
                    if (previouslyPersistedData && previouslyPersistedData[componentFOOData.uniqueInstanceName]) {
                        previouslyPersistedComponentData = previouslyPersistedData[componentFOOData.uniqueInstanceName];
                    }

                    var componentFOO = new ComponentFOO(componentFOOData, self.loading, params.title, previouslyPersistedComponentData);

                    componentFOO.savedData.subscribe(function() {
                        var dataToPersist = self.dataToPersist();
                        dataToPersist[componentFOOData.uniqueInstanceName] = koMapping.toJS(componentFOO.savedData());
                        self.dataToPersist(dataToPersist);
                    });

                    componentFOO.hasUnsavedData.subscribe(function(foo) {
                        var hasUnsavedData = Object.values(self.componentFOOLookup()).reduce(function(acc, componentFOOBAR) {
                            if (componentFOOBAR.hasUnsavedData()) {
                                acc = true;
                            } 
                            return acc;
                        }, false);

                        self.hasUnsavedData(hasUnsavedData);
                    });

                    componentFOOLookup[componentFOOData.uniqueInstanceName] = componentFOO;

                    self.componentFOOLookup(componentFOOLookup);
                });

                var sectionInfo = [layoutSection.sectionTitle, componentFOONames];

                self.pageLayout.push(sectionInfo);
            });
        };

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
             * Keep in mind that anything extending newStep that overrides this method should include similar logic to handle for wastebin if there is a wastebin use case for that particular step in the workflow.
            **/
            var wastebin;
            if (ko.unwrap(params.wastebin)) {
                wastebin = koMapping.toJS(params.wastebin);
            }

            return {
                wastebin: wastebin,
                pageLayout: koMapping.toJS(self.pageLayout),
            };
        };
        params.defineStateProperties();

        this.initialize();
    }

    ko.components.register('component-based-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/component-based-step.htm'
        }
    });

    return viewModel;
});
