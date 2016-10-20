require([
    'underscore',
    'knockout',
    'views/graph/graph-page-view',
    'views/list',
    'viewmodels/alert',
    'report-manager-data',
    'arches',
    'bindings/dragDrop'
], function(_, ko, PageView, ListView, AlertViewModel, data, arches) {
    var showTemplateLibrary = ko.observable(false);

    data.reports.forEach(function(report) {
        report.template = _.find(data.templates, function(template) {
            return report.template_id === template.templateid;
        });
    });
    var viewModel = {
        showTemplateLibrary: showTemplateLibrary,
        toggleTemplateLibrary: function(){
            showTemplateLibrary(!showTemplateLibrary());
        },
        selectedReportId: ko.observable(null),
        templates: ko.observableArray(data.templates),
        reports: ko.observableArray(data.reports)
    };

    viewModel.templateLibraryStatus = ko.pureComputed(function() {
        return showTemplateLibrary() ? 'show-card-library' : 'hide-card-library';
    }, viewModel);

    viewModel.templateList = new ListView({
        items: viewModel.templates
    });

    var alertFailure = function () {
        pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
    };

    viewModel.addReport = function(data){
        this.loading(true);
        $.ajax({
            type: "POST",
            url: 'add_report',
            data: JSON.stringify({
                template_id: data.templateid
            }),
            success: function(response) {
                viewModel.reports.push(response);
                pageView.viewModel.loading(false);
            },
            error: function(response) {
                pageView.viewModel.loading(false);
                alertFailure();
            }
        });
    };

    viewModel.deleteReport = function (report) {
        this.loading(true);
        $.ajax({
            type: "DELETE",
            url: arches.urls.report_editor + report.reportid + '/delete',
            success: function(response) {
                pageView.viewModel.loading(false);
                viewModel.reports.remove(report);
            },
            error: function(response) {
                pageView.viewModel.loading(false);
                alertFailure();
            }
        });
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

    viewModel.newReport = ko.computed({
        read: function() {
            return viewModel.reports().length ? viewModel.reports()[0] : null;
        },
        write: function(value) {
            viewModel.addReport(value);
        }
    });

    var pageView = new PageView({
        viewModel: viewModel
    });
});
