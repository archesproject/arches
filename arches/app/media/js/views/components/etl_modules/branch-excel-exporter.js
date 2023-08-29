define([
    'knockout',
    'viewmodels/excel-file-export',
    'templates/views/components/etl_modules/branch-excel-exporter.htm',
], function(ko, ExcelFileExportViewModel, branchExcelExporterTemplate) {
    return ko.components.register('branch-excel-exporter', {
        viewModel: ExcelFileExportViewModel,
        template: branchExcelExporterTemplate,
    });
});
