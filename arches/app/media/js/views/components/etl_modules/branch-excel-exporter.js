define([
    'underscore',
    'jquery',
    'js-cookie',
    'knockout',
    'uuid',
    'arches',
    'viewmodels/alert-json',
    'templates/views/components/etl_modules/branch-excel-exporter.htm',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
], function(_, $, Cookies, ko, uuid, arches, JsonErrorAlertViewModel, branchExcelExporterTemplate) {
    return ko.components.register('branch-excel-exporter', {
        viewModel: function(params) {
            const self = this;

            this.loadDetails = params.load_details || ko.observable();
            this.state = params.state;
            this.loading = params.loading || ko.observable();
            this.moduleId = params.etlmoduleid;
            this.loadId = params.loadId || uuid.generate();
            this.formData = new window.FormData();
            this.searchUrl = ko.observable();

            this.graphs = ko.observable();
            this.selectedGraph = ko.observable();
            this.selectedGraph.subscribe(val=>console.log(val));
            this.resourceids = ko.observable();
    
            this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
            this.validationErrors = params.validationErrors || ko.observable();
            this.validated = params.validated || ko.observable();
            this.getErrorReport = params.getErrorReport;
            this.getNodeError = params.getNodeError;

            this.getGraphs = async function(){
                self.loading(true);
                const response = await self.submit('get_graphs');
                const json = await response.json();
                self.graphs(json.result);
                self.loading(false);
            };

            this.exportResources = async function() {
                self.formData.append('graph_id', self.selectedGraph());

                const response = await self.submit('export');
                const blob = await response.blob();
                const urlObject = window.URL.createObjectURL(blob);
                const a = window.document.createElement('a');
                window.document.body.appendChild(a);
                a.href = urlObject;
                a.download = 'export.xlsx';
                a.click();

                setTimeout(() => {
                    window.URL.revokeObjectURL(urlObject);
                    window.document.body.removeChild(a);
                }, 0);
                this.loading(false);
            };

            this.submit = function(action) {
                self.formData.append('action', action);
                self.formData.append('load_id', self.loadId);
                self.formData.append('module', self.moduleId);
                return fetch(arches.urls.etl_manager, {
                    method: 'POST',
                    body: self.formData,
                    credentials: 'include',
                    headers: {
                        "X-CSRFToken": Cookies.get('csrftoken')
                    }
                });
            };

            this.init = function(){
                self.getGraphs();
            };
    
            this.init();    
        },
        template: branchExcelExporterTemplate,
    });
});
