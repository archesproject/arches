import ko from 'knockout';
import ArchesJsonImportViewModel from 'viewmodels/arches-json-importer';
import ArchesJsonImporterTemplate from 'templates/views/components/etl_modules/arches-json-importer.htm';


export default ko.components.register('arches-json-importer', {
    viewModel: ArchesJsonImportViewModel,
    template: ArchesJsonImporterTemplate,
});
