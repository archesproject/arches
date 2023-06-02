define([
    'knockout',
    'views/components/etl_modules/base-bulk-string-editor',
    'templates/views/components/etl_modules/base-bulk-string-editor.htm',
], function(ko, BaseEditorViewModel, baseStringEditorTemplate) {
    const viewModel = function(params) {
        BaseEditorViewModel.apply(this, [params]);
        this.operation('case');
    };
    ko.components.register('bulk-case-editor', {
        viewModel: viewModel,
        template: baseStringEditorTemplate,
    });
    return viewModel;
});