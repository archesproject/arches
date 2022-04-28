define([
    'knockout',
    'viewmodels/function',
    'models/graph',
    'views/graph/graph-designer/graph-tree',
],
function(ko, FunctionViewModel, GraphModel, GraphTree) {
    return ko.components.register('views/components/functions/resource-edits', {
        viewModel: function(params) {
            var self = this;
            FunctionViewModel.apply(this, arguments);
            this.selectedNodes = ko.observableArray();
            this.graphModel = new GraphModel({'data':this.graph});
            this.graphTree = new GraphTree({
                graphModel: this.graphModel
            });
            this.graphTree.selectItem = function(selectedNode){
                if(self.nodeCollectsData(selectedNode)){
                    selectedNode.selected(!selectedNode.selected());
                }
            };
            
            this.items = this.graphTree.items;
            this.items().forEach(function(node) {
                var selected = this.config.selected_nodes().find(function(selectedNodeid){
                    return node.id === selectedNodeid;
                });
                node.selected(!!selected);
            }, this);

            this.nodeCollectsData = function(node) {
                return self.graphModel.get('widgets').find(function(widget){
                    return node.id === widget.node_id;
                });
            };

            this.selectedNodes = ko.computed(function(){
                return this.items().filter(function(node){
                    return node.selected();
                });
            }, this);

            this.selectedNodeNames = ko.computed(function() {
                var nodenames = [];
                this.items().reduce(function(previousnode, currentnode){
                    if(currentnode.selected()) {
                        nodenames.push(currentnode.name());
                    }
                }, nodenames);
                return nodenames;
            }, this);

            this.selectedNodes.subscribe(function(nodes){
                var nodeids = [];
                var nodegroups = [];
                nodes.forEach(function(node) {
                    nodeids.push(node.id);
                    nodegroups.push(node.nodeGroupId());
                });
                this.config.selected_nodes(nodeids);
                this.config.triggering_nodegroups(nodegroups);
            }, this);

        },
        template: {
            require: 'text!templates/views/components/functions/resource-edits.htm'
        }
    });
});
