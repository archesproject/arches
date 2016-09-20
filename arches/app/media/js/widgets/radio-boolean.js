define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a radio-boolean-widget component for use in forms
    * @function external:"ko.components".radio-boolean-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the select input
    * @param {string} params.config.trueValue - label alongside the true boolean button
    * @param {string} params.config.falseValue - label alongside the false boolean button
    */
    return ko.components.register('radio-boolean-widget', {
        viewModel: function(params) {
            params.configKeys = ['trueLabel', 'falseLabel'];
            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/radio-boolean' }
    });
});
