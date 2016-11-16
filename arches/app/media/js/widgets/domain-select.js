define([
    'knockout',
    'viewmodels/domain-widget',
    'plugins/knockout-select2'
], function(ko, DomainWidgetViewModel) {
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
    return ko.components.register('domain-select-widget', {
        viewModel: function(params) {
            params.configKeys = ['placeholder'];
            DomainWidgetViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!widget-templates/select'
        }
    });
});
