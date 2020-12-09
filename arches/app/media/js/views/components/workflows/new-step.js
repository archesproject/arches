define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'models/graph',
    'viewmodels/card',
    'viewmodels/alert',
], function(_, $, arches, ko, koMapping, GraphModel, CardViewModel, AlertViewModel) {
    function viewModel(params) {
        var self = this;

        // if (params.workflow) {
        //     if (!params.resourceid()) {
        //         if (params.workflow.state.steps[params._index]) {
        //             this.resourceId(params.workflow.state.steps[params._index].resourceid);
        //         } else {
        //             this.resourceId(params.workflow.state.resourceid);
        //         }
        //     } else {
        //         this.resourceId = params.resourceid;
        //     }
        // }

        this.url = arches.urls.api_card + ko.unwrap(params.graphid);
        
        this.alert = params.alert || ko.observable(null);
        this.altButtons =  params.altButtons || ko.observable(null);
        this.hideDefaultButtons = params.hideDefaultButtons || ko.observable(false);
        
        this.loading = params.loading || ko.observable(true);
        this.complete = params.complete || ko.observable(false);

        this.requiredWidgets = {};
        
        /* source-of-truth for page data */
        this.layoutSections = ko.observable();

        var generateInitialLayoutConfig = function() {
            $.getJSON(self.url, function(data) {
                /* add widgets to each section config */ 
                var layoutSections = ko.toJS(params.layoutSections).map(function(layoutSection) {
                    layoutSection.widgetConfigs.map(function(widgetConfig) {
                        var widget = data.widgets.find(function(widget) { return widget.widgetid === widgetConfig.widgetid });
                        if (widget) { 
                            widgetConfig['widget'] = widget; 
                            widgetConfig['value'] = ko.observable();

                            /* if the widget is marked as required, let's add a subscription to know when self.complete === true */ 
                            if (widgetConfig.required) {
                                self.requiredWidgets[widgetConfig.widgetInstanceName] = null;

                                widgetConfig['value'].subscribe(function(value) {
                                    self.requiredWidgets[widgetConfig.widgetInstanceName] = value;

                                    var complete = true;
                                    Object.values(self.requiredWidgets).forEach(function(value) {
                                        if (!Boolean(value)) { complete = false }
                                    });

                                    // console.log(complete, self.layoutSections())

                                    self.complete(complete);
                                });
                            }
                        }
                    });
    
                    return layoutSection;
                });

                self.layoutSections(layoutSections);
            });

            self.loading = false;
        };
        
        generateInitialLayoutConfig();

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
                wastebin = koMapping.toJS(params.wastebin)

                // if (ko.unwrap(wastebin.hasOwnProperty('resourceid'))) {
                //     wastebin.resourceid = ko.unwrap(params.resourceid);
                // }
            }
            
            return {
                // resourceid: ko.unwrap(params.resourceid) || this.workflow.state.resourceid,
                wastebin: wastebin
            };
        };


        this.setStateProperties = function(){
            // Sets properties in defineStateProperties to the state.
            if (params.workflow) {
                params.workflow.state.steps[params._index] = params.defineStateProperties();
            }
        };

        // self.onSaveSuccess = function(tiles) {
        //     // var tile;
        //     // if (tiles.length > 0 || typeof tiles == 'object') {
        //     //     tile = tiles[0] || tiles;
        //     //     params.resourceid(tile.resourceinstance_id);
        //     //     params.tileid(tile.tileid);
        //     //     self.resourceId(tile.resourceinstance_id);
        //     // }
        //     self.setStateProperties();
        //     if (params.workflow) {
        //         params.workflow.updateUrl();
        //     }
        //     if (self.completeOnSave === true) { self.complete(true); }
        // };

    }
    ko.components.register('new-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/new-step.htm'
        }
    });
    return viewModel;
});
