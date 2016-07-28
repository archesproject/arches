define(['knockout', 'underscore'], function (ko, _) {
    /**
    * registers a text-widget component for use in forms
    * @extends ko.components
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the text input
    * @param {string} params.config.placeholder - default text to show in the text input
    */
    return ko.components.register('text-widget', {
        viewModel: function(params) {
            this.value = params.value;
            this.label = params.config.label;
            this.placeholder = params.config.placeholder
        },
        template: { require: 'text!widget-templates/text' }
    });
});
