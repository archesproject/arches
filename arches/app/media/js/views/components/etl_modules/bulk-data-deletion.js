define([
    'knockout',
    'knockout-mapping',
    'jquery',
    'uuid',
    'arches',
    'viewmodels/alert',
    'viewmodels/alert-json',
    'templates/views/components/etl_modules/bulk-data-deletion.htm',
    'views/components/simple-switch',
    'bindings/datatable',
    'bindings/dropzone',
    'bindings/resizable-sidepanel',
], function(ko, koMapping, $, uuid, arches, AlertViewModel, JsonErrorAlertViewModel, bulkDataDeletionTemplate) {
    const viewModel = function(params) {
        const self = this;

        this.loadDetails = params.load_details;
        this.editHistoryUrl = `${arches.urls.edit_history}?transactionid=${ko.unwrap(params.selectedLoadEvent)?.loadid}`;
        this.state = params.state;
        this.loading = params.loading || ko.observable();
        this.alert = params.alert;
        this.moduleId = params.etlmoduleid;
        this.selectedLoadEvent = params.selectedLoadEvent || ko.observable();
        this.formatTime = params.formatTime;
        this.timeDifference = params.timeDifference;
        this.loading(true);
        this.graphs = ko.observable();
        this.selectedGraph = ko.observable();
        this.nodegroups = ko.observable();
        this.selectedNodegroup = ko.observable();
        this.formData = new window.FormData();
        this.loadId = params.loadId || uuid.generate();
        this.resourceids = ko.observable();
        this.searchUrl = ko.observable();
        this.previewing = ko.observable(false);
        this.numberOfResources = ko.observable();
        this.numberOfTiles = ko.observable();
        this.showPreview = ko.observable(false);
        this.previewValue = ko.observable();

        this.activeTab = ko.observable("TileDeletion");
        this.activeTab.subscribe(() => {
            self.selectedGraph(null);
            self.selectedNodegroup(null);
            self.searchUrl(null);
        });

        this.ready = ko.computed(() => {
            self.showPreview(false);
            self.numberOfResources(null);
            self.numberOfTiles(null);
            return (self.searchUrl() && self.activeTab() === "DeletionBySearchUrl")
                || (self.selectedGraph() && self.activeTab() === "DeletionByGraph")
                || (self.selectedNodegroup() && self.activeTab() === "TileDeletion");
        });

        this.getGraphs = function() {
            self.loading(true);
            self.submit('get_graphs').then(function(response) {
                self.graphs(response.result);
                self.loading(false);
            });
        };

        this.preview = function() {
            self.previewing(true);
            self.showPreview(false);
            this.addAllFormData();
            self.submit('preview').then(function(response) {
                self.numberOfResources(response.result.resource);
                self.numberOfTiles(response.result.tile);
                self.previewValue(response.result.preview?.map((value) => JSON.stringify(value)));
                self.showPreview(true);
            }).fail(function(err) {
                self.alert(
                    new JsonErrorAlertViewModel(
                        'ep-alert-red',
                        err.responseJSON["data"],
                        null,
                        function () {}
                    )
                );
            }).always(function() {
                self.deleteAllFormData();
                self.previewing(false);
            });
        };

        this.getGraphName = function(graphId) {
            let graph;
            if (self.graphs()) {
                graph = self.graphs().find(function(graph) {
                    return graph.graphid == graphId;
                });
            }
            return graph?.name;
        };

        this.getNodegroupName = function(nodegroupId) {
            let nodegroup;
            if (self.nodegroups()) {
                nodegroup = self.nodegroups().find(function(nodegroup) {
                    return nodegroup.nodegroupid == nodegroupId;
                });
            }
            return nodegroup?.name;
        };

        this.addAllFormData = () => {
            if (self.searchUrl()) { self.formData.append('search_url', self.searchUrl()); }
            if (self.selectedNodegroup()) {
                self.formData.append('nodegroup_id', self.selectedNodegroup());
                self.formData.append('nodegroup_name', self.getNodegroupName(self.selectedNodegroup()));
            }
            if (self.selectedGraph()) {
                self.formData.append('graph_id', self.selectedGraph());
                self.formData.append('graph_name', self.getGraphName(self.selectedGraph()));
            }
            if (self.resourceids()) { self.formData.append('resourceids', JSON.stringify(self.resourceids())); }
        };

        this.deleteAllFormData = () => {
            self.formData.delete('search_url');
            self.formData.delete('nodegroup_id');
            self.formData.delete('nodegroup_name');
            self.formData.delete('graph_id');
            self.formData.delete('graph_name');
            self.formData.delete('resourceids');
        };

        this.selectedGraph.subscribe(function(graph) {
            if (graph) {
                self.loading(true);
                self.formData.append('graphid', graph);
                self.submit('get_nodegroups').then(function(response) {
                    const nodegroups = response.result;
                    self.selectedNodegroup(null);
                    self.nodegroups(nodegroups);
                    self.loading(false);
                });
            } else {
                self.nodegroups(null);
            }
        });

        this.deleteAlert = function() {
            self.alert(
                new AlertViewModel(
                    "ep-alert-blue",
                    arches.translations.confirmBulkDelete.title,
                    arches.translations.confirmBulkDelete.text,
                    function() {},
                    function() {
                        self.addAllFormData();
                        params.activeTab("import");

                        // perform the delete action if the user confirms
                        self.submit('delete');
                    })
            );
        };

        this.bulkDelete = function() {
            self.deleteAlert();
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
            })
                .fail(function(err) {
                    // show an error alert if the delete action fails
                    self.alert(
                        new JsonErrorAlertViewModel(
                            'ep-alert-red',
                            err.responseJSON["data"],
                            null,
                            function () {}
                        )
                    );
                });
        };

        this.init = function() {
            this.getGraphs();
        };

        this.init();
    };
    ko.components.register('bulk-data-deletion', {
        viewModel: viewModel,
        template: bulkDataDeletionTemplate,
    });
    return viewModel;
});
