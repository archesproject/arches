import ko from "knockout";
import koMapping from "knockout-mapping";
import $ from "jquery";
import dropzone from "dropzone";
import stringUtils from "utils/strings";
import uuid from "uuid";
import arches from "arches";
import JsonErrorAlertViewModel from "viewmodels/alert-json";
import importSingleCSVTemplate from "templates/views/components/etl_modules/import-single-csv.htm";
import "views/components/simple-switch";
import "bindings/datatable";
import "bindings/dropzone";
import "bindings/resizable-sidepanel";


const viewModel = function(params) {
    const self = this;
    this.loadDetails = params.load_details || ko.observable();
    this.state = params.state;
    this.loading = params.loading || ko.observable();
    this.alert = params.alert;
    this.moduleId = params.etlmoduleid;
    this.graphs = ko.observable();
    this.selectedGraph = ko.observable();
    this.nodes = ko.observable();
    this.fileInfo = ko.observable({name:"", size:""});
    this.hasHeaders = ko.observable(true);
    this.csvArray = ko.observable();
    this.headers = ko.observable();
    this.fieldMapping = ko.observableArray();
    this.csvBody = ko.observable();
    this.csvExample = ko.observable();
    this.csvFileName = ko.observable();
    this.numberOfCol = ko.observable();
    this.numberOfRow = ko.observable();
    this.numberOfExampleRow = ko.observable();
    this.languages = ko.observableArray();
    this.languages(arches.languages);
    this.fileAdded = ko.observable(false);
    this.validated = ko.observable();
    this.validationError = ko.observableArray();
    this.formData = new window.FormData();
    this.loadId = params.loadId || uuid.generate();
    this.uniqueId = uuid.generate();
    this.uniqueidClass = ko.computed(function() {
        return "unique_id_" + self.uniqueId;
    });

    this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
    this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
    this.validationErrors = params.validationErrors || ko.observable();
    this.validated = params.validated || ko.observable();
    this.getErrorReport = params.getErrorReport;
    this.getNodeError = params.getNodeError;
    this.formatTime = params.formatTime;
    this.timeDifference = params.timeDifference;
    this.ready = ko.computed(() => {
        return self.selectedGraph() && self.fieldMapping().find((mapping) => mapping.node());
    });
    this.suggestField = function(i) {
        let bestMatch = null;
        let highestScore = 0;
        if (!!self.headers()) {
            const header = stringUtils.normalizeText(self.headers()[i]);
            if (header == 'resourceid')
                return null;
    
            self.nodes().forEach(function(node) {
                if (node.name) {
                    const nameNorm = stringUtils.normalizeText(node.name);
                    const aliasNorm = node.alias ? stringUtils.normalizeText(node.alias) : '';
    
                    // Compute similarity scores
                    const scoreWithName = stringUtils.compareTwoStrings(header, nameNorm);
                    const scoreWithAlias = stringUtils.compareTwoStrings(header, aliasNorm);
                    const bestNodeScore = Math.max(scoreWithName, scoreWithAlias);
                    if (bestNodeScore > highestScore) {
                        highestScore = bestNodeScore;
                        bestMatch = node;
                    }
                }
            });
    
            // Return the alias of the best match if the highest score is above a certain threshold (e.g., 0.8)
            if (bestMatch && highestScore > 0.5) {
                return bestMatch.alias;
            }
        }
        return null;
    }
    this.guessAllMappings = function() {
        if (self.headers()) {
            self.headers().forEach((header, i) => {
                const bestMatchNode = self.suggestField(i);
                if (bestMatchNode && self.fieldMapping().length > i) {
                    self.fieldMapping()[i].node(bestMatchNode);
                }
            });
        }
    };

    this.createTableConfig = function(col) {
        return {
            paging: false,
            searching: false,
            scrollCollapse: true,
            info: false,
            // columnDefs: [{
            //     orderable: false,
            //     targets: -1,
            // }],
            columns: Array(col).fill(null)
        };
    };

    this.hasHeaders.subscribe(function(val){
        self.headers(null);
        if (val) {
            self.headers(self.csvArray()[0]);
            self.csvBody(self.csvArray().slice(1));
        } else {
            self.headers(Array.apply(0, Array(self.csvArray()[0].length)).map(function(_,b) { return b + 1; }));
            self.csvBody(self.csvArray());
        }
    });

    this.headers.subscribe(function(headers){
        if (headers) {
            self.fieldMapping(
                headers.map(function(header){
                    return {
                        field: header,
                        node: ko.observable(),
                        language: ko.observable(
                            arches.languages.find(lang => lang.code == arches.activeLanguage)
                        ),
                    };
                })
            );
        }
    });

    this.formatSize = function(size) {
        var bytes = size;
        if(bytes == 0) return '0 Byte';
        var k = 1024;
        var dm = 2;
        var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return '<strong>' + parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + '</strong> ' + sizes[i];
    };

    this.csvArray.subscribe(function(val){
        self.numberOfCol(val[0].length);
        if (self.hasHeaders()) {
            self.headers(val[0]);
            self.csvBody(val.slice(1));
        } else {
            self.headers(null);
            self.csvBody(val);
        }
    });

    this.selectedGraph.subscribe(graph => {
        if (!graph) {self.nodes(null);}
    });

    this.csvBody.subscribe(val => {
        self.numberOfRow(val.length);
        self.csvExample(val.slice(0, 5));
    });

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

    this.selectedGraph.subscribe(function(graph){
        if (graph){
            self.loading(true);
            self.formData.append('graphid', graph);
            self.submit('get_nodes').then(function(response){
                const nodes = response.result.map(node => ({ ...node, label: node.alias }));
                self.stringNodes = nodes.reduce((acc, node) => {
                    if (node.datatype === 'string') {
                        acc.push(node.alias);
                    }
                    return acc;
                }, []);
                nodes.unshift({
                    alias: "resourceid",
                    label: arches.translations.idColumnSelection,
                });
                self.nodes(nodes);
                self.loading(false);
            });
        }
    });

    this.addFile = function(file){
        self.loading(true);
        self.fileInfo({name: file.name, size: file.size});
        self.formData.append('file', file, file.name);
        self.submit('read').then(function(response){
            self.csvArray(response.result.csv);
            self.csvFileName(response.result.csv_file);
            if (response.result.config) {
                self.fieldMapping(response.result.config.mapping);
                self.selectedGraph(response.result.config.graph);
            }
            self.formData.delete('file');
            self.fileAdded(true);
            self.loading(false);
        }).fail(function(err) {
            console.log(err);
            self.alert(new JsonErrorAlertViewModel('ep-alert-red', err.responseJSON, null, function(){}));
            self.loading(false);
        });
    };

    this.write = function(){
        if (!self.ready()) { return; }
        const fieldnames = koMapping.toJS(self.fieldMapping).map(fieldname => {return fieldname.node;});
        const fieldMapping = koMapping.toJS(self.fieldMapping);
        self.formData.append('fieldnames', fieldnames);
        self.formData.append('fieldMapping', JSON.stringify(fieldMapping));
        self.formData.append('hasHeaders', self.hasHeaders());
        self.formData.append('graphid', self.selectedGraph());
        self.formData.append('csvFileName', self.csvFileName());
        self.loading(true);
        self.submit('start').then(data => {
            params.activeTab("import");
            self.formData.append('async', true);
            self.submit('write').then(data => {
                console.log(data.result);
            }).fail( function(err) {
                console.log(err);
                self.alert(
                    new JsonErrorAlertViewModel(
                        'ep-alert-red',
                        err.responseJSON["data"],
                        null,
                        function(){}
                    )
                );
            }).always(() => {
                self.loading(false);
            });
        }).fail(error => console.log(error.responseJSON.data));
    };

    this.validate =function(){
        self.validated(false);
        const fieldnames = koMapping.toJS(self.fieldMapping).map(fieldname => fieldname.node);
        const fieldMapping = koMapping.toJS(self.fieldMapping);
        self.formData.append('fieldnames', fieldnames);
        self.formData.append('fieldMapping', JSON.stringify(fieldMapping));
        self.formData.append('hasHeaders', self.hasHeaders());
        self.formData.append('graphid', self.selectedGraph());
        self.submit('validate').then(data => {
            self.validated(true);
            self.validationError(data.result);
        }).fail(error => console.log(error));
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

    this.dropzoneOptions = {
        url: "arches.urls.root",
        dictDefaultMessage: '',
        autoProcessQueue: false,
        uploadMultiple: false,
        // acceptedFiles: ["text/csv"],
        autoQueue: false,
        clickable: ".fileinput-button." + this.uniqueidClass(),
        previewsContainer: '#hidden-dz-previews',
        init: function() {
            self.dropzone = this;
            this.on("addedfile", self.addFile);
            this.on("error", function(file, error) {
                file.error = error;
            });
        }
    };
    this.init = function(){
        this.getGraphs();
    };

    this.init();
};
ko.components.register('import-single-csv', {
    viewModel: viewModel,
    template: importSingleCSVTemplate,
});
export default viewModel;
