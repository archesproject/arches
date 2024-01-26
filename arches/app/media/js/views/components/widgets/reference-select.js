define([
    'knockout',
    'viewmodels/widget',
    'templates/views/components/widgets/reference-select.htm',
    'bindings/select2-query',
], function(ko, WidgetViewModel, referenceSelectTemplate) {
    const viewModel = function(params) {
        WidgetViewModel.apply(this, [params]);
    };

    return ko.components.register('reference-select-widget', {
        viewModel: viewModel,
        template: referenceSelectTemplate,
    });
});
