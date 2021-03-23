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
    function NonTileBasedComponent(complete) {
        var self = this;

        this.value = ko.observable();
        this.value.subscribe(function(value) {
            self.addedData.remove(function(datum) {
                return datum[0] === self.componentData.uniqueInstanceName
            });

            self.addedData.push([self.componentData.uniqueInstanceName, value]);
        });

        this.initialize = function() {
            if (self.previouslyPersistedComponentData) {
                self.value(self.previouslyPersistedComponentData[0][1]);
            }
            
            self.loading(false);
        };

        this.save = function() {
            complete(true);
            self.savedData(self.addedData());
        };

        this.reset = function() {
            self.value(self.previouslyPersistedComponentData ? self.previouslyPersistedComponentData[0][1] : null)
            self.addedData.removeAll();
        };

        this.initialize();
    };


    function TileBasedComponent() {
        var self = this;

        this.tile = ko.observable();
        this.card = ko.observable();
        this.topCards = ko.observable();

        self.isDirty = ko.computed(function() {
            if (self.tile()) {
                return self.tile().dirty();
            }
            return false;
        });

        this.initialize = function() {
            if (self.componentData.tilesManaged === "one") {
                self.tile.subscribe(function(tile) {
                    if (tile) {
                        if (self.previouslyPersistedComponentData) {
                            self.savedData(self.previouslyPersistedComponentData);
                            self.addedData.push(self.previouslyPersistedComponentData[0].data);

                            /* force the value of current tile data observables */ 
                            Object.keys(tile.data).forEach(function(key) {
                                if (ko.isObservable(tile.data[key])) {
                                    tile.data[key](self.previouslyPersistedComponentData[0].data[key]);
                                }
                            });

                            tile._tileData(koMapping.toJSON(tile.data));
                        }
                    }
                });

                self.isDirty.subscribe(function(dirty) {
                    if (dirty && !self.loading()) {
                        self.addedData.removeAll();
                        self.addedData.push(ko.toJS(self.tile().data));
                    }
                });
            }
    
            $.getJSON(( arches.urls.api_card + this.getCardResourceIdOrGraphId() ), function(data) {
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
                    self.componentData.parameters.nodegroupid = self.componentData.parameters.nodegroupid || card.nodegroup_id;
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
    
                flattenTree(self.topCards, []).forEach(function(item) {
                    if (item.constructor.name === 'CardViewModel' && item.nodegroupid === ko.unwrap(self.componentData.parameters.nodegroupid)) {
                        if (ko.unwrap(self.componentData.parameters.parenttileid) && item.parent && ko.unwrap(self.componentData.parameters.parenttileid) !== item.parent.tileid) {
                            return;
                        }
                        if (self.customCardLabel) item.model.name(ko.unwrap(self.customCardLabel));
                        self.card(item);
                        if (ko.unwrap(self.componentData.parameters.tileid)) {
                            ko.unwrap(item.tiles).forEach(function(tile) {
                                if (tile.tileid === ko.unwrap(self.componentData.parameters.tileid)) {
                                    self.tile(tile);
                                }
                            });
                        } else if (ko.unwrap(self.componentData.parameters.createTile) !== false) {
                            self.tile(item.getNewTile());
                        }
                    }
                });
    
                self.componentData.parameters.card = self.card();
                self.componentData.parameters.tile = self.tile();
                self.componentData.parameters.loading = self.loading;
                self.componentData.parameters.provisionalTileViewModel = self.provisionalTileViewModel;
                self.componentData.parameters.reviewer = data.userisreviewer;
    
                self.loading(false);
            });
        };

        this.save = function() {
            self.tile().save(
                function(){ /* onFail */ },
                function(savedTileData) {
                    self.savedData.removeAll();
                    self.savedData.unshift(savedTileData);
                    self.complete(true);
                }
            );
        };

        this.reset = function() {
            self.tile().reset();

            self.addedData.removeAll();
            self.addedData.unshift(self.savedData()[0].data);
        };

        this.initialize();
    };


    function MultipleTileBasedComponent(title) {
        var self = this;

        this.currentlyEditedData = ko.observable(null);
        this.itemName = ko.observable(ko.unwrap(title) ? ko.unwrap(title) : 'Items');

        TileBasedComponent.apply(this);

        this.initialize = function() {
            if (self.previouslyPersistedComponentData) {
                self.previouslyPersistedComponentData.forEach(function(previouslyPersistedDatum) {
                    if (previouslyPersistedDatum.tileid) {
                        /* add tileid to nodeData for reference. */ 
                        previouslyPersistedDatum.data.tileid = previouslyPersistedDatum.tileid;
                    }
    
                    self.addedData.push(previouslyPersistedDatum.data);
                    self.savedData.push(previouslyPersistedDatum);
                });
            }
        };

        this.addOrUpdateEntry = function() {
            var tileData = koMapping.toJS(self.tile().data);
            var currentlyEditedData = self.currentlyEditedData();
            
            if (currentlyEditedData) {
                tileData.tileid = currentlyEditedData.tileid;
                self.addedData.replace(currentlyEditedData, tileData);
                self.currentlyEditedData(null);
            }
            else {
                self.addedData.unshift(tileData);
            }

            self.tile().reset();
        };

        this.loadEntryIntoEditor = function(data) {
            self.currentlyEditedData(data);

            var tile = self.tile();

            /* force the value of current tile data observables */ 
            Object.keys(tile.data).forEach(function(key) {
                if (ko.isObservable(tile.data[key])) {
                    tile.data[key](data[key]);
                }
            });
        };

        this.save = function() {
            self.loading(true);
            var processedTiles = ko.observableArray([]);
            processedTiles.subscribe(function(tiles){
                var allData = self.addedData().length + self.savedData().length;
                if (tiles.length <= allData) {
                    self.complete(true);
                }
            })

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
                            processedTiles.push(savedTileData);
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
                        function(){/* onFail */},
                        function(savedTileData) {
                            var previousTileData = ko.utils.arrayFirst(self.savedData(), function(savedDatum) {
                                return savedDatum.tileid === savedTileData.tileid;
                            });

                            self.savedData.replace(previousTileData, savedTileData);
                            self.addedData.replace(previousTileData.data, savedTileData.data);
                            processedTiles.push(savedTileData);
                        },
                    )

                    self.tile(self.card().getNewTile());
                }
            });

            removedTiles.forEach(function(data) {
                var tile = self.tile();
                tile.tileid = data.tileid;

                tile.deleteTile();
                processedTiles.push(data)
            });

            self.savedData.removeAll(removedTiles);

            self.currentlyEditedData(null);
            self.tile().reset();
        };

        this.clearForm = function() {
            var tile = self.tile();

            Object.keys(tile.data).forEach(function(key) {
                if (ko.isObservable(tile.data[key])) {
                    tile.data[key](null);
                }
            });
        };

        this.reset = function() {
            self.currentlyEditedData(null);
            self.tile().reset();

            self.addedData.removeAll();
            self.savedData.removeAll();

            if (self.previouslyPersistedComponentData) {
                self.previouslyPersistedComponentData.forEach(function(previouslyPersistedDatum) {
                    if (previouslyPersistedDatum.tileid) {
                        /* add tileid to nodeData for reference. */ 
                        previouslyPersistedDatum.data.tileid = previouslyPersistedDatum.tileid;
                    }

                    self.addedData.push(previouslyPersistedDatum.data);
                    self.savedData.push(previouslyPersistedDatum);
                });
            }
        };

        this.initialize();
    };


    function WorkflowComponentAbstract(componentData, previouslyPersistedComponentData, resourceId, title, complete) {
        var self = this;
        this.complete = complete;
        this.resourceId = resourceId;
        this.componentData = componentData;
        this.previouslyPersistedComponentData = previouslyPersistedComponentData;

        this.loading = ko.observable(true);

        this.addedData = ko.observableArray();
        this.savedData = ko.observableArray();

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
            if (!componentData.tilesManaged || componentData.tilesManaged === "none") {
                NonTileBasedComponent.apply(self, [complete]);
            }
            else if (componentData.tilesManaged === "one") {
                TileBasedComponent.apply(self);
            }
            else if (componentData.tilesManaged === "many") {
                MultipleTileBasedComponent.apply(self, [title] );
            }
        };

        this.getCardResourceIdOrGraphId = function() {
            return (ko.unwrap(this.resourceId) || ko.unwrap(componentData.parameters.graphid));
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
                if (workflowComponentAbstract.loading()) {
                    isLoading = true;
                }
            });

            return isLoading;
        });

        this.initialize = function() {
            if (ko.isObservable(params.loading)) {
                this.loading.subscribe(function(loading) {
                    params.loading(loading);
                })
            };
            
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
                previouslyPersistedComponentData, 
                self.resourceId,
                params.title, 
                self.complete
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

            // self.complete(true);
        };

        this.reset = function() {
            Object.values(self.workflowComponentAbstractLookup()).forEach(function(workflowComponentAbstract) {
                workflowComponentAbstract.reset();
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
