define([
    'knockout',
    'views/components/etl_modules/base-editor',
    'templates/views/components/etl_modules/base-editor.htm',
], function(ko, BaseEditorViewModel, baseEditorTemplate) {
    const viewModel = function(params) {
        BaseEditorViewModel.apply(this, [params]);
        this.operation('replace');
    };
    ko.components.register('bulk-replace-editor', {
        viewModel: viewModel,
        template: baseEditorTemplate,
    });
    return viewModel;
});