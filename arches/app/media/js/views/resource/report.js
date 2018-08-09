require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
    'models/report',
    'models/graph',
    'models/card',
    'viewmodels/card',
    'resource-report-data',
    'report-templates',
    'bindings/chosen',
    'card-components'
], function($, _, ko, arches, BaseManagerView, ReportModel, GraphModel, CardModel, CardViewModel, data, reportLookup) {
    var ResourceReportView = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            var report = null;

            var graphModel = new GraphModel({
                data: data.graph,
                datatypes: data.datatypes,
                ontology_namespaces: data.ontology_namespaces
            });

            var cards = _.filter(data.cards, function(card) {
                var nodegroup = _.find(data.graph.nodegroups, function(group) {
                    return group.nodegroupid === card.nodegroup_id;
                });
                return !nodegroup || !nodegroup.parentnodegroup_id;
            }).map(function(card) {
                return new CardViewModel({
                    card: card,
                    graphModel: graphModel,
                    resourceId: data.resourceId,
                    displayname: data.displayname,
                    cards: data.cards,
                    tiles: data.tiles,
                    cardwidgets: data.cardwidgets
                });
            });

            if (data.report) {
                report =  new ReportModel(_.extend(data, {graphModel: graphModel, cards: cards}));
            }

            this.viewModel.reportLookup = reportLookup;
            this.viewModel.report = report;
            this.viewModel.graph = data.graph;

            var createLookup = function(list, idKey) {
                return _.reduce(list, function(lookup, item) {
                    lookup[item[idKey]] = item;
                    return lookup;
                }, {});
            };
            this.viewModel.widgetLookup = createLookup(data.widgets, 'widgetid');
            this.viewModel.cardComponentLookup = createLookup(data.cardComponents, 'componentid');
            this.viewModel.nodeLookup = createLookup(graphModel.get('nodes')(), 'nodeid');
            BaseManagerView.prototype.initialize.call(this, options);
        }
    });
    return new ResourceReportView();
});
