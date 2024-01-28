define([
    'knockout',
    'viewmodels/reference-select',
    'templates/views/components/widgets/reference-select.htm',
    'bindings/select2-query',
], function(ko, ReferenceSelectViewModel, referenceSelectTemplate) {
    const viewModel = function(params) {
        ReferenceSelectViewModel.apply(this, [params]);
    };

    return ko.components.register('reference-select-widget', {
        viewModel: viewModel,
        template: referenceSelectTemplate,
    });
});
