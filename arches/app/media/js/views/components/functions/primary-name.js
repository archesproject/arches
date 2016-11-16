define(['knockout', 
        'knockout-mapping',
        'viewmodels/function', 
        'bindings/chosen'], 
function (ko, koMapping, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/primary-name', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var nodegroups = {};
            this.cards = ko.observableArray();
            
            this.graph.cards.forEach(function(card){
                var found = !!_.find(this.graph.nodegroups, function(nodegroup){
                    return nodegroup.parentnodegroup_id === card.nodegroup_id
                }, this);
                if(!found && !(card.nodegroup_id in nodegroups)){
                    this.cards.push(card);
                    nodegroups[card.nodegroup_id] = true;
                }
            }, this);

            this.string_template = params.config.string_template;
            this.nodegroup_id = params.config.nodegroup_id;
            this.nodegroup_id.subscribe(function(nodegroup_id){
                this.string_template(nodegroup_id);
                var nodes = _.filter(this.graph.nodes, function(node){
                    return node.nodegroup_id === nodegroup_id;
                }, this);
                var templateFragments = [];
                _.each(nodes, function(node){
                    templateFragments.push('<' + node.name + '>');
                }, this);

                var template = templateFragments.join(', ');
                this.string_template(template);

            }, this);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated")}, 300);
        },
        template: {
            require: 'text!templates/views/components/functions/primary-name.htm'
        }
    });
})