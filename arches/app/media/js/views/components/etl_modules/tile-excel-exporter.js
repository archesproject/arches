define([
    'knockout',
    'viewmodels/excel-file-export',
    'templates/views/components/etl_modules/tile-excel-exporter.htm',
], function(ko, ExcelFileExportViewModel, tileExcelExporterTemplate) {
    return ko.components.register('tile-excel-exporter', {
        viewModel: ExcelFileExportViewModel,
        template: tileExcelExporterTemplate,
    });
});
