define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'utils/resource',
    'utils/report',
    'views/components/reports/scenes/name'
], function($, _, ko, arches, resourceUtils, reportUtils) {
    return ko.components.register('modification-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {id: 'name', title: 'Names and Classifications'},
                {id: 'substance', title: 'Substance'},
                // {id: 'temporal', title: 'Temporal Relations'}, commented because no cards available
                {id: 'location', title: 'Location'},
                {id: 'parameters', title: 'Parameters & Outcomes'},
                {id: 'parthood', title: 'Parthood'},
                // {id: 'aboutness', title: 'Aboutness'}, commented because no cards available
                {id: 'description', title: 'Description'},
                {id: 'documentation', title: 'Documentation'},
                {id: 'json', title: 'JSON'},
            ];
            self.reportMetadata = ko.observable(params.report?.report_json);
            self.resource = ko.observable(self.reportMetadata()?.resource);
            self.displayname = ko.observable(ko.unwrap(self.reportMetadata)?.displayname);
            self.activeSection = ko.observable('name');
            self.nameDataConfig = {
                exactMatch: undefined,
            };
            self.documentationDataConfig = {
                subjectOf: undefined,
            };
            self.nameCards = {};
            self.descriptionCards = {};
            self.documentationCards = {};
            self.substanceCards = {};
            self.summary = params.summary;

            if(params.report.cards) {
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards)

                self.documentationCards = {
                    digitalReference: self.cards?.['digital reference to modification'],
                };

                self.nameCards = {
                    name: self.cards?.['name of modification'],
                    identifier: self.cards?.['identifier for modification'],
                    type: self.cards?.['type of modification']
                }

                self.descriptionCards = {
                    statement: self.cards?.['statement about modification']
                };
                self.substanceCards = {
                    timespan: self.cards?.['timespan of modification'],
                };
            }

            self.locationData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Location', 
                            data: [{
                                key: 'location of modification', 
                                value: self.getRawNodeValue(self.resource(), 'took place at'), 
                                card: self.cards?.['location of modification'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.parameterData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Parameters & Outcomes', 
                            data: [{
                                key: 'technique of modification', 
                                value: self.getRawNodeValue(self.resource(), 'technique'), 
                                card: self.cards?.['technique of modification'],
                                type: 'resource'
                            },{
                                key: 'procedure of modification', 
                                value: self.getRawNodeValue(self.resource(), 'used process'), 
                                card: self.cards?.['procedure of modification'],
                                type: 'resource'
                            },{
                                key: 'object modified during modification', 
                                value: self.getRawNodeValue(self.resource(), 'modified'), 
                                card: self.cards?.['object modified during modification'],
                                type: 'resource'
                            },{
                                key: 'person carrying out modification', 
                                value: self.getRawNodeValue(self.resource(), 'carried out by'), 
                                card: self.cards?.['person carrying out modification'],
                                type: 'resource'
                            },{
                                key: 'tool for modification', 
                                value: self.getRawNodeValue(self.resource(), 'used object'), 
                                card: self.cards?.['tool for modification'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.substanceDataConfig = {
                dimension: undefined,
                timespan: {path: 'timespan', key: 'timespan of modification'}
            };

            self.parthoodData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Parthood', 
                            data: [{
                                key: 'parent project of modification', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                card: self.cards?.['parent project of modification'],
                                type: 'resource'
                            }]
                        }
                    ]
            })

            /*self.aboutnessData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Aboutness', 
                            data: [{
                                key: 'influenced by', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                card: self.cards?.['parent project of modification'],
                                type: 'resource'
                            }]
                        }
                    ]
            });*/
        },
        template: { require: 'text!templates/views/components/reports/modification.htm' }
    });
});
