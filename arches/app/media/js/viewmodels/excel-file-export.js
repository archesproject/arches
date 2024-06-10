define([
    'underscore',
    'jquery',
    'js-cookie',
    'knockout',
    'uuid',
    'arches',
    'viewmodels/alert-json',
    'dropzone',
    'bindings/select2-query',
    'bindings/dropzone',
    'views/components/simple-switch',
], function(_, $, Cookies, ko, uuid, arches, JsonErrorAlertViewModel) {
    const ExcelFileExportViewModel = function(params) {
        const self = this;

        this.loadDetails = params.load_details || ko.observable();
        this.state = params.state;
        this.loading = params.loading || ko.observable();
        this.moduleId = params.etlmoduleid;
        this.loadId = params.loadId || uuid.generate();
        this.formData = new window.FormData();
        this.searchUrl = ko.observable();
        this.formatTime = params.formatTime;
        this.timeDifference = params.timeDifference;
        this.exportConceptsAs = ko.observable('uuids');

        this.graphs = arches.resources.map(resource => ({name: resource.name, graphid: resource.graphid}));
        this.selectedGraph = ko.observable();
        this.resourceids = ko.observable();

        this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
        this.validationErrors = params.validationErrors || ko.observable();
        this.validated = params.validated || ko.observable();
        this.getErrorReport = params.getErrorReport;
        this.getNodeError = params.getNodeError;
        this.alert = params.alert;
        this.filename = ko.observable();

        this.getGraphName = (selectedGraphId) => {
            if (self.graphs) {
                return self.graphs.find((graph) => graph.graphid === selectedGraphId).name;
            }
        };

        this.exportResources = async function() {
            if (self.searchUrl()) { self.formData.append('search_url', self.searchUrl()); }
            self.formData.append('graph_id', self.selectedGraph());
            self.formData.append('graph_name', self.getGraphName(self.selectedGraph()));
            self.formData.append('export_concepts_as', self.exportConceptsAs());
            const response = await self.submit('export');
            params.activeTab("import");

            if (response.ok) {
                const json = await response.json();
                console.log(json.result);
            }
            else {
                const err = await response.json();
                console.log(err);
                self.alert(
                    new JsonErrorAlertViewModel(
                        'ep-alert-red',
                        err.data,
                        null,
                        function(){}
                    )
                );
            }
            this.loading(false);
        };

        this.submit = function(action) {
            self.formData.append('action', action);
            self.formData.append('load_id', self.loadId);
            self.formData.append('module', self.moduleId);

            if (self.filename()) {
                self.formData.append('filename', self.filename());
            }
            
            return fetch(arches.urls.etl_manager, {
                method: 'POST',
                body: self.formData,
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                }
            });
        };
    };
    return ExcelFileExportViewModel;
});
