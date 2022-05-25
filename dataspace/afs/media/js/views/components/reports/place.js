define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'utils/report',
    'views/components/reports/scenes/name',
    'views/components/reports/scenes/location'
], function($, _, ko, arches, reportUtils) {
    return ko.components.register('place-report', {
        viewModel: function(params) {
            var self = this;
            params.configKeys = ['tabs', 'activeTabIndex'];
            Object.assign(self, reportUtils);
            self.sections = [
                {id: 'name', title: 'Names and Classifications'},
                {id: 'location', title: 'Location'},
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
                exactMatch: "external uri"
            };
            self.documentationDataConfig = {
                'subjectOf': undefined,
                'label': undefined
            };
            self.nameCards = {};
            self.descriptionCards = {};
            self.documentationCards = {};
            self.locationCards = {};
            self.summary = params.summary;
            
            if(params.report.cards){
                const cards = params.report.cards;
                
                self.cards = self.createCardDictionary(cards)

                self.nameCards = {
                    name: self.cards?.["name of place"],
                    identifier: self.cards?.["identifier"],
                    exactMatch: self.cards?.["external uri for place"],
                    type: self.cards?.["type of place"],
                };

                self.descriptionCards = {
                    statement: self.cards?.["statement about place"],
                };

                self.documentationCards = {
                    digitalReference: self.cards?.['digital reference to place'],
                };

                self.locationCards = {
                    location: self.cards?.['geospatial definition of place'],
                };
            }

            self.parthoodData = ko.observable({
                sections: 
                    [
                        {
                            title: "Parthood", 
                            data: [{
                                key: 'parent place', 
                                value: self.getRawNodeValue(self.resource(), 'part of'), 
                                card: self.cards?.['parent place'],
                                type: 'resource'
                            }]
                        }
                    ]
            });

            self.geojson = self.getNodeValue(self.resource(), 'defined by')
        },
        template: { require: 'text!templates/views/components/reports/place.htm' }
    });
});
