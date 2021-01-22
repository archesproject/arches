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
        var componentConfig = ko.toJS(componentConfig);

        return {
            required: ko.observable(componentConfig.required),
            uniqueInstanceName: ko.observable(componentConfig.uniqueInstanceName),
            componentName: ko.observable(componentConfig.componentName),
            graphIds: ko.observable(componentConfig.graphIds),
            value: ko.mapping.fromJS(componentConfig.value),
        }
    };

    function viewModel(params) {
        var self = this;

        this.value = params.value || ko.observable();
        this.loading = params.loading || ko.observable(false);
        this.complete = params.complete || ko.observable(false);

        this.requiredComponentData = {};

        /* source-of-truth for page data */
        this.pageLayout = {
            sections: ko.observableArray(),
        };

        this.initialize = function() {
            if (self.complete() === true) {
                var cachedValue = ko.unwrap(params.value);

                console.log(cachedValue)
    
                if (cachedValue && cachedValue.pageLayout.sections) {
                    this.updatePageLayout(cachedValue.pageLayout.sections);
                }
            }
            else {
                this.updatePageLayout(params.layoutSections);
            }
    
        };

        this.updatePageLayout = function(layoutSections) {
            self.requiredComponentData = {};
            self.pageLayout.sections([]);

            var layoutSections = ko.toJS(layoutSections);

            layoutSections.forEach(function(layoutSection) {
                var section = new Section(layoutSection.sectionTitle)

                layoutSection.componentConfigs.forEach(function(componentConfig) {
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

        this.finish = function() {
            console.log("AAAA", params.defineStateProperties())
            params.value(params.defineStateProperties());

            if (self.complete() === false) {
                self.complete(true);
            }
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
                wastebin = koMapping.toJS(params.wastebin)
            }

            return {
                wastebin: wastebin,
                pageLayout: koMapping.toJS(self.pageLayout),
            };
        };

        this.initialize();
    };

    ko.components.register('component-based-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/component-based-step.htm'
        }
    });

    return viewModel;
});