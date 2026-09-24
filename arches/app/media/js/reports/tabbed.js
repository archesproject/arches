import ko from 'knockout';
import TabbedReportViewModel from 'viewmodels/tabbed-report';
import tabbedReportTemplate from 'templates/views/report-templates/tabbed.htm';
import 'bindings/sortable';

export default ko.components.register('tabbed-report', {
    viewModel: TabbedReportViewModel,
    template: tabbedReportTemplate,
});
