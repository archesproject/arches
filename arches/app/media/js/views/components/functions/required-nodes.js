define(['knockout',
        'knockout-mapping',
        'viewmodels/function',
        'bindings/chosen'],
function (ko, koMapping, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/required-nodes', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var nodegroups = {};
            this.nodegroup_id = params.config.nodegroup_id;
            this.required_nodes = params.config.required_nodes;
            this.cards = ko.observableArray();
            this.nodeOptions = ko.observableArray();

            this.updateNodeOptions = function(nodegroup_id){
                  var nodes = _.filter(this.graph.nodes, function(node){
                      return node.nodegroup_id === nodegroup_id;
                  }, this);
                  this.nodeOptions(nodes);
              }

            if (this.nodegroup_id()) {
              this.updateNodeOptions(this.nodegroup_id())
            }

            this.graph.cards.forEach(function(card){
                var found = !!_.find(this.graph.nodegroups, function(nodegroup){
                    return nodegroup.parentnodegroup_id === card.nodegroup_id
                }, this);
                if(!found && !(card.nodegroup_id in nodegroups)){
                    this.cards.push(card);
                    nodegroups[card.nodegroup_id] = true;
                }
            }, this);

            this.updateNodeValues = function(){
              return function(){
                $("select[data-bind^=chosen]").trigger("chosen:updated")
              }
            }

            this.nodegroup_id = params.config.nodegroup_id;
            this.nodegroup_id.subscribe(function(nodegroup_id){
                var nodes = _.filter(this.graph.nodes, function(node){
                    return node.nodegroup_id === nodegroup_id;
                }, this);
                this.nodeOptions(nodes);
                window.setTimeout(this.updateNodeValues(), 100);
            }, this);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated")}, 300);
        },
        template: {
            require: 'text!templates/views/components/functions/required-nodes.htm'
        }
    });
})
