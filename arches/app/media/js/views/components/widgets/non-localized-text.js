define([
    'knockout', 
    'underscore', 
    'viewmodels/widget',
    'arches',
    'templates/views/components/widgets/non-localized-text.htm'
], function (ko, _, WidgetViewModel, arches, nonlocalizedTextWidgetTemplate) {
    /**
    * registers a text-widget component for use in forms
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    * @param {string} params.config().uneditable - disables widget
    */

    const viewModel = function(params) {
        params.configKeys = ['placeholder', 'width', 'maxLength', 'defaultValue', 'uneditable'];
    
            WidgetViewModel.apply(this, [params]);

            const self = this;
    
            this.disable = ko.computed(() => {
                return ko.unwrap(self.disabled) || ko.unwrap(self.uneditable); 
            }, self);
    };

    return ko.components.register('non-localized-text-widget', {
        viewModel: viewModel,
        template: nonlocalizedTextWidgetTemplate
    });
});
