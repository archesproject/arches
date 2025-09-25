import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import workbenchTemplate from 'templates/views/components/workbench.htm';
import ariaUtils from 'utils/aria';
import 'bindings/sortable';


var viewModel = function(params) {
    var self = this;

        
    this.activeTab = ko.observable(params.activeTab);
    this.showTabs = ko.observable(true);
    this.hideSidePanel = function(focusElement) {
        self.activeTab(undefined);
        if(focusElement){
            ariaUtils.shiftFocus(focusElement);
        }
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
export default viewModel;
