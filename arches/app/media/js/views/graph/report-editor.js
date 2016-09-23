require([
    'knockout',
    'views/graph/graph-page-view',
    'views/graph/report-editor/report-editor-tree',
    'views/graph/report-editor/report-editor-form',
    'views/graph/report-editor/report-editor-preview',
    'report-editor-data',
    'arches'
], function(ko, PageView, ReportEditorTree, ReportEditorForm, ReportEditorPreview, data, arches) {
    var viewModel = {
        selectedReportId: ko.observable(null),
        reports: ko.observableArray(data.reports)
    };

    viewModel.openReport = function (reportId) {
        pageView.viewModel.navigate(arches.urls.report_editor + reportId);
    };

    viewModel.selectedReportId.subscribe(function(reportId) {
        if (reportId) {
            viewModel.openReport(reportId);
        }
    });

    viewModel.reportOptions = ko.computed(function () {
        var options = [{
            name: null,
            reportid: null,
            disabled: true
        }]
        return options.concat(viewModel.reports());
    });

    viewModel.reportEditorTree = new ReportEditorTree();
    viewModel.reportEditorForm = new ReportEditorForm();
    viewModel.reportEditorPreview = new ReportEditorPreview();

    var pageView = new PageView({
        viewModel: viewModel
    });
});
