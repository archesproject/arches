define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'utils/resource',
    'utils/report',
    'views/components/reports/scenes/name'
], function($, _, ko, arches, resourceUtils, reportUtils) {
    return ko.components.register('collection-set-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {id: 'name', title: 'Names and Classifications'},
                {id: 'existence', title: 'Existence'},
                {id: 'events', title: 'Events'},
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
                subjectOf: undefined,
                label: undefined // set to undefined per airtable - not visible
            };
            self.existenceEvents = ['creation'];
            self.existenceDataConfig = {
                creation: { 
                    graph: 'created',
                    metadata: [{
                        key: 'creator',
                        path: 'created_carried out by',
                        type: 'resource'
                    },{
                        key: 'creation event location',
                        path: 'created_location',
                        type: 'resource'
                    },{
                        key: 'creation event type',
                        path: 'created_type',
                        type: 'resource'
                    }]}
            };


            self.eventEvents = ['curation'];
            self.eventDataConfig = {
                curation: { 
                    graph: 'curation',
                    metadata: [{
                        key: 'person in curation event',
                        path: 'curation_carried out by',
                        type: 'resource'
                    },{
                        key: 'location of curation event',
                        path: 'curation_location',
                        type: 'resource'
                    },{
                        key: 'curation event type',
                        path: 'curation_type',
                        type: 'kv'
                    }]}
            };
            self.nameCards = {};
            self.descriptionCards = {};
            self.documentationCards = {};
            self.existenceCards = {};
            self.eventCards = {};
            self.summary = params.summary;

            if(params.report.cards){
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards)

                self.nameCards = {
                    name: self.cards?.['name of collection'],
                    identifier: self.cards?.['identifier of collection'],
                    type: self.cards?.['type of collection']
                };
                
                self.descriptionCards = {
                    statement: self.cards?.['statement about collection'],
                };
                
                self.documentationCards = {
                    digitalReference: self.cards?.['digital reference to collection'],
                };

                self.existenceCards = {
                    creation: {
                        card: self.cards?.['creation event of collection'],
                        subCards: {
                            name: 'name for creation event',
                            identifier: 'identifier of creation event',
                            timespan: 'timespan of creation event',
                            statement: 'statement about creation event',
                        }
                    },
                };

                self.eventCards = {
                    curation: {
                        card: self.cards?.['curation event of collection'],
                        subCards: {
                            name: 'name for curation event',
                            identifier: 'identifier of curation event',
                            timespan: 'timespan of curation event',
                            statement: 'statement about curation event',
                        }
                    },
                };
            }

            self.usedInData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Used In', 
                            data: [{
                                key: 'Related Projects', 
                                value: self.getRawNodeValue(self.resource(), 'used in'), 
                                card: self.cards?.['related project of collection'],
                                type: 'resource'
                            }]
                        }
                    ]
            });
        },
        template: { require: 'text!templates/views/components/reports/collection-set.htm' }
    });
});
