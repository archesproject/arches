define([
    'views/list',
    'views/graph-manager/graph-base',
    'models/graph',
    'knockout'
], function(ListView, GraphBase, GraphModel , ko) {
    var BranchList = ListView.extend({
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);

            this.graphModel = options.graphModel;
            this.editNode = this.graphModel.get('editNode');
            this.items = options.branches;
            this.items().forEach(function (branch) {
                branch.ontology_property = ko.observable('');
                branch.graphModel = new GraphModel({
                    data: branch.graph
                })
            });
            this.selectedItem = ko.observable(null);
        },

        selectItem: function(item, evt){
            if(item.selected()){
                this.selectedItem(null)
            }else{
                this.selectedItem(item);
                this.graph = new GraphBase({
                    el: $('#branch-preview'),
                    graphModel: item.graphModel
                });

            }
            ListView.prototype.selectItem.apply(this, arguments);
        },

        appendBranch: function(){
            if(this.editNode()){
                this.graphModel.appendBranch(this.editNode().nodeid, this.selectedItem().ontology_property(), this.selectedItem().graphmetadataid, function(response){
                }, this)

            }
        },

        closeForm: function(){
            this.clearSelection();
            this.selectedItem(null);
        }

    });
    return BranchList;
});
