require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'models/report',
    'models/graph',
    'models/card',
    'viewmodels/card',
    'report-templates',
    'bindings/chosen',
    'card-components'
], function($, _, ko, arches, BaseManagerView, ReportModel, GraphModel, CardModel, CardViewModel, reportLookup) {
    console.log("YEAH")
    var foo = ko.components.register('report', {
        viewModel: BaseManagerView.extend({
            initialize: function(options){

                this.loading = ko.observable(false)
            }
        }),
        template: { require: 'text!templates/views/resource/report.htm' }
    });

    return foo
});
