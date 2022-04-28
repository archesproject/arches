define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'dropzone',
    'bindings/dropzone',
], function(_, ko, ImporterViewModel, dropzone) {
    return ko.components.register('branch-csv-importer', {
        viewModel: function(params) {
            const self = this;
            this.moduleId = params.etlmoduleid;
            ImporterViewModel.apply(this, arguments);
            this.loading = params.config.loading;
            this.response.subscribe(val => {
                console.log(val);
            });

            this.write = function(){
                self.loading(true);
                self.submit('write').then(function(response){
                    self.loading(false);
                    if (response.ok) {
                        return response.json();
                    }
                }).then(function(response) {
                    if (response?.result === "success"){
                        self.response(null);
                    }
                }).catch(function(err) {    
                    // eslint-disable-next-line no-console
                    console.log(err);
                });
            };    
        },
        template: { require: 'text!templates/views/components/etl_modules/branch-csv-importer.htm' }
    });
});