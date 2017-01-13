require([
    'jquery',
    'underscore',
    'knockout',
    'views/base-manager',
    'viewmodels/alert',
    'arches',
    'view-data',
    'graph-manager-data',
    'bootstrap',
    'bindings/hover',
    'bindings/chosen'
], function($, _, ko, BaseManager, AlertViewModel, arches, data, graphManagerData) {

    var GraphView = BaseManager.extend({
        /**
        * Initializes an instance of BaseManager, optionally using a passed in view
        * model
        *
        * @memberof BaseManager.prototype
        * @param {object} options - additional options to pass to the view
        * @return {object} an instance of GraphView
        */
        initialize: function (options) {
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
                        window.location = response.graphid + '/settings';
                    },
                    error: function(response) {
                        self.viewModel.loading(false);
                    }
                });
            };

            this.viewModel.leaveDropdown = function(e){
              $('.dropdown').dropdown('toggle')
            };

            this.viewModel.allGraphs().forEach(function(graph) {
                graph.root = null;
                graph.isCard = false;
                if (graphManagerData && typeof graphManagerData.root_nodes === 'object') {
                    graph.root = _.find(graphManagerData.root_nodes, function(node) {
                        return node.graph_id === graph.graphid
                    });
                    if (graph.root) {
                        graph.isCard = (graph.root.nodegroup_id === graph.root.nodeid);
                    }
                }

                graph.hover = ko.observable(false);
                graph.clone = function() {
                    newGraph(graph.graphid + '/clone');
                };
                graph.exportGraph = function(model) {
                    window.open(graph.graphid + '/export', '_blank');
                };
                graph.exportMappingFile = function(model) {
                    window.open(graph.graphid + '/export_mapping_file', '_blank');
                };
                graph.deleteGraph = function () {
                    self.viewModel.alert(new AlertViewModel('ep-alert-red', arches.confirmGraphDelete.title, arches.confirmGraphDelete.text, function() {
                        return;
                    }, function(){
                        self.viewModel.loading(true);
                        $.ajax({
                            complete: function (request, status) {
                                self.viewModel.loading(false);
                                if (status === 'success') {
                                    self.viewModel.allGraphs.remove(graph);
                                }
                            },
                            type: "DELETE",
                            url: graph.graphid
                        });
                    }));
                };
            });

            this.viewModel.showResources = ko.observable(window.location.hash!=='#branches');

            _.defaults(this.viewModel, {
                groupedGraphs: ko.observable({
                    groups: [
                        { name: 'Resource Models', items: self.viewModel.resources() },
                        { name: 'Branches', items: self.viewModel.graphs() }
                    ]
                }),
                graphId: ko.observable(null),
                showFind: ko.observable(false),
                currentList: ko.computed(function() {
                    if (self.viewModel.showResources()) {
                        return self.viewModel.resources();
                    } else {
                        return self.viewModel.graphs() ;
                    }
                }),
                newResource: function () {
                    newGraph('new', {isresource: true});
                },
                newGraph: function () {
                    newGraph('new', {isresource: false});
                },
                importGraph: function (data, e) {
                    var formData = new FormData();
                    formData.append("importedGraph", e.target.files[0]);

                    $.ajax({
                        type: "POST",
                        url: 'import/',
                        processData: false,
                        data: formData,
                        cache: false,
                        contentType: false,
                        success: function(response) {
                          if (response[0].length != 0) {
                            if (typeof(response[0])) {
                              response = response[0].join('<br />')
                            }
                              self.viewModel.alert(new AlertViewModel('ep-alert-red', arches.graphImportFailed.title, response[0]));
                            }
                            else {
                              window.location.reload(true);
                            }
                        },
                        error: function(response) {
                            self.viewModel.alert(new AlertViewModel('ep-alert-red', arches.graphImportFailed.title, 'Please contact your system administrator for more details.'));
                            self.viewModel.loading(false);
                        },
                    });
                },
                importButtonClick: function () {
                    $("#fileupload").trigger('click');
                }
            });


            this.viewModel.graphId.subscribe(function (graphid) {
                if(graphid && graphid !== ""){
                    self.viewModel.navigate(arches.urls.graph + graphid + '/settings');
                }
            });

            BaseManager.prototype.initialize.call(this, options);
        }

    });
    return new GraphView();

    $('.dropdown').dropdown();
});
