define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'arches',
    'dropzone',
    'bindings/dropzone',
    'bindings/select2-query'
], function(_, ko, ImporterViewModel, arches, dropzone) {
    return ko.components.register('branch-csv-importer', {
        viewModel: function(params) {
            const self = this;
            this.moduleId = params.etlmoduleid;
            ImporterViewModel.apply(this, arguments);
            this.loading = params.config.loading;
            this.templates = ko.observableArray();
            this.selectedTemplate = ko.observable();

            const getGraphs = async function() {
                let response = await fetch(arches.urls.graphs_api);
                if (response.ok) {
                    let graphs = await response.json();
                    let templates = graphs.map(function(graph){
                        return {text: graph.name, id: graph.graphid};
                    });
                    self.templates(templates);
                }
              }

            getGraphs();

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