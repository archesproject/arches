define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'bindings/sortable'
], function($, _, arches, ko) {
    var viewModel = function(params) {
        var self = this;

        this.activeTab = ko.observable(params.activeTab);
        this.hideSidePanel = function() {
            self.activeTab(undefined);
        };

        this.toggleTab = function(tabName) {
            if (self.activeTab() === tabName) {
                self.activeTab(null);
            } else {
                self.activeTab(tabName);
            }
        };
    };

    ko.components.register('workbench', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workbench.htm'
        }
    });
    return viewModel;
});
