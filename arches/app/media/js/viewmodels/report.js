define(['knockout', 'knockout-mapping', 'underscore', 'moment', 'bindings/let'], function(ko, koMapping, _, moment) {
    var ReportViewModel = function(params) {
        var self = this;
        this.report = params.report || null;
        this.reportDate = moment().format('MMMM D, YYYY');
        this.configForm = params.configForm || false;
        this.configType = params.configType || 'header';
        this.editorContext = params.editorContext || false;

        this.configState = params.report.configState || ko.observable({});
        this.configJSON = params.report.configJSON || ko.observable({});
        this.configObservables = params.configObservables || {};
        this.configKeys = params.configKeys || [];
        // if (typeof this.config !== 'function') {
        //     this.config = ko.observable(this.config);
        // }

        this.hasProvisionalData = ko.pureComputed(function() {
            return _.some(self.tiles(), function(tile){
                return _.keys(ko.unwrap(tile.provisionaledits)).length > 0;
            });
        });

        var subscribeConfigObservable = function(obs, key) {
            self[key] = obs[key];
            if (obs[key]) {
                obs[key].subscribe(function(val) {
                    self.configJSON(koMapping.toJS(self.configState));
                });
            }

            // self.config.subscribe(function(val) {
            //     console.log('do you even work bro?')
            //     if (val[key] !== obs[key]()) {
            //         obs[key](val[key]);
            //     }
            // });

            // if (Array.isArray(obs[key]())) {
            //     obs[key]().forEach(function(item){
            //         for (var property in ko.unwrap(item)) {
            //             if (item.hasOwnProperty(property)) {
            //                 subscribeConfigObservable(item, property);
            //             }
            //         }
            //     });
            // } else {
            //     for (var property in ko.unwrap(obs[key])) {
            //         if (obs[key]().hasOwnProperty(property)) {
            //             subscribeConfigObservable(obs, property);
            //         }
            //     }
            // }
        };
        // _.each(this.configObservables, subscribeConfigObservable);
        // this.mappedConfigs = koMapping.fromJS(this.report.get('config'));

        _.each(this.configKeys, function(key) {
            console.log('mapping configs')
            subscribeConfigObservable(self.configState, key);
        });

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
