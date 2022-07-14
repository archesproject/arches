define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'templates/views/components/workbench.htm',
    'bindings/sortable',
], function($, _, ko, arches, workbenchTemplate) {
    var viewModel = function(params) {
        var self = this;

        this.translations = arches.translations;
        this.activeTab = ko.observable(params.activeTab);
        this.showTabs = ko.observable(true);
        this.hideSidePanel = function() {
            self.activeTab(undefined);
        };

        if (this.card) {
            this.card.allowProvisionalEditRerender(false);
        }

        this.expandSidePanel = ko.computed(function(){
            if (self.tile) {
                return self.tile.hasprovisionaledits() && self.reviewer === true;
            } else {
                return false;
            }
        });
        
        this.workbenchWrapperClass = ko.observable();

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
        template: workbenchTemplate,
    });
    return viewModel;
});
