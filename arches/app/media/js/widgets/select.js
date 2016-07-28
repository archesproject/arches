define(['knockout', 'underscore', 'plugins/knockout-select2'], function (ko, _) {
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
    return ko.components.register('select-widget', {
        viewModel: function(params) {
            this.value = params.value;
            this.label = params.config.label;
            this.placeholder = params.config.placeholder
            this.options = params.config.options
        },
        template: { require: 'text!widget-templates/select' }
    });
});
