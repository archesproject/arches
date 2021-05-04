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
            var nodegroups = {};
            FunctionViewModel.apply(this, arguments);
            this.selectedNodes = ko.observableArray();
            this.graphModel = new GraphModel({'data':this.graph});
            this.graphTree = new GraphTree({
                graphModel: this.graphModel
            });

            this.items = this.graphTree.items;

            this.graphTree.selectItem = function(selectedNode){
                if (self.nodeIsChecked(selectedNode)){
                    var newSelectedNodes = [];
                    self.selectedNodes().forEach(function(node){
                        if (node !== selectedNode) {
                            newSelectedNodes.push(node);
                        }
                    });
                    self.selectedNodes(newSelectedNodes);
                } else {
                    self.selectedNodes.push(selectedNode);
                }
            };

            this.nodeIsChecked = function(node){
                return self.selectedNodes().find(function(selectedNode){
                    return node === selectedNode;
                });
            };

            this.nodeCollectsData = function(node) {
                return self.graphModel.get('widgets').find(function(widget){
                    return node.id === widget.node_id;
                });
            };

            this.selectedNodes.subscribe(function(nodes){
                console.log(nodes);
                var nodeids = [];
                var nodegroups = [];
                nodes.forEach(function(node) {
                    nodeids.push(node.id);
                    nodegroups.push(node.nodeGroupId());
                });
                this.config.selected_nodes(nodeids);
                this.config.triggering_nodegroups(nodegroups);
            }, this);
            
            this.graphModel.on('select-node', function(node) {
                this.graphTree.expandParentNode(node);
            }, this);

        },
        template: {
            require: 'text!templates/views/components/functions/resource-edits.htm'
        }
    });
});
