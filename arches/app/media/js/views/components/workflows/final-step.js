define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'models/graph',
    'models/report',
    'viewmodels/card'
], function(_, $, arches, ko, GraphModel, ReportModel, CardViewModel) {
    function viewModel(params) {
        var self = this;
        this.urls = arches.urls;
        if (!params.resourceid() && params.requirements){
            params.resourceid(params.requirements.resourceid);
        }
        this.workflowid = params.workflow.state.workflowid;
        this.resourceid = params.resourceid();
        var url = arches.urls.api_card + (ko.unwrap(this.resourceid));
        this.report = ko.observable();
        this.loading = ko.observable(true);
        this.nodegroupids = params.workflow.steps
            .filter(function(step){return ko.unwrap(step.nodegroupid);})
            .map(function(x){return ko.unwrap(x.nodegroupid);});

        $.getJSON(url, function(data) {
            var displayname = ko.observable(data.displayname);
            var graphModel = new GraphModel({
                data: {
                    nodes: data.nodes,
                    nodegroups: data.nodegroups,
                    edges: []
                },
                datatypes: data.datatypes
            });

            var topCards = _.filter(data.cards, function(card) {
                var nodegroup = _.find(data.nodegroups, function(group) {
                    return (group.nodegroupid === card.nodegroup_id);
                });
                return (!nodegroup || !nodegroup.parentnodegroup_id) && _.contains(self.nodegroupids, card.nodegroup_id);
            }).map(function(card) {
                params.nodegroupid = params.nodegroupid || card.nodegroup_id;
                return new CardViewModel({
                    card: card,
                    graphModel: graphModel,
                    tile: null,
                    resourceId: self.resourceId,
                    displayname: displayname,
                    cards: data.cards,
                    tiles: data.tiles,
                    cardwidgets: data.cardwidgets,
                    userisreviewer: data.userisreviewer,
                    loading: self.loading
                });
            });

            topCards.forEach(function(topCard) {
                topCard.topCards = topCards;
            }, this);

            self.report(new ReportModel(_.extend(data, {graphModel: graphModel, cards: topCards})));
            self.loading(false);
        });

        params.stateProperties = function(){
            return {};
        };
    }
    return ko.components.register('final-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/final-step.htm'
        }
    });
});
