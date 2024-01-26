define([
    'underscore',
    'jquery',
    'knockout',
    'knockout-mapping',
    'arches',
    'models/graph',
    'viewmodels/card',
    'viewmodels/provisional-tile',
    'viewmodels/alert',
    'uuid',
    'js-cookie',
    'templates/views/components/workflows/workflow-component-abstract.htm',
], function(_, $, ko, koMapping, arches, GraphModel, CardViewModel, ProvisionalTileViewModel, AlertViewModel, uuid, Cookies, workflowComponentAbstractTemplate) {
    function NonTileBasedComponent() {
        var self = this;
         

        this.initialize = function() {
            self.loading(false);
        };

        this.save = function() {
            self.complete(false);
            self.saving(true);

            self.setToWorkflowHistory('value', self.value()).then(() => {
                self.savedData(self.value());
                self.complete(true);
                self.saving(false);
            });
        };

        this.reset = function() {
            self.value(self.savedData() ? self.savedData() : null);
        };

        this.initialize();
    }


    function TileBasedComponent() {
        var self = this;
         

        this.tile = ko.observable();
        this.tiles = ko.observable();

        this.card = ko.observable();
        this.topCards = ko.observable();

        this.loadData = function(loadedData) {
            let data;
            if (!Array.isArray(loadedData)) {
                data = [loadedData];
            }
            else {
                data = loadedData;
            }
            
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
                self.tile.subscribe(function(tile) {
                    if (!self.tiles()) {
                        self.tiles([tile]);
                    } 
                });

                self.tiles.subscribe(function(tiles) {
                    if (tiles && !self.saving()) {
                        if (self.savedData()) {  /* if the refresh after tile save */
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
                self.componentData.parameters.dirty = self.dirty;
                self.componentData.parameters.save = self.save;
                self.componentData.parameters.tiles = self.tiles;
    
                self.loading(false);
            });
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
    }

    function AbstractCardAdapter() {  // CURRENTLY IN DEVLEOPMENT, USE AT YOUR OWN RISK!
        var self = this;
        this.cardinality = ko.observable();

        this.initialize = function() {
            self.loading(true);
            
            $.getJSON(( arches.urls.api_nodegroup(self.componentData.parameters['nodegroupid']) ), function(nodegroupData) {
                self.cardinality(nodegroupData.cardinality);

                const resourceInstanceDataPromise = new Promise(function(resolve, _reject) {
                    const resourceInstanceId = self.componentData.parameters['resourceid'];
    
                    if (resourceInstanceId) {
                        $.getJSON(
                            ( arches.urls.resource + `/${resourceInstanceId}/tiles?nodeid=${self.componentData.parameters['nodegroupid']}`),
                            function(data) {
                                resolve(data);
                            }
                        );
                    }
                    else {
                        resolve(null);
                    }
                });

                resourceInstanceDataPromise.then( function(data) {
                    if (self.cardinality() === '1') {
                        if (data && data['tiles'].length) {
                            self.componentData.parameters['tileid'] = data['tiles'][0]['tileid'];
                            self.complete(true);
                        }
                        TileBasedComponent.apply(self);
                    }
                    else if (self.cardinality() === 'n') {
                        MultipleTileBasedComponent.apply(self);
                        if (data && data['tiles'].length) {
                            self.complete(true);
                        }
                        
                        self.card.subscribe(function(card) {
                            if (!card.selected()) {
                                card.selected(card.tiles().length);
                            }
                        });

                        self.onSaveSuccess = function(savedData) {  // LEGACY -- DO NOT USE
                            if (!(savedData instanceof Array)) { savedData = [savedData]; }

                            let previouslySavedData = self.savedData();
                            if (!previouslySavedData) {
                                previouslySavedData = [];
                            }

                            self.savedData(
                                previouslySavedData.concat(
                                    savedData.map(function(savedDatum) {
                                        return {
                                            tileData: savedDatum._tileData(),
                                            tileId: savedDatum.tileid,
                                            nodegroupId: savedDatum.nodegroup_id,
                                            resourceInstanceId: savedDatum.resourceinstance_id,
                                        };
                                    })
                                )
                            );

                            self.value(self.savedData());

                            self.componentData.parameters.dirty(false);
                            self.card().getNewTile(true);  // `true` is forceNewTile
                            self.card().selected(true);
                            self.dirty(false);
                            self.saving(false);
                            self.complete(true);

                            /**
                             * TODO: this is a hack to get around previous data autofilling forms when creating a new tile in cardinality n cards
                             * It should be removed when we're able to figure out how to prevent that logic
                             * */ 
                            window.location.reload();  
                        };
                    }
                });

            });
        };

        this.initialize();
    }


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
            else if (self.savedData() ) {
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
            self.multiTileUpdated(hasDirtyTiles);
            return hasDirtyTiles;
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

                    if (self.savedData()) {
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

        this.saveMultiTiles = function() {
            self.complete(false);
            self.saving(true);
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
                        return savedData.find(function(datum) {
                            return datum.tileid === tile.tileid;
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
    }


    function WorkflowComponentAbstract(params) {
        var self = this;

        this.workflowId = params.workflowId;
        this.workflowName = params.workflowName;
        this.componentData = params.componentData;
        this.workflowHistory = params.workflowHistory;
        this.alert = params.alert;
        
        this.locked = params.locked;
        this.lockExternalStep = params.lockExternalStep;
        this.lockableExternalSteps = params.lockableExternalSteps;

        this.id = ko.observable();

        this.resourceId = ko.observable();
                
        this.loading = ko.observable(false);
        this.saving = ko.observable(false);

        this.savedComponentPaths = {};
        this.value = ko.observable(null);

        this.complete = ko.observable(false);
        this.error = ko.observable();
        this.dirty = ko.observable(); /* user can manually set dirty state */

        this.AlertViewModel = AlertViewModel;
        this.saveOnQuit = ko.observable();

        this.isStepActive = params.isStepActive;
        this.isStepActive.subscribe(function(stepActive) {
            if (stepActive) {
                self.loadComponent();
            }
        });

        this.savedData = ko.observable(null);
        this.savedData.subscribe(function(savedData) {
            self.setToWorkflowHistory('value', savedData);
        });

        this.multiTileUpdated = ko.observable();
        this.hasUnsavedData = ko.computed(function() {
            var hasUnsavedData = false;

            if (self.componentData.tilesManaged === "many") {
                if (self.multiTileUpdated()) {
                    hasUnsavedData = true;
                }
            } else {
                if (!_.isEqual(self.savedData(), self.value())) {
                    hasUnsavedData = true;
                }
                else if (self.dirty()) {
                    hasUnsavedData = true;
                }
            }

            return hasUnsavedData;
        });

        this.initialize = function() {
            /* cached ID logic */ 
            if (params.workflowComponentAbstractId) {
                self.id(params.workflowComponentAbstractId);
            }
            else {
                self.id(uuid.generate());
            }

            const savedValue = self.getSavedValue();
            if (savedValue) {
                self.savedData(savedValue);
                self.value(savedValue);
                self.complete(true);
            }
        };

        this.loadComponent = function() {
            self.loading(true);
    
            /* 
                Checks format of parameter values for external-component-path-patterned arrays.
                If parameter value matches pattern, get external component data and update value in self.componentData
            */ 
            if (self.componentData.parameters) {
                Object.keys(self.componentData.parameters).forEach(function(componentDataKey) {
                    var componentDataValue = self.componentData.parameters[componentDataKey];

                    if (params.isValidComponentPath(componentDataValue)) {
                        self.componentData.parameters[componentDataKey] = params.getDataFromComponentPath(componentDataValue);
                        self.savedComponentPaths[componentDataKey] = componentDataValue;
                    }
                    else if (self.savedComponentPaths[componentDataKey]) {
                        self.componentData.parameters[componentDataKey] = params.getDataFromComponentPath(self.savedComponentPaths[componentDataKey]);
                    }
                });
            }

            if (self.savedData()) {
                self.value(self.savedData());
                self.complete(true);
            }

            if (self.componentData && self.componentData['parameters']) {
                self.resourceId(ko.unwrap(self.componentData['parameters']['resourceid']));
                self.componentData['parameters']['renderContext'] = 'workflow';
            }

            if (self.componentData.componentType === 'card') {
                let previouslySavedValue = self.getSavedValue();
                let previouslySavedResourceInstanceId;

                if (previouslySavedValue) {
                    if (!(previouslySavedValue instanceof Array)) { previouslySavedValue = [previouslySavedValue]; }
    
                    if (previouslySavedValue[0]['resourceInstanceId']) {
                        previouslySavedResourceInstanceId = previouslySavedValue[0]['resourceInstanceId'];
                        params['componentData']['parameters']['resourceid'] =  previouslySavedResourceInstanceId;
                    }
                }

                AbstractCardAdapter.apply(self);
            }

            else if (!self.componentData.tilesManaged || self.componentData.tilesManaged === "none") {
                NonTileBasedComponent.apply(self);
            }
            else if (self.componentData.tilesManaged === "one") {
                TileBasedComponent.apply(self);
            }
            else if (self.componentData.tilesManaged === "many") {
                MultipleTileBasedComponent.apply(self, [params.title] );
            }
        };

        this.setToWorkflowHistory = async function(key, value) {
            const workflowid = self.workflowId;
            const workflowname = self.workflowName;
            
            const workflowHistory = {
                workflowid,
                workflowname,
                completed: false,
                componentdata: {
                    // Django view will patch in this key, keeping existing keys
                    [self.id()]: {
                        [key]: value,
                    },
                },
            };

            await fetch(arches.urls.workflow_history + workflowid, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                },
                body: JSON.stringify(workflowHistory),
            });

        };

        this.getSavedValue = function() {
            const savedValue = this.workflowHistory.componentdata?.[self.id()];
            if (savedValue) {
                return savedValue['value'];
            }
        };

        this.getCardResourceIdOrGraphId = function() {
            return (ko.unwrap(self.componentData.parameters.resourceid) || ko.unwrap(self.componentData.parameters.graphid));
        };

        this.save = function(){};  /* overwritten by inherited components */

        this._saveComponent = function(componentBasedStepResolve, componentBasedStepReject) {
            self.complete(false);
            var completeSubscription = self.complete.subscribe(function(complete) {
                if (complete) {

                    if (componentBasedStepResolve) {
                        componentBasedStepResolve({
                            [self.componentData.uniqueInstanceName]: self.savedData(),
                        });
                    }
                    completeSubscription.dispose();  /* disposes after save */
                    errorSubscription.dispose();  /* disposes after save */
                }
            });

            var errorSubscription = self.error.subscribe(function(error) {
                if (error) {

                    if (componentBasedStepReject) {
                        componentBasedStepReject(error);
                        self.error(null);
                    }
                    completeSubscription.dispose();  /* disposes after save */
                    errorSubscription.dispose();  /* disposes after save */
                }
            });

            // only saves updated tiles
            if (ko.unwrap(self.dirty) || ko.unwrap(self.hasDirtyTiles) || ko.unwrap(self.hasUnsavedData)) {
                if (self.componentData.tilesManaged === "many"){
                    self.saveMultiTiles();
                } else {
                    self.save();
                }
            }
            else {
                self.complete(true);
            }
        };

        this._resetComponent = function(componentBasedStepResolve) {
            if (ko.unwrap(self.tile)) {
                ko.unwrap(self.tile).reset();
            }

            componentBasedStepResolve(self.reset());
        };

        this.initialize();
    }

    ko.components.register('workflow-component-abstract', {
        template: workflowComponentAbstractTemplate,
    });

    return WorkflowComponentAbstract;
});
