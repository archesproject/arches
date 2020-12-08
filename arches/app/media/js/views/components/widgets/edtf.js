define(['knockout', 'underscore', 'viewmodels/widget'], function(ko, _, WidgetViewModel) {
    /**
    * registers a edtf-widget component for use in forms
    * @function external:"ko.components".edtf-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    * @param {string} params.config().label - label to use alongside the text input
    * @param {string} params.config().placeholder - default text to show in the text input
    */
    return ko.components.register('edtf-widget', {
        viewModel: function(params) {
            params.configKeys = ['placeholder', 'defaultValue'];
            this.showEDTFFormats = ko.observable(false);
            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/edtf' }
    });
});
