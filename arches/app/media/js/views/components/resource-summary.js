define([
    'knockout',
    'jquery',
    'underscore',
    'models/graph',
    'arches',
    'report-templates',
    'models/report',
    'viewmodels/card'
], function(ko, $, _, GraphModel, arches, reportLookup, ReportModel, CardViewModel) {
    if (!("graphCache" in arches)) {
        arches.graphCache = {};
    }
    return ko.components.register('resource-summary', {
        viewModel: function(params) {
            var self = this;
            this.resourceId = params.resourceId;
            this.graphId = params.graphId;
            this.loading = ko.observable(false);
            this.reportLookup = reportLookup;
            this.resourceId.subscribe(function(resId) {
                setupReport(resId, this.graphId());
            }, this);
            var setupReport = function(resId, graphId) {
                var qs = '?json=True';
                var graph = !!graphId ? arches.graphCache[graphId] : null;
                if (graph) qs += '&exclude_graph=True';
                self.loading(true);
                $.getJSON(arches.urls.resource_report + resId + qs, function(data) {
                    if (!graph) {
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
                        arches.graphCache[data.graph.graphid] = graph;
                    }

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

                    self.report = new ReportModel(_.extend(data, {
                        graphModel: graph.graphModel,
                        graph: graph.graph,
                        datatypes: graph.datatypes
                    }));
                    self.loading(false);
                });
            };

            if(this.resourceId !== null){
                setupReport(this.resourceId(), this.graphId());
            }
        },
        template: { require: 'text!templates/views/components/resource-summary.htm' }
    });

});
