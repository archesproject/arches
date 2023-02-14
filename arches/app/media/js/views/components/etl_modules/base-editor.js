define([
    'knockout',
    'knockout-mapping',
    'jquery',
    'uuid',
    'arches',
    'viewmodels/alert',
    'viewmodels/alert-json',
    'templates/views/components/etl_modules/base-editor.htm',
    'views/components/simple-switch',
    'bindings/datatable',
    'bindings/dropzone',
    'bindings/resizable-sidepanel',
], function(ko, koMapping, $, uuid, arches, AlertViewModel, JsonErrorAlertViewModel, baseEditorTemplate) {
    const viewModel = function(params) {
        const self = this;

        this.load_details = params.load_details;
        this.state = params.state;
        this.loading = params.loading || ko.observable();
        this.alert = params.alert;
        this.moduleId = params.etlmoduleid;
        this.loading(true);
        this.languages = ko.observable(arches.languages);
        this.selectedLanguage = ko.observable();
        // this.selectedLanguage(arches.languages?.find(lang => lang.code == arches.activeLanguage));
        this.graphs = ko.observable();
        this.selectedGraph = ko.observable();
        this.nodes = ko.observable();
        this.selectedNode = ko.observable();
        self.selectedNodeName = ko.observable();
        this.operation = ko.observable();
        this.oldText = ko.observable();
        this.newText = ko.observable();
        this.validated = ko.observable();
        this.validationError = ko.observableArray();
        this.formData = new window.FormData();
        this.loadId = params.loadId || uuid.generate();
        this.resourceids = ko.observable();
        this.previewValue = ko.observable();
        this.showPreview = ko.observable(false);

        this.getGraphs = function(){
            self.loading(true);
            self.submit('get_graphs').then(function(response){
                self.graphs(response.result);
                self.selectedGraph(self.graphs()[0].graphid);
                self.loading(false);
            });
        };

        this.getGraphName = function(graphId){
            let graph;
            if (self.graphs()) {
                graph = self.graphs().find(function(graph){
                    return graph.graphid == graphId;
                });
            }
            return graph?.name;
        };

        this.selectedNode.subscribe(nodeid => { self.selectedNodeName(self.nodes().find(node => node.nodeid === nodeid).name); });

        this.selectedGraph.subscribe(function(graph){
            if (graph){
                self.loading(true);
                self.formData.append('graphid', graph);
                self.submit('get_nodes').then(function(response){
                    const nodes = response.result.map(node => ({ ...node, label: node.alias }));
                    self.nodes(nodes);
                    self.loading(false);
                });
            }
        });

        this.preview = function() {
            if (self.operation() === 'replace' && (!self.oldText() || !self.newText())){
                self.alert(
                    new AlertViewModel(
                        'ep-alert-red',
                        "",
                        "The old and new texts should be provided to replace texts",
                        null,
                        function(){}
                    )
                );
                return;
            }
            self.formData.append('operation', self.operation());
            if (self.selectedNode()) { self.formData.append('node_id', self.selectedNode()); }
            if (self.selectedGraph()) { self.formData.append('graph_id', self.selectedGraph()); }
            if (self.selectedLanguage()) { self.formData.append('language_code', self.selectedLanguage().code); }
            if (self.oldText()) { self.formData.append('old_text', self.oldText()); }
            if (self.newText()) { self.formData.append('new_text', self.newText()); }
            if (self.resourceids()) { self.formData.append('resourceids', JSON.stringify(self.resourceids())); }
            self.submit('preview').then(data => {
                console.log(data.result);
                self.previewValue(data.result);
                self.showPreview(true);
            }).fail(function(err) {
                console.log(err);
            }).always(function() {
                self.formData.delete('operation');
                self.formData.delete('node_id');
                self.formData.delete('graph_id');
                self.formData.delete('language_code');
                self.formData.delete('old_text');
                self.formData.delete('new_text');
                self.formData.delete('resourceids');    
            });
        };

        this.write = function() {
            if (self.operation() === 'replace' && (!self.oldText() || !self.newText())){
                self.alert(
                    new AlertViewModel(
                        'ep-alert-red',
                        "",
                        "The old and new texts should be provided to replace texts",
                        null,
                        function(){}
                    )
                );
                return;
            }
            self.formData.append('operation', self.operation());
            if (self.selectedNode()) { self.formData.append('node_id', self.selectedNode()); }
            if (self.selectedNodeName()) { self.formData.append('node_name', self.selectedNodeName()); }
            if (self.selectedGraph()) { self.formData.append('graph_id', self.selectedGraph()); }
            if (self.selectedLanguage()) { self.formData.append('language_code', self.selectedLanguage().code); }
            if (self.oldText()) { self.formData.append('old_text', self.oldText()); }
            if (self.newText()) { self.formData.append('new_text', self.newText()); }
            if (self.resourceids()) { self.formData.append('resourceids', JSON.stringify(self.resourceids())); }
            self.loading(true);
            params.activeTab("import");
            self.submit('write').then(data => {
                params.activeTab("import");
                console.log(data.result);
            }).fail( function(err) {
                self.alert(
                    new JsonErrorAlertViewModel(
                        'ep-alert-red',
                        err.responseJSON["data"],
                        null,
                        function(){}
                    )
                );
            });
        };

        this.submit = function(action) {
            self.formData.append('action', action);
            self.formData.append('load_id', self.loadId);
            self.formData.append('module', self.moduleId);
            return $.ajax({
                type: "POST",
                url: arches.urls.etl_manager,
                data: self.formData,
                cache: false,
                processData: false,
                contentType: false,
            });
        };

        this.init = function(){
            this.getGraphs();
        };

        this.init();
    };
    ko.components.register('bulk-data-editor', {
        viewModel: viewModel,
        template: baseEditorTemplate,
    });
    return viewModel;
});