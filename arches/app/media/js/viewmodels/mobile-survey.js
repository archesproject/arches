define([
    'jquery',
    'arches',
    'underscore',
    'knockout',
    'views/mobile-survey-manager/identity-list',
    'models/mobile-survey',
    'views/components/widgets/map',
    'bindings/sortable'
], function($, arches, _, ko, IdentityList, MobileSurveyModel) {
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
        this.allResources = params.resources;
        this.allIdentities = params.identities;
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

        this.getRootCards = function(flatcards) {
            var allcards = ko.unwrap(flatcards);
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
            };
            getSubCardIds(allcards);
            rootCards = allcards.filter(function(card){
                var isRootCard = _.contains(subCardIds, card.cardid) === false;
                if (isRootCard) {
                    card.approved = ko.observable(_.contains(self.mobilesurvey.cards(), card.cardid));
                    card.approved.subscribe(function(val){
                        val === true ? self.mobilesurvey.cards.push(card.cardid) : self.mobilesurvey.cards.remove(card.cardid);
                    });
                }
                return isRootCard;
            });
            return ko.observableArray(rootCards);
        };

        this.updateResourceCards = function(resource){
            $.ajax({
                url: arches.urls.resource_cards.replace('//', '/' + resource.id + '/')
            })
                .done(function(data){
                    var rootCards = self.getRootCards(data.cards);
                    resource.cards(ko.unwrap(rootCards));
                });
        };

        this.navigateToManager = function() {
            window.location = arches.urls.mobile_survey;
        };

        this.initializeResource = function(r) {
            r.istopnode = false;
            r.childNodes = ko.observableArray([]);
            r.pageid = 'resourcemodel';
            r.selected = ko.observable(false);
            r.namelong = 'Model Details';
            r.description = 'Summary of how this model participates in the survey';
            r.cards = self.getRootCards(r.cards);
            r.added = ko.observable(r.cards().length > 0);
            r.hasApprovedCards = ko.pureComputed(function(){
                var result = r.cards().filter(function(c){return ko.unwrap(c.approved) === true;}).length > 0;
                if (result === false) {
                    self.mobilesurvey.datadownloadconfig.resources.remove(r.id);
                }
                return result;
            });
            r.added.subscribe(function(val){
                if (val === true && r.cards().length === 0) {
                    self.updateResourceCards(r);
                } else if (val === false) {
                    r.cards().forEach(function(c){
                        c.approved(false);
                    });
                }
            });
        };

        this.initializeIdentities = function(identity) {
            identity.istopnode = false;
            identity.childNodes = ko.observableArray([]);
            identity.pageid = 'identity';
            identity.namelong = identity.name;
            identity.iconclass = identity.type === 'group' ? 'fa fa-users' : 'fa fa-user';
            identity.description = 'Manage users that participate in this survey';
        };

        this.displayUser = ko.observable();

        this.resetCards = function(cards){
            _.each(self.allResources, function(r){
                _.each(r.cards(), function(c){
                    c.approved(_.contains(cards(), c.cardid));
                });
                r.hasApprovedCards() ? r.added(true) : r.added(false);
            });
        };

        this.resetIdentities = function(mobilesurvey){
            var groups = mobilesurvey.groups;
            var users = mobilesurvey.users;
            if (this.identityList.selected()) {
                this.identityList.selected().selected(false);
            }
            _.each(this.identityList.items(), function(item){
                var identitytype = item.type === 'user' ? users : groups;
                item.approved(_.contains(identitytype(), item.id));
            });
        };

        _.each(this.allResources, this.initializeResource);
        _.each(this.allIdentities, this.initializeIdentities);

        this.selectedResourceIds = ko.pureComputed({
            read: function() {
                return this.allResources.filter(function(r) {
                    if (r.added()) {
                        return r;
                    }
                }).map(function(rr){return rr.id;});
            },
            write: function(value) {
                _.each(this.allResources, function(r){
                    r.added(_.contains(value, r.id));
                });
            },
            owner: this
        });

        this.selectedResources = ko.pureComputed(function(){
            var resources = this.allResources.filter(function(r){
                if (r.added() || (r.cards().length > 0 && r.hasApprovedCards())) {
                    return r;
                }
            });
            return resources;
        }, this);

        this.selectedGroups = ko.pureComputed(function(){
            var ids = this.allIdentities.filter(function(id){
                if (ko.unwrap(id.approved) && id.type === 'group') {
                    return id;
                }
            });
            return ids;
        }, this);

        this.getSelect2ResourcesConfig = function(){
            return {
                clickBubble: true,
                disabled: false,
                data: {results: this.allResources.map(function(r){return {text: r.name, id: r.id};})},
                value: this.selectedResourceIds,
                multiple: true,
                placeholder: "select a model",
                allowClear: true
            };
        };

        this.getSelectedGroupIds = function(){
            return this.allIdentities.filter(function(id) {
                if (ko.unwrap(id.approved) && id.type === 'group') {
                    return id;
                }
            }).map(function(idobj){return String(idobj.id);});
        };

        this.selectAllGroupUsers = function() {
            if (self.selectedNode) {
                self.selectedNode().fullusers.forEach(function(user) {
                    if (user.approved() === false) {
                        user.approved(true);
                        self.mobilesurvey.toggleIdentity(user);
                    }
                });
            }
        };

        this.clearAllGroupUsers = function() {
            if (self.selectedNode) {
                self.selectedNode().fullusers.forEach(function(user) {
                    if (user.approved() === true) {
                        user.approved(false);
                        self.mobilesurvey.toggleIdentity(user);
                    }
                });
            }
        };

        this.selectedGroupsIds = ko.computed({
            read: function() {
                return this.getSelectedGroupIds();
            },
            write: function(value) {
                var longer;
                var shorter;
                var previousValue = this.getSelectedGroupIds();
                if (previousValue.length > value.length) {
                    longer = previousValue;
                    shorter = value;
                } else if (previousValue.length < value.length) {
                    longer = value;
                    shorter = previousValue;
                }
                var diff = _.difference(longer, shorter)[0];
                var group = _.find(this.allIdentities, function(id){
                    return (id.type === 'group' && Number(diff) === id.id);
                });
                group.approved(!group.approved());
                this.mobilesurvey.toggleIdentity(group);
            },
            owner: this,
            beforeChange: true
        });

        this.getSelect2GroupsConfig = function(){
            return {
                clickBubble: true,
                disabled: false,
                data: {results: this.allIdentities.filter(function(id){return id.type==='group';}).map(function(g){return {text: g.name, id: g.id};})},
                value: this.selectedGroupsIds,
                multiple: true,
                placeholder: "select a group",
                allowClear: true
            };
        };

        this.loading = ko.observable(false);

        this.surveyReady = ko.pureComputed(function(){
            var status = {
                cards: this.mobilesurvey.cards().length > 0,
                identities: this.mobilesurvey.users().length > 0 || this.mobilesurvey.groups().length > 0,
                daterange: !!this.mobilesurvey.startdate() && !!this.mobilesurvey.enddate(),
                mapsources: !!this.mobilesurvey.onlinebasemaps().default || !!this.mobilesurvey.tilecache(),
                bounds: this.mobilesurvey.bounds().features.length > 0,
            };
            status.incomplete =  [status.cards, status.identities, status.daterage, status.mapsources, status.bounds].includes(false);
            if (status.incomplete) {
                this.mobilesurvey.active(false);
            }
            return status;
        }, this);

        this.treenodes = [{
            name: this.mobilesurvey.name,
            namelong: 'Summary',
            description: 'Survey summary and status',
            id: 'root',
            selected: ko.observable(true),
            istopnode: true,
            iconclass: 'fa fa-globe',
            status: this.surveyReady,
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
                iconclass: 'fa fa-user-plus',
                pageactive: ko.observable(false),
                childNodes: this.selectedGroups,
                expanded: ko.observable(false)
            }
            ])
        }];

    };
    return MobileSurveyViewModel;
});
