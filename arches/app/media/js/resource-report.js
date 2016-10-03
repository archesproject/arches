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

            var setupTiles = function(card) {
                card.tiles = _.filter(data.tiles, function(tile) {
                    tile.nodegroup_id === card.nodegroup_id;
                });
                card.cards.forEach(setupTiles);
            };
            data.cards.forEach(setupTiles);

            this.viewModel.reportLookup = reportLookup;
            this.viewModel.report = new ReportModel(data);
            BaseManagerView.prototype.initialize.call(this, options)
        }
    });
    return new ResourceReportView();
});
