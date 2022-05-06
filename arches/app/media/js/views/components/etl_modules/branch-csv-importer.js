define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'viewmodels/alert',
    'arches',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
], function(_, ko, ImporterViewModel, AlertViewModel, arches, dropzone) {
    return ko.components.register('branch-csv-importer', {
        viewModel: function(params) {
            const self = this;
            this.moduleId = params.etlmoduleid;
            ImporterViewModel.apply(this, arguments);
            this.loading = params.config.loading;
            this.templates = ko.observableArray();
            this.selectedTemplate = ko.observable();
            this.loadStatus = ko.observable('ready');

            function getCookie(name) {
                if (!document.cookie) {
                    return null;
                }
                
                const xsrfCookies = document.cookie.split(';')
                    .map(c => c.trim())
                    .filter(c => c.startsWith(name + '='));
                
                if (xsrfCookies.length === 0) {
                    return null;
                }
                return decodeURIComponent(xsrfCookies[0].split('=')[1]);
            }

            this.downloadTemplate = async () => {
                const url = `/etl-manager`
                const formData = new FormData();
                formData.append("id", ko.unwrap(this.selectedTemplate));
                formData.append("format", "xls");
                formData.append("module", ko.unwrap(self.moduleId));;
                formData.append("action", "download");
                
                const response = await window.fetch(url, {
                    method: 'POST',
                    body: formData,
                    credentials: 'same-origin',
                    headers: {
                        "Accept": "application/json",
                        "X-CSRFToken": getCookie("csrftoken")
                    }
                });

                const blob = await response.blob();
                const urlObject = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                document.body.appendChild(a);
                a.href = urlObject;
                a.download = `${this.templates().filter(x => x.id == this.selectedTemplate())[0].text}%20-%20Template.xls`;
                a.click();

                setTimeout(() => {
                    window.URL.revokeObjectURL(urlObject);
                    document.body.removeChild(a);
                }, 0);
                this.loading(false);
            };

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