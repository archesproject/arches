import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import arches from 'arches';
import graphManagerData from 'views/graph-manager-data';
import BaseManager from 'views/base-manager';
import AlertViewModel from 'viewmodels/alert';
import JsonErrorAlertViewModel from 'viewmodels/alert-json';
import 'bootstrap';
import 'bindings/hover';
import 'bindings/chosen';
import 'utils/set-csrf-token';


var GraphView = BaseManager.extend({
    /**
    * Initializes an instance of BaseManager, optionally using a passed in view
    * model
    *
    * @memberof BaseManager.prototype
    * @param {object} options - additional options to pass to the view
    * @return {object} an instance of GraphView
    */
    initialize: function(options) {
        var self = this;
        /**
        * creates a request to add a new graph; redirects to the graph settings
        * page for the new graph on success
        *
        * @param  {string} url - the url to be used in the request
        * @param  {object} data (optional) - data to be included in request
        */
        var newGraph = function(url, data) {
            data = data || {};
            self.viewModel.loading(true);
            $.ajax({
                type: "POST",
                url: url,
                data: JSON.stringify(data),
                success: function(response) {
                    window.location = arches.urls.graph_designer(response.graphid);
                },
                error: function() {
                    self.viewModel.loading(false);
                }
            });
        };

        this.viewModel.leaveDropdown = function(){
            $('.dropdown').dropdown('toggle');
        };

        this.viewModel.allGraphs().forEach(function(graph) {
            graph.root = null;
            graph.isCard = false;
            if (graphManagerData && typeof graphManagerData.root_nodes === 'object') {
                graph.root = _.find(graphManagerData.root_nodes, function(node) {
                    return node.graph_id === graph.graphid;
                });
                if (graph.root) {
                    graph.isCard = (graph.root.nodegroup_id === graph.root.nodeid);
                }
            }

            graph.hover = ko.observable(false);
            graph.clone = function() {
                newGraph(arches.urls.clone_graph(graph.graphid));
            };
            graph.exportGraph = function(model) {
                window.open(arches.urls.export_graph(graph.graphid), '_blank');
            };
            graph.exportMappingFile = function(model) {
                window.open(arches.urls.export_mapping_file(graph.graphid), '_blank');
            };
            graph.deleteGraph = function() {
                self.viewModel.alert(new AlertViewModel(
                    'ep-alert-red',
                    arches.translations.confirmGraphDelete.title,
                    arches.translations.confirmGraphDelete.text,
                    function() {
                        return;
                    }, function(){
                        self.viewModel.loading(true);
                        $.ajax({
                            type: "DELETE",
                            url: arches.urls.delete_graph(graph.graphid),
                            complete: function(response, status) {
                                self.viewModel.loading(false);
                                if (status === 'success') {
                                    self.viewModel.allGraphs.remove(graph);
                                } else {
                                    self.viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                                }
                            }
                        });
                    }
                ));
            };
            graph.deleteInstances = function() {
                self.viewModel.alert(new AlertViewModel(
                    'ep-alert-red',
                    arches.translations.confirmAllResourceDelete.title,
                    arches.translations.confirmAllResourceDelete.text,
                    function() {
                        return;
                    }, function(){
                        self.viewModel.loading(true);
                        $.ajax({
                            type: "DELETE",
                            url: arches.urls.delete_instances(graph.graphid),
                            complete: function(response, status) {
                                self.viewModel.loading(false);
                                if (status === 'success') {
                                    self.viewModel.alert(new AlertViewModel('ep-alert-blue', response.responseJSON.title, response.responseJSON.message));
                                } else {
                                    self.viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                                }
                            }
                        });
                    }
                ));
            };
        });

        this.viewModel.showResources = ko.observable(window.location.hash!=='#branches');

        _.defaults(this.viewModel, {
            arches: arches,
            groupedGraphs: ko.observable({
                groups: [
                    { name: 'Resource Models', items: self.viewModel.resources() },
                    { name: 'Branches', items: self.viewModel.graphs() }
                ]
            }),
            graphId: ko.observable(null),
            showFind: ko.observable(false),
            currentList: ko.computed(function() {
                let resources;

                if (self.viewModel.showResources()) {
                    resources = self.viewModel.resources();
                } else {
                    resources = self.viewModel.graphs();
                }

                return resources.reduce((acc, resource) => {
                    if (!resource.source_identifier_id) {
                        const draftGraph = resources.find(graph => graph.source_identifier_id === resource.graphid);

                        if (draftGraph) {
                            resource['has_unpublished_changes'] = draftGraph['has_unpublished_changes'];
                        }

                        acc.push(resource);
                    }
                    return acc;
                }, []);
            }),
            newResource: function() {
                newGraph('new', {isresource: true});
            },
            newGraph: function() {
                newGraph('new', {isresource: false});
            },
            importGraph: function(data, e) {
                var formData = new FormData();
                formData.append("importedGraph", e.target.files[0]);

                self.viewModel.loading(true);
                $.ajax({
                    type: "POST",
                    url: 'import/',
                    processData: false,
                    data: formData,
                    cache: false,
                    contentType: false,
                    success: function(response) {
                        if (response[0].length != 0) {
                            // eslint-disable-next-line no-constant-condition
                            if (typeof(response[0])) {
                                response = response[0].join('<br />');
                            }
                            self.viewModel.alert(new AlertViewModel('ep-alert-red', arches.translations.graphImportFailed.title, response));
                        }
                        else {
                            window.location.reload(true);
                        }
                    },
                    error: function(response) {
                        self.viewModel.alert(
                            new AlertViewModel('ep-alert-red', arches.translations.graphImportFailed.title, arches.translations.pleaseContactSystemAdministrator)
                        );
                        self.viewModel.loading(false);
                    },
                });
            },
            importButtonClick: function() {
                $("#fileupload").trigger('click');
            }
        });


        this.viewModel.graphId.subscribe(function(graphid) {
            if(graphid && graphid !== ""){
                self.viewModel.navigate(arches.urls.graph_designer(graphid));
            }
        });

        BaseManager.prototype.initialize.call(this, options);
    }

});
export default new GraphView();
