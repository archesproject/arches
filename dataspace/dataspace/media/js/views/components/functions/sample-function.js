define(['jquery',
    'knockout',
    'viewmodels/function',
    'bindings/chosen'],
function($, ko, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/sample-function', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var nodegroups = {};
            this.triggering_nodegroups = params.config.triggering_nodegroups;
            this.cards = ko.observableArray();
            this.graph.cards.forEach(function(card){
                this.cards.push(card);
                nodegroups[card.nodegroup_id] = true;
            }, this);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated");}, 300);
        },
        template: {
            require: 'text!templates/views/components/functions/sample-function.htm'
        }
    });
});
