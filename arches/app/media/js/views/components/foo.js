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

        this.loading = ko.observable(false);

        console.log("foo", params)

        this.version = arches.version;
        this.resourceid = params.resourceid;

        this.template = ko.observable();
        this.report = ko.observable();

        this.reportDate = moment().format('MMMM D, YYYY');

        this.initialize = function() {
            if (ko.unwrap(self.resourceid)) {
                var url = arches.urls.api_resource_report(self.resourceid);
                self.fetchResourceData(url);
            }
            else {
                self.loading(false);
            }
        };

        this.fetchResourceData = function(url) {
            window.fetch(url).then(function(response){
                if (response.ok) {
                    return response.json();
                }
                else {
                    throw new Error(arches.translations.reNetworkReponseError);
                }
            }).then(function(responseJson) {
                var template = responseJson.template
                self.template(template);
    
                if (template.preload_resource_data) {
                    self.preloadResourceData(responseJson)
                }
                else {
                    self.report(responseJson.resource_instance);
                }
    
                self.loading(false);
            });
        };
        
        this.preloadResourceData = function(responseJson) {
            self.tiles = ko.computed(function() {
                var tiles = [];
                if (ko.unwrap(self.report)) {
                    ko.unwrap(self.report().cards).forEach(function(card) {
                        getCardTiles(card, tiles);
                    });
                }
                return tiles;
            });
    
            self.hasProvisionalData = ko.pureComputed(function() {
                return _.some(self.tiles(), function(tile){
                    return _.keys(ko.unwrap(tile.provisionaledits)).length > 0;
                });
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
    
            self.hideEmptyNodes = ko.observable();

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

            self.hideEmptyNodes(responseJson.hide_empty_nodes); 
        };

        this.initialize();
    };
    ko.components.register('foo', {
        viewModel: Foo,
        template: { require: 'text!templates/views/components/foo.htm' }
    });
    return Foo;
});
