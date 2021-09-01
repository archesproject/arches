define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'models/graph',
    'viewmodels/card',
    'viewmodels/provisional-tile',
    'viewmodels/alert',
    'uuid',
], function(_, $, arches, ko, koMapping, GraphModel, CardViewModel, ProvisionalTileViewModel, AlertViewModel, uuid) {
    WORKFLOW_COMPONENT_ABSTRACTS_LABEL = 'workflow-component-abstracts';

    function NonTileBasedComponent() {
        var self = this;

        this.addedData = ko.observableArray();

        this.value.subscribe(function(value) {
            self.addedData.remove(function(datum) {
                return datum[0] === self.componentData.uniqueInstanceName
            });

            self.addedData.push([self.componentData.uniqueInstanceName, value]);
            if (self.previouslyPersistedComponentData) {
                self.hasUnsavedData(!(_.isEqual(value, self.previouslyPersistedComponentData[0][1])));
            }
            else{
                self.hasUnsavedData(!!value);
            }
            self.hasUnsavedData.valueHasMutated();
        });

        this.initialize = function() {
            if (self.previouslyPersistedComponentData) {
                self.value(self.previouslyPersistedComponentData[0][1]);
            }
            self.loading(false);
        };

        this.save = function() {
            self.complete(false);
            self.saving(true);

            self.savedData(self.addedData());
            
            self.complete(true);
            self.saving(false);
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
        this.tiles = ko.observable();

        this.card = ko.observable();
        this.topCards = ko.observable();

        self.isDirty = ko.observable();

        self.saveFunction = ko.observable();

        this.loadData = function(data) {
            /* a flat object of the previously saved data for all tiles */ 
            var tileDataLookup = data.reduce(function(acc, componentData) {
                var parsedTileData = componentData.data || JSON.parse(componentData.tileData);

                Object.keys(parsedTileData).forEach(function(key) {
                    acc[key] = parsedTileData[key];
                });

                return acc;
            }, {});

            self.tiles().forEach(function(tile) {
                /* force the value of current tile data observables */
                Object.keys(tile.data).forEach(function(key) {
                    if (ko.isObservable(tile.data[key])) {
                        tile.data[key](tileDataLookup[key]);
                    }
                });
                tile._tileData(koMapping.toJSON(tile.data));
                
                data.forEach(function(datum){                    
                    if (datum.tileData) {
                        if (JSON.stringify(Object.keys(koMapping.toJS(tile.data)).sort()) 
                            === JSON.stringify(Object.keys(JSON.parse(datum.tileData)).sort())) {
                            tile.nodegroup_id = datum.nodegroupId;
                            tile.tileid = datum.tileId;
                            tile.resourceinstance_id = datum.resourceInstanceId;        
                        }
                    }
                });
            });
        };

        this.initialize = function() {
            if (self.componentData.tilesManaged === "one") {
                self.isDirty.subscribe(function(dirty) {
                    self.hasUnsavedData(dirty);
                });

                self.tile.subscribe(function(tile) {
                    if (!self.tiles()) {
                        self.tiles([tile]);
                    } 
                });

                self.tiles.subscribe(function(tiles) {
                    if (tiles && !self.saving()) {
                        if (self.savedData().length) {  /* if the refresh after tile save */
                            self.loadData(self.savedData());
                        }
                        else if (self.previouslyPersistedComponentData) { /* if previously saved data */
                            self.loadData(self.previouslyPersistedComponentData);
                        }
                       
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

                self.graphModel = graphModel;
    
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

                self.card.subscribe(function(card){
                    if (ko.unwrap(card.widgets) && self.componentData.parameters.hiddenNodes) {
                        card.widgets().forEach(function(widget){
                            if (self.componentData.parameters.hiddenNodes.indexOf(widget.node_id()) > -1) {
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

                self.flattenTree(self.topCards, []).forEach(function(item) {
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
                self.componentData.parameters.dirty = self.isDirty;
                self.componentData.parameters.saveFunction = self.saveFunction;
                self.componentData.parameters.tiles = self.tiles;




                // setTimeout(function() {
                //     console.log('adfs90')
                //     self.save = function(){
                //         console.log('sdf9sdf0')
                //         self.save()
                //     };
                // }, 7000)

                // Object.defineProperty(Object.prototype, "save", {
                //     set: function (value) {
                //         this._value = value;
                //     },
                //     get: function () {
                //         return "changed";
                //     }
                // });

                // var foo = {
                //     set: function(target, prop, val) {
                //         if (prop === 'save') {
                //             console.log(prop)
                //             target[prop] = function(){
                //                 console.log('90dsf')
                //                 val();
                //             };
                //             return false
                //         }
                //         else {
                //             target[prop] = val;
                //             return true;
                //         }
                //     }
                // };
        
                self.bar = new Proxy(self, {});

                var baz = {
                    apply: function(target, thisArg, argumentsList) {

                        console.log("hmmmm")
                    }
                  }

                self.save = new Proxy(self.bar.save, baz)
    
                self.loading(false);
            });
        };

        this.save = function() {
            self.complete(false);

            self.saving(true);

            var saveFunction = self.saveFunction();

            if (saveFunction) { saveFunction(); }

            self.saving(false);
        };

        this.onSaveSuccess = function(savedData) {  // LEGACY -- DO NOT USE
            if (!(savedData instanceof Array)) { savedData = [savedData]; }
            
            self.savedData(savedData.map(function(savedDatum) {
                return {
                    tileData: savedDatum._tileData(),
                    tileId: savedDatum.tileid,
                    nodegroupId: savedDatum.nodegroup_id,
                    resourceInstanceId: savedDatum.resourceinstance_id,
                };
            }));

            self.saving(false);
            self.complete(true);
        };

        this.reset = function() {
            self.tiles().forEach(function(tile) {
                tile.reset();
            });
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

        this.getTiles = function(nodegroupId, tileId) {
            var tiles = [];
            this.flattenTree(self.topCards, []).forEach(function(item) {
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

        this.initialize();
    };


    function MultipleTileBasedComponent(title) {
        var self = this;
        TileBasedComponent.apply(this);

        this.tileLoadedInEditor = ko.observable();

        this.itemName = ko.observable(ko.unwrap(title) ? ko.unwrap(title) : 'Items');

        this.hasDirtyTiles = ko.computed(function() {
            var tiles = self.tiles();
            var hasDirtyTiles = false;

            if (!tiles) { 
                hasDirtyTiles = true; 
            }
            else if (self.savedData().length ) {
                if (self.savedData().length !== tiles.length) {
                    hasDirtyTiles = true;
                }

                self.savedData().forEach(function(savedDatum) {
                    var matchingTile = tiles.find(function(tile) {
                        return tile.tileid === savedDatum.tileid;
                    });

                    if (!matchingTile) {
                        hasDirtyTiles = true;
                    }
                    else if (!_.isEqual(savedDatum.data, koMapping.toJS(matchingTile.data))) {
                        hasDirtyTiles = true;
                    }
                });
            }
            else if (!self.previouslyPersistedComponentData && tiles.length) {
                hasDirtyTiles = true;
            }
            else if (self.previouslyPersistedComponentData) {
                if (self.previouslyPersistedComponentData.length !== tiles.length) {
                    hasDirtyTiles = true;
                }

                self.previouslyPersistedComponentData.forEach(function(persistedComponentData) {
                    var matchingTile = tiles.find(function(tile) {
                        return tile.tileid === persistedComponentData.tileid;
                    });

                    if (!matchingTile) {
                        hasDirtyTiles = true;
                    }
                    else if (!_.isEqual(persistedComponentData.data, koMapping.toJS(matchingTile.data))) {
                        hasDirtyTiles = true;
                    }
                });
            }
            // else if (self.isDirty()) {
            //     hasDirtyTiles = true;
            // }

            return hasDirtyTiles;
        });
        self.hasDirtyTiles.subscribe(function(hasDirtyTiles) {
            self.hasUnsavedData(hasDirtyTiles);
        });
        
        this.initialize = function() {
            self.loading(true);

            var savingSubscription = self.saving.subscribe(function(saving) {
                if (!saving) {
                    savingSubscription.dispose(); /* self-disposing subscription only runs once */
                    self.initialize();
                }
            });

            var multiTileInitSubscription = self.tiles.subscribe(function(tiles) {
                /* 
                    at this point in load `self.tiles()` contains a reference to the empty
                    tile we're using to map values to other tiles. This removes the empty
                    mapping tile from being tracked
                */
                if (tiles.length === 1 && !tiles[0].tileid) {
                    var savedTiles = [];

                    if (self.savedData().length) {
                        var savedData = self.savedData();

                        savedData.forEach(function(savedDatum) {
                            var newTile = self.card().getNewTile(true);

                            newTile.tileid = savedDatum.tileid;
                            newTile.data = koMapping.fromJS(savedDatum.data);
                            
                            savedTiles.unshift(newTile);
                        });
                    }

                    multiTileInitSubscription.dispose();  /* self-disposing subscription only runs once */ 
                    self.tiles(savedTiles);
                }
            });

            /* load previously persisted data */ 
            var multiTilePersistedDataSubscription = self.tiles.subscribe(function(tiles) {
                if (self.previouslyPersistedComponentData && (!tiles || !tiles.length)) {
                    var persistedTiles = [];

                    self.previouslyPersistedComponentData.forEach(function(persistedComponentData) {
                        var newTile = self.card().getNewTile(true);

                        newTile.tileid = persistedComponentData.tileid;
                        newTile.data = koMapping.fromJS(persistedComponentData.data);

                        persistedTiles.unshift(newTile);
                    });

                    multiTilePersistedDataSubscription.dispose();  /* self-disposing subscription only runs once */ 
                    self.tiles(persistedTiles);
                }
            });

        };

        this.addOrUpdateTile = function() {
            var tiles = self.tiles();
            self.tiles(null);

            /* breaks observable chain */ 
            var tileData = koMapping.fromJSON(
                koMapping.toJSON(self.tile().data)
            );

            var tileLoadedInEditor = self.tileLoadedInEditor();

            if (tileLoadedInEditor) {
                var index = _.findIndex(tiles, tileLoadedInEditor);
                
                if (index > -1) {
                    tileLoadedInEditor.data = tileData;
                    tiles[index] = tileLoadedInEditor;
                }

                
                self.tileLoadedInEditor(null);
            }
            else {
                var newTile = self.card().getNewTile(true);
                newTile.data = tileData;

                tiles.unshift(newTile);
            }

            self.tiles(tiles);
            self.tile().reset();
        };

        this.loadTileIntoEditor = function(data) {
            self.tileLoadedInEditor(data);

            var tile = self.tile();

            /* force the value of current tile data observables */ 
            Object.keys(tile.data).forEach(function(key) {
                if (ko.isObservable(tile.data[key])) {
                    tile.data[key](data.data[key]());
                }
            });
        };

        this.tilesToRemove = ko.observableArray();

        this.removeTile = function(data) {
            var filteredTiles = self.tiles().filter(function(tile) { return tile !== data; });
            if (data.tileid) {
                self.tilesToRemove.push(data);
            }
            self.tiles(filteredTiles);
        };

        this.save = function() {
            self.complete(false);
            self.saving(true);
            self.savedData.removeAll();
            self.previouslyPersistedComponentData = [];
            
            var unorderedSavedData = ko.observableArray();

            self.tiles().forEach(function(tile) {
                tile.save(
                    function(){/* onFail */}, 
                    function(savedTileData) {
                        unorderedSavedData.push(savedTileData);
                    }
                );
            });

            self.tilesToRemove().forEach(function(tile) {
                tile.deleteTile(
                    function(response) {
                        self.alert(new AlertViewModel(
                            'ep-alert-red', 
                            response.responseJSON.title,
                            response.responseJSON.message,
                            null, 
                            function(){ return; }
                        ));
                    },
                    function() {
                        self.tilesToRemove.remove(tile);
                        if ( self.tilesToRemove().length === 0 ) {
                            self.complete(true);
                            self.loading(true);
                            self.saving(false);
                        }
                    }
                );
            });

            var saveSubscription = unorderedSavedData.subscribe(function(savedData) {
                if (savedData.length === self.tiles().length) {
                    self.complete(true);
                    self.loading(true);
                    self.saving(false);

                    var orderedSavedData = self.tiles().map(function(tile) {
                        return savedData.find(function(zzz) {
                            return zzz.tileid === tile.tileid;
                        });
                    });

                    self.savedData(orderedSavedData.reverse());

                    saveSubscription.dispose();  /* self-disposing subscription only runs once */ 
                }
            });
        };

        this.clearEditor = function() {
            self.tile().reset();
        };

        this.reset = function() {
            self.tileLoadedInEditor(null);
            self.tile().reset();
            self.initialize();
            self.loading(false);
        };

        this.initialize();
    };


    function viewModel(params) {
        var self = this;

        console.log('asdf90fads90', params)

        // console.log("90ds", componentData, workflowComponentAbstractId, isValidComponentPath, getDataFromComponentPath, title, isStepSaving, locked, lockExternalStep, lockableExternalSteps, workflowId, alert, outerSaveOnQuit)
        this.workflowId = params.workflowId;
        this.componentData = params.componentData;
        this.alert = params.alert;
        
        this.locked = params.locked;
        this.lockExternalStep = params.lockExternalStep;
        this.lockableExternalSteps = params.lockableExternalSteps;

        this.id = ko.observable();

        this.resourceId = ko.observable();
                
        this.loading = ko.observable(false);
        this.saving = ko.observable(false);
        this.complete = ko.observable(false);


        this.savedData = ko.observableArray();
        this.hasUnsavedData = ko.observable();

        this.AlertViewModel = AlertViewModel;

        this.value = ko.observable();
        this.previouslyPersistedComponentData;

        this.saveOnQuit = ko.observable();
        this.saveOnQuit.subscribe(function(val){
            outerSaveOnQuit(val);
        });

        this.initialize = function() {
            self.loading(true);

            /* cached ID logic */ 
            if (params.workflowComponentAbstractId) {
                self.id(params.workflowComponentAbstractId)
            }
            else {
                self.id(uuid.generate());
            }

            /* 
                Checks format of parameter values for external-component-path-patterned arrays.
                If parameter value matches pattern, get external component data and update value in self.componentData
            */ 
            if (self.componentData.parameters) {
                Object.keys(self.componentData.parameters).forEach(function(componentDataKey) {
                    var componentDataValue = self.componentData.parameters[componentDataKey];
    
                    if (params.isValidComponentPath(componentDataValue)) {
                        self.componentData.parameters[componentDataKey] = params.getDataFromComponentPath(componentDataValue);
                    }
                });
            }

            self.previouslyPersistedComponentData = self.getFromLocalStorage('value');
            if (self.previouslyPersistedComponentData) {
                self.value(self.previouslyPersistedComponentData);
                self.complete(true);
            }

            if (self.componentData && self.componentData['parameters']) {
                self.resourceId(ko.unwrap(self.componentData['parameters']['resourceid']));
                self.componentData['parameters']['renderContext'] = 'workflow';
            }

            if (!self.componentData.tilesManaged || self.componentData.tilesManaged === "none") {
                NonTileBasedComponent.apply(self);
            }
            else if (self.componentData.tilesManaged === "one") {
                TileBasedComponent.apply(self);
            }
            else if (self.componentData.tilesManaged === "many") {
                MultipleTileBasedComponent.apply(self, [title] );
            }
        };

        this.setToLocalStorage = function(key, value) {
            var allComponentsLocalStorageData = JSON.parse(localStorage.getItem(WORKFLOW_COMPONENT_ABSTRACTS_LABEL)) || {};

            if (!allComponentsLocalStorageData[self.id()]) {
                allComponentsLocalStorageData[self.id()] = {};
            }

            allComponentsLocalStorageData[self.id()][key] = value ? koMapping.toJSON(value) : value;

            localStorage.setItem(
                WORKFLOW_COMPONENT_ABSTRACTS_LABEL, 
                JSON.stringify(allComponentsLocalStorageData)
            );
        };

        this.getFromLocalStorage = function(key) {
            var allComponentsLocalStorageData = JSON.parse(localStorage.getItem(WORKFLOW_COMPONENT_ABSTRACTS_LABEL)) || {};

            console.log(allComponentsLocalStorageData, self.id())
            if (allComponentsLocalStorageData[self.id()] && typeof allComponentsLocalStorageData[self.id()][key] !== "undefined") {
                return JSON.parse(allComponentsLocalStorageData[self.id()][key]);
            }
        };

        this.getCardResourceIdOrGraphId = function() {
            return (ko.unwrap(componentData.parameters.resourceid) || ko.unwrap(componentData.parameters.graphid));
        };

        this._saveComponent = function(componentBasedStepResolve) {
            var completeSubscription = self.complete.subscribe(function(complete) {
                if (complete) {
                    self.setToLocalStorage('value', self.savedData());

                    componentBasedStepResolve({
                        [self.componentData.uniqueInstanceName]: self.savedData(),
                    });

                    completeSubscription.dispose();  /* disposes after save */
                }
            });

            self.save();
        };

        this.initialize();
    }

    ko.components.register('workflow-component-abstract', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/workflow-component-abstract.htm'
        }
    });

    return viewModel;
});
