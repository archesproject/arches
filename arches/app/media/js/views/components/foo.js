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
        this.summary = Boolean(params.summary);

        this.template = ko.observable();
        this.report = ko.observable();

        console.log('in foo component')

        this.initialize = function() {
            if (ko.unwrap(self.resourceid)) {
                var url = arches.urls.api_resource_report(self.resourceid);

                self.fetchResourceData(url).then(function(responseJson) {
                    var template = responseJson.template;
                    self.template(template);
                    
                    if (template.preload_resource_data) {
                        self.preloadResourceData(responseJson)
                    }
                    else {
                        self.report(responseJson.resource_instance);
                    }
        
                    self.loading(false);
                });

            }
            else {
                self.loading(false);
            }
        };

        this.fetchResourceData = function(url) {
            return window.fetch(url).then(function(response){
                if (response.ok) {
                    return response.json();
                }
                else {
                    throw new Error(arches.translations.reNetworkReponseError);
                }
            });
        };
        
        this.preloadResourceData = function(responseJson) {
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

            responseJson.tiles = JSON.parse(responseJson.tiles);

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
                    tiles: responseJson.tiles,
                    cardwidgets: graph.cardwidgets
                });
            });

            var report = new ReportModel(_.extend(responseJson, {
                resourceid: self.resourceid,
                graphModel: graph.graphModel,
                graph: graph.graph,
                datatypes: graph.datatypes
            }));

            report['hideEmptyNodes'] = responseJson.hide_empty_nodes;

            self.report(report);
        };

        this.initialize();
    };
    ko.components.register('foo', {
        viewModel: Foo,
        template: { require: 'text!templates/views/components/foo.htm' }
    });
    return Foo;
});
