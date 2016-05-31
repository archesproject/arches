define([
    'views/list',
    'views/graph-manager/graph-base',
    'models/graph',
    'knockout'
], function(ListView, GraphBase, GraphModel , ko) {
    var BranchList = ListView.extend({
        /**
        * A backbone view to manage a list of branch graphs
        * @augments ListView
        * @constructor
        * @name BranchList
        */

        /**
        * initializes the view with optional parameters
        * @memberof BranchList.prototype
        * @param {object} options
        * @param {boolean} options.graphModel - a reference to the selected {@link GraphModel}
        * @param {boolean} options.branches - an observableArray of branches
        */
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);

            this.loading = options.loading || ko.observable(false);
            this.failed = options.failed || ko.observable(false);
            this.graphModel = options.graphModel;
            this.selectedNode = this.graphModel.get('selectedNode');
            this.items = options.branches;
            this.items().forEach(function (branch) {
                branch.graphModel = new GraphModel({
                    data: branch.graph
                })
            });
            this.selectedBranch = ko.observable(null);
            this.viewMetadata = ko.observable(false);

            this.selectedNode.subscribe(function(node){
                if(node){
                    _.each(this.items(), function(branch){
                        branch.filtered(true);
                        var found = _.find(branch.graph.domain_connections, function(domain_connection){
                            return _.find(domain_connection.ontology_classes, function(ontology_class){
                                return ontology_class === node.ontologyclass();
                            }, this)
                        }, this);
                        if(found){
                            branch.filtered(false);
                        }
                    }, this);
                }
            }, this);
        },

        /**
        * Sets the selected branch from the users selection
        * @memberof BranchList.prototype
        * @param {object} item - the branch object the user selected
        * @param {object} evt - click event object
        */
        selectItem: function(item, evt){
            ListView.prototype.selectItem.apply(this, arguments);

            if(item.selected()){
                this.selectedBranch(item);
                this.graph = new GraphBase({
                    el: $('#branch-preview'),
                    graphModel: item.graphModel
                });
                this.viewMetadata(true);
            }else{
                this.selectedBranch(null);
                this.viewMetadata(false);
            }
        },

        /**
        * Appends the currently selected branch onto the currently selected node in the graph
        * @memberof BranchList.prototype
        * @param {object} item - the branch object the user selected
        * @param {object} evt - click event object
        */
        appendBranch: function(item, evt){
            var self = this;
            if(this.selectedNode()){
                this.loading(true);
                var ontology_connection = _.find(item.graph.domain_connections, function(domain_connection){
                    return _.find(domain_connection.ontology_classes, function(ontology_class){
                        return ontology_class === this.selectedNode().ontologyclass();
                    }, this)
                }, this);
                if(ontology_connection){
                    this.graphModel.appendBranch(this.selectedNode().nodeid, ontology_connection.ontology_property, item.graphid, function(response, status){
                        self.failed(status !== 'success');
                        self.loading(false);
                    }, this)
                }else{
                    this.loading(false);
                    this.failed(true);
                }
            }
            this.closeForm();
        },

        /**
        * Closes the form and deselects the currently selected branch
        * @memberof BranchList.prototype
        */
        closeForm: function(){
            this.clearSelection();
            this.selectedBranch(null);
            this.viewMetadata(false);
        },


    });
    return BranchList;
});
