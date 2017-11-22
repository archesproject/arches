define([
    'arches',
    'underscore',
    'knockout',
    'views/mobile-survey-manager/identity-list',
    'views/mobile-survey-manager/resource-list',
    'models/mobile-survey',
    'bindings/sortable'
], function(arches, _, ko, IdentityList, ResourceList, MobileSurveyModel) {
    /**
    * A base viewmodel for project management
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

        this.getProjectResources = function(project){
            var successCallback = function(data){
                project.collectedResources(true)
                _.each(data.resources, self.processResources)
                _.each(self.resourceList.items(), self.flattenCards)
            }
            if (!project.collectedResources()) {
                $.ajax({
                    url: arches.urls.mobile_survey_resources(project.id)
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

        this.projects = ko.observableArray(
            params.projects.map(function (project) {
                return new MobileSurveyModel({
                    source: project,
                    identities: params.identities
                });
            })
        );

        this.projectFilter = ko.observable('');
        this.filteredProjects = ko.computed(function () {
            var filter = self.projectFilter();
            var list = self.projects();
            if (filter.length === 0) {
                return list;
            }
            return _.filter(list, function(project) {
                return project.name().toLowerCase().indexOf(filter.toLowerCase()) >= 0;
            });
        });

        this.loading = ko.observable(false);
        this.selectedProject = ko.observable(null);

        this.selectedProject.subscribe(function(val){
            if (val) {
                self.identityList.clearSelection();
                self.identityList.items()[0].selected(true);
                self.resourceList.clearSelection();
                self.resourceList.items()[0].selected(true);
                self.resourceList.resetCards(val.cards());
                val.update();
            }
        });

    };
    return MobileSurveyManagerViewModel;
});
