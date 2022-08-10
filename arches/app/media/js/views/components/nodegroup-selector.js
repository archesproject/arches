define([
    'jquery',
    'underscore',
    'knockout', 
    'knockout-mapping',
    'viewmodels/function', 
    'models/graph',
    'bindings/chosen',
    'templates/views/components/nodegroup-selector.htm'
], function($, _, ko, koMapping, FunctionViewModel, GraphModel, chosen, nodegroupSelectorTemplate) {
    return ko.components.register('views/components/nodegroup-selector', {
        viewModel: function(params) {
             
            FunctionViewModel.apply(this, arguments);
            var nodegroups = {};
            this.cards = ko.observableArray();

            this.graph.cards.forEach(function(card){
                var found = !!_.find(this.graph.nodegroups, function(nodegroup){
                    return nodegroup.parentnodegroup_id === card.nodegroup_id;
                }, this);
                if(!found && !(card.nodegroup_id in nodegroups)){
                    this.cards.push(card);
                    nodegroups[card.nodegroup_id] = true;
                }
            }, this);

            this.triggering_nodegroups = params.triggering_nodegroups;

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated");}, 300);
        },
        template: nodegroupSelectorTemplate,
    });
});