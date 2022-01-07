define([
    'arches',
    'jquery',
    'underscore',
    'knockout',
    'report-templates',
    'models/report',
    'models/graph',
    'viewmodels/card'
], function(arches, $, _, ko, reportLookup, ReportModel, GraphModel) {
    var ResourceReportAbstract = function(params) {
        var self = this;
        var CardViewModel = require('viewmodels/card');

        this.loading = ko.observable(true);

        this.version = arches.version;
        this.resourceid = ko.unwrap(params.resourceid);

        this.summary = Boolean(params.summary);
        this.configForm = params.configForm;
        this.configType = params.configType;

        this.template = ko.observable();
        this.report = ko.observable();

        this.initialize = function() {
            var url;
            params.cache = params.cache === undefined ? true : params.cache;

            if (params.report) {
                if (
                    (!params.disableDisambiguatedReport
                    && !params.report.report_json 
                    && params?.report?.attributes?.resourceid) 
                    || !params.cache
                ) {
                    url = arches.urls.api_bulk_disambiguated_resource_instance + `?v=beta&resource_ids=${params.report.attributes.resourceid != '' ? params.report.attributes.resourceid : window.location.pathname.split("/")[2]}`;
                    if(params.report.defaultConfig?.uncompacted_reporting) {
                        url += '&uncompacted=true';
                    }

                    $.getJSON(url, function(resp) {
                        const resourceId = params.report.attributes.resourceid != '' ? params.report.attributes.resourceid : window.location.pathname.split("/")?.[2];
                        params.report.report_json = resp?.[resourceId];
    
                        self.template(reportLookup[params.report.templateId()]);
                        self.report(params.report);
                        self.loading(false);
                    });
                }
                else {
                    this.template(reportLookup[params.report.templateId()]);
                    this.report(params.report);
    
                    self.loading(false);
                }
            } 
            else if (self.resourceid) {
                url = arches.urls.api_resource_report(self.resourceid) + "?v=beta&uncompacted=true";

                self.fetchResourceData(url).then(function(responseJson) {
                    var template = responseJson.template;
                    self.template(template);
                    if (template.preload_resource_data) {
                        self.preloadResourceData(responseJson);
                    }
                    else {
                        self.report({
                            'template': responseJson.template,
                            'report_json': responseJson.report_json,
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

            var graph = {
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
            report['report_json'] = responseJson.report_json;

            self.report(report);
        };

        self.initialize();
    };
    ko.components.register('resource-report-abstract', {
        viewModel: ResourceReportAbstract,
        template: { require: 'text!templates/views/components/resource-report-abstract.htm' }
    });
    return ResourceReportAbstract;
});
