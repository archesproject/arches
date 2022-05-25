define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'utils/resource',
    'utils/report',
    'views/components/reports/scenes/name',
    'views/components/reports/scenes/json' 
], function($, _, ko, arches, resourceUtils, reportUtils) {
    return ko.components.register('observation-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {id: 'name', title: 'Names and Classifications'},
                {id: 'substance', title: 'Substance'},
                {id: 'location', title: 'Location'},
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
                exactMatch: undefined,
            };
            self.documentationDataConfig = {
                'subjectOf': undefined,
                'label': undefined
            };
            self.substanceDataConfig = {
                dimension: undefined,
                timespan: {path: 'timespan', key: 'timespan of observation'}
            };
            self.nameCards = {};
            self.descriptionCards = {};
            self.documentationCards = {};
            self.substanceCards = {};
            self.summary = params.summary;

            if(params.report.cards){
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards)

                self.nameCards = {
                    name: self.cards?.['name of observation'],
                    identifier: self.cards?.['identifier of observation'],
                    type: self.cards?.['type of observation']
                }

                self.descriptionCards = {
                    statement: self.cards?.['statement about observation'],
                };

                self.documentationCards = {
                    digitalReference: self.cards?.['digital reference to observation'],
                };
                self.substanceCards = {
                    timespan: self.cards?.['timespan of observation'],
                };
            };
                        
            self.locationData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Location of Observation', 
                            data: [{
                                key: 'location of observation', 
                                value: self.getRawNodeValue(self.resource(), 'took place at'), 
                                card: self.cards?.['location of observation'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.parthoodData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Parthood', 
                            data: [{
                                key: 'parent event of observation', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                card: self.cards?.['parent event of observation'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.parthoodData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Parthood', 
                            data: [{
                                key: 'parent event of observation', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                card: self.cards?.['parent event of observation'],
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
                                key: 'technique of observation', 
                                value: self.getRawNodeValue(self.resource(), 'technique'), 
                                card: self.cards?.['technique of observation'],
                                type: 'resource'
                            },{
                                key: 'procedure / method used during observation', 
                                value: self.getRawNodeValue(self.resource(), 'used process'), 
                                card: self.cards?.['parent event of observation'],
                                type: 'resource'
                            },{
                                key: 'object observed during observation', 
                                value: self.getRawNodeValue(self.resource(), 'observed'), 
                                card: self.cards?.['object observed during observation'],
                                type: 'resource'
                            },{
                                key: 'recorded value of observation', 
                                value: self.getRawNodeValue(self.resource(), 'recorded value'), 
                                card: self.cards?.['recorded value of observation'],
                                type: 'resource'
                            },{
                                key: 'person carrying out observation', 
                                value: self.getRawNodeValue(self.resource(), 'carried out by'), 
                                card: self.cards?.['person carrying out observation'],
                                type: 'resource'
                            },{
                                key: 'instrument / tool used for observation', 
                                value: self.getRawNodeValue(self.resource(), 'used instrument'), 
                                card: self.cards?.['instrument/tool used for observation'],
                                type: 'resource'
                            },{
                                key: 'digital resource used in observation', 
                                value: self.getRawNodeValue(self.resource(), 'used digital resource'), 
                                card: self.cards?.['digital resource used in observation'],
                                type: 'resource'
                            }]
                        }
                    ]
            });
        },
        
        template: { require: 'text!templates/views/components/reports/observation.htm' }
    });
});
