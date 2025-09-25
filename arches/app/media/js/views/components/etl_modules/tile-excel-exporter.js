import ko from 'knockout';
import ExcelFileExportViewModel from 'viewmodels/excel-file-export';
import tileExcelExporterTemplate from 'templates/views/components/etl_modules/tile-excel-exporter.htm';

export default ko.components.register('tile-excel-exporter', {
    viewModel: ExcelFileExportViewModel,
    template: tileExcelExporterTemplate,
});
