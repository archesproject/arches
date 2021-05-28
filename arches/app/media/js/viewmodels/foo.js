define([
    'knockout', 
    'knockout-mapping',
    'underscore', 
    'views/base-manager', 
    'moment', 
    'report-templates',
    'models/report',
    'bindings/let', 
    'views/components/simple-switch',
], function(ko, koMapping, _, BaseManagerView, moment, reportLookup, ReportModel) {
    var FooViewModel = BaseManagerView.extend({
        initialize: function(params) {
            _.extend(this, params.viewModel);
            
            var self = this;

    
            console.log('foo vm', self, params, reportLookup)
    
        }
    });
    
    
    return FooViewModel;
});
