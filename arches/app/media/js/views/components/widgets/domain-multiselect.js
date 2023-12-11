define([
    'knockout',
    'viewmodels/domain-widget',
    'templates/views/components/widgets/select.htm'
], function(ko, DomainWidgetViewModel, selectTemplate) {
    /**
     * registers a select-widget component for use in forms
     * @function external:"ko.components".select-widget
     * @param {object} params
     * @param {boolean} params.value - the value being managed
     * @param {object} params.config -
     * @param {string} params.config.label - label to use alongside the select input
     * @param {string} params.config.placeholder - default text to show in the select input
     * @param {string} params.config.options -
     */

    const viewModel = function(params) {
        params.configKeys = ['placeholder', 'defaultValue'];
         
        DomainWidgetViewModel.apply(this, [params]);

        this.multiple = true;
    };

    return ko.components.register('domain-multiselect-widget', {
        viewModel: viewModel,
        template: selectTemplate,
    });
});
