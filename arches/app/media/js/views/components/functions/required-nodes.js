define(['knockout',
        'knockout-mapping',
        'views/list',
        'viewmodels/function',
        'bindings/chosen'],
function (ko, koMapping, ListView, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/required-nodes', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var nodegroups = {};
            this.nodegroup_id = params.config.nodegroup_id;
            this.required_nodes = params.config.required_nodes;
            this.triggering_nodegroups = params.config.triggering_nodegroups;
            this.cards = ko.observableArray();
            this.nodes = ko.observableArray();
            this.required = JSON.parse(this.required_nodes());
            var self = this;

            this.required_nodes.subscribe(function(a){
              res = [];
              _.each(self.required, function(val, key){
                if (val().length > 0) {
                  res.push(key);
                }
              })
              self.triggering_nodegroups(res)
            })

            this.compareRequiredNodes = function(thing){
              var self = this;
              return function(thing) {
                self.required_nodes(JSON.stringify(koMapping.toJS(self.required)))
              }
            }

            _.each(this.graph.nodes, function(node){
              if (_.has(self.required, node.nodegroup_id)) {
                if (!ko.isObservable(self.required[node.nodegroup_id])) {
                  self.required[node.nodegroup_id] = ko.observableArray(self.required[node.nodegroup_id])
                  self.required[node.nodegroup_id].subscribe(self.compareRequiredNodes(node))
                }
                if (_.contains(self.required[node.nodegroup_id](), node.nodeid)) {
                  node.selected = ko.observable(true);
                }
              }
              self.nodes.push(node);
            })

            this.toggleRequired = function(e){
              e.selected(!e.selected())
              if (!_.has(self.required, e.nodegroup_id)) {
                self.required[e.nodegroup_id] = ko.observableArray()
                self.required[e.nodegroup_id].subscribe(self.compareRequiredNodes(e))
                self.required[e.nodegroup_id].push(e.nodeid)
              } else {
                if (_.contains(self.required[e.nodegroup_id](), e.nodeid)) {
                  self.required[e.nodegroup_id].remove(e.nodeid)
                } else {
                  self.required[e.nodegroup_id].push(e.nodeid)
                }
              }
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

            this.cardList = new ListView({
                items: this.nodes,
                groups: this.cards
            });

        },
        template: {
            require: 'text!templates/views/components/functions/required-nodes.htm'
        }
    });
})
