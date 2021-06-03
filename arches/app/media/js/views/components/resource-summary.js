define([
    'knockout',
    'jquery',
    'underscore',
    'models/graph',
    'arches',
    'report-templates',
    'models/report',
    'card-components',
], function(ko, $, _, GraphModel, arches, reportLookup, ReportModel, cardComponents) {
    var viewModel = function(){
        this.loading = ko.observable(true);
        console.log(this)
    };
    ko.components.register('resource-summary', {
        viewModel: viewModel,
        template: { 
            require: 'text!templates/views/components/resource-summary.htm' 
        }
    });
});
