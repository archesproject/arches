import ko from 'knockout';
import BaseEditorViewModel from 'views/components/etl_modules/base-bulk-string-editor';
import baseStringEditorTemplate from 'templates/views/components/etl_modules/base-bulk-string-editor.htm';

const viewModel = function (params) {
    BaseEditorViewModel.apply(this, [params]);
    this.operation('case');
};

ko.components.register('bulk-case-editor', {
    viewModel,
    template: baseStringEditorTemplate,
});

export default viewModel;
