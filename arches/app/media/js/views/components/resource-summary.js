define([
    'knockout',
    'jquery',
    'underscore',
    'models/graph',
    'arches',
    'report-templates',
    'models/report',
    'card-components',
], function(ko, $, _, GraphModel, arches, reportLookup, ReportModel, cardComponents) {
    if (!("graphCache" in arches)) {
        arches.graphCache = {};
    }
    var outerVM = ko.observable();
    var viewModel = function(params){
        var self = this;
        var CardViewModel = require('viewmodels/card');
        this.loading = ko.observable(false);
        this.reportLookup = reportLookup;
        this.graphId = params.graphId || ko.observable();
        this.dataSource = params.source || ko.observable();
        this.resourceId = params.resourceId;
        this.resourceId.subscribe(function(resId) {
            this.setupReport(resId, this.graphId(), this.dataSource());
        }, this);
        var processReportData = function(data, graph) {
            data.cards = _.filter(graph.cards, function(card) {
                var nodegroup = _.find(graph.graph.nodegroups, function(group) {
                    return group.nodegroupid === card.nodegroup_id;
                });
                return !nodegroup || !nodegroup.parentnodegroup_id;
            }).map(function(card) {
                return new CardViewModel({
                    card: card,
                    graphModel: graph.graphModel,
                    resourceId: data.resourceid,
                    displayname: data.displayname,
                    cards: graph.cards,
                    tiles: data.tiles,
                    cardwidgets: graph.cardwidgets
                });
            });

            data.templates = self.reportLookup;
            data.cardComponents = cardComponents;
            self.report = new ReportModel(_.extend(data, {
                graphModel: graph.graphModel,
                graph: graph.graph,
                datatypes: graph.datatypes
            }));
            self.loading(false);
        };
        this.setupReport = function(resId, graphId, source) {
            var qs = '?json=True';
            var graph = !!graphId ? arches.graphCache[graphId] : null;
            self.loading(true);
            if (graph) processReportData(
                {
                    "tiles": source.tiles,
                    "related_resources": [],
                    "displayname": source.displayname,
                    "resourceid": source.resourceinstanceid
                },
                graph
            );
            else {
                $.getJSON(arches.urls.resource_report + resId + qs, function(data) {
                    var graphModel = new GraphModel({
                        data: data.graph,
                        datatypes: data.datatypes
                    });

                    graph = {
                        graphModel: graphModel,
                        cards: data.cards,
                        graph: data.graph,
                        datatypes: data.datatypes,
                        cardwidgets: data.cardwidgets
                    };
                    arches.graphCache[graphId] = graph;
                    processReportData(data, graph);
                });
            }
        };

        if(this.resourceId !== null){
            this.setupReport(this.resourceId(), this.graphId(), this.dataSource());
        }

        outerVM(this);
    };

    ko.components.register('resource-summary', {
        viewModel: viewModel,
        template: { 
            require: 'text!templates/views/components/resource-summary.htm' 
        }
    });

    // if you subscribe to outerVM then you can list to when it gets initialized during the ko.component initialization
    // then you should be able to access the instantiated viewModel
    return outerVM;
});
