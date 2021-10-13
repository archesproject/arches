define([
    'underscore',
    'knockout',
    'knockout-mapping',
    'models/abstract',
    'arches'
], function(_, ko, koMapping, AbstractModel, arches) {
    return AbstractModel.extend({
        url: arches.urls.collector_designer,

        initialize: function(options) {
            var self = this;
            self.identities = options.identities || [];
            self._mobilesurvey = ko.observable('{}');
            self.name = ko.observable('');
            self.description = ko.observable('');
            self.startdate = ko.observable(null);
            self.enddate = ko.observable(null);
            self.active = ko.observable(false);
            self.activatedOnServer = ko.observable(options.source.active);
            self.createdby = ko.observable(null);
            self.lasteditedby = ko.observable(null);
            self.users = ko.observableArray([]);
            self.groups = ko.observableArray([]);
            self.showDetails = ko.observable(false);
            self.cards = ko.observableArray([]);
            self.datadownloadconfig = koMapping.fromJS(options.source.datadownloadconfig) || ko.observable();
            self.tilecache = ko.observable('');
            self.onlinebasemap = ko.observable(options.source.onlinebasemaps || ko.observable());
            self.bounds = ko.observable(self.getDefaultBounds(null));
            self.collectedResources = ko.observable(false);
            self.showCustomDataDownload = ko.observable(false);
            self.datadownloadconfig.resources.extend({ rateLimit: 50 });

            var getUserName = function(id) {
                var user = _.find(self.identities, function(i) {
                    return i.type === 'user' && i.id === id;
                });
                return user ? user.name : '';
            };

            self.setIdentityApproval = function() {
                var groups = ko.unwrap(this.groups);
                var users = ko.unwrap(this.users);
                _.each(this.identities, function(item) {
                    item.approved(false);
                    if ((item.type === 'group' && _.contains(groups, item.id)) ||
                        (item.type === 'user' && _.contains(users, item.id))) {
                        item.approved(true);
                    }
                });
            };

            self.selectedUser = ko.observable();

            _.each(this.identities, function(item) {
                item.filtered(false);
                if (item.type === 'group') {
                    item.fullusers = _.filter(self.identities, function(id) {
                        return (id.type === 'user' && _.contains(id.group_ids, item.id));
                    });
                    item.selected.subscribe(function(val){
                        if(val) {
                            self.selectedUser(item.fullusers[0]);
                        }
                    });
                }
            });

            self.createdbyName = ko.computed(function() {
                return getUserName(self.createdby());
            });

            self.lasteditedbyName = ko.computed(function() {
                return getUserName(self.lasteditedby());
            });

            self.onlinebasemaps = ko.computed(function(){
                var basemaps = {default: ko.unwrap(self.onlinebasemap)};
                return basemaps;
            });

            self.userFilter = ko.observable('');

            self.userFilter.subscribe(function(filter){
                _.each(self.identities, function(id) {
                    var regex = new RegExp(filter);
                    if (id.type && id.type === 'user' && regex.test(id.name)) {
                        id.filtered(false);
                    } else {
                        id.filtered(true);
                    }
                });
            });

            self.approvedUserNames = ko.computed(function() {
                var names = [];
                _.each(self.identities, function(identity) {
                    if (identity.type === 'user' && identity.approved()) {
                        names.push(identity.name);
                    }
                }, this);
                return names;
            });

            self.approvedGroupNames = ko.computed(function() {
                var names = [];
                _.each(self.identities, function(identity) {
                    if (identity.type === 'group' && identity.approved()) {
                        names.push(identity.name);
                    }
                }, this);
                return names;
            });

            self.hasIdentity = function(identity) {
                var approved = false;
                if (identity) {
                    approved = identity.approved();
                }
                return approved;
            };

            self.toggleIdentity = function(identity) {
                if (identity) {
                    var currentIdentities = identity.type === 'user' ? self.users : self.groups;
                    if (self.hasIdentity(identity) === false) {
                        currentIdentities.remove(identity.id);
                        if (identity.type === 'group') {
                            _.chain(self.identities).filter(function(id) {
                                return id.type === 'user' && _.contains(_.pluck(identity.users, 'id'), id.id);
                            }, this).each(function(user) {
                                if (_.intersection(user.group_ids, self.groups()).length === 0) { // user does not belong to any accepted groups
                                    user.approved(false);
                                    self.users.remove(user.id);
                                }
                            });
                        }
                    } else {
                        if (!_.contains(currentIdentities(), identity.id)) {
                            currentIdentities.push(identity.id);
                        }
                        identity.approved(true);
                        if (identity.type === 'group') {
                            _.chain(self.identities).filter(function(id) {
                                return id.type === 'user' && _.contains(_.pluck(identity.users, 'id'), id.id);
                            }, this).each(function(user) {
                                if (_.intersection(user.group_ids, self.groups()).length > 0) {
                                    user.approved(true);
                                    if (!_.contains(self.users(), user.id)) {
                                        self.users.push(user.id);
                                    }
                                }
                            });
                        }
                    }
                }
            };

            self.updateResourceDownloadList = function(val){
                if (_.contains(self.datadownloadconfig.resources(), val.id)) {
                    self.datadownloadconfig.resources.remove(val.id);
                } else {
                    self.datadownloadconfig.resources.push(val.id);
                }
            };

            self.updateCards = function(cards) {
                var approvedCards = _.chain(cards)
                    .filter(function(card){
                        if (card.approved()) {
                            return card.cardid;
                        }
                    })
                    .pluck('cardid').value();
                var diff = _.difference(self.cards(), approvedCards);
                self.cards(_.union(diff, approvedCards));
            };

            self.addAllCardsByResource = function(val) {
                var resource = val.resourceList.selected();
                _.each(resource.cards(), function(card){
                    card.approved(true);
                });
                self.updateCards(resource.cards());
            };

            self.removeAllCardsByResource = function(val) {
                var resource = val.resourceList.selected();
                _.each(resource.cards(), function(card){
                    card.approved(false);
                    self.cards.remove(card.cardid);
                });
            };

            self.toggleShowDetails = function() {
                //used in the profile manager
                self.setIdentityApproval();
                self.showDetails(!self.showDetails());
            };

            self.parse(options.source);
            self.setIdentityApproval();
            self.json = ko.computed(function() {
                var jsObj = ko.toJS({
                    name: self.name,
                    description: self.description,
                    startdate: self.startdate,
                    enddate: self.enddate,
                    active: self.active,
                    id: self.get('id'),
                    groups: self.groups,
                    users: self.users,
                    cards: self.cards,
                    bounds: self.bounds,
                    tilecache: self.tilecache,
                    onlinebasemaps: ko.unwrap(self.onlinebasemaps),
                    datadownloadconfig: koMapping.toJS(self.datadownloadconfig)
                });
                return JSON.stringify(_.extend(JSON.parse(self._mobilesurvey()), jsObj));
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._mobilesurvey() || !self.get('id');
            });
        },

        getDefaultBounds: function(geojson) {
            var result = geojson;
            if (!geojson) {
                var fc = {"type": "FeatureCollection", "features": []};
                var geomFactory = function(coords){
                    return { "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": coords
                        },
                        "properties": {}
                    };
                };
                //TODO: make the true project boundry available in the arches object rather than just the hexBinBounds
                //and use the true bounds here instead of the hexBinBounds.
                var extent = arches.hexBinBounds;
                var coords = [[
                    [extent[0], extent[1]],
                    [extent[2], extent[1]],
                    [extent[2], extent[3]],
                    [extent[0], extent[3]],
                    [extent[0], extent[1]]
                ]];
                fc.features.push(geomFactory(coords));
                result = fc;
            }
            return result;
        },

        parse: function(source) {
            var self = this;
            self._mobilesurvey(JSON.stringify(source));
            self.name(source.name);
            self.description(source.description);
            self.startdate(source.startdate);
            self.enddate(source.enddate);
            self.active(source.active);
            self.activatedOnServer(source.active);
            self.createdby(source.createdby_id);
            self.lasteditedby(source.lasteditedby_id);
            self.groups(source.groups);
            self.users(source.users);
            self.cards(source.cards);
            self.tilecache(source.tilecache);
            self.bounds(self.getDefaultBounds(source.bounds));
            self.onlinebasemap(source.onlinebasemaps ? source.onlinebasemaps['default'] : source.onlinebasemaps);
            self.set('id', source.id);
        },

        reset: function() {
            this.parse(JSON.parse(this._mobilesurvey()), self);
        },

        getInitialSurvey: function() {
            return JSON.parse(this._mobilesurvey());
        },

        _getURL: function(method) {
            return this.url(this.id);
        },

        save: function(userCallback, scope) {
            var self = this;
            var method = "POST";
            var callback = function(request, status, model) {
                if (typeof userCallback === 'function') {
                    userCallback.call(this, request, status, model);
                }
                if (status === 'success') {
                    self.set('id', request.responseJSON.mobile_survey.id);
                    self.createdby(request.responseJSON.mobile_survey.createdby_id);
                    self.lasteditedby(request.responseJSON.mobile_survey.lasteditedby_id);
                    self.groups(request.responseJSON.mobile_survey.groups);
                    self.users(request.responseJSON.mobile_survey.users);
                    self.cards(request.responseJSON.mobile_survey.cards);
                    self.tilecache(request.responseJSON.mobile_survey.tilecache);
                    self.bounds(self.getDefaultBounds(request.responseJSON.mobile_survey.bounds));
                    self.datadownloadconfig.download(request.responseJSON.mobile_survey.datadownloadconfig.download);
                    self.datadownloadconfig.count(request.responseJSON.mobile_survey.datadownloadconfig.count);
                    self.datadownloadconfig.resources(request.responseJSON.mobile_survey.datadownloadconfig.resources);
                    self.datadownloadconfig.custom(request.responseJSON.mobile_survey.datadownloadconfig.custom);
                    self.activatedOnServer(request.responseJSON.mobile_survey.active);
                    this._mobilesurvey(this.json());
                }
            };
            return this._doRequest({
                type: method,
                url: this._getURL(method),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'save');
        },

        toJSON: function() {
            return JSON.parse(this.json());
        },

        update: function() {
            this.setIdentityApproval();
        }
    });
});
