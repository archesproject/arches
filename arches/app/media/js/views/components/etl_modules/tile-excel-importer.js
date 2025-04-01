import _ from 'underscore';
import ko from 'knockout';
import ImporterViewModel from 'viewmodels/base-import-view-model';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import ExcelFileImportViewModel from 'viewmodels/excel-file-import';
import tileExcelImporterTemplate from 'templates/views/components/etl_modules/tile-excel-importer.htm';
import 'dropzone';
import 'bindings/select2-query';
import 'bindings/dropzone';


export default ko.components.register('tile-excel-importer', {
    viewModel: ExcelFileImportViewModel,
    template: tileExcelImporterTemplate,
});
