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
    'bindings/chosen'
], function($, _, ko, arches, BaseManagerView, ReportModel, GraphModel, data, reportLookup) {
    var ResourceReportView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            var report = null;
            var setupTiles = function(card) {
                card.tiles = _.filter(data.tiles, function(tile) {
                    return tile.nodegroup_id === card.nodegroup_id;
                });
                card.tiles.forEach(function(t1) {
                    t1.tiles = _.filter(data.tiles, function(t2) {
                        return t1.tileid === t2.parenttile_id;
                    });
                });
                card.cards.forEach(setupTiles);
            };

            var graphModel = new GraphModel({
                data: data.graph,
                datatypes: data.datatypes,
                ontology_namespaces: data.ontology_namespaces
            });

            if (data.report) {
                data.cards.forEach(setupTiles);
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
