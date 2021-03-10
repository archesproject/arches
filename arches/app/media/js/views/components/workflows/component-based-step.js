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
    function ComponentFOO(componentConfig, loading, title) {
        var self = this;

        var params = componentConfig.parameters;  /* CLEAN THIS OUT */

        this.resourceId = ko.observable();
        if (ko.unwrap(params.resourceid)) {
            self.resourceId(ko.unwrap(params.resourceid));
        } 
        else if (params.workflow && ko.unwrap(params.workflow.resourceId)) {
            self.resourceId(ko.unwrap(params.workflow.resourceId));
        } 

        this.componentName = componentConfig.componentName;
        this.componentParameters = componentConfig.parameters;

        this.manageTile = componentConfig.manageTile || false;
        this.manageMultipleTiles = componentConfig.manageMultipleTiles || false;

        // this.loading = ko.observable(loading());  /* MUST NOT be able to set parent loading state */

        this.loading = loading;

        this.initialize = function() {
            if (this.manageTile) {
                self.initializeTileBasedComponent();
            }
            else if (this.manageMultipleTiles) {
                self.initializeMultipleTileBasedComponent();
            }
        };

        this.initializeTileBasedComponent = function() {
            self.tile = ko.observable();
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
                
                console.log("REALLY?00011", self, componentConfig)
                loading(false)
            });
        };

        this.initializeMultipleTileBasedComponent = function() {
            this.manageTile = true;
            this.addedTileData = ko.observableArray();

            this.itemName = ko.observable(ko.unwrap(title) ? ko.unwrap(title) : 'Items');

            this.addTile = function() {
                var tileData = koMapping.toJS(self.tile().data);
                this.addedTileData.unshift(tileData);
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

        this.value = params.value || ko.observable();



        // REFACTOR TO INCLUDE ALL COMPONENTS
        this.loading = params.loading || ko.observable();
        this.loading(true);
        
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
        this.componentFOOLookup = {};

        /* END source-of-truth for page data */
        



        this.initialize = function() {
            ko.toJS(params.layoutSections).forEach(function(layoutSection) {
                var componentFOONames = [];

                layoutSection.componentConfigs.forEach(function(componentFOOData) {
                    componentFOONames.push(componentFOOData.uniqueInstanceName);
                    self.componentFOOLookup[componentFOOData.uniqueInstanceName] = new ComponentFOO(componentFOOData, self.loading, params.title);
                });

                var sectionInfo = [layoutSection.sectionTitle, componentFOONames];

                self.pageLayout.push(sectionInfo);
            });


            // var cachedValue = ko.unwrap(params.value);

            // if (cachedValue && cachedValue.pageLayout.sections) {
            //     this.updatePageLayout(cachedValue.pageLayout.sections);
            // }
            // else {
            // }


            // this.updatePageLayout(params.layoutSections);

        };

        this.updatePageLayout = function(layoutSections) {
            self.pageLayout.sections([]); /* clear page section data */

            var requiredComponentData = {};

            var hasAllRequiredComponentData = function(requiredComponentData) {
                return Object.values(requiredComponentData).reduce(function(acc, value) {
                    if (!value()) { acc = false; }
                    return acc;
                }, true);
            };

            ko.toJS(layoutSections).forEach(function(layoutSection) {
                var section = new Section(layoutSection.sectionTitle);

                layoutSection.componentConfigs.forEach(function(componentConfigData) {
                    var componentConfig = new ComponentConfig(componentConfigData, self.rootPageVm);

                    /* save value on update */ 
                    componentConfig.value.subscribe(function() {
                        params.value(params.defineStateProperties());
                    });


                    // WATCHES REQUIRED VALUES AND AUTO_COMPLETES CARD
                    // /* if a component is marked as 'required' let's add a subscription to track its value */ 
                    // if (componentConfig.required()) {
                    //     requiredComponentData[componentConfig.uniqueInstanceName()] = ko.observable(componentConfig.value());

                    //     componentConfig.value.subscribe(function(value) {
                    //         requiredComponentData[componentConfig.uniqueInstanceName()](value);
                    //         hasAllRequiredComponentData(requiredComponentData) ? self.complete(true) : self.complete(false);
                    //     });
                    // }

                    section.componentConfigs.push(componentConfig);
                });

                self.pageLayout.sections.push(section);
                hasAllRequiredComponentData(requiredComponentData) ? self.complete(true) : self.complete(false);
            });
        };

        this.quit = function() {
            // this.complete(false);
            // self.updatePageLayout(koMapping.toJS(params.layoutSections));
            // self.setStateProperties();
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
