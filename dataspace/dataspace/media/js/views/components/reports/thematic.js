define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'viewmodels/report',
    'bindings/chosen'
], function($, _, ko, koMapping, arches, ReportViewModel) {
    NODE_ID = "@node_id";
    TILE_ID = "@tile_id";
    VALUE = "@value";
    NON_DATA_COLLECTING_NODE = "NON_DATA_COLLECTING_NODE";

    TAB_DATA = [
        {
            title: "Names/Classification",
            sections: [
                {
                    nodeId: 'b9c1ced7-b497-11e9-a4da-a4d18cec433a',  /* assumes each section contains a single node */
                    sectionTitle: "Name(s) of Thing",
                    hasPlusSign: true,
                    childNodeInformation: [
                        { 
                            nodeId: 'b9c1d8a6-b497-11e9-876b-a4d18cec433a',
                            columnName: 'Name',
                            
                        },
                        { 
                            nodeId: 'b9c1d7ab-b497-11e9-9ab7-a4d18cec433a',
                            columnName: 'Name Type',
                        },
                        { 
                            nodeId:'b9c1d400-b497-11e9-90ea-a4d18cec433a', 
                            columnName: 'Language',
                        },
                    ],
                },
                {
                    nodeId: '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a',  /* assumes each section contains a single node */
                    sectionTitle: "Type of Object",
                },
                {
                    nodeId: '22c150ca-b498-11e9-9adc-a4d18cec433a',  /* assumes each section contains a single node */
                    sectionTitle: "Identifiers",
                    hasPlusSign: true,
                    childNodeInformation: [
                        { 
                            nodeId: '22c169b5-b498-11e9-bdad-a4d18cec433a',
                            columnName: 'Identifier',
                        },
                        { 
                            nodeId: '22c15cfa-b498-11e9-b5e3-a4d18cec433a',
                            columnName: 'Identifier Type',
                        },
                    ],
                }
            ],
        },
        {
            title: "Existence",
            sections: [],
        },
        {
            title: "Parameters",
            sections: [],
        },
        {
            title: "Parts",
            sections: [],
        },
        {
            title: "Temporal Relations",
            sections: [],
        },
        {
            title: "Location",
            sections: [],
        },
        {
            title: "Descriptions",
            sections: [],
        }
    ];

    var ThematicReportTab = function(tabDatum, disambiguatedResourceGraph, hideEmptySections) {
        var self = this;

        this.hideEmptySections = hideEmptySections;  /* READ-ONLY on this level */

        /* BEGIN page layout source-of-truth */ 
        this.title = tabDatum.title;
        this.sections = ko.observableArray(tabDatum.sections);
        /* END page layout source-of-truth */ 

        this.initialize = function() {
            self.mapResourceInstanceDataToSections(tabDatum, disambiguatedResourceGraph);
        };

        this.mapResourceInstanceDataToSections = function(tabDatum, disambiguatedResourceGraph) {
            tabDatum.sections.forEach(function(section) {
                /* BEGIN normalize resourceInstanceData shape */ 
                var resourceInstanceData = Object.values(disambiguatedResourceGraph.resource).find(function(topLevelData) {
                    if (topLevelData instanceof Array) {
                        return topLevelData[0][NODE_ID] === section.nodeId;  /* all data has same nodeId */
                    }
                    return topLevelData[NODE_ID] === section.nodeId;
                });

                if (!(resourceInstanceData instanceof Array)) {
                    if (!resourceInstanceData) {
                        resourceInstanceData = [];
                    }
                    else {
                        resourceInstanceData = [ resourceInstanceData ];
                    }
                }
                /* END normalize resourceInstanceData shape */ 

                section['resourceInstanceData'] = resourceInstanceData;
            });
        };

        this.getResourceInstanceNodeData = function(nodeId, resourceInstanceData) {
            if (resourceInstanceData[NODE_ID] === nodeId) {
                return resourceInstanceData[NODE_ID];
            }
            else {
                return Object.values(resourceInstanceData).find(function(resourceInstanceChildNodeData) {
                    return resourceInstanceChildNodeData[NODE_ID] === nodeId;
                });
            }
        };
        
        this.initialize();
    };

    var viewModel = function(params) {
        var self = this;
        ReportViewModel.apply(this, [params]);

        this.loading = ko.observable();

        this.disambiguatedResourceGraph = ko.observable();

        this.reportTabs = ko.observableArray();

        this.activeTabIndex = ko.observable(0);
        this.activeTab = ko.computed(function() {
            if (self.reportTabs().length) {
                return self.reportTabs()[self.activeTabIndex()];
            }
        });

        this.emptyReportSectionsHidden = ko.observable(false);

        this.initialize = function() {
            self.loading(true);

            var url = arches.urls.api_resources(params.report.get('resourceid')) + '?format=json&compact=false';

            $.get(url, function(data) {
                self.disambiguatedResourceGraph(data);

                TAB_DATA.forEach(function(tabDatum) {
                    self.reportTabs.push(
                        new ThematicReportTab(
                            tabDatum,
                            self.disambiguatedResourceGraph(),
                            self.emptyReportSectionsHidden
                        )
                    );
                });

                self.loading(false);
            });
        };

        this.toggleEmptyReportSections = function() {
            self.emptyReportSectionsHidden(!self.emptyReportSectionsHidden());
        };

        this.initialize();
    };

    ko.components.register('thematic-report', {
        viewModel: viewModel,
        template: { require: 'text!report-templates/thematic' }
    });
});
