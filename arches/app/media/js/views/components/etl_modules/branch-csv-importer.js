define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'dropzone',
    'bindings/dropzone',
], function(_, ko, ImporterViewModel, dropzone) {
    return ko.components.register('branch-csv-importer', {
        viewModel: function(params) {
            this.moduleId = params.etlmoduleid;
            ImporterViewModel.apply(this, arguments);
            this.loading = params.config.loading;
            this.response.subscribe(val => {
                console.log(val);
            });
        },
        template: { require: 'text!templates/views/components/etl_modules/branch-csv-importer.htm' }
    });
});