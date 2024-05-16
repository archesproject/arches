define([
    'underscore',
    'knockout',
    'viewmodels/excel-file-import',
    'templates/views/components/etl_modules/branch-excel-importer.htm',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
], function(_, ko, ExcelFileImportViewModel, BranchExcelImporterTemplate) {
    return ko.components.register('branch-excel-importer', {
        viewModel: ExcelFileImportViewModel,
        template: BranchExcelImporterTemplate,
    });
});
