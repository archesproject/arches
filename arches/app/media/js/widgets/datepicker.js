define(['knockout', 'underscore', 'bindings/datepicker'], function (ko, _) {
    /**
    * registers a datepicker-widget component for use in forms
    * @function external:"ko.components".datepicker-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the text input
    * @param {string} params.config.placeholder - default text to show in the text input
    */
    return ko.components.register('datepicker-widget', {
        viewModel: function(params) {
            this.value = params.value;
            this.label = params.label;
            this.placeholder = params.config.placeholder
        },
        template: { require: 'text!widget-templates/datepicker' }
    });
});
