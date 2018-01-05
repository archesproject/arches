define([
    'arches',
    'underscore',
    'knockout',
    'views/mobile-survey-manager/identity-list',
    'views/mobile-survey-manager/resource-list',
    'models/mobile-survey',
    'views/components/widgets/map',
    'bindings/sortable'
], function(arches, _, ko, IdentityList, ResourceList, MobileSurveyModel) {
    /**
    * A base viewmodel for mobile survey management
    *
    * @constructor
    * @name MobileSurveyManagerViewModel
    *
    * @param  {string} params - a configuration object
    */
    var MobileSurveyManagerViewModel = function(params) {
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
                    dispatchEvent(new Event('resize'))
                }, 200)
        }

        this.defaultCenterX = arches.mapDefaultX;
        this.defaultCenterY = arches.mapDefaultY;
        this.geocoderDefault = arches.geocoderDefault;
        this.mapDefaultZoom = arches.mapDefaultZoom;
        this.mapDefaultMaxZoom = arches.mapDefaultMaxZoom;
        this.mapDefaultMinZoom = arches.mapDefaultMinZoom;

        this.flattenCards = function(r) {
            var addedCardIds = [];
            _.each(r.cards, function(card) {
                if (card.cards.length > 0) {
                    _.each(card.cards, function(subcard) {
                        subcard.name = card.name + ' - ' + subcard.name;
                        r.cardsflat.push(subcard)
                        addedCardIds.push(subcard.cardid)
                    })
                }
            });
            _.each(r.cards, function(card) {
                if (_.contains(addedCardIds, card.cardid) === false && card.cards.length == 0) {
                    addedCardIds.push(card.cardid)
                    r.cardsflat.push(card)
                }
            });
        }

        _.each(params.resources, function(r){
            r.cardsflat = ko.observableArray();
            self.flattenCards(r);
        });

        this.resourceList = new ResourceList({
            items: ko.observableArray(params.resources)
        });

        this.processResource = function(data) {
                    self.resourceList.initCards(data.cards)
                    self.resourceList.selected().cards(data.cards)
                    self.flattenCards(self.resourceList.selected())
        }

        this.processResources = function(data) {
            if (_.some(self.resourceList.items(), function(r) {return data.id === r.id}) === false) {
                data.cards = ko.observableArray(data.cards)
                data.cardsflat = ko.observableArray();
                self.resourceList.initCards(data.cards)
                self.resourceList.items.push(data)
            }
        }

        this.getMobileSurveyResources = function(mobilesurvey){
            var successCallback = function(data){
                mobilesurvey.collectedResources(true)
                _.each(data.resources, self.processResources)
                _.each(self.resourceList.items(), self.flattenCards)
            }
            if (!mobilesurvey.collectedResources()) {
                $.ajax({
                    url: arches.urls.mobile_survey_resources(mobilesurvey.id)
                })
                .done(successCallback)
                .fail(function(data){console.log('request failed', data)})
            }
        }

        this.resourceList.selected.subscribe(function(val){
            if (val) {
                if (ko.unwrap(val.cards).length === 0) {
                    $.ajax({
                        url: arches.urls.resource_cards.replace('//', '/' + val.id + '/')
                    })
                    .done(self.processResource)
                    .fail(function(data){console.log('card request failed', data)})
                }
            }
        }, self);

        this.mobilesurveys = ko.observableArray(
            params.mobilesurveys.map(function (mobilesurvey) {
                return new MobileSurveyModel({
                    source: mobilesurvey,
                    identities: params.identities
                });
            })
        );

        this.mobileSurveyFilter = ko.observable('');

        this.filteredMobileSurveys = ko.computed(function () {
            var filter = self.mobileSurveyFilter();
            var list = self.mobilesurveys();
            if (filter.length === 0) {
                return list;
            }
            return _.filter(list, function(mobilesurvey) {
                return mobilesurvey.name().toLowerCase().indexOf(filter.toLowerCase()) >= 0;
            });
        });

        this.loading = ko.observable(false);
        this.selectedMobileSurvey = ko.observable(null);

        this.selectedMobileSurvey.subscribe(function(val){
            if (val) {
                self.identityList.clearSelection();
                self.resourceList.clearSelection();
                self.resourceList.resetCards(val.cards());
                val.update();
            }
        });

    };
    return MobileSurveyManagerViewModel;
});
