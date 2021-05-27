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
    return ko.components.register('report', {
        viewModel: ResourceReportView = BaseManagerView.extend({
            initialize: function(options){
                console.log("YEAH")
            }
        }),
        template: { require: 'text!templates/views/resource/report.htm' }
    });
    return new ResourceReportView();
});
