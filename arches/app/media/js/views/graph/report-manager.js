require([
    'underscore',
    'knockout',
    'views/graph/graph-page-view',
    'views/list',
    'viewmodels/alert',
    'models/report',
    'models/graph',
    'report-manager-data',
    'arches',
    'bindings/dragDrop'
], function(_, ko, PageView, ListView, AlertViewModel, ReportModel, GraphModel, data, arches) {
    var showTemplateLibrary = ko.observable(false);

    var reportModels = [];
    var graphModel = new GraphModel({
        data: data.graph,
        datatypes: data.datatypes,
        ontology_namespaces: data.ontology_namespaces
    });
    data.reports.forEach(function(report) {
        var reportModel = new ReportModel(_.extend({report: report, graphModel: graphModel, cardComponents: []}, data));
        reportModel.template = _.find(data.templates, function(template) {
            return report.template_id === template.templateid;
        });
        reportModels.push(reportModel);
    });
    var viewModel = {
        showTemplateLibrary: showTemplateLibrary,
        toggleTemplateLibrary: function(){
            showTemplateLibrary(!showTemplateLibrary());
        },
        selectedReportId: ko.observable(null),
        templates: ko.observableArray(data.templates),
        reports: ko.observableArray(reportModels)
    };

    viewModel.templateLibraryStatus = ko.pureComputed(function() {
        return showTemplateLibrary() ? 'show-card-library' : 'hide-card-library';
    }, viewModel);

    viewModel.templateList = new ListView({
        items: viewModel.templates
    });

    var alertFailure = function() {
        pageView.viewModel.alert(new AlertViewModel('ep-alert-red', arches.requestFailed.title, arches.requestFailed.text));
    };

    viewModel.addReport = function(newReportData){
        this.loading(true);
        $.ajax({
            type: "POST",
            url: 'add_report',
            data: JSON.stringify({
                template_id: newReportData.templateid
            }),
            success: function(response) {
                var reportModel = new ReportModel(_.extend({report: response, graphModel: graphModel}, data));
                reportModel.template = _.find(data.templates, function(template) {
                    return response.template_id === template.templateid;
                });
                viewModel.reports.push(reportModel);
                pageView.viewModel.loading(false);
            },
            error: function(response) {
                pageView.viewModel.loading(false);
                alertFailure();
            }
        });
    };

    viewModel.deleteReport = function(report) {
        this.loading(true);
        $.ajax({
            type: "DELETE",
            url: arches.urls.report_editor + report.get('reportid')(),
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

    viewModel.openReport = function(reportId) {
        pageView.viewModel.navigate(arches.urls.report_editor + reportId);
    };

    viewModel.selectedReportId.subscribe(function(reportId) {
        if (reportId) {
            viewModel.openReport(reportId);
        }
    });

    viewModel.reportOptions = ko.computed(function() {
        var options = [{
            name: null,
            reportid: null,
            disabled: true
        }];
        var reports = _.map(viewModel.reports(), function(reportModel) {
            return {
                name: reportModel.get('name'),
                reportid: reportModel.get('reportid')
            };
        });
        return options.concat(options.concat(reports));
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
