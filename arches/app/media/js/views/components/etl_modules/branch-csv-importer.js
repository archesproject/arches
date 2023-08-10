define([
    'underscore',
    'knockout',
    'viewmodels/excel-file-import',
    'templates/views/components/etl_modules/branch-csv-importer.htm',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
], function(_, ko, ExcelFileImportViewModel, branchCSVImporterTemplate) {
    return ko.components.register('branch-csv-importer', {
        viewModel: ExcelFileImportViewModel,
        template: branchCSVImporterTemplate,
    });
});
