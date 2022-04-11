define([
    'knockout',
    'arches',
], function(ko, arches) {
    return ko.components.register('etl-manager', {
        viewModel: function(params) {
            var self = this;
            this.loading = params.loading;
            this.loading(true);
            this.selectedModule = ko.observable();
            this.activeTab = ko.observable();
            this.isImport = ko.observable(true);
            this.moduleSearchString = ko.observable('');
            this.tabs = [
                {id: 'start', title: 'Start'},
                {id: 'details', title: 'Task Details'},
                {id: 'import', title: 'Import Tasks'},
                {id: 'export', title: 'Export Tasks'},
            ];
            this.selectModule = function(etlmodule) {
                self.selectedModule(etlmodule);
                self.activeTab("details");
            };

            this.fetchLoadEvent = function(){
                const url = arches.urls.etl_manager + "?action=loadEvent";
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    console.log(data)
                });
            };

            this.fetchStagedData = function(loadid){
                const url = arches.urls.etl_manager + "?action=stagedData&loadid="+loadid;
                window.fetch(url).then(function(response){
                    if(response.ok){
                        return response.json();
                    }
                }).then(function(data){
                    console.log(data)
                });
            };

            this.init = function(){
                const url = arches.urls.etl_manager + "?action=modules";
                window.fetch(url).then(function(response){
                        if(response.ok){
                            return response.json();
                    }
                    }).then(function(data){
                        self.etlModules = data.map(function(etl){
                            etl.config.loading = self.loading;
                            require([etl.component]);
                            return etl;
                        });
                        self.loading(false);
                    });
                    this.activeTab("start");
            };

            this.init();
        },
        template: { require: 'text!templates/views/components/plugins/etl-manager.htm' }
    });
});
