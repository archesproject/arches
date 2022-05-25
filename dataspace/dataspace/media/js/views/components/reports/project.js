define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'utils/resource',
    'utils/report',
    'views/components/reports/scenes/name'
], function($, _, ko, arches, resourceUtils, reportUtils) {
    return ko.components.register('project-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {id: 'name', title: 'Names and Classifications'},
                {id: 'substance', title: 'Substance'},
                {id: 'temporal', title: 'Temporal Relations'},
                {id: 'parameters', title: 'Parameters & Outcomes'},
                {id: 'parthood', title: 'Parthood'},
                {id: 'description', title: 'Description'},
                {id: 'documentation', title: 'Documentation'},
                {id: 'json', title: 'JSON'},
            ];
            self.reportMetadata = ko.observable(params.report?.report_json);
            self.resource = ko.observable(self.reportMetadata()?.resource);
            self.displayname = ko.observable(ko.unwrap(self.reportMetadata)?.displayname);
            self.activeSection = ko.observable('name');
            self.nameDataConfig = {
                exactMatch: undefined
            };
            self.documentationDataConfig = {
                label: undefined,
                subjectOf: 'influenced by',
            };
            self.substanceDataConfig = {
                dimension: undefined,
                timespan: {path: 'timespan', key: 'dates of project'}
            };
            self.nameCards = {};
            self.descriptionCards = {};
            self.documentationCards = {};
            self.summary = params.summary;

            if(params.report.cards){
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards)

                self.nameCards = {
                    name: self.cards?.['name of project'],
                    identifier: self.cards?.['identifier for project'],
                    type: self.cards?.['scale of project']
                };
                self.descriptionCards = {
                    statement: self.cards?.['statement about project'],
                };
                self.documentationCards = {
                    digitalReference: self.cards?.['digital reference to project'],
                    subjectOf: self.cards?.['source reference work for project'],
                };
                self.substanceCards = {
                    timespan: self.cards?.['dates of project'],
                };
            };

            self.parthoodData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Parthood', 
                            data: [{
                                key: 'parent project', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                card: self.cards?.['parent project'],
                                type: 'resource'
                            }]
                        }
                    ]
            });
            self.temporalData = ko.observable({
                sections: [
                    {
                        title: 'Temporal Relations of Project', 
                        data: [
                            /*{
                                key: 'Project Period', 
                                value: self.getRawNodeValue(self.resource(), 'during'), 
                                card: self.cards?.['temporal relations of project'],
                                type: 'resource'
                            },*/
                            {
                                key: 'Occurs After Event', 
                                value: self.getRawNodeValue(self.resource(), 'starts after'), 
                                card: self.cards?.['temporal relations of project'],
                                type: 'resource'
                            },{
                                key: 'Occurs Before Event', 
                                value: self.getRawNodeValue(self.resource(), 'ends before'), 
                                card: self.cards?.['temporal relations of project'],
                                type: 'resource'
                            }
                        ]
                    }
                ]
            });
            self.parameterData = ko.observable({
                sections: [
                    {
                        title: 'Project Team', 
                        data: [{
                            key: 'project team', 
                            value: self.getRawNodeValue(self.resource(), 'carried out by'), 
                            card: self.cards?.['project team'],
                            type: 'resource'
                        }]
                    },
                    {
                        title: 'Activity Type of Project', 
                        data: [{
                            key: 'activity type of project', 
                            value: self.getRawNodeValue(self.resource(), 'technique'), 
                            card: self.cards?.['activity type of project'],
                            type: 'resource'
                        }]
                    }
                ]
            });
        },
        template: { require: 'text!templates/views/components/reports/project.htm' }
    });
});
