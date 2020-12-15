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
        console.log(componentConfig)
        return {
            required: componentConfig.required,
            uniqueInstanceName: componentConfig.uniqueInstanceName,
            componentName: componentConfig.componentName,
            graphIds: componentConfig.graphIds,
            value: ko.observable(
                componentConfig.value ? componentConfig.value() : null
            ),
        }
    };
    
    function viewModel(params) {
        var self = this;
        console.log("AHAHA", self)

        this.value = params.value || ko.observable();
        this.loading = params.loading || ko.observable(false);
        this.complete = params.complete || ko.observable(false);

        this.requiredComponentData = {};
        
        /* source-of-truth for page data */
        this.pageLayout = {
            sections: ko.observableArray(),
        };

        this.updatePageLayout = function(layoutSections) {
            self.requiredComponentData = {};
            self.pageLayout.sections([]);

            layoutSections().forEach(function(layoutSection) {
                var section = new Section(layoutSection.sectionTitle)

                layoutSection.componentConfigs().forEach(function(componentConfig) {
                    var componentConfig = new ComponentConfig(componentConfig);
    
                    /* if a component is marked as 'required' let's add a subscription to track its value */ 
                    if (componentConfig.required()) {
                        self.requiredComponentData[componentConfig.uniqueInstanceName()] = ko.observable();
    
                        componentConfig.value.subscribe(function(value) {
                            self.requiredComponentData[componentConfig.uniqueInstanceName()](value);
    
                            var allRequiredDataObtained = Object.values(self.requiredComponentData).reduce(function(acc, value) {
                                if (!value()) { acc = false }
                                return acc;
                            }, true);

                            if (allRequiredDataObtained) { self.finish(); }
                        });
                    }
    
                    section.componentConfigs.push(componentConfig);
                });
    
                self.pageLayout.sections.push(section);
            });
        };

        this.getStateProperties = function(){
            // Gets properties in defineStateProperties to the state.
            if (params.workflow) {
                return params.workflow.state.steps[params._index];
            }
        };

        this.setStateProperties = function(){
            // Sets properties in defineStateProperties to the state.
            if (params.workflow) {
                params.workflow.state.steps[params._index] = params.defineStateProperties();
            }
        };

        this.finish = function() {
            self.setStateProperties();

            if (self.complete() === false) {
                self.complete(true);
            }
        };

        this.quit = function() {
            this.complete(false);
            self.updatePageLayout(koMapping.toJS(params.layoutSections));
            self.setStateProperties();
        };




        /* BEGIN logic to run on load */ 

        console.log('000', params, self.getStateProperties())

        
        if (self.complete() === true) {
            var previouslySavedData = self.getStateProperties();

            if (previouslySavedData && previouslySavedData.pageLayout.sections) {
                this.updatePageLayout(previouslySavedData.pageLayout.sections);
            }
        }
        else {
            this.updatePageLayout(params.layoutSections);
        }

        /* END logic to run on load */ 



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
            }
            
            return {
                wastebin: wastebin,
                pageLayout: self.pageLayout,
            };
        };
    }
    ko.components.register('new-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/new-step.htm'
        }
    });
    return viewModel;
});
