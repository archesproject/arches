define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * registers a text-widget component for use in forms
    * @function external:"ko.components".text-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the text input
    * @param {string} params.config.placeholder - default text to show in the text input
    */
    return ko.components.register('text-widget', {
        viewModel: function(params) {
            params.configKeys = ['placeholder'];

            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/text' }
    });
});
