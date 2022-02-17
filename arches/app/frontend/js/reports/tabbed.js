define([
    'knockout',
    'viewmodels/tabbed-report'
], function(ko, TabbedReportViewModel) {
    return ko.components.register('tabbed-report', {
        viewModel: TabbedReportViewModel,
        template: { require: 'text!report-templates/tabbed' }
    });
});
