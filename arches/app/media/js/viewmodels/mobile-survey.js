define([
    'jquery',
    'arches',
    'underscore',
    'knockout',
    'views/mobile-survey-manager/identity-list',
    'views/mobile-survey-manager/resource-list',
    'models/mobile-survey',
    'views/components/widgets/map',
    'bindings/sortable'
], function($, arches, _, ko, IdentityList, ResourceList, MobileSurveyModel) {
    /**
    * A base viewmodel for mobile survey management
    *
    * @constructor
    * @name MobileSurveyViewModel
    *
    * @param  {string} params - a configuration object
    */
    var MobileSurveyViewModel = function(params) {
        var self = this;
        this.dateFormat = 'YYYY-MM-DD';

        this.identityList = new IdentityList({
            items: ko.observableArray(params.identities)
        });

        this.basemap = _.filter(arches.mapLayers, function(layer) {
            return !layer.isoverlay;
        })[0];

        this.resizeMap = function() {
            setTimeout(
                function() {
                    window.dispatchEvent(new window.Event('resize'));
                }, 200);
        };

        this.defaultCenterX = arches.mapDefaultX;
        this.defaultCenterY = arches.mapDefaultY;
        this.geocoderDefault = arches.geocoderDefault;
        this.mapDefaultZoom = arches.mapDefaultZoom;
        this.mapDefaultMaxZoom = arches.mapDefaultMaxZoom;
        this.mapDefaultMinZoom = arches.mapDefaultMinZoom;

        this.mobilesurvey = new MobileSurveyModel({source: params.mobilesurvey, identities: params.identities});

        this.getRootCards = function(r) {
            var subCardIds = [];
            var rootCards;
            var getSubCardIds = function(cards){
                _.each(cards, function(card) {
                    if (card.cards.length > 0) {
                        _.each(card.cards, function(subcard) {
                            subCardIds.push(subcard.cardid);
                            getSubCardIds(subcard.cards);
                        });
                    }
                });
            }
            getSubCardIds(r.cards);
            rootCards = r.cards.filter(function(card){
                var isRootCard = _.contains(subCardIds, card.cardid) === false;
                if (isRootCard) {
                    card.approved = ko.observable(_.contains(self.mobilesurvey.cards(), card.cardid))
                }
                return isRootCard;
            });
            return ko.observableArray(rootCards);
        };

        _.each(params.resources, function(r){
            r.istopnode = false;
            r.childNodes = ko.observableArray([]);
            r.pageid = 'resourcemodel';
            r.selected = ko.observable(false);
            r.namelong = 'Model Details';
            r.description = 'Summary of how this model participates in the survey';
            r.cards = self.getRootCards(r);
            console.log(r.cards());
        });

        this.resourceList = ko.observableArray(params.resources);

        this.processResource = function(data) {
            self.resourceList.initCards(data.cards);
            self.resourceList.selected().cards(data.cards);
            self.flattenCards(self.resourceList.selected());
        };

        this.processResources = function(data) {
            if (_.some(self.resourceList.items(), function(r) {return data.id === r.id;}) === false) {
                data.cards = ko.observableArray(data.cards);
                data.cardsflat = ko.observableArray();
                self.resourceList.initCards(data.cards);
                self.resourceList.items.push(data);
            }
        };

        this.getMobileSurveyResources = function(){
            var successCallback = function(data){
                self.mobilesurvey.collectedResources(true);
                _.each(data.resources, self.processResources);
                _.each(self.resourceList.items(), self.flattenCards);
            };
            if (!this.mobilesurvey.collectedResources()) {
                $.ajax({
                    url: arches.urls.mobile_survey_resources(this.mobilesurvey.id)
                })
                    .done(successCallback)
                    .fail(function(data){console.log('request failed', data);});
            }
        };

        this.resourceList.subscribe(function(val){
            if (val) {
                if (ko.unwrap(val.cards).length === 0) {
                    $.ajax({
                        url: arches.urls.resource_cards.replace('//', '/' + val.id + '/')
                    })
                        .done(self.processResource)
                        .fail(function(data){console.log('card request failed', data);});
                }
            }
        }, self);

        // viewModel.selectedResourceIds = ko.computed(function(val){
        //     return [];
        // });
        //
        this.selectedResources = ko.computed(function(){
            var resources = params.resources.filter(function(r){
                if (r.cards().length > 0) {
                    return r;
                }
            });
            return resources;
        });

        this.select2Config = {
            clickBubble: true,
            disabled: false,
            data: {results: params.resources.map(function(r){return {text: r.name, id: r.id};})},
            value: ko.observableArray([]),
            multiple: true,
            placeholder: "select a model",
            allowClear: true
        };

        this.loading = ko.observable(false);

        this.treenodes = [{
            name: this.mobilesurvey.name,
            namelong: 'Summary',
            description: 'Survey summary and status',
            id: 'root',
            selected: ko.observable(true),
            istopnode: true,
            iconclass: 'fa fa-globe',
            pageactive: ko.observable(true),
            expanded: ko.observable(true),
            childNodes: ko.observableArray([{
                name: 'Settings',
                namelong: 'Survey Settings',
                description: 'Define data collection parameters for your survey',
                id: 'settings',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-wrench',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'Map Extent',
                namelong: 'Map Extent',
                description: 'Draw a polygon to define the area over which you want to collect data in this survery',
                id: 'mapextent',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-map-marker',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'Map Sources',
                namelong: 'Basemap Source',
                description: 'Provide a basemap source url. Use an offline source for users without access to cell/wi-fi service',
                id: 'mapsources',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-th',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'Models',
                namelong: 'Models',
                description: 'Summary of models in this survey',
                id: 'models',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-bookmark',
                pageactive: ko.observable(false),
                childNodes: this.selectedResources,
                expanded: ko.observable(false)
            },
            {
                name: 'Data',
                namelong: 'Data download',
                description: 'Define the data you will allow users to download',
                id: 'data',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-bar-chart-o',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            },
            {
                name: 'People',
                namelong: 'People',
                description: 'Summary of people invited to participate in this survey',
                id: 'people',
                selected: ko.observable(false),
                istopnode: false,
                iconclass: 'fa fa-group',
                pageactive: ko.observable(false),
                childNodes: ko.observableArray([]),
                expanded: ko.observable(false)
            }
            ])
        }];

    };
    return MobileSurveyViewModel;
});
