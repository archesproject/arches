define([
    'knockout',
    'viewmodels/tabbed-report',
    'templates/views/report-templates/tabbed.htm'
], function(ko, TabbedReportViewModel, tabbedReportTemplate) {
    return ko.components.register('tabbed-report', {
        viewModel: TabbedReportViewModel,
        template: tabbedReportTemplate,
    });
});
