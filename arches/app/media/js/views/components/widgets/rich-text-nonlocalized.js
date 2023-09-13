define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'arches',
    'templates/views/components/widgets/rich-text-nonlocalized.htm',
    'bindings/ckeditor'
], function (ko, _, WidgetViewModel, arches, richTextNonlocalizedTemplateWidget) {
    /**
    * registers a rich-text-widget component for use in forms
    * @function external:"ko.components".rich-text-widget
    * @param {object} params
    * @param {string} params.value - the value being managed
    * @param {function} params.config - observable containing config object
    */

    const viewModel = function (params) {
        params.configKeys = ['displayfullvalue'];
        WidgetViewModel.apply(this, [params]);
        this.displayfullvalue(params.displayfullvalue);
    };

    return ko.components.register('rich-text-nonlocalized-widget', {
        viewModel: viewModel,
        template: richTextNonlocalizedTemplateWidget
    });
});
