import ko from 'knockout';
import koMapping from 'knockout-mapping';
import $ from 'jquery';
import uuid from 'uuid';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import JsonErrorAlertViewModel from 'viewmodels/alert-json';
import baseStringEditorTemplate from 'templates/views/components/etl_modules/base-bulk-string-editor.htm';
import 'views/components/simple-switch';
import 'bindings/datatable';
import 'bindings/dropzone';
import 'bindings/resizable-sidepanel';


const viewModel = function(params) {
    const self = this;

    this.operationLabel = {
        "trim": "Trim",
        "replace": "Replace (Case Sensitive)",
        "replace_i": "Replace (Case Insensitive)",
        "capitalize": "Capitalize",
        "capitalize_trim": "Capitalize (Also, remove leading/trailing spaces)",
        "upper": "Uppercase",
        "upper_trim": "Uppercase (Also, remove leading/trailing spaces)",
        "lower": "Lowercase",
        "lower_trim": "Lowercase (Also, remove leading/trailing spaces)",
    };

    this.load_details = params.load_details;
    this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
    this.statusDetails = this.selectedLoadEvent()?.load_description?.split("|");
    this.showStatusDetails = ko.observable(false);
    this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
    this.state = params.state;
    this.loading = params.loading || ko.observable();
    this.alert = params.alert;
    this.moduleId = params.etlmoduleid;
    this.formatTime = params.formatTime;
    this.timeDifference = params.timeDifference;
    this.config = params.config;
    this.loading(true);
    this.previewing = ko.observable();
    this.languages = ko.observable(arches.languages);
    this.selectedLanguage = ko.observable(this.languages().find(lang => lang.code === arches.activeLanguage));
    this.graphs = ko.observable();
    this.selectedGraph = ko.observable();
    this.nodes = ko.observable();
    this.selectedNode = ko.observable();
    this.selectedNodeName = ko.observable();
    this.operation = ko.observable();
    this.oldText = ko.observable();
    this.newText = ko.observable();
    this.validated = ko.observable();
    this.validationError = ko.observableArray();
    this.formData = new window.FormData();
    this.loadId = params.loadId || uuid.generate();
    this.resourceids = ko.observable();
    this.previewValue = ko.observable();
    this.previewLimit = ko.observable();
    this.showPreview = ko.observable(false);
    this.searchUrl = ko.observable();
    this.caseInsensitive = ko.observable();
    this.wholeWord = ko.observable();
    this.trim = ko.observable();
    this.numberOfResources = ko.observable(0);
    this.numberOfTiles = ko.observable(0);
    this.selectedCaseOperation = ko.observable();

    this.caseOperations = [
        {name: 'capitalize', label: 'Capitalize'},
        {name: 'upper', label: 'Upper Case'},
        {name: 'lower', label: 'Lower Case'}
    ];
    this.getGraphs = function(){
        self.loading(true);
        self.submit('get_graphs').then(function(response){
            self.graphs(response.result);
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

    this.ready = ko.computed(() => {
        const ready = !!self.selectedGraph() &&
            !!self.selectedNode() &&
            !self.previewing() &&
            ((self.operation() == 'replace' && !!self.oldText() && !!self.newText() || self.operation() != 'replace'));
        return ready;
    });

    this.clearResults = ko.computed(() => {
        // if any of these values change then clear the preview results
        self.showPreview(false);
        // we don't actually care about the results of the following
        let clearResults = '';
        [self.selectedGraph(),
            self.selectedCaseOperation(),
            self.selectedNode(),
            self.searchUrl(),
            self.selectedLanguage(),
            ((self.operation() == 'replace' && !!self.oldText() && !!self.newText() || self.operation() != 'replace'))
        ].forEach(function(item){
            clearResults += item?.toString();
        });
        return clearResults;
    });

    this.allowEditOperation = ko.computed(() => {
        return self.ready() && self.numberOfTiles() > 0 && self.showPreview();
    });

    this.addAllFormData = () => {
        if (self.operation() == 'case'){
            self.formData.append('operation', self.selectedCaseOperation());
        } else {
            self.formData.append('operation', self.operation());
        }
        if (self.searchUrl()) { self.formData.append('search_url', self.searchUrl()); }
        if (self.selectedNode()) { self.formData.append('node_id', self.selectedNode()); }
        if (self.selectedNodeName()) { self.formData.append('node_name', self.selectedNodeName()); }
        if (self.selectedGraph()) { self.formData.append('graph_id', self.selectedGraph()); }
        if (self.selectedLanguage()) { self.formData.append('language_code', self.selectedLanguage().code); }
        if (self.caseInsensitive()) { self.formData.append('case_insensitive', self.caseInsensitive()); }
        if (self.wholeWord()) { self.formData.append('whole_word', self.wholeWord()); }
        if (self.trim()) { self.formData.append('also_trim', self.trim()); }
        if (self.oldText()) { self.formData.append('old_text', self.oldText()); }
        if (self.newText()) { self.formData.append('new_text', self.newText()); }
        if (self.resourceids()) { self.formData.append('resourceids', JSON.stringify(self.resourceids())); }
    };

    self.deleteAllFormData = () => {
        self.formData.delete('operation');
        self.formData.delete('search_url');
        self.formData.delete('node_id');
        self.formData.delete('node_name');
        self.formData.delete('graph_id');
        self.formData.delete('language_code');
        self.formData.delete('case_insensitive');
        self.formData.delete('whole_word');
        self.formData.delete('also_trim');
        self.formData.delete('old_text');
        self.formData.delete('new_text');
        self.formData.delete('resourceids');
    };

    this.selectedNode.subscribe(nodeid => {
        if (nodeid) {
            self.selectedNodeName(self.nodes().find(node => node.nodeid === nodeid).label);
        }
    });

    this.selectedGraph.subscribe(function(graph){
        if (graph){
            self.loading(true);
            self.formData.append('graphid', graph);
            self.submit('get_nodes').then(function(response){
                const nodes = response.result.map(node => (
                    { ...node,
                        label: `${JSON.parse(node.card_name)[arches.activeLanguage]} - ${JSON.parse(node.widget_label)[arches.activeLanguage]}` 
                    }));
                self.selectedNode(null);
                self.nodes(nodes);
                self.loading(false);
            });
        } else {
            self.nodes(null);
        }
    });

    this.preview = function() {
        if (!self.ready()) {
            return;
        }

        self.previewing(true);
        self.showPreview(false);
        self.previewValue([]);

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

        self.addAllFormData();
        self.submit('preview').then(data => {
            self.previewValue(data.result.value);
            self.showPreview(true);
            self.numberOfResources(data.result.number_of_resources);
            self.numberOfTiles(data.result.number_of_tiles);
            self.previewLimit(data.result.preview_limit);
        }).fail(function(err) {
            self.alert(
                new JsonErrorAlertViewModel(
                    'ep-alert-red',
                    err.responseJSON["data"],
                    null,
                    function(){}
                )
            );
        }).always(function() {
            self.previewing(false);
            self.deleteAllFormData();
        });
    };

    this.write = function() {
        if (!self.allowEditOperation()) {
            return;
        }
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

        self.addAllFormData();
        params.activeTab("import");
        self.submit('write').then(data => {
            //console.log(data.result);
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
    template: baseStringEditorTemplate,
});
export default viewModel;
