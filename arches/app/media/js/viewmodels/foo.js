define([
    'knockout', 
    'knockout-mapping', 
    'underscore', 
    'moment', 
    'report-templates',
    'models/report',
    'bindings/let', 
    'views/components/simple-switch',
    'views/components/foo'
], function(ko, koMapping, _, moment, reportLookup, ReportModel) {
    var FooViewModel = function(params) {
        var self = this;
        this.reportMetadata = ko.observable(reportLookup[params.report_template_id])

        this.loading = ko.observable(true)
        this.loading = ko.observable(false)

        console.log(self.reportMetadata())
    };
    return FooViewModel;
});
