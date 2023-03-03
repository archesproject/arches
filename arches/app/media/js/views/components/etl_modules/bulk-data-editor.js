define([
    'knockout',
    'knockout-mapping',
    'jquery',
    'uuid',
    'arches',
    'viewmodels/alert-json',
    'templates/views/components/etl_modules/bulk-data-editor.htm',
    'views/components/simple-switch',
    'bindings/datatable',
    'bindings/dropzone',
    'bindings/resizable-sidepanel',
], function(ko, koMapping, $, uuid, arches, JsonErrorAlertViewModel, bulkDataEditorTemplate) {
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
        this.operation = ko.observable();
        this.oldText = ko.observable();
        this.newText = ko.observable();
        this.validated = ko.observable();
        this.validationError = ko.observableArray();
        this.formData = new window.FormData();
        this.loadId = params.loadId || uuid.generate();
        this.resourceids = ko.observable();

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
        this.selectedNode.subscribe(value=>console.log(value, value));

        // this.resourceids(['cde6aa45-8013-433e-b1f1-9040ca011d7d', '08d547ab-16a9-4a66-b7ec-2e33bf9cd510']);
        this.write = function() {
            self.formData.append('operation', self.operation());
            if (self.selectedNode()) { self.formData.append('node_id', self.selectedNode()); }
            if (self.selectedGraph()) { self.formData.append('graph_id', self.selectedGraph()); }
            if (self.selectedLanguage()) { self.formData.append('language_code', self.selectedLanguage().code); }
            if (self.oldText()) { self.formData.append('old_text', self.oldText()); }
            if (self.newText()) { self.formData.append('new_text', self.newText()); }
            if (self.resourceids()) { self.formData.append('resourceids', JSON.stringify(self.resourceids())); }
            self.loading(true);
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
        template: bulkDataEditorTemplate,
    });
    return viewModel;
});