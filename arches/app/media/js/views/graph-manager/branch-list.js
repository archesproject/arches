define([
    'views/list',
    'views/graph-manager/graph-base',
    'models/graph',
    'knockout'
], function(ListView, GraphBase, GraphModel , ko) {
    var BranchList = ListView.extend({
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);

            this.loading = options.loading || ko.observable(false);
            this.graphModel = options.graphModel;
            this.selectedNode = this.graphModel.get('selectedNode');
            this.items = options.branches;
            this.items().forEach(function (branch) {
                branch.ontology_property = ko.observable('');
                branch.graphModel = new GraphModel({
                    data: branch.graph
                })
            });
            this.selectedBranch = ko.observable(null);
            this.viewMetadata = ko.observable(false);
        },

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

        appendBranch: function(item, evt){
            var self = this;
            if(this.selectedNode()){
                this.loading(true);
                this.graphModel.appendBranch(this.selectedNode().nodeid, item.ontology_property(), item.graphid, function(response){
                    self.loading(false);
                }, this)
            }
            this.closeForm();
        },

        closeForm: function(){
            this.clearSelection();
            this.selectedBranch(null);
            this.viewMetadata(false);
        },



    });
    return BranchList;
});
