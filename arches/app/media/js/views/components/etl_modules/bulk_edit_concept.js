define([
    'knockout',
    'jquery',
    'uuid',
    'arches',
    'viewmodels/alert-json',
    'templates/views/components/etl_modules/bulk_edit_concept.htm',
    'views/components/widgets/concept-select',
    'select-woo'
], function(ko, $, uuid, arches, JsonErrorAlertViewModel, baseStringEditorTemplate) {
    const ViewModel = function(params) {
        const self = this;
        this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
        this.load_details = params.load_details ?? {};
        this.loadId = params.loadId || uuid.generate();
        this.showStatusDetails = ko.observable(false);
        this.moduleId = params.etlmoduleid;
        this.previewing = ko.observable();
        this.formData = new window.FormData();
        this.saveid = ko.observableArray();
        this.savenode = ko.observableArray();
        this.searchUrl = ko.observable();
        // this.dropdownConcept = ko.observableArray();
        this.allchildconcept = ko.observableArray();
        this.dropdownnodes = ko.observableArray();
        this.allinformationTable = ko.observableArray();
        this.selectednode = ko.observable();
        this.dropdowngraph = ko.observableArray();
        this.selectedGraph = ko.observable();
        this.conceptOld = ko.observable();
        this.conceptNew = ko.observable();
        this.conceptOldLang = ko.observable();
        this.conceptNewLang = ko.observable();
        this.rdmCollection = null;
        this.rdmCollectionLanguages = ko.observableArray();
        this.defaultLanguage = ko.observable();
        // this.dropdownConceptReplace = ko.observableArray();
        this.tableVisible = ko.observable(false);
        this.showPreviewTalbe = ko.observable(true);
        this.showPreview = ko.observable(false);
        this.reportUrl = ko.observable(window.location.href.split('/').slice(0, 3).join('/')+'/report/');
        //paging
        this.currentPageIndex = ko.observable(0);
        //loading status
        this.formatTime = params.formatTime;
        this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
        this.statusDetails = this.selectedLoadEvent()?.load_description?.split("|");
        this.timeDifference = params.timeDifference;

        
        this.addAllFormData = () => {
            if (self.selectedGraph()) { self.formData.append('selectedGraph', self.selectedGraph()); }
            if (self.saveid()) { self.formData.append('saveid', self.saveid()); }
            if (self.savenode()) { self.formData.append('savenode', self.savenode()); }
            if (self.conceptOld()) { self.formData.append('conceptOld', self.conceptOld()); }
            if (self.conceptNew()) { self.formData.append('conceptNew', self.conceptNew()); }
            if (self.allchildconcept()) { self.formData.append('allchildconcept', self.allchildconcept()); }
            if (self.conceptOldLang()) { self.formData.append('conceptOldLang', self.conceptOldLang()); }
            if (self.conceptNewLang()) { self.formData.append('conceptNewLang', self.conceptNewLang()); }
            if (self.selectednode()) { self.formData.append('selectednode', JSON.stringify(self.selectednode())); }
            if (self.allinformationTable()) { self.formData.append('table', self.allinformationTable()); }
            if (self.searchUrl()) { self.formData.append('search_url', self.searchUrl()); }
            if (self.rdmCollection) { self.formData.append('rdmCollection', self.rdmCollection); }
        };
        self.deleteAllFormData = () => {
            self.formData.delete('selectedGraph');
            self.formData.delete('saveid');
            self.formData.delete('savenode');
            self.formData.delete('conceptOld');
            self.formData.delete('conceptNew');
            self.formData.delete('allchildconcept');
            self.formData.delete('conceptOldLang');
            self.formData.delete('conceptNewLang');
            self.formData.delete('selectednode');
            self.formData.delete('table');
            self.formData.delete('search_url');
            self.formData.delete('rdmCollection');
        };
        //lenght table
        self.listLength = ko.computed(function() {
            return self.allinformationTable().length;
        });
        //paging
        // Function to navigate to the previous page
        self.previousPage = function() {
            if (self.currentPageIndex() > 0) {
                self.currentPageIndex(self.currentPageIndex() - 1);
            }
        };
        // Function to navigate to the next page
        self.nextPage = function() {
            if (self.currentPageIndex() < self.maxPageIndex()) {
                self.currentPageIndex(self.currentPageIndex() + 1);
            }
        };
        // Computed observable to calculate the maximum page index
        self.maxPageIndex = ko.computed(function() {
            return Math.ceil(self.listLength() / 5) - 1;
        });

        // Computed observable to paginate rows
        self.paginatedRows = ko.computed(function() {
            var startIndex = self.currentPageIndex() * 5;
            var endIndex = startIndex + 5;
            return self.allinformationTable().slice(startIndex, endIndex);
        });

        //make url
        self.constructReportUrl = function(dataItem) {
            return self.reportUrl() + dataItem[0];
        };

        //delete Row in table
        this.deleteRow = function(data) {
            self.addAllFormData();
            // Remove the row from the allinformationTable array
            self.allinformationTable.remove(data);
        };

        //call python code to display the change
        this.getPreviewData = function() {
            self.addAllFormData();
            self.allinformationTable.removeAll();
            self.tableVisible(true);
            self.showPreview(true);
            self.submit('get_preview_data').then(data => {
                
                for (var i = 0; i < data.result.length; i++){
                    self.allinformationTable.push(data.result[i]);
                }
                
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

        this.ready = ko.computed(() => {
            const ready = !!self.selectedGraph() &&
                !!self.selectednode() &&
                !self.previewing() &&
                self.conceptNew() !== self.conceptOld() &&
                !!self.conceptNew() &&
                !!self.conceptOld();
            return ready;
        });

        this.selectednode.subscribe((node) => {
            self.rdmCollection = node.rdmCollection;
            self.addAllFormData();
            self.conceptNew("");
            self.conceptOld("");
            // self.dropdownConcept.removeAll();
            // self.dropdownConceptReplace.removeAll();
            self.allchildconcept.removeAll();
            self.tableVisible(false);

            self.submit('get_collection_languages').then(data => {
                self.rdmCollectionLanguages(data.result);
                if(data.result.length > 0) {
                    self.conceptOldLang(data.result[0].id);
                    self.conceptNewLang(data.result[0].id);
                }
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
                //self.previewing(false);
            });
        });

        //select old language
        // this.language = function(dd) {
        //     self.addAllFormData();
        //     self.tableVisible(false);
        //     dd.removeAll();
        //     self.submit('select_language').then(data => {
        //         for (var i = 0; i < data.result.length; i++){
        //             dd.push(data.result[i]);
        //         }   
        //     }).fail(function(err) {
        //         self.alert(
        //             new JsonErrorAlertViewModel(
        //                 'ep-alert-red',
        //                 err.responseJSON["data"],
        //                 null,
        //                 function(){}
        //             )
        //         );
        //     }).always(function() {
        //         self.previewing(false);
        //     });
        // };

        //select nodes and take the specific value
        this.selectedGraph.subscribe((graphid) => {
            self.addAllFormData();
            self.dropdownnodes.removeAll();
            self.savenode.removeAll();
            self.conceptNew("");
            self.conceptOld("");
            self.allchildconcept.removeAll();
            self.tableVisible(false);
            self.showPreview(false);
            self.submit('get_graphs_node').then(data => {
                const nodes = data.result.map(node => (
                    {   node: node.nodeid,
                        label: `${JSON.parse(node.card_name)[arches.activeLanguage]} - ${JSON.parse(node.widget_label)[arches.activeLanguage]}`,
                        rdmCollection: JSON.parse(node.config).rdmCollection
                    }));
                self.dropdownnodes(nodes);
                // for (var i = 0; i < data.result.length; i++){
                    
                //     self.dropdownnodes.push(data.result[i][0]);
                //     self.savenode.push(data.result[i]);
                // }   
                
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
            });

        });

        //take the graphs 
        this.allgraph = function() {
            self.addAllFormData();
            self.dropdowngraph.removeAll();
            self.saveid.removeAll();
            self.dropdownnodes.removeAll();
            self.savenode.removeAll();
            // self.dropdownConcept.removeAll();
            // self.dropdownConceptReplace.removeAll();
            self.allchildconcept.removeAll();
            self.tableVisible(false);
            self.showPreview(false);

            self.submit('get_graphs').then(data => {
                data.result.forEach(graph => {
                    self.dropdowngraph.push({"graphName": graph.name, "graphid": graph.graphid});
                });
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
            });
        };
        
        this.write = function() {
            self.showPreview(false);
            self.showPreviewTalbe(false);
            self.addAllFormData();
            params.activeTab("import");
            self.submit('write').then(data => {
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

        this.submit = function(action, data) {
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
        
        this.allgraph();
    };

    // Register the 'bulk_edit_concept' component
    ko.components.register('bulk_edit_concept', {
        viewModel: ViewModel,
        template: baseStringEditorTemplate,
    });

    // Apply bindings after registering the component
    //ko.applyBindings(new ViewModel()); // This makes Knockout get to work
    return ViewModel;
});
