define([
    'arches',
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'moment',
    'report-templates',
    'card-components',
    'models/report',
    'viewmodels/card',
    'models/graph'
], function(arches, $, _, ko, koMapping, moment, reportLookup, cardComponents, ReportModel, CardViewModel, GraphModel) {
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

        this.hasProvisionalData = ko.pureComputed(function() {
            return _.some(self.tiles(), function(tile){
                return _.keys(ko.unwrap(tile.provisionaledits)).length > 0;
            });
        });

        console.log("AAAAA", self, params)
        // this.configJSON = ko.computed(function(){
        //     self.configKeys.forEach(function(config) {
        //         self[config] = self.configState[config];
        //     });

        //     var report = self.report();

        //     report.configJSON(koMapping.toJS(report.configState));

        //     self.report(report);

        //     return report.configJSON;

        // }).extend({deferred: true});

        var getCardTiles = function(card, tiles) {
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

                console.log("AAAAAA", responseJson)
                var graphModel = new GraphModel({
                    data: JSON.parse(responseJson.graph_json),
                    datatypes: JSON.parse(responseJson.datatypes_json),
                });

                graph = {
                    graphModel: graphModel,
                    cards: JSON.parse(responseJson.cards),
                    graph: JSON.parse(responseJson.graph_json),
                    datatypes: JSON.parse(responseJson.datatypes_json),
                    cardwidgets: JSON.parse(responseJson.cardwidgets)
                };
                

                responseJson.cards = _.filter(graph.cards, function(card) {
                    var nodegroup = _.find(graph.graph.nodegroups, function(group) {
                        return group.nodegroupid === card.nodegroup_id;
                    });
                    return !nodegroup || !nodegroup.parentnodegroup_id;
                }).map(function(card) {
                    return new CardViewModel({
                        card: card,
                        graphModel: graph.graphModel,
                        resourceId: self.resourceid,
                        displayname: responseJson.displayname,
                        cards: graph.cards,
                        tiles: JSON.parse(responseJson.tiles),
                        cardwidgets: graph.cardwidgets
                    });
                });
    
                responseJson.templates = reportLookup;
                responseJson.cardComponents = cardComponents;

                self.report(new ReportModel(_.extend(responseJson, {
                    graphModel: graph.graphModel,
                    graph: graph.graph,
                    datatypes: graph.datatypes
                })));






                // var cards = JSON.parse(responseJson.cards).reduce(function(acc, card) {
                //     acc.push(new CardViewModel(card));
                //     return acc;
                // }, []);

                console.log("foo", self, self.tiles(), self.hasProvisionalData())
                var template = responseJson.template
                self.template(template);





                if (template.preload_resource_data) {





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
