define([
    'underscore',
    'knockout',
    'models/abstract',
    'arches'
], function(_, ko, AbstractModel, arches) {
    return AbstractModel.extend({
        url: arches.urls.project,

        initialize: function(options) {
            var self = this;
            self.identities = options.identities || [];
            if (this.identities.items().length) {
                this.identities.items()[0].selected(true)
            }
            self._project = ko.observable('{}');
            self.name = ko.observable('');
            self.active = ko.observable(false);
            self.createdby = ko.observable(null);
            self.lasteditedby = ko.observable(null);
            self.users = ko.observableArray();
            self.groups = ko.observableArray();

            var getUserName = function(id) {
                var user = _.find(self.identities.items(), function(i) {
                    return i.type === 'user' && i.id === id;
                });
                return user ? user.name : '';
            };

            self.createdbyName = ko.computed(function () {
                return getUserName(self.createdby());
            });

            self.lasteditedbyName = ko.computed(function () {
                return getUserName(self.lasteditedby());
            });

            self.approvedUserNames = ko.computed(function(){
                names = [];
                _.each(self.identities.items(), function(identity){
                    if(identity.type === 'user' && identity.approved()){
                        names.push(identity.name);
                    }
                }, this);
                return names;
            })

            self.approvedGroupNames = ko.computed(function(){
                names = [];
                _.each(self.identities.items(), function(identity){
                    if(identity.type === 'group' && identity.approved()){
                        names.push(identity.name);
                    }
                }, this);
                return names;
            })

            self.userFilter = ko.observable('');

            self.filteredUsers = ko.computed(function () {
                var filter = self.userFilter();
                var list = self.identities.groupUsers();
                if (filter.length === 0) {
                    return list;
                }
                return _.filter(list, function(user) {
                    if (user.username.startsWith(filter)) {return user}
                });
            });

            self.hasIdentity = function(){
                var inGroups = false;
                var inUsers = false;
                var identity =  self.identities.selected();
                if (identity.type === 'user') {
                    var inUsers = _.contains(self.users(), identity.id)
                } else {
                    var inGroups = _.contains(self.groups(), identity.id)
                }
                return inUsers || inGroups
            };

            self.toggleIdentity = function() {
                var identity =  self.identities.selected();
                if (identity) {
                    var identities = identity.type === 'user' ? self.users : self.groups;
                    if (self.hasIdentity()) {
                        identities.remove(identity.id);
                        if (identity.type === 'user') {
                            var usersAcceptedGroups = _.intersection(identity.group_ids, self.groups());
                            if (usersAcceptedGroups.length > 0) {
                                console.log('User still accepted via:', usersAcceptedGroups) //TODO Indicate to user approved groups a user belongs to
                            } else {
                                identity.approved(false);
                            };
                        } else {
                            identity.approved(false);
                            _.chain(self.identities.items()).filter(function(id) {
                                return id.type === 'user'
                            }).each(function(user) {
                                if (_.contains(self.users(), user.id) === false && _.intersection(user.group_ids, self.groups()).length === 0) {
                                    user.approved(false);
                                }
                            })
                        } ;
                    } else {
                        identities.push(identity.id);
                        identity.approved(true);
                        _.chain(self.identities.items()).filter(function(id) {
                            return id.type === 'user'
                        }).each(function(user) {
                            if (_.intersection(user.group_ids, self.groups()).length > 0) {
                                user.approved(true);
                            }
                        })
                    };
                };
            };

            self.parse(options.source);

            self.json = ko.computed(function() {
                var jsObj = ko.toJS({
                    name: self.name,
                    active: self.active,
                    id: self.get('id'),
                    groups: self.groups,
                    users: self.users,
                })
                return JSON.stringify(_.extend(JSON.parse(self._project()), jsObj))
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._project() || !self.get('id');
            });
        },

        parse: function(source) {
            var self = this;
            self._project(JSON.stringify(source));
            self.name(source.name);
            self.active(source.active);
            self.createdby(source.createdby_id);
            self.lasteditedby(source.lasteditedby_id);
            self.groups(source.groups);
            self.users(source.users);

            self.set('id', source.id);
        },

        reset: function() {
            this.parse(JSON.parse(this._project()), self);
        },

        _getURL: function(method){
            return this.url;
        },

        save: function (userCallback, scope) {
            var self = this;
            var method = "POST";
            var callback = function (request, status, model) {
                if (typeof userCallback === 'function') {
                    userCallback.call(this, request, status, model);
                }
                if (status==='success') {
                    self.set('id', request.responseJSON.project.id);
                    self.createdby(request.responseJSON.project.createdby_id);
                    self.lasteditedby(request.responseJSON.project.lasteditedby_id);
                    self.groups(request.responseJSON.project.groups);
                    self.users(request.responseJSON.project.users);
                    this._project(this.json());
                };
            };
            this._doRequest({
                type: method,
                url: this._getURL(method),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'save');
        },

        toJSON: function() {
            return JSON.parse(this.json());
        },

        update: function() {
            this.identities.clearSelection();
            this.identities.items()[0].selected(true)
            var groups = ko.unwrap(this.groups)
            var users = ko.unwrap(this.users)
            _.each(this.identities.items(), function(item) {
                item.approved(false);
                if ((item.type === 'group' && _.contains(groups, item.id)) ||
                    (item.type === 'user' && _.contains(users, item.id)) ||
                    (item.type === 'user' && _.intersection(item.group_ids, groups).length)) {
                    item.approved(true);
                }
            })
        }
    });
});
