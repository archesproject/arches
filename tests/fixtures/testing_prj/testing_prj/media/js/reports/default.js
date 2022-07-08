define([
    'knockout', 
    'arches',
    'viewmodels/report', 
    'templates/views/report-templates/default.htm'
], function(ko, arches, ReportViewModel, defaultReportTemplate) {
    return ko.components.register('default-report', {
        viewModel: function(params) {
            params.configKeys = [];
            this.translations = arches.translations;
            
            ReportViewModel.apply(this, [params]);
        },
        template: defaultReportTemplate,
    });
});
