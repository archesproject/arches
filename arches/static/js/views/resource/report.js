require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'models/report',
    'resource-report-data',
    'report-templates',
    'bindings/chosen'
], function($, _, ko, arches, BaseManagerView, ReportModel, data, reportLookup) {
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

            if (data.report) {
                data.cards.forEach(setupTiles);
                report =  new ReportModel(data);
            }

            this.viewModel.reportLookup = reportLookup;
            this.viewModel.report = report;
            this.viewModel.graph = data.graph;
            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new ResourceReportView();
});
