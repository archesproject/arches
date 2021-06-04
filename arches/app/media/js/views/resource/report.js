require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'moment',
    'views/base-manager',
    'models/graph',
    'viewmodels/card',
    'models/report',
    'report-templates',
], function($, _, ko, koMapping, arches, moment, BaseManagerView, GraphModel, CardViewModel, ReportModel, reportLookup) {
    var ddd = BaseManagerView.extend({
        initialize: function(options){
            var self = this;

            this.reportDate = moment().format('MMMM D, YYYY');
            this.foo = ko.observable();
            this.report = ko.observable();
            
            this.initialize = function() {
                var resourceId = $('#resourceId').data('value');
                var url = arches.urls.api_resource_report(resourceId);
                self.fetchResourceData(url);
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
                    var template = responseJson.template;

                    if (template.preload_resource_data) {
                        self.preloadResourceData(responseJson);
                    }
                    // else {
                    //     self.report(responseJson.resource_instance);
                    // }

                    self.foo(responseJson.template.componentname)

                    BaseManagerView.prototype.initialize.call(self, options);
                });
            };

            this.preloadResourceData = function(responseJson) {
                console.log("DI", responseJson)
                // self.tiles = ko.computed(function() {
                //     var tiles = [];
                //     if (ko.unwrap(self.report)) {
                //         ko.unwrap(self.report().cards).forEach(function(card) {
                //             getCardTiles(card, tiles);
                //         });
                //     }
                //     return tiles;
                // });
        
                // self.hasProvisionalData = ko.pureComputed(function() {
                //     return _.some(self.tiles(), function(tile){
                //         return _.keys(ko.unwrap(tile.provisionaledits)).length > 0;
                //     });
                // });
        
                // var getCardTiles = function(card, tiles) {
                //     var cardTiles = ko.unwrap(card.tiles);
                //     cardTiles.forEach(function(tile) {
                //         tiles.push(tile);
                //         tile.cards.forEach(function(card) {
                //             getCardTiles(card, tiles);
                //         });
                //     });
                // };
        
                // self.hideEmptyNodes = ko.observable();
    
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
                // responseJson.cardComponents = cardComponents;
    
                self.report(new ReportModel(_.extend(responseJson, {
                    graphModel: graph.graphModel,
                    graph: graph.graph,
                    datatypes: graph.datatypes
                })));

                console.log("SSSSS", self)
    
                // self.hideEmptyNodes(responseJson.hide_empty_nodes); 
            };


            _.defaults(self.viewModel, {
                // configKeys: self.configKeys,
                // configJSON: self.configJSON,
                report: self.report,
                templateComponentName: self.foo,
                reportDate: self.reportDate,
            });

            console.log('report vew', self, options)
            this.initialize();
        }
    });

    // var foo = ko.components.register('report', {
    //     viewModel: fooVM,
    //     template: { require: 'text!templates/views/resource/report.htm' }
    // });

    return new ddd()
});
