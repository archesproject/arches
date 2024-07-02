define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'arches',
    'viewmodels/alert',
    'viewmodels/jsonld-importer',
    'templates/views/components/etl_modules/jsonld-importer.htm',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
], function(_, ko, ImporterViewModel, arches, AlertViewModel, JSONLDImportViewModel, JSONLDImporterTemplate) {
    return ko.components.register('jsonld-importer', {
        viewModel: JSONLDImportViewModel,
        template: JSONLDImporterTemplate,
    });
});
