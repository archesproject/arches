define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'arches',
    'viewmodels/alert',
    'viewmodels/excel-file-import',
    'templates/views/components/etl_modules/branch-csv-importer.htm',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
], function(_, ko, ImporterViewModel, arches, AlertViewModel, ExcelFileImportViewModel, branchCSVImporterTemplate) {
    return ko.components.register('branch-csv-importer', {
        viewModel: ExcelFileImportViewModel,
        template: branchCSVImporterTemplate,
    });
});
