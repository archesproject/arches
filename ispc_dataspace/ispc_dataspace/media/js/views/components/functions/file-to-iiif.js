define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/list',
    'viewmodels/function',
    'bindings/chosen'],
function($, _, ko, koMapping, ListView, FunctionViewModel, chosen) {
    return ko.components.register('views/components/functions/file-to-iiif', {
        viewModel: function(params) {
            FunctionViewModel.apply(this, arguments);
            var nodegroups = {};
            this.triggering_nodegroups = params.config.triggering_nodegroups;
            this.cards = ko.observableArray();
            this.graph.cards. forEach(function(card){
                this.cards.push(card);
                nodegroups[card.nodegroup_id] = true;
            }, this);

            window.setTimeout(function(){$("select[data-bind^=chosen]").trigger("chosen:updated");}, 300);
        },
        template: {
            require: 'text!templates/views/components/functions/file-to-iiif.htm'
        }
    });
});
