define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'viewmodels/alert',
    'dropzone',
    'bindings/dropzone',
], function(_, ko, ImporterViewModel, AlertViewModel, dropzone) {
    return ko.components.register('branch-csv-importer', {
        viewModel: function(params) {
            const self = this;

            this.load_details = params.load_details;
            this.state = params.state;
            this.loading = params.loading || ko.observable();

            this.moduleId = params.etlmoduleid;
            ImporterViewModel.apply(this, arguments);
            this.loadStatus = ko.observable('ready');

            this.write = function(){
                self.loading(true);
                self.loadStatus("loading");
                self.submit('write').then(function(response){
                    self.loading(false);
                    return response.json();
                }).then(function(response) {
                    if (response?.result === "success"){
                        self.loadStatus('successful');
                    } else {
                        self.alert(new AlertViewModel('ep-alert-red', response.title, response.message));
                        self.loadStatus('failed');
                    }
                }).catch(function(err) {    
                    // eslint-disable-next-line no-console
                    console.log(err);
                    self.loadStatus('failed');
                });
            };    
        },
        template: { require: 'text!templates/views/components/etl_modules/branch-csv-importer.htm' }
    });
});