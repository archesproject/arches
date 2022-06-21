define([
    'underscore',
    'knockout',
    'viewmodels/base-import-view-model',
    'arches',
    'viewmodels/alert',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
], function(_, ko, ImporterViewModel, arches, AlertViewModel) {
    return ko.components.register('branch-csv-importer', {
        viewModel: function(params) {
            const self = this;
            this.loadDetails = params.load_details || ko.observable();
            this.state = params.state;
            this.loading = params.loading || ko.observable();
            this.data2 = ko.observable(false);

            this.moduleId = params.etlmoduleid;
            ImporterViewModel.apply(this, arguments);
            this.templates = ko.observableArray();
            this.selectedTemplate = ko.observable();
            this.loadStatus = ko.observable('ready');
            this.downloadMode = ko.observable(false);

            this.toggleDownloadMode = () => {
                this.downloadMode(!this.downloadMode());
                if (this.downloadMode() && !ko.unwrap(this.templates).length) {
                    getGraphs();
                }
            };

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
                const url = `/etl-manager`;
                const formData = new window.FormData();
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
                const a = window.document.createElement('a');
                window.document.body.appendChild(a);
                a.href = urlObject;
                a.download = `${this.templates().filter(x => x.id == this.selectedTemplate())[0].text}.xlsx`;
                a.click();

                setTimeout(() => {
                    window.URL.revokeObjectURL(urlObject);
                    window.document.body.removeChild(a);
                }, 0);
                this.loading(false);
            };

            const getGraphs = async function() {
                const response = await fetch(arches.urls.graphs_api);
                if (response.ok) {
                    let graphs = await response.json();
                    let templates = graphs.map(function(graph){
                        return {text: graph.name, id: graph.graphid};
                    });
                    self.templates(templates);
                }
            };

            this.addFile = async function(file){
                self.loading(true);
                self.fileInfo({name: file.name, size: file.size});
                const formData = new window.FormData();
                formData.append('file', file, file.name);
                const response = await self.submit('read', formData);
                if (response.ok) {
                    const data = await response.json();
                    self.loading(false);
                    self.response(data);
                    self.loadDetails(data);
                } else {
                    // eslint-disable-next-line no-console
                    console.log('error');
                    self.loading(false);
                }
            };

            this.start = async function(){
                self.loading(true);
                const response = await self.submit('start');
                self.loading(false);
                params.activeTab("import");
                if (response.ok) {
                    const data = await response.json();
                    self.response(data); 
                    self.write();
                }
            };

            this.write = async function(){
                self.loading(true);
                const formData = new window.FormData();
                formData.append('load_details', JSON.stringify(self.loadDetails()));
                const response = await self.submit('write', formData);
                self.loading(false);
                if (response.ok) {
                    const data = await response.json();
                    self.response(data); 
                }
                else {
                    const data = await response.json();
                    this.alert(new AlertViewModel(
                        'ep-alert-red',
                        data["data"]["title"],
                        data["data"]["message"],
                        null,
                        function(){}
                    ));
                }
            };
        },
        template: { require: 'text!templates/views/components/etl_modules/branch-csv-importer.htm' }
    });
});
