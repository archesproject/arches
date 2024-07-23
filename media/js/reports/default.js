define([
    'knockout', 
    'viewmodels/report', 
    'templates/views/report-templates/default.htm'
], function(ko, ReportViewModel, defaultReportTemplate) {
    return ko.components.register('default-report', {
        viewModel: function(params) {
            params.configKeys = [];

            ReportViewModel.apply(this, [params]);
        },
        template: defaultReportTemplate
    });
});
