import _ from 'underscore';
import ko from 'knockout';
import ExcelFileImportViewModel from 'viewmodels/excel-file-import';
import BranchExcelImporterTemplate from 'templates/views/components/etl_modules/branch-excel-importer.htm';
import 'dropzone';
import 'bindings/select2-query';
import 'bindings/dropzone';

export default ko.components.register('branch-excel-importer', {
    viewModel: ExcelFileImportViewModel,
    template: BranchExcelImporterTemplate,
});
