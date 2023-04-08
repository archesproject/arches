define([
    'knockout',
    'views/components/etl_modules/base-bulk-string-editor',
    'templates/views/components/etl_modules/base-bulk-string-editor.htm',
], function(ko, BaseEditorViewModel, baseStringEditorTemplate) {
    const viewModel = function(params) {
        BaseEditorViewModel.apply(this, [params]);
        this.operation('replace');
    };
    ko.components.register('bulk-replace-editor', {
        viewModel: viewModel,
        template: baseStringEditorTemplate,
    });
    return viewModel;
});