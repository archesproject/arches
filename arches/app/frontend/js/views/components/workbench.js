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
        template: {
            require: 'text!templates/views/components/workbench.htm'
        }
    });
    return viewModel;
});
