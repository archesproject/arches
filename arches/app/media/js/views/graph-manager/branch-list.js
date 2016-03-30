define([
    'views/list',
    'views/graph-manager/graph-base',
    'knockout'
], function(ListView, GraphBase, ko) {
    var BranchList = ListView.extend({
        initialize: function(options) {
            ListView.prototype.initialize.apply(this, arguments);

            // this.branchInfoPanel = new BranchInfoView({
            //     el: $('#branch-panel')
            // });

            this.items = options.branches;
            this.showingForm = ko.observable(false);
            this.selectedItem = ko.observable(null);
        },

        selectItem: function(item, evt){
            if(item.selected()){
                this.showingForm(false);
                this.selectedItem(null);
            }else{
                this.selectedItem(item);
                this.showingForm(true);
                item.graph.nodes.forEach(function (node) {
                    node.editing = ko.observable(false);
                    node.name = ko.observable(node.name);
                });
                this.graph = new GraphBase({
                    el: $('#branch-preview'),
                    nodes: ko.observableArray(item.graph.nodes),
                    edges: ko.observableArray(item.graph.edges)
                });
            }
            ListView.prototype.selectItem.apply(this, arguments);
        },

        closeForm: function(){
            this.showingForm(false);
        }

    });
    return BranchList;
});
