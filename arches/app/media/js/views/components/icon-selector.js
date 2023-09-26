define([
    'knockout', 
    'templates/views/components/icon-selector.htm',
    'bindings/key-events-click'
], function(ko, iconSelectorTemplate) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a icon-selector component for use in forms
    * @function external:"ko.components".icon-selector
    * @param {object} params
    * @param {observable} params.selectedIconObservable - the currently selected icon
    * @param {observable} params.iconFilter
    * @param {array} params.iconList
    * @param {string} params.label
    */
    return ko.components.register('views/components/icon-selector', {
        viewModel: function(params) {
             
            this.selectedIcon = params.selectedIconObservable;
            this.iconFilter = params.iconFilter;
            this.iconList = params.iconList;
            this.label = params.label;
        },
        template: iconSelectorTemplate
    });
});