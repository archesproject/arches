require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'models/report',
    'models/graph',
    'resource-report-data',
    'report-templates',
    'bindings/chosen',
    'card-components'
], function($, _, ko, arches, BaseManagerView, ReportModel, GraphModel, data, reportLookup) {
    var ResourceReportView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            var report = null;

            var graphModel = new GraphModel({
                data: data.graph,
                datatypes: data.datatypes,
                ontology_namespaces: data.ontology_namespaces
            });

            if (data.report) {
                report =  new ReportModel(_.extend({graphModel: graphModel}, data));
            }

            this.viewModel.reportLookup = reportLookup;
            this.viewModel.report = report;
            this.viewModel.graph = data.graph;
            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new ResourceReportView();
});
