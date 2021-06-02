define([
    'arches',
    'jquery',
    'knockout',
    'knockout-mapping',
    'moment',
    'models/report',
    'models/card',
    'models/graph'
], function(arches, $, ko, koMapping, moment, ReportModel, CardModel, GraphModel) {
    var Foo = function(params) {
        var self = this;

        this.loading = ko.observable(true);

        this.version = arches.version;
        this.resourceid = params.resourceid;

        this.template = ko.observable();

        /* maybe refactor to one report structure */ 
        this.report = ko.observable();
        this.reportData = ko.observable();
        this.reportData.subscribe(function(reportData) {
            console.log(reportData)
        });

        this.reportDate = moment().format('MMMM D, YYYY');

        /* BEGIN legacy */
        this.hideEmptyNodes = ko.observable();  /* not working */

        this.tiles = ko.computed(function() {
            var tiles = [];
            if (ko.unwrap(self.report)) {
                console.log(self.report())
                ko.unwrap(self.report().cards).forEach(function(card) {
                    getCardTiles(card, tiles);
                });
            }
            return tiles;
        });

        var getCardTiles = function(card, tiles) {
            console.log('getCardTiles', card, tiles)
            var cardTiles = ko.unwrap(card.tiles);
            cardTiles.forEach(function(tile) {
                tiles.push(tile);
                tile.cards.forEach(function(card) {
                    getCardTiles(card, tiles);
                });
            });
        };

        /* END legacy */ 

        var url = arches.urls.api_resource_report(this.resourceid);

        window.fetch(url)
            .then(function(response){
                if (response.ok) {
                    return response.json();
                }
                else {
                    throw new Error(arches.translations.reNetworkReponseError);
                }
            })
            .then(function(responseJson) {

                var ggg = new GraphModel({
                    data: JSON.parse(responseJson.graph_json),
                    datatypes: JSON.parse(responseJson.datatypes_json),
                });

                
                var cards = JSON.parse(responseJson.cards).reduce(function(acc, card) {
                    acc.push(new CardModel(card));
                    return acc;
                }, []);

                console.log("JSON REPONSE", responseJson, JSON.parse(responseJson.graph_json), ggg, cards)
                var template = responseJson.template
                self.template(template);

                if (template.preload_resource_data) {






                    self.report(new ReportModel({
                        templateId: template.templateid,
                        cards: JSON.parse(responseJson.cards),
                    }));
                }
                else {
                    self.reportData(responseJson.resource_instance);
                }

                self.loading(false);
            });

        console.log('foo component', this, params, arches)
    };
    ko.components.register('foo', {
        viewModel: Foo,
        template: { require: 'text!templates/views/components/foo.htm' }
    });
    return Foo;
});
