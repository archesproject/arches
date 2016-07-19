define([
    'views/list',
    'views/graph/graph-manager/graph-base',
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
            var self = this;
            ListView.prototype.initialize.apply(this, arguments);

            this.loading = options.loading || ko.observable(false);
            this.failed = options.failed || ko.observable(false);
            this.disableAppendButton = options.disableAppendButton || ko.observable(false);
            this.graphModel = options.graphModel;
            this.selectedNode = this.graphModel.get('selectedNode');
            options.branches.forEach(function (branch) {
                branch.selected = ko.observable(false);
                branch.filtered = ko.observable(false);
                branch.graphModel = new GraphModel({
                    data: branch
                })
                this.items.push(branch);
            }, this);
            this.selectedBranch = ko.observable(null);
            this.viewMetadata = ko.observable(false);

            var valueListener = ko.computed(function() {
                var node = self.selectedNode;
                if(!!node()){
                    var oc = node().ontologyclass();
                    var datatype = node().datatype();
                    var collector = node().isCollector();
                    return oc + datatype + collector;
                }
                return false;
            });

            var updateList = function(){
                if(this.selectedNode()){
                    _.each(this.items(), function(branch){
                        branch.filtered(true);
                        if(this.graphModel.canAppend(branch.graphModel)){
                            branch.filtered(false);
                        }
                    }, this);
                }
            }
            valueListener.subscribe(updateList, this);
            updateList.call(this);
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
                this.failed(false);
                this.graphModel.appendBranch(this.selectedNode().nodeid, null, item.graphModel, function(response, status){
                    this.loading(false);
                    _.delay(_.bind(function(){
                        this.failed(status !== 'success');
                        if(!(this.failed())){
                            this.closeForm();
                        }
                    }, this), 300, true);
                }, this)
            }
        },

        /**
        * Closes the form and deselects the currently selected branch
        * @memberof BranchList.prototype
        */
        closeForm: function(){
            this.clearSelection();
            this.selectedBranch(null);
            this.viewMetadata(false);

            this.trigger('close');
        },


    });
    return BranchList;
});
