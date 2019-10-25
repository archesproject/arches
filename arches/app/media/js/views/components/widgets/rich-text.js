define(['knockout', 'underscore', 'viewmodels/widget', 'bindings/ckeditor'], function (ko, _, WidgetViewModel) {
    /**
    * registers a rich-text-widget component for use in forms
    * @function external:"ko.components".rich-text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    */
    return ko.components.register('rich-text-widget', {
        viewModel: function(params) {
            params.configKeys = ['displayfullvalue'];
            WidgetViewModel.apply(this, [params]);
            this.displayfullvalue(params.displayfullvalue);
        },
        template: { require: 'text!widget-templates/rich-text' }
    });
});
