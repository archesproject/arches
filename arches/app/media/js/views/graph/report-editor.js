require([
    'knockout',
    'views/graph/graph-page-view',
    'views/graph/report-editor/report-editor-tree',
    'views/graph/report-editor/report-editor-form',
    'views/graph/report-editor/report-editor-preview',
    'models/report',
    'models/card',
    'report-editor-data',
    'arches',
    'bindings/sortable'
], function(ko, PageView, ReportEditorTree, ReportEditorForm, ReportEditorPreview, ReportModel, CardModel, data, arches) {
    var viewModel = {
        selectedReportId: ko.observable(data.report.reportid),
        reports: ko.observableArray(data.reports)
    };

    viewModel.report = new ReportModel(data);

    viewModel.reset = function () {
        viewModel.report.reset();
        viewModel.selection('header');
    };

    viewModel.dirty = viewModel.report.dirty;

    viewModel.selection = ko.observable('header');

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

    var subViewModel = {
        report: viewModel.report,
        selection: viewModel.selection
    }
    viewModel.reportEditorTree = new ReportEditorTree(subViewModel);
    viewModel.reportEditorForm = new ReportEditorForm(subViewModel);
    viewModel.reportEditorPreview = new ReportEditorPreview(subViewModel);

    var pageView = new PageView({
        viewModel: viewModel
    });
});
