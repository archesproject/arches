define([
    'knockout',
    'jquery',
    'uuid',
    'arches',
    'viewmodels/alert-json',
    'templates/views/components/etl_modules/bulk_edit_concept.htm',
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
        this.nodeid = ko.observable();
        this.dropdownConcept = ko.observableArray();
        this.allchildconcept = ko.observableArray();
        this.dropdownnodes = ko.observableArray();
        this.allinformationTable = ko.observableArray();
        this.selectednode = ko.observable();
        this.dropdowngraph = ko.observableArray();
        this.selectedgrapgh = ko.observable();
        this.Selectold = ko.observable();
        this.Selectnew = ko.observable();
        this.vaoldlanguage = ko.observable();
        this.vanewlanguage = ko.observable();
        this.dropdownoldlang = ko.observableArray();
        this.dropdownnewlang = ko.observableArray();
        this.dropdownConceptReplace = ko.observableArray();
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
            if (self.selectedgrapgh()) { self.formData.append('selectedgrapgh', self.selectedgrapgh()); }
            if (self.saveid()) { self.formData.append('saveid', self.saveid()); }
            if (self.savenode()) { self.formData.append('savenode', self.savenode()); }
            if (self.Selectold()) { self.formData.append('Selectold', self.Selectold()); }
            if (self.Selectnew()) { self.formData.append('Selectnew', self.Selectnew()); }
            if (self.allchildconcept()) { self.formData.append('allchildconcept', self.allchildconcept()); }
            if (self.vaoldlanguage()) { self.formData.append('vaoldlanguage', self.vaoldlanguage()); }
            if (self.vanewlanguage()) { self.formData.append('vanewlanguage', self.vanewlanguage()); }
            if (self.selectednode()) { self.formData.append('selectednode', self.selectednode()); }
            if (self.allinformationTable()) { self.formData.append('table', self.allinformationTable()); }
            if (self.nodeid) { self.formData.append('nodeid', self.nodeid); }
            if (self.searchUrl()) { self.formData.append('search_url', self.searchUrl()); }
        };
        self.deleteAllFormData = () => {
            self.formData.delete('selectedgrapgh');
            self.formData.delete('saveid');
            self.formData.delete('savenode');
            self.formData.delete('Selectold');
            self.formData.delete('Selectnew');
            self.formData.delete('allchildconcept');
            self.formData.delete('vaoldlanguage');
            self.formData.delete('vanewlanguage');
            self.formData.delete('selectednode');
            self.formData.delete('table');
            self.formData.delete('nodeid');
            self.formData.delete('search_url');
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
        this.ReplaceConcept = function() {
            self.addAllFormData();
            self.allinformationTable.removeAll()
            self.tableVisible(true);
            self.showPreview(true);
            self.submit('replaceConcept').then(data => {
                
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

        //select concept and create dropdwon with olad and new
        this.selectconcept = function() {
            self.addAllFormData();
            self.dropdownConcept.removeAll()
            self.dropdownConceptReplace.removeAll()
            self.allchildconcept.removeAll();
            self.dropdownnewlang.removeAll();
            self.dropdownoldlang.removeAll();
            self.tableVisible(false);
            
            self.submit('list_concepts').then(data => {
                
                for (var i = 0; i < data.result.length; i++){
                    if(i < data.result.length -1){
                        
                        self.dropdownConcept.push(data.result[i][1]);
                        self.allchildconcept.push(data.result[i]);
                        self.dropdownConceptReplace.push(data.result[i][1]);
                    }else{
                        this.nodeid = data.result[i][0];
                    }
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
            });
        };

        //select old language
        this.language = function(type) {
            self.addAllFormData();
            self.tableVisible(false);
            if (type === 'Old') {
                self.dropdownoldlang.removeAll();
                self.submit('select_language', 'language_old').then(data => {
                
                    for (var i = 0; i < data.result.length; i++){
                        self.dropdownoldlang.push(data.result[i]);
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
                });
            }
            else if (type === 'New') {
                self.dropdownnewlang.removeAll();
                self.submit('select_language', "language_new").then(data => {
                    for (var i = 0; i < data.result.length; i++){
    
                        self.dropdownnewlang.push(data.result[i]);
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
                });
            }

        };

        //select nodes and take the specific value
        this.allnodes = function() {
            self.addAllFormData();
            self.dropdownnodes.removeAll();
            self.savenode.removeAll();
            self.dropdownoldlang.removeAll();
            self.dropdownnewlang.removeAll();
            self.dropdownConcept.removeAll();
            self.dropdownConceptReplace.removeAll();
            self.allchildconcept.removeAll();
            self.tableVisible(false);
            self.showPreview(false);
            self.submit('get_graphs_node').then(data => {
                for (var i = 0; i < data.result.length; i++){
                    
                    self.dropdownnodes.push(data.result[i][0]);
                    self.savenode.push(data.result[i]);
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
            });
        };



        //take the graphs 
        this.allgraph = function() {
            self.addAllFormData();
            self.dropdowngraph.removeAll();
            self.dropdownoldlang.removeAll();
            self.dropdownnewlang.removeAll();
            self.saveid.removeAll();
            self.dropdownnodes.removeAll();
            self.savenode.removeAll();
            self.dropdownConcept.removeAll()
            self.dropdownConceptReplace.removeAll()
            self.allchildconcept.removeAll();
            self.tableVisible(false);
            self.showPreview(false);

            self.submit('all_graph').then(data => {
                for (var i = 0; i < data.result.length; i++){
                    self.dropdowngraph.push(data.result[i][1]);
                    self.saveid.push(data.result[i]);

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
            });
        };
        
        this.write = function() {
            self.showPreview(false);
            self.showPreviewTalbe(false)
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
            if (data){
                self.formData.append("type_lang", data)
            }
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
    ko.applyBindings(new ViewModel()); // This makes Knockout get to work
    return ViewModel;
});
