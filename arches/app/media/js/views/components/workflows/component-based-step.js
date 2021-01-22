define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'knockout-mapping',
    'viewmodels/card',
], function(_, $, arches, ko, koMapping) {
    function Section(sectionTitle, componentConfigs) {
        if (!componentConfigs) {
            componentConfigs = ko.observableArray();
        }

        return {
            sectionTitle: sectionTitle,
            componentConfigs: componentConfigs,
        };
    }

    function ComponentConfig(componentConfig) {
        var parsedComponentConfig = ko.toJS(componentConfig);

        return {
            required: ko.observable(parsedComponentConfig.required),
            uniqueInstanceName: ko.observable(parsedComponentConfig.uniqueInstanceName),
            componentName: ko.observable(parsedComponentConfig.componentName),
            parameters: ko.observable(parsedComponentConfig.parameters),
            value: ko.mapping.fromJS(parsedComponentConfig.value),  /* mapping all values to observables */
        };
    }

    function viewModel(params) {
        var self = this;

        this.value = params.value || ko.observable();
        this.loading = params.loading || ko.observable(false);
        this.complete = params.complete || ko.observable(false);

        /* source-of-truth for page data */
        this.pageLayout = {
            sections: ko.observableArray(),
        };

        this.initialize = function() {
            var cachedValue = ko.unwrap(params.value);

            if (cachedValue && cachedValue.pageLayout.sections) {
                this.updatePageLayout(cachedValue.pageLayout.sections);
            }
            else {
                this.updatePageLayout(params.layoutSections);
            }
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
                    var componentConfig = new ComponentConfig(componentConfigData);

                    /* save value on update */ 
                    componentConfig.value.subscribe(function() {
                        params.value(params.defineStateProperties());
                    });

                    /* if a component is marked as 'required' let's add a subscription to track its value */ 
                    if (componentConfig.required()) {
                        requiredComponentData[componentConfig.uniqueInstanceName()] = ko.observable(componentConfig.value());

                        componentConfig.value.subscribe(function(value) {
                            requiredComponentData[componentConfig.uniqueInstanceName()](value);
                            hasAllRequiredComponentData(requiredComponentData) ? self.complete(true) : self.complete(false);
                        });
                    }

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
