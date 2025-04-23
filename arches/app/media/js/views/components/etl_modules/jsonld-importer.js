import _ from 'underscore';
import ko from 'knockout';
import ImporterViewModel from 'viewmodels/base-import-view-model';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import JSONLDImportViewModel from 'viewmodels/jsonld-importer';
import JSONLDImporterTemplate from 'templates/views/components/etl_modules/jsonld-importer.htm';
import 'dropzone';
import 'bindings/select2-query';
import 'bindings/dropzone';


export default ko.components.register('jsonld-importer', {
    viewModel: JSONLDImportViewModel,
    template: JSONLDImporterTemplate,
});
