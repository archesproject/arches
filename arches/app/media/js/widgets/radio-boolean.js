define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * knockout components namespace used in arches
    * @external "ko.components"
    * @see http://knockoutjs.com/documentation/component-binding.html
    */

    /**
    * registers a switch-widget component for use in forms
    * @function external:"ko.components".switch-widget
    * @param {object} params
    * @param {boolean} params.value - the value being managed
    * @param {object} params.config -
    * @param {string} params.config.label - label to use alongside the select input
    * @param {string} params.config.subtitle - subtitle to use alongside the select input
    * @param {string|true} [params.config.on=true] - the value to use for the "on" state of the switch
    * @param {string|false} [params.config.off=false] - the value to use for the "off" state of the switch
    */
    return ko.components.register('radio-boolean-widget', {
        viewModel: function(params) {
            params.configKeys = ['trueLabel', 'falseLabel'];
            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/radio-boolean' }
    });
});
