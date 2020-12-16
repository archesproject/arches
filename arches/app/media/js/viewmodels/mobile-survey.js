define([
    'jquery',
    'arches',
    'underscore',
    'moment',
    'knockout',
    'views/mobile-survey-manager/identity-list',
    'models/mobile-survey',
    'views/components/widgets/map',
    'bindings/sortable'
], function($, arches, _, moment, ko, IdentityList, MobileSurveyModel) {
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
        this.transStrings = params.transstrings;

        this.basemap = _.filter(arches.mapLayers, function(layer) {
            return !layer.isoverlay;
        })[0];

        this.resizeMap = function() {
            setTimeout(
                function() {
                    window.dispatchEvent(new window.Event('resize'));
                }, 200);
        };

        this.context = params.context;

        if (this.context !== 'userprofile') {
            this.history = params.history;
            this.locked = _.keys(this.history.editors).length > 0 || false;
            this.history.lastsync = moment(this.history.lastsync);
            _.each(this.history.editors, function(editor) {
                editor.lastsync = moment(editor.lastsync);
            });
        }
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

        this.convertCountToInt = function() {
            var count = this.mobilesurvey.datadownloadconfig.count;
            count(parseInt(count()));
        };

        this.updateResourceCards = function(resource){
            $.ajax({
                url: arches.urls.resource_cards.replace('//', '/' + resource.id + '/')
            })
                .done(function(data){
                    var rootCards = self.getRootCards(data.cards);
                    rootCards.sort(function(a, b) {
                        return a.sortorder - b.sortorder;
                    })();
                    resource.cards(ko.unwrap(rootCards));
                });
        };

        this.navigateToManager = function() {
            window.location = arches.urls.collector_manager;
        };

        this.initializeResource = function(r) {
            r.istopnode = false;
            r.childNodes = ko.observableArray([]);
            r.pageid = 'resourcemodel';
            r.selected = ko.observable(false);
            r.namelong = arches.translations.mobileSurveyNameLong;
            r.description = arches.translations.mobileSurveyDesc;
            r.cards = self.getRootCards(r.cards);
            r.hasApprovedCards = ko.pureComputed(function(){
                var result = r.cards().filter(function(c){return ko.unwrap(c.approved) === true;}).length > 0;
                if (result === false) {
                    self.mobilesurvey.datadownloadconfig.resources.remove(r.id);
                } else if (_.contains(self.mobilesurvey.datadownloadconfig.resources(), r.id) === false) {
                    self.mobilesurvey.datadownloadconfig.resources.push(r.id);
                }
                return result;
            });
            r.added = ko.observable(r.hasApprovedCards());
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
            identity.description = self.transStrings.identity.description;
        };

        this.displayUser = ko.observable();

        this.resetCards = function(){
            var initialsurvey = this.mobilesurvey.getInitialSurvey();
            var initialcards = initialsurvey.cards;
            var initialresources = initialsurvey.datadownloadconfig.resources;
            _.each(self.allResources, function(r){
                _.each(r.cards(), function(c){
                    c.approved(_.contains(initialcards, c.cardid));
                });
                r.hasApprovedCards() ? r.added(true) : r.added(false);
            });
            self.mobilesurvey.datadownloadconfig.resources(initialresources);
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

        if (this.context != 'userprofile') {
            _.each(this.allIdentities, this.initializeIdentities);
        }

        this.resourceOrderedCards = ko.pureComputed(function(){
            var cards = [];
            self.allResources.forEach(function(r){
                r.cards()
                    .filter(function(f){if (f.approved()){return f;}})
                    .forEach(function(m){
                        cards.push(m.cardid);
                    });
            });
            return cards;
        });

        this.mobilesurvey.cards(this.resourceOrderedCards());

        this.resourceOrderedCards.subscribe(function(val){
            self.mobilesurvey.cards(val);
        });

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
                closeOnSelect: false,
                placeholder: this.transStrings.modelplaceholder,
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
                closeOnSelect: false,
                placeholder: this.transStrings.groupplaceholder,
                allowClear: true
            };
        };

        this.loading = ko.observable(false);

        this.surveyReady = ko.pureComputed(function(){
            var status = {
                cards: this.mobilesurvey.cards().length > 0,
                identities: this.mobilesurvey.users().length > 0 || this.mobilesurvey.groups().length > 0,
                daterange: !!this.mobilesurvey.startdate() && !!this.mobilesurvey.enddate(),
                unexpired: !!this.mobilesurvey.enddate() && ((moment(this.mobilesurvey.enddate()).add(1, 'days') - moment()) > 0),
                mapsources: !!this.mobilesurvey.onlinebasemaps().default || !!this.mobilesurvey.tilecache(),
                bounds: this.mobilesurvey.bounds().features.length > 0
            };
            status.incomplete =  [
                status.cards,
                status.identities,
                status.daterage,
                status.mapsources,
                status.bounds,
                status.unexpired
            ].includes(false);

            return status;
        }, this);

        this.surveyReady.subscribe(function(val){
            if (val.incomplete) {
                this.mobilesurvey.active(false);
            }
            //TODO: Switch the active status back to true if activatedOnServer is True
            // Currently this does not work properly because activatedOnServer() is not updating in time.
            //else if (!status.incomplete && this.mobilesurvey.activatedOnServer() === true) {
            //     this.mobilesurvey.active(true);
            // }
        }, this);

        if (this.context !== 'userprofile' ) {
            this.treenodes = [{
                name: this.mobilesurvey.name,
                namelong: this.transStrings.root.namelong,
                description: this.transStrings.root.description,
                id: 'root',
                selected: ko.observable(true),
                istopnode: true,
                iconclass: 'fa fa-globe',
                status: this.surveyReady,
                pageactive: ko.observable(true),
                expanded: ko.observable(true),
                childNodes: ko.observableArray([{
                    name: this.transStrings.settings.name,
                    namelong: this.transStrings.settings.namelong,
                    description: this.transStrings.settings.description,
                    id: 'settings',
                    selected: ko.observable(false),
                    istopnode: false,
                    iconclass: 'fa fa-wrench',
                    pageactive: ko.observable(false),
                    childNodes: ko.observableArray([]),
                    expanded: ko.observable(false)
                },
                {
                    name: this.transStrings.mapextent.name,
                    namelong: this.transStrings.mapextent.namelong,
                    description: this.transStrings.mapextent.description,
                    id: 'mapextent',
                    selected: ko.observable(false),
                    istopnode: false,
                    iconclass: 'fa fa-map-marker',
                    pageactive: ko.observable(false),
                    childNodes: ko.observableArray([]),
                    expanded: ko.observable(false)
                },
                {
                    name: this.transStrings.mapsources.name,
                    namelong: this.transStrings.mapsources.namelong,
                    description: this.transStrings.mapsources.description,
                    id: 'mapsources',
                    selected: ko.observable(false),
                    istopnode: false,
                    iconclass: 'fa fa-th',
                    pageactive: ko.observable(false),
                    childNodes: ko.observableArray([]),
                    expanded: ko.observable(false)
                },
                {
                    name: this.transStrings.models.name,
                    namelong: this.transStrings.models.namelong,
                    description: this.transStrings.models.description,
                    id: 'models',
                    selected: ko.observable(false),
                    istopnode: false,
                    iconclass: 'fa fa-bookmark',
                    pageactive: ko.observable(false),
                    childNodes: this.selectedResources,
                    expanded: ko.observable(true)
                },
                {
                    name: this.transStrings.data.name,
                    namelong: this.transStrings.data.namelong,
                    description: this.transStrings.data.description,
                    id: 'data',
                    selected: ko.observable(false),
                    istopnode: false,
                    iconclass: 'fa fa-bar-chart-o',
                    pageactive: ko.observable(false),
                    childNodes: ko.observableArray([]),
                    expanded: ko.observable(false)
                },
                {
                    name: this.transStrings.people.name,
                    namelong: this.transStrings.people.namelong,
                    description: this.transStrings.people.description,
                    id: 'people',
                    selected: ko.observable(false),
                    istopnode: false,
                    iconclass: 'fa fa-user-plus',
                    pageactive: ko.observable(false),
                    childNodes: this.selectedGroups,
                    expanded: ko.observable(true)
                }
                ])
            }];
        }
    };
    return MobileSurveyViewModel;
});
