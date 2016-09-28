require([
    'knockout',
    'views/graph/graph-page-view',
    'report-editor-data',
    'arches'
], function(ko, PageView, data, arches) {
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

    var pageView = new PageView({
        viewModel: viewModel
    });
});
