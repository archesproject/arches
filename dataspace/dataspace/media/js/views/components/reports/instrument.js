define([
    'jquery', 
    'underscore', 
    'knockout', 
    'arches', 
    'viewmodels/tabbed-report', 
    'utils/resource', 
    'utils/report', 
    'views/components/reports/scenes/name', 
    'views/components/reports/scenes/description', 
    'views/components/reports/scenes/documentation', 
    'views/components/reports/scenes/existence', 
    'views/components/reports/scenes/substance',  
    'views/components/reports/scenes/json', 
    'views/components/reports/scenes/default' 
], 
    function($, _, ko, arches, TabbedReportViewModel, resourceUtils, reportUtils) {
    return ko.components.register('instrument-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {'id': 'name', 'title': 'Names and Classifications'}, 
                {'id': 'existence', 'title': 'Existence'},
                {'id': 'substance', 'title': 'Substance'},
                {'id': 'actor-relations', 'title': 'Actor Relations'},
                {'id': 'location', 'title': 'Location'},
                {'id': 'parthood', 'title': 'Parthood'},
                {'id': 'sethood', 'title': 'Sethood'},
                {'id': 'description', 'title': 'Description'},
                {'id': 'documentation', 'title': 'Documentation'},
                {'id': 'json', 'title': 'JSON'},
            ];
            self.reportMetadata = ko.observable(params.report?.report_json);
            self.resource = ko.observable(self.reportMetadata()?.resource);
            self.displayname = ko.observable(ko.unwrap(self.reportMetadata)?.displayname);
            self.activeSection = ko.observable('name');
            self.nameDataConfig = { 'exactMatch': undefined };
            self.documentationDataConfig = {
                'subjectOf': undefined, 
            };
            self.existenceDataConfig = {
                'production': {
                    graph: 'production',
                    metadata: [{
                        key: 'production event type',
                        path: 'production_type',
                        type: 'resource'
                    },{
                        key: 'producer',
                        path: 'production_carried out by',
                        type: 'resource'
                    },{
                        key: 'production event location',
                        path: 'production_location',
                        type: 'resource'
                    }]
                },
            };
            self.nameCards = {};
            self.descriptionCards = {}
            self.documentationCards = {};
            self.existenceCards = {};
            self.substanceCards = {};
            self.summary = params.summary;

            if(params.report.cards){
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards);

                self.nameCards = {
                    name: self.cards?.["name of instrument"],
                    identifier: self.cards?.["identifier for instrument"],
                    type: self.cards?.["type of instrument"]
                };
                self.existenceCards = {
                    production: {
                        card: self.cards?.["production event of instrument"],
                        subCards: {
                            name: 'name for production event',
                            identifier: 'identifier for production event',
                            timespan: 'timespan of production event',
                            statement: 'statement about production event',
                        }
                    }
                };

                self.documentationCards = {
                    digitalReference: self.cards?.["digital reference to instrument"],
                };

                self.descriptionCards = {
                    statement: self.cards?.['statement about instrument']
                };
                self.substanceCards = {
                    dimension: self.cards?.['dimension of instrument']
                }
            }

            self.locationData = ko.observable({
                sections: 
                    [
                        {
                            title: "Location", 
                            data: [{
                                key: 'current location', 
                                value: self.getRawNodeValue(self.resource(), 'current location'), 
                                card: self.cards?.['current location of instrument'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.parthoodData = ko.observable({
                sections: 
                    [
                        {
                            title: "Parthood", 
                            data: [{
                                key: 'parent instrument', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                card: self.cards?.['parent instrument'],
                                type: 'resource'
                            }]
                        }
                    ]
            });


            self.actorData = ko.observable({
                sections: 
                    [
                        {
                            title: "Actor Relations", 
                            data: [{
                                key: 'current owner', 
                                value: self.getRawNodeValue(self.resource(), 'current owner'), 
                                card: self.cards?.['current owner of instrument'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.sethoodData = ko.observable({
                sections: 
                    [
                        {
                            title: "Sethood", 
                            data: [{
                                key: 'Member of Set', 
                                value: self.getRawNodeValue(self.resource(), 'member of'), 
                                card: self.cards?.['part of set'],
                                type: 'resource'
                            }]
                        }
                    ]
            });
        },
        template: { require: 'text!templates/views/components/reports/instrument.htm' }
    });
});
