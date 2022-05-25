define([
    'jquery',
    'underscore', 
    'knockout', 
    'arches', 
    'utils/resource', 
    'utils/report', 
    'views/components/reports/scenes/name', 
    'views/components/reports/scenes/description', 
    'views/components/reports/scenes/documentation', 
    'views/components/reports/scenes/existence', 
    'views/components/reports/scenes/substance',
    'views/components/reports/scenes/json',  
    'views/components/reports/scenes/default'], 
    function($, _, ko, arches, resourceUtils, reportUtils) {
    return ko.components.register('digital-resource-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {id: 'name', title: 'Names and Classifications'}, 
                {id: 'existence', title: 'Existence'},
                {id: 'substance', title: 'Substance'},
                {id: 'events', title: 'Events'},
                {id: 'parthood', title: 'Parthood'},
                {id: 'sethood', title: 'Sethood'},
                {id: 'carriers', title: 'Information Carriers & Information Carried'},
                {id: 'aboutness', title: 'Aboutness'},
                {id: 'description', title: 'Description'},
                {id: 'documentation', title: 'Documentation'},
                {id: 'json', title: 'JSON'},
            ];

            self.filesTable = {
                ...self.defaultTableConfig,
                columns: Array(3).fill(null)
            };

            self.visible = { files: ko.observable(true) }
            self.reportMetadata = ko.observable(params.report?.report_json);
            self.resource = ko.observable(self.reportMetadata()?.resource);
            self.displayname = ko.observable(ko.unwrap(self.reportMetadata)?.displayname);
            self.activeSection = ko.observable('name');
            self.nameDataConfig = { exactMatch: undefined };
            self.documentationDataConfig = {
                'subjectOf': undefined, 
                'digitalReference': undefined
            };
            self.existenceDataConfig = {
                creation: {
                    graph: 'creation',
                    metadata: [{
                        key: 'creator',
                        path: 'creation_carried out by',
                        type: 'resource'
                    },{
                        key: 'creation event location',
                        path: 'creation_location',
                        type: 'resource'
                    },{
                        key: 'creation event type',
                        path: 'creation_type',
                        type: 'resource'
                    },{
                        key: 'creation event technique',
                        path: 'creation_technique',
                        type: 'resource'
                    },{
                        key: 'physical object used in creation event',
                        path: 'creation_used object',
                        type: 'resource'
                    }]
                },
            };

            self.eventsDataConfig = {
                'digital service': {
                    graph: 'service',
                    metadata: [{
                        key: 'conforms to',
                        path: 'service_conforms to',
                        type: 'resource'
                    },{
                        key: 'service type',
                        path: 'service_type',
                        type: 'resource'
                    }]
                },
            };
            self.existenceEvents = ['creation'];
            self.eventsEvents = ['digital service'];
            self.nameCards = {};
            self.descriptionCards = {}
            self.documentationCards = {};
            self.substanceCards = {};
            self.existenceCards = {};
            self.eventsCards = {};
            self.summary = params.summary;

            if(params.report.cards){
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards)
                self.nameCards = {
                    name: self.cards?.['name of digital resource'],
                    identifier: self.cards?.['identifier of digital resource'],
                    type: self.cards?.['type of digital resource']
                };

                self.descriptionCards = {
                    statement: self.cards['statement about digital resource']
                };

                self.substanceCards = {
                    dimension: self.cards?.['dimension of digital resource']
                };

                self.existenceCards = {
                    creation: {
                        card: self.cards?.['creation event of digital resource'],
                        subCards: {
                            name: 'name for creation event',
                            identifier: 'identifier for creation event',
                            timespan: 'timespan of creation event',
                            statement: 'statement about creation event',
                        }
                    },
                };

                /*self.eventsCards = {
                    creation: {
                        card: self.cards?.['creation event of digital resource'],
                        subCards: {
                            name: 'name for creation event',
                            identifier: 'identifier for creation event',
                            timespan: 'timespan of creation event',
                            statement: 'statement about creation event',
                        }
                    },
                };*/
            }

            self.aboutnessData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Aboutness', 
                            data: [{
                                key: 'text carried by object', 
                                value: self.getRawNodeValue(self.resource(), 'carries text'), 
                                card: self.cards?.['text carried by object'],
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
                                key: 'parent digital resource', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.files = ko.observableArray(
                self.getRawNodeValue(self.resource(), 'file')?.map(x => {
                    const name =  self.getNodeValue(x, 'file_details', 0, 'name');
                    const tileid =  self.getTileId(x);
                    const metadataExists = self.nestedDataExists(x, '@node_id', '@tile_id', 'file_details');
                    return {name, metadataExists, tileid}
                }
            ));

            self.sethoodData = ko.observable({
                sections: 
                    [
                        {
                            title: 'Sethood', 
                            data: [{
                                key: 'collection that includes digital resource', 
                                value: self.getRawNodeValue(self.resource(), 'member of'), 
                                card: self.cards?.['collection that includes digital resource'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.additionalData = ko.observableArray([{
                key: 'standards conformed to by digital resource', 
                value: self.getNodeValue(self.resource(), 'conforms to'), 
                href: self.getNodeValue(self.resource(), 'conforms to'), 
                card: self.cards?.['standards conformed to by digital resource'],
                type: 'href'
            }]);
        },
        template: { require: 'text!templates/views/components/reports/digital-resource.htm' }
    });
});
