define([
    'knockout',
    'arches',
    'views/components/etlmodules/import-single-csv'
], function(ko, arches) {
    return ko.components.register('etl-manager', {
        viewModel: function(params) {
            var self = this;
            this.loading = params.loading;
            this.loading(true);
            this.selectedModule = ko.observable();

            this.init = function(){
                window.fetch(arches.urls.etl_manager)
                    .then(function(response){
                        if(response.ok){
                            return response.json();
                        }
                    })
                    .then(function(data){
                        self.etlmodules = data.map(function(etl){
                            etl.config.loading = self.loading;
                            return etl;
                        });
                        self.loading(false);
                    });
            };

            this.init();
        },
        template: { require: 'text!templates/views/components/plugins/etl-manager.htm' }
    });
});
