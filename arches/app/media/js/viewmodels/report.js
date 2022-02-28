define(['knockout', 'knockout-mapping', 'underscore', 'moment', 'bindings/let', 'views/components/simple-switch'], function(ko, koMapping, _, moment) {
    var ReportViewModel = function(params) {
        var self = this;

        this.report = params.report || null;
        this.summary = params.summary || false;
        this.reportDate = moment().format('MMMM D, YYYY');
        this.configForm = params.configForm || false;
        this.configType = params.configType || 'header';
        this.editorContext = params.editorContext || false;

        this.configState = params.report.configState || ko.observable({});
        this.configJSON = params.report.configJSON || ko.observable({});
        this.configObservables = params.configObservables || {};
        this.configKeys = params.configKeys || [];

        this.hasProvisionalData = ko.pureComputed(function() {
            return _.some(self.tiles(), function(tile){
                return _.keys(ko.unwrap(tile.provisionaledits)).length > 0;
            });
        });
        
        this.hideEmptyNodes = ko.observable(params.report.hideEmptyNodes);

        this.configJSON = ko.computed(function(){
            self.configKeys.forEach(function(config) {
                self[config] = self.configState[config];
            });
            self.report.configJSON(koMapping.toJS(self.report.configState));
            return self.report.configJSON;
        }).extend({deferred: true});

        var getCardTiles = function(card, tiles) {
            var cardTiles = ko.unwrap(card.tiles);
            cardTiles.forEach(function(tile) {
                tiles.push(tile);
                tile.cards.forEach(function(card) {
                    getCardTiles(card, tiles);
                });
            });
        };

        this.tiles = ko.computed(function() {
            var tiles = [];
            if (self.report) {
                ko.unwrap(self.report.cards).forEach(function(card) {
                    getCardTiles(card, tiles);
                });
            }
            return tiles;
        });
    };
    return ReportViewModel;
});
