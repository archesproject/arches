define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'utils/resource',
    'utils/report'
], function($, _, ko, arches, resourceUtils, reportUtils) {
    return ko.components.register('person-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {id: 'name', title: 'Names and Classifications'},
                {id: 'existence', title: 'Existence'},
                {id: 'events', title: 'Events'},
                {id: 'parthood', title: 'Parthood'},
                {id: 'description', title: 'Description'},
                {id: 'documentation', title: 'Documentation'},
                {id: 'communication', title: 'Communication'},
                {id: 'json', title: 'JSON'},
            ];
            self.reportMetadata = ko.observable(params.report?.report_json);
            self.resource = ko.observable(self.reportMetadata()?.resource);
            self.displayname = ko.observable(ko.unwrap(self.reportMetadata)?.displayname);
            self.activeSection = ko.observable('name');
            self.contactPointsTable = {
                ...self.defaultTableConfig,
                columns: Array(3).fill(null)
            };
            self.visible = {
                contactPoints: ko.observable(true)
            }
            self.sourceData = ko.observable({
                sections:
                    [
                        {
                            title: 'References',
                            data: [{
                                key: 'source reference work',
                                value: self.getRawNodeValue(self.resource(), 'source'),
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.nameDataConfig = {
                type: undefined,
            };
            self.documentationDataConfig = {
                subjectOf: undefined
            };

            self.existenceEvents = ['birth', 'death'];
            self.existenceDataConfig = {
                birth: {
                    graph: 'birth',
                    metadata: [],
                    children: {
                        names: true,
                        statements: true,
                        identifiers: false,
                        timespan: true,
                        location: true
                    }
                },
                death: {
                    graph: 'death',
                    metadata: [],
                    children: {
                        names: true,
                        statements: true,
                        identifiers: false,
                        timespan: true,
                        location: true
                    }
                },
            };

            self.eventEvents = ['professional activity', 'group joining', 'group leaving'];
            self.eventDataConfig = {
                'professional activity': {
                    graph: 'profession activity',
                    metadata: [{
                        key: 'professional activity type',
                        path: 'profession activity_type',
                        type: 'kv'
                    },{
                        key: 'particular professional activity technique',
                        path: 'profession activity_technique',
                        type: 'kv'
                    },{
                        key: 'location of professional activity',
                        path: 'profession activity_location',
                        type: 'resource'
                    }],
                    children: {
                        names: true,
                        statements: true,
                        identifiers: false,
                        timespan: true,
                        location: false
                    }
                },
                'group joining': {
                    graph: 'joined group',
                    metadata: [{
                        key: 'group joined',
                        path: 'joined group_joined to',
                        type: 'resource'
                    },{
                        key: 'group role',
                        path: 'joined group_type',
                        type: 'kv'
                    },{
                        key: 'location of group joining event',
                        path: 'joined group_location',
                        type: 'resource'
                    }],
                    children: {
                        names: true,
                        statements: true,
                        identifiers: false,
                        timespan: true,
                        location: false
                    }
                },
                'group leaving': {
                    graph: 'left group',
                    metadata: [{
                        key: 'group left',
                        path: 'left group_left group',
                        type: 'resource'
                    },{
                        key: 'group leaving event type',
                        path: 'left group_type',
                        type: 'kv'
                    },{
                        key: 'location of group leaving event',
                        path: 'left group_location',
                        type: 'resource'
                    }],
                    children: {
                        names: true,
                        statements: true,
                        identifiers: false,
                        timespan: true,
                        location: false
                    }
                },
            };
            self.nameCards = {};
            self.descriptionCards = {};
            self.documentationCards = {};
            self.existenceCards = {};
            self.communicationCards = {};
            self.eventCards = {};
            self.summary = params.summary;
            self.cards = {};

            if(params.report.cards){
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards)

                self.nameCards = {
                    name: self.cards?.['name of person'],
                    identifier: self.cards?.['identifier for person'],
                    exactMatch: self.cards?.['external uri for person'],
                };

                self.descriptionCards = {
                    statement: self.cards?.['statement about person'],
                };

                self.documentationCards = {
                    digitalReference: self.cards?.['digital reference for person'],
                };

                self.communicationCards = {
                    contactPoints: self.cards?.['contact information for person'],
                };

                self.existenceCards = {
                    birth: { 
                        card: self.cards?.['birth event of person'],
                        subCards: {
                            name: 'name for birth event',
                            timespan: 'timespan of birth event',
                            statement: 'statement about birth event',
                            location: 'location of birth event',
                        }
                    },
                    death: {
                        card:  self.cards?.['death event of person'],
                        subCards: {
                            name: 'name for death event',
                            timespan: 'timespan of death event',
                            statement: 'statement about death event',
                            location: 'location of death event'
                        }
                    },
                };
                
                self.eventCards = {
                    'professional activity': {
                        card: self.cards?.['professional activity of person'],
                        subCards: {
                            name: 'name for professional activity',
                            timespan: 'timespan of professional activity',
                            statement: 'statement about professional activity',
                        }
                    },
                    'group joining': {
                        card: self.cards?.['group joining event of person'],
                        subCards: {
                            name: 'name for group joining event',
                            timespan: 'timespan of group joining event',
                            statement: 'statement about group joining event',
                        }
                    },
                    'group leaving': {
                        card: self.cards?.['group leaving event of person'],
                        subCards: {
                            name: 'name for group leaving event',
                            timespan: 'timespan of group leaving event',
                            statement: 'statement about group leaving event',
                        }
                    }
                };
            }

            self.parthoodData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Parthood', 
                            data: [{
                                key: 'member of group', 
                                value: self.getRawNodeValue(self.resource(), 'member of'), 
                                card: self.cards?.['group person is member of'],
                                type: 'resource'
                            }]
                        }
                    ]
            });
        },
        template: { require: 'text!templates/views/components/reports/person.htm' }
    });
});
