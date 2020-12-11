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
    function Section(sectionTitle, componentConfigs) {
        if (!componentConfigs) {
            componentConfigs = ko.observableArray();
        }

        return {
            sectionTitle: sectionTitle,
            componentConfigs: componentConfigs,
        }
    };

    function ComponentConfig(componentConfig) {
        return {
            required: componentConfig.required,
            uniqueInstanceName: componentConfig.uniqueInstanceName,
            componentName: componentConfig.componentName,
            graphIds: componentConfig.graphIds,
            value: ko.observable(
                componentConfig.defaultValue ? componentConfig.defaultValue : null
            ),
        }
    };
    
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

        // this.url = arches.urls.api_card + ko.unwrap(params.graphid);
        
        this.alert = params.alert || ko.observable(null);
        this.altButtons =  params.altButtons || ko.observable(null);
        this.hideDefaultButtons = params.hideDefaultButtons || ko.observable(false);
        
        this.loading = params.loading || ko.observable(false);
        this.complete = params.complete || ko.observable(false);

        this.requiredComponentData = {};
        
        /* source-of-truth for page data */
        this.pageLayout = {
            sections: ko.observableArray(),
        };

        /* setup pageLayout */ 
        ko.toJS(params.layoutSections).forEach(function(layoutSection) {
            var section = new Section(layoutSection.sectionTitle)

            layoutSection.componentConfigs.forEach(function(componentConfig) {
                var componentConfig = new ComponentConfig(componentConfig);

                /* if a component is marked as 'required' let's add a subscription to track its value */ 
                if (componentConfig.required) {
                    self.requiredComponentData[componentConfig.uniqueInstanceName] = ko.observable();

                    componentConfig['value'].subscribe(function(value) {
                        self.requiredComponentData[componentConfig.uniqueInstanceName](value);

                        var complete = Object.values(self.requiredComponentData).reduce(function(acc, value) {
                            if (!value()) { acc = false }
                            return acc;
                        }, true);

                        self.complete(complete);
                    });
                }

                section.componentConfigs.push(componentConfig);
            });

            self.pageLayout.sections.push(section);
        });

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
