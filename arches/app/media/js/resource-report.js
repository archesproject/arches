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
                card.cards.forEach(setupTiles);
            };

            if (data.report) {
                data.cards.forEach(setupTiles);
                report =  new ReportModel(data);
            }

            this.viewModel.reportLookup = reportLookup;
            this.viewModel.report = report;
            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new ResourceReportView();
});
