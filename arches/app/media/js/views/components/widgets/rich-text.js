define([
    'knockout', 
    'underscore', 
    'viewmodels/widget', 
    'templates/views/components/widgets/rich-text.htm',
    'bindings/ckeditor',
], function(ko, _, WidgetViewModel, richTextWidgetTemplate) {
    /**
    * registers a rich-text-widget component for use in forms
    * @function external:"ko.components".rich-text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    */

    const viewModel = function(params) {
        params.configKeys = ['displayfullvalue'];
        WidgetViewModel.apply(this, [params]);
        this.displayfullvalue(params.displayfullvalue);
    };

    return ko.components.register('rich-text-widget', {
        viewModel: viewModel,
        template: richTextWidgetTemplate,
    });
});
