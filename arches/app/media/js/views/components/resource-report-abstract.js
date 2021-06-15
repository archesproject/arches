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
    var ResourceReportAbstract = function(params) {
        var self = this;

        this.loading = ko.observable(true);

        this.version = arches.version;
        this.resourceid = params.resourceid;
        this.summary = Boolean(params.summary);

        this.template = ko.observable();
        this.report = ko.observable();
        
        this.initialize = function() {
            console.log("!!!!", params)
            if (params.report && params.report.disambiguated_resource) {
                this.template(reportLookup[params.report.templateId()]);
                this.report(params.report);

                self.loading(false);
            }
            else if (params.report) {
                var url = arches.urls.api_bulk_bar + `?resource_ids=${params.report.attributes.resourceid}`;

                $.getJSON(url, function(resp) {
                    params.report.disambiguated_resource = resp[params.report.attributes.resourceid];

                    self.template(reportLookup[params.report.templateId()]);
                    self.report(params.report);
                    self.loading(false);
                })
            }
            else if (ko.unwrap(self.resourceid)) {
                var url = arches.urls.api_resource_report(self.resourceid);

                self.fetchResourceData(url).then(function(responseJson) {

                    console.log('hhh', responseJson)
                    var template = responseJson.template;
                    self.template(template);
                    
                    if (template.preload_resource_data) {
                        self.preloadResourceData(responseJson)
                    }
                    else {
                        self.report({
                            'template': responseJson.template,
                            'disambiguated_resource': responseJson.disambiguated_resource,
                        });
                    }
        
                    self.loading(false);
                });

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
                data: responseJson.graph,
                datatypes: responseJson.datatypes,
            });

            graph = {
                graphModel: graphModel,
                cards: responseJson.cards,
                graph: responseJson.graph,
                datatypes: responseJson.datatypes,
                cardwidgets: responseJson.cardwidgets
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
            report['disambiguated_resource'] = responseJson.disambiguated_resource;

            self.report(report);
        };

        this.initialize();
    };
    ko.components.register('resource-report-abstract', {
        viewModel: ResourceReportAbstract,
        template: { require: 'text!templates/views/components/resource-report-abstract.htm' }
    });
    return ResourceReportAbstract;
});
