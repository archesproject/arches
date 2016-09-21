require([
    'knockout',
    'views/graph/graph-page-view',
    'views/list',
    'report-manager-data',
    'arches',
    'bindings/dragDrop'
], function(ko, PageView, ListView, data, arches) {
    var showTemplateLibrary = ko.observable(false);

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
        // TODO add report....
    };

    viewModel.deleteReport = function (report) {
        this.loading(true);
        // TODO delete report....
    };

    viewModel.openReport = function (reportId) {
        pageView.viewModel.navigate(arches.urls.report + reportId);
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
