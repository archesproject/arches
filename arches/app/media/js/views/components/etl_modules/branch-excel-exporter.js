import ko from 'knockout';
import ExcelFileExportViewModel from 'viewmodels/excel-file-export';
import branchExcelExporterTemplate from 'templates/views/components/etl_modules/branch-excel-exporter.htm';

export default ko.components.register('branch-excel-exporter', {
    viewModel: ExcelFileExportViewModel,
    template: branchExcelExporterTemplate,
});
