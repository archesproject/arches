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
    function WorkflowComponentAbstract(componentConfig, loading, title, previouslyPersistedComponentData, resourceId) {
        var self = this;

        this.resourceId = resourceId;
        
        this.componentName = componentConfig.componentName;
        this.componentParameters = componentConfig.parameters;
        this.tilesManaged = componentConfig.tilesManaged;

        this.addedData = ko.observableArray();
        this.savedData = ko.observableArray();

        this.loading = ko.observable();

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
            self.loading(true);

            console.log("INIT", self, componentConfig, self.loading())

            if (this.tilesManaged === "one") {
                self.initializeTileBasedComponent(previouslyPersistedComponentData);
            }
            else if (this.tilesManaged === "many") {
                self.initializeMultipleTileBasedComponent(previouslyPersistedComponentData);
            }

        };

        this.initializeTileBasedComponent = function(previouslyPersistedData) {
            self.tile = ko.observable();

            // self.loading(true)

            if (!self.tilesManaged === "many") {
                self.tile.subscribe(function(sd) {
                    if (sd) {
                        if (previouslyPersistedData) {
                            var tile = self.tile();
    
                            /* force the value of current tile data observables */ 
                            Object.keys(tile.data).forEach(function(key) {
                                if (ko.isObservable(tile.data[key])) {
                                    tile.data[key](previouslyPersistedData[0].data[key]);
                                }
                            });
    
                            tile._tileData(koMapping.toJSON(tile.data));
                        }
                    }
                })
            }

            self.isDirty = ko.computed(function() {
                if (self.tile()) {
                    return self.tile().dirty();
                }

                return false;
            });

            if (!self.tilesManaged === "many") {
                self.isDirty.subscribe(function() {
                    self.addedData.removeAll();
                    self.addedData.push(self.tile().data);
                });
            }

            self.card = ko.observable();
            self.topCards = ko.observable();

            var url = arches.urls.api_card + this.getCardResourceIdOrGraphId();
            $.getJSON(url, function(data) {
                /* important to ensure load is set here to keep components from rendering before they're ready */
                // self.loading(true);  

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
                    componentConfig.parameters.nodegroupid = componentConfig.parameters.nodegroupid || card.nodegroup_id;
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
                    if (item.constructor.name === 'CardViewModel' && item.nodegroupid === ko.unwrap(componentConfig.parameters.nodegroupid)) {
                        if (ko.unwrap(componentConfig.parameters.parenttileid) && item.parent && ko.unwrap(componentConfig.parameters.parenttileid) !== item.parent.tileid) {
                            return;
                        }
                        if (self.customCardLabel) item.model.name(ko.unwrap(self.customCardLabel));
                        self.card(item);
                        if (ko.unwrap(componentConfig.parameters.tileid)) {
                            ko.unwrap(item.tiles).forEach(function(tile) {
                                if (tile.tileid === ko.unwrap(componentConfig.parameters.tileid)) {
                                    self.tile(tile);
                                }
                            });
                        } else if (ko.unwrap(componentConfig.parameters.createTile) !== false) {
                            self.tile(item.getNewTile());
                        }
                    }
                });
    

                if (!self.tilesManaged === "many") {
                console.log("AAAddddddAAAAA", componentConfig, self.loading())

                    self.save = function() {
                            self.tile().save(
                                function(){/* onFail */},
                                function(savedTileData) {
                                    self.savedData.unshift(savedTileData);
                                },
                            )
                    };

                    self.reset = function() {
                        self.tile().reset();
                    };
                }

                // if (self.card() && self.tile()) {
                    console.log("AAAAAAAA", componentConfig, self.loading())
                    componentConfig.parameters.card = self.card();
                    componentConfig.parameters.tile = self.tile();
                    componentConfig.parameters.loading = loading;
                    componentConfig.parameters.provisionalTileViewModel = self.provisionalTileViewModel;
                    componentConfig.parameters.reviewer = data.userisreviewer;

                    self.loading(false);
                // }
            });
        };

        this.initializeMultipleTileBasedComponent = function(previouslyPersistedData) {
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

            this.addOrUpdateEntry = function() {
                // self.loading(true)

                var tileData = koMapping.toJS(self.tile().data);

                var editingData = self.editingData();

                tileData.tileid = editingData.tileid;

                if (editingData) {
                    self.addedData.replace(editingData, tileData);
                    self.editingData(false);
                }
                else {
                    this.addedData.unshift(tileData);
                }

                self.tile().reset();

                // self.loading(false)
            }

            this.loadEntryIntoEditor = function(data) {
                // self.loading(true)

                self.editingData(data);

                var tile = self.tile();

                /* force the value of current tile data observables */ 
                Object.keys(tile.data).forEach(function(key) {
                    if (ko.isObservable(tile.data[key])) {
                        tile.data[key](data[key]);
                    }
                });

                // self.loading(false)
            }

            this.save = function() {
                self.loading(true);

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

                    // BUG HERE MAYBE
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
                            function(){/* onFail */},
                            function(savedTileData) {
                                var previousTileData = ko.utils.arrayFirst(self.savedData(), function(savedDatum) {
                                    return savedDatum.tileid === savedTileData.tileid;
                                });

                                self.savedData.replace(previousTileData, savedTileData);
                                self.addedData.replace(previousTileData.data, savedTileData.data);
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

                self.tile().reset();
            };

            this.reset = function() {
                self.editingData(false);
                self.tile().reset();

                self.addedData.removeAll();
                self.savedData.removeAll();

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

        this.resourceId = ko.observable();
        if (ko.unwrap(params.resourceid)) {
            self.resourceId(ko.unwrap(params.resourceid));
        } 
        else if (params.workflow && ko.unwrap(params.workflow.resourceId)) {
            self.resourceId(ko.unwrap(params.workflow.resourceId));
        } 

        this.complete = params.complete || ko.observable(false);

        this.dataToPersist = ko.observable({});
        self.dataToPersist.subscribe(function(data) {
            params.value(data);
        })

        this.hasUnsavedData = ko.observable(false);
        this.hasUnsavedData.subscribe(function(hasUnsavedData) {
            params.hasDirtyTile(hasUnsavedData);
        })

        /* 
            `pageLayout` is an observableArray of arrays representing section Information ( `sectionInfo` ).

            `sectionInfo` is an array where the first item is the `sectionTitle` parameter, and the second 
            item is an array of `uniqueInstanceName`.
        */ 
        this.pageLayout = ko.observableArray();
        
        /*
            `workflowComponentAbstractLookup` is an object where we pair a `uniqueInstanceName` 
            key to `WorkflowComponentAbstract` class objects.
        */ 
        this.workflowComponentAbstractLookup = ko.observable({});

        this.loading = ko.computed(function() {
            var isLoading = false;

            /* if no components loaded */ 
            if ( !Object.values(self.workflowComponentAbstractLookup()).length ) {
                isLoading = true;
            }

            Object.values(self.workflowComponentAbstractLookup()).forEach(function(workflowComponentAbstract) {
                if (
                    workflowComponentAbstract.tilesManaged === 'one'
                    || workflowComponentAbstract.tilesManaged === 'many'
                ) {
                    if (workflowComponentAbstract.loading()) {
                        isLoading = true;
                    }
                }
            });

            return isLoading;
        })

        this.initialize = function() {
            params.clearCallback(self.reset);

            params.preSaveCallback(self.save);
    
            params.postSaveCallback(function() {
                self.hasUnsavedData(false);
            });

            ko.toJS(params.layoutSections).forEach(function(layoutSection) {
                var uniqueInstanceNames = [];

                layoutSection.componentConfigs.forEach(function(workflowComponentAbtractData) {
                    uniqueInstanceNames.push(workflowComponentAbtractData.uniqueInstanceName);

                    var previouslyPersistedData = ko.unwrap(params.value);

                    var previouslyPersistedComponentData;
                    if (previouslyPersistedData && previouslyPersistedData[workflowComponentAbtractData.uniqueInstanceName]) {
                        previouslyPersistedComponentData = previouslyPersistedData[workflowComponentAbtractData.uniqueInstanceName];
                    }

                    self.updateWorkflowComponentAbstractLookup(workflowComponentAbtractData, previouslyPersistedComponentData);
                });

                var sectionInfo = [layoutSection.sectionTitle, uniqueInstanceNames];

                self.pageLayout.push(sectionInfo);
            });
        };

        this.updateWorkflowComponentAbstractLookup = function(workflowComponentAbtractData, previouslyPersistedComponentData) {
            var workflowComponentAbstractLookup = self.workflowComponentAbstractLookup();

            var workflowComponentAbstract = new WorkflowComponentAbstract(
                workflowComponentAbtractData, 
                self.loading,
                params.title, 
                previouslyPersistedComponentData, 
                self.resourceId
            );

            workflowComponentAbstract.savedData.subscribe(function() {
                var dataToPersist = self.dataToPersist();
                dataToPersist[workflowComponentAbtractData.uniqueInstanceName] = koMapping.toJS(workflowComponentAbstract.savedData());
                self.dataToPersist(dataToPersist);
            });

            /* 
                checks if all `workflowComponentAbstract`s have saved data if a single `workflowComponentAbstract` 
                updates its data, neccessary for correct aggregate behavior
            */
            workflowComponentAbstract.hasUnsavedData.subscribe(function() {
                var hasUnsavedData = Object.values(self.workflowComponentAbstractLookup()).reduce(function(acc, workflowComponentAbstract) {
                    if (workflowComponentAbstract.hasUnsavedData()) {
                        acc = true;
                    } 
                    return acc;
                }, false);

                self.hasUnsavedData(hasUnsavedData);
            });

            workflowComponentAbstractLookup[workflowComponentAbtractData.uniqueInstanceName] = workflowComponentAbstract;

            self.workflowComponentAbstractLookup(workflowComponentAbstractLookup);
        };

        this.save = function() {
            Object.values(self.workflowComponentAbstractLookup()).forEach(function(workflowComponentAbstract) {
                if (workflowComponentAbstract.hasUnsavedData()) {
                    workflowComponentAbstract.save();
                } 
            });
        };

        this.reset = function() {
            Object.values(self.workflowComponentAbstractLookup()).forEach(function(workflowComponentAbstract) {
                workflowComponentAbstract.reset();
            });
            self.hasUnsavedData(false);
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
