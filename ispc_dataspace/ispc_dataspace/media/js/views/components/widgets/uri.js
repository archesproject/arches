define(['knockout', 'underscore', 'viewmodels/widget'], function (ko, _, WidgetViewModel) {
    /**
    * registers a uri-widget component for use in forms
    * @function external:"ko.components".uri-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    */
    return ko.components.register('uri-widget', {
        viewModel: function(params) {
            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/uri' }
    });
});
