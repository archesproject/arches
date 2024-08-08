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
        this.config = params.config;
        this.state = params.state;
        this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
        this.load_details = params.load_details ?? {};
        this.loadId = params.loadId || uuid.generate();
        this.showStatusDetails = ko.observable(false);
        this.moduleId = params.etlmoduleid;
        this.previewing = ko.observable();
        this.formData = new window.FormData();
        this.searchUrl = ko.observable();
        this.dropdownnodes = ko.observableArray();
        this.selectedNode = ko.observable();
        this.dropdowngraph = ko.observableArray();
        this.selectedGraph = ko.observable();
        this.conceptOld = ko.observable();
        this.conceptNew = ko.observable();
        this.conceptOldLang = ko.observable();
        this.conceptNewLang = ko.observable();
        this.rdmCollection = null;
        this.rdmCollectionLanguages = ko.observableArray();
        this.showPreview = ko.observable(false);
        //paging
        this.currentPageIndex = ko.observable(0);
        this.tilesToRemove = ko.observableArray();
        //length table
        this.numberOfTiles = ko.observable();
        this.numberOfResources = ko.observable();
        this.previewLimit = ko.observable();
        //loading status
        this.formatTime = params.formatTime;
        this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
        this.statusDetails = this.selectedLoadEvent()?.load_description?.split("|");
        this.timeDifference = params.timeDifference;
        this.alert = params.alert || ko.observable();
        
        this.addAllFormData = () => {
            self.formData = new window.FormData();
            self.formData.append('load_id', self.loadId);
            self.formData.append('module', self.moduleId);
            if (self.selectedGraph()) { self.formData.append('selectedGraph', self.selectedGraph()); }
            if (self.conceptOld()) { self.formData.append('conceptOld', self.conceptOld()); }
            if (self.conceptNew()) { self.formData.append('conceptNew', self.conceptNew()); }
            if (self.selectedNode()) { self.formData.append('selectedNode', JSON.stringify(self.selectedNode())); }
            if (self.searchUrl()) { self.formData.append('search_url', self.searchUrl()); }
            if (self.rdmCollection) { self.formData.append('rdmCollection', self.rdmCollection); }
            self.formData.append('currentPageIndex', self.currentPageIndex());
            self.formData.append('tilesToRemove', self.tilesToRemove());
        };

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

        self.currentPageIndex.subscribe((pageIndex) => {
            self.getPreviewData();
        });
        // Computed observable to calculate the maximum page index
        self.maxPageIndex = ko.computed(function() {
            return Math.ceil(self.numberOfTiles() / 5) - 1;
        });

        // Computed observable to paginate rows
        self.paginatedRows = ko.observableArray();

        //make url
        self.constructReportUrl = function(dataItem) {
            return arches.urls.reports + dataItem.resourceid;
        };

        this.ready = ko.computed(() => {
            const ready = !!self.selectedGraph() &&
                !!self.selectedNode() &&
                !self.previewing() &&
                self.conceptNew() !== self.conceptOld() &&
                !!self.conceptNew() &&
                !!self.conceptOld();
            return ready;
        });

        this.clearResults = ko.computed(() => {
            // if any of these values change then clear the preview results
            self.showPreview(false);
            self.tilesToRemove.removeAll();
            self.currentPageIndex(0);
            // we don't actually care about the results of the following
            let clearResults = '';
            [
                self.selectedGraph(),
                self.selectedNode(),
                self.conceptOldLang(),
                self.conceptNewLang(),
                self.conceptOld(),
                self.conceptNew()
            ].forEach(function(item){
                clearResults += item?.toString();
            });
            return clearResults;
        });

        this.allowEditOperation = ko.computed(() => {
            return self.ready() && self.numberOfTiles() > 0 && self.showPreview();
        });

        this.inTileList = (tileToFind) => {
            const tile = self.tilesToRemove().find((tileid) => {
                return tileid === tileToFind.tileid;
            });
            return !!tile;
        };

        //delete Row in table
        this.addToList = function(tileid) {
            const list = new Set([...self.tilesToRemove(), tileid]);
            self.tilesToRemove(list);
        };

        //call python code to display the change
        this.getPreviewData = function() {
            self.showPreview(true);
            self.submit('preview').then(data => {
                self.numberOfResources(data.result.number_of_resources);
                self.numberOfTiles(data.result.number_of_tiles);
                self.previewLimit(data.result.preview_limit);
                self.paginatedRows(data.result.values);
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

        this.selectedNode.subscribe((node) => {
            self.conceptNew(undefined);
            self.conceptOld(undefined);
            self.rdmCollectionLanguages.removeAll();
            
            if(!!node){
                self.rdmCollection = node.rdmCollection;
    
                self.submit('get_collection_languages').then(data => {
                    self.rdmCollectionLanguages(data.result);
                    if(data.result.length > 0) {
                        window.setTimeout(() =>{
                            self.conceptOldLang(data.result[0].id);
                            self.conceptNewLang(data.result[0].id);
                        }, 500);
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
            }
        });

        //select nodes and take the specific value
        this.selectedGraph.subscribe((graphid) => {
            self.dropdownnodes.removeAll();
            self.conceptNew(undefined);
            self.conceptOld(undefined);
            self.selectedNode(undefined);
            self.submit('get_graphs_node').then(data => {
                const nodes = data.result.map(node => (
                    {   node: node.nodeid,
                        label: `${JSON.parse(node.card_name)[arches.activeLanguage]} - ${JSON.parse(node.widget_label)[arches.activeLanguage]}`,
                        rdmCollection: JSON.parse(node.config).rdmCollection
                    }));
                self.dropdownnodes(nodes);
                
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
            self.dropdowngraph.removeAll();
            self.dropdownnodes.removeAll();
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
            if (!self.allowEditOperation()) {
                return;
            }
            self.showPreview(false);
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
            self.addAllFormData();
            self.formData.append('action', action);
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
