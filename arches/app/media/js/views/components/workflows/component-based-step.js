const { type } = require("jquery");

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
], function(_, $, arches, ko, koMapping, GraphModel, CardViewModel, ProvisionalTileViewModel) {
    function Section(sectionTitle, componentConfigs) {
        if (!componentConfigs) {
            componentConfigs = ko.observableArray();
        }

        return {
            sectionTitle: sectionTitle,
            componentConfigs: componentConfigs,
        };
    }

    function ComponentFOO(componentConfig, ddd) {
        console.log("IN ComponentFOO", componentConfig)
        var parsedComponentConfig = ko.toJS(componentConfig);

        // console.log('!!!!', parsedComponentConfig,);

        
        // ko.components.get(parsedComponentConfig.componentName, function(foo) {
        //     console.log('REALLY?', foo,)
        //     var bar = ko.components.defaultLoader.loadViewModel(parsedComponentConfig.componentName, , function(){console.log("$#*(@")});
        //     console.log('REALLY?', foo, bar)
    
        //     // ko.components.loaders.unshift(bar)
        // });

        // var lll = function(params) {
        //     console.log(params)

        // };
        // var iii =  {
        //     required: ko.observable(parsedComponentConfig.required),
        //     uniqueInstanceName: ko.observable(parsedComponentConfig.uniqueInstanceName),
        //     componentName: ko.observable(parsedComponentConfig.componentName),
        //     parameters: ko.observable(parsedComponentConfig.parameters),
        //     value: ko.mapping.fromJS(parsedComponentConfig.value),  /* mapping all values to observables */
        // };

        ko.components.get(parsedComponentConfig.componentName, function(foo) {
            // if (!foo instanceof Array) {

                var lll = foo.createViewModel.apply({}, [componentConfig.parameters]);

                console.log('REALLY?', foo, lll, $('.foofoo')[0])

                // ko.components.register('foofoo', {
                //     template
                // })


                ddd.foofoo(require('text!templates/views/components/cards/default.htm'))


                // ko.renderTemplate(
                //     require('text!templates/views/components/cards/default.htm'),
                //     foo.createViewModel,
                //     {},
                //     $('.foofoo')[0],
                //     'replaceNode'
                // )



                // var ddd = iii.parameters;
                
                // ddd.pageVm = rootPageVm;
                // ko.cleanNode($('.foofoo')[0]);
                // ko.applyBindings(lll, $('.foofoo')[0])
                // console.log('REALLY?', foo, lll, $('.foofoo')[0])
    
                // var ppp = foo.createViewModel(ddd)
    
                // console.log('REALLY?', ppp)
    
                // iii.vvv = ppp;
                // iii.template = foo.template
            // }
    
        });


        // ko.components.defaultLoader.loadViewModel(parsedComponentConfig.componentName, lll, lll)

        // return iii;


    }

    function viewModel(params) {
        var self = this;

        this.value = params.value || ko.observable();
        this.loading = params.loading || ko.observable(false);
        this.complete = params.complete || ko.observable(false);

        this.rootPageVm = ko.observable();
        this.rootPageVm.subscribe(function(pageVm) {
            console.log(pageVm)
        })

        this.foofoo = ko.observable();


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
        







        // self.flattenTree = function(parents, flatList) {
        //     _.each(ko.unwrap(parents), function(parent) {
        //         flatList.push(parent);
        //         var childrenKey = parent.tiles ? 'tiles' : 'cards';
        //         self.flattenTree(
        //             ko.unwrap(parent[childrenKey]),
        //             flatList
        //         );
        //     });
        //     return flatList;
        // };


        this.qux = function(data, fooParams) {
            console.log("IN QUX", data, fooParams)
                // var handlers = {
                //     'after-update': [],
                //     'tile-reset': []
                // };
                var displayname = ko.observable(data.displayname);
                var createLookup = function(list, idKey) {
                    return _.reduce(list, function(lookup, item) {
                        lookup[item[idKey]] = item;
                        return lookup;
                    }, {});
                };

                var tile = ko.observable();
                var card = ko.observable();
    
                var reviewer = data.userisreviewer;
                var provisionalTileViewModel = new ProvisionalTileViewModel({
                    tile: tile,
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
                    // params.nodegroupid = params.nodegroupid || card.nodegroup_id;
                    return new CardViewModel({
                        card: card,
                        graphModel: graphModel,
                        tile: null,
                        resourceId: self.resourceId,
                        displayname: displayname,
                        // handlers: handlers,
                        cards: data.cards,
                        tiles: data.tiles,
                        provisionalTileViewModel: provisionalTileViewModel,
                        cardwidgets: data.cardwidgets,
                        userisreviewer: data.userisreviewer,
                        loading: self.loading
                    });
                });

                console.log('topcards', topCards)
    
                // self.card.subscribe(function(card){
                //     if (card) {
                //         card.context = 'workflow';

                //         if (params.preSaveCallback) {
                //             card.preSaveCallback = params.preSaveCallback;
                //         }
                //         if (params.postSaveCallback) {
                //             card.postSaveCallback = params.postSaveCallback;
                //         }
                //     }
                //     if (ko.unwrap(card.widgets) && params.hiddenNodes) {
                //         card.widgets().forEach(function(widget){
                //             if (params.hiddenNodes.indexOf(widget.node_id()) > -1) {
                //                 widget.visible(false);
                //             }
                //         });
                //     }
                // });
    
                topCards.forEach(function(topCard) {
                    topCard.topCards = topCards;
                });
    
                var widgetLookup = createLookup(
                    data.widgets,
                    'widgetid'
                );
                var cardComponentLookup = createLookup(
                    data['card_components'],
                    'componentid'
                );
                var nodeLookup = createLookup(
                    graphModel.get('nodes')(),
                    'nodeid'
                );
                // self.on = function(eventName, handler) {
                //     if (handlers[eventName]) {
                //         handlers[eventName].push(handler);
                //     }
                // };
    
                self.flattenTree(topCards, []).forEach(function(item) {
                    if (item.constructor.name === 'CardViewModel' && item.nodegroupid === ko.unwrap(fooParams.nodegroupid)) {
                        console.log("ITEM", item)
                        // if (ko.unwrap(params.parenttileid) && item.parent && ko.unwrap(params.parenttileid) !== item.parent.tileid) {
                        //     return;
                        // }
                        // if (self.customCardLabel) item.model.name(ko.unwrap(self.customCardLabel));

                        card(item);

                        if (ko.unwrap(fooParams.tileid)) {
                            ko.unwrap(item.tiles).forEach(function(tile) {
                                if (tile.tileid === ko.unwrap(fooParams.tileid)) {
                                    tile(tile);
                                }
                            });
                        } else if (ko.unwrap(fooParams.createTile) !== false) {
                            tile(item.getNewTile());
                        }
                    }
                });

                return [card, tile];
        };


        this.initialize = function() {
            console.log("ComponentBasedStep initialize", self, params)

            ko.toJS(params.layoutSections).forEach(function(layoutSection) {
                var componentFOONames = [];

                layoutSection.componentConfigs.forEach(function(componentFOOData) {
                    componentFOONames.push(componentFOOData.uniqueInstanceName);
                    self.componentFOOLookup[componentFOOData.uniqueInstanceName] = ComponentFOO(componentFOOData, self);
                });

                var sectionInfo = [layoutSection.sectionTitle, componentFOONames];

                self.pageLayout.push(sectionInfo);
            });

            console.log("initialize, after page section param parse", self, params)


            // var cachedValue = ko.unwrap(params.value);

            // if (cachedValue && cachedValue.pageLayout.sections) {
            //     this.updatePageLayout(cachedValue.pageLayout.sections);
            // }
            // else {
            // }






            // var foofoo = {
            //     loadComponent: function(name, componentConfig, callback) {
            //         console.log("HAUIAHIUAHUIAHUIA", name, componentConfig, this)
            //         var templatePath = componentConfig.template.require;

            //         if (templatePath.match('card')) {
            //             console.log('card here!', this, componentConfig, self, params)

            //             var selfoo = this;


            //             var fff = function(fooParams) {
            //                 console.log('!!J', fooParams)

            //                 var foo = require([templatePath]);
            //                 console.log('!!ll', foo)
                            
            //                 componentConfig.viewModel.apply(selfoo, [fooParams]);
            //                 componentConfig.template = ko.components.defaultLoader.loadTemplate(name, componentConfig.template, callback)




                            
            //                 // var url = arches.urls.api_card + fooParams.graphid;

            //                 // $.getJSON(url, function(data) {
            //                 //     // console.log("fff", selfoo, data, fooParams)
            //                 //     // fooParams.card = 'foo'

            //                 //     var [card, tile] = self.qux(data, fooParams);


            //                 //     console.log("REALLY?", card, tile, fooParams)
            //                 //     fooParams.card = ko.unwrap(card);
            //                 //     fooParams.tile = ko.unwrap(tile);
            //                 //     fooParams.loading = self.loading;


            //                 //     componentConfig.viewModel.apply(selfoo, [fooParams]);

                                
            //                 //     console.log("BUH?", componentConfig, self)
            //                 //     console.log("BUH?", componentConfig)


            //                 // });
            //             };

            //             callback({
            //                 template: componentConfig.template,
            //                 createViewModel: fff,
            //             });

            //         }
            //         else {
            //             callback(null)
            //         }
            //     },
            //     loadViewModel: function(name, viewModelConfig, callback) {
            //         console.log('LOAD VIEWMODEL', name, viewModelConfig, callback)
            //     },
            //     loadTemplate: function(name, templateConfig, callback) {
            //         console.log('LOAD Template', name, templateConfig, callback)

            //     },

            // }
            // ko.components.loaders.unshift(foofoo);



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




        



        this.getCardResourceIdOrGraphId = function() { // override for different cases
            return (ko.unwrap(this.resourceId) || ko.unwrap(params.graphid));
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
