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
            self._project = ko.observable('{}');
            self.name = ko.observable('');
            self.description = ko.observable('');
            self.startdate = ko.observable(null);
            self.enddate = ko.observable(null);
            self.active = ko.observable(false);
            self.createdby = ko.observable(null);
            self.lasteditedby = ko.observable(null);
            self.users = ko.observableArray();
            self.groups = ko.observableArray();
            self.showDetails = ko.observable(false);

            var getUserName = function(id) {
                var user = _.find(self.identities, function(i) {
                    return i.type === 'user' && i.id === id;
                });
                return user ? user.name : '';
            };

            self.setIdentityApproval = function() {
                var groups = ko.unwrap(this.groups)
                var users = ko.unwrap(this.users)
                _.each(this.identities, function(item) {
                    item.approved(false);
                    if ((item.type === 'group' && _.contains(groups, item.id)) ||
                        (item.type === 'user' && _.contains(users, item.id))) {
                        item.approved(true);
                    }
                })
            };

            _.each(this.identities, function(item) {
                if (item.type === 'group') {
                    _.each(item.users, function(user){
                        if (!user.expanded) {
                            user.expanded = ko.observable(false);
                        }
                    })
                }
            })

            self.createdbyName = ko.computed(function() {
                return getUserName(self.createdby());
            });

            self.lasteditedbyName = ko.computed(function() {
                return getUserName(self.lasteditedby());
            });


            self.selectedIdentity = ko.computed(function() {
                var selected = _.filter(self.identities, function(identity) {
                    return ko.unwrap(identity.selected);
                });
                return selected.length > 0 ? selected[0] : undefined;
            });

            self.approvedUserNames = ko.computed(function() {
                names = [];
                _.each(self.identities, function(identity) {
                    if (identity.type === 'user' && identity.approved()) {
                        names.push(identity.name);
                    }
                }, this);
                return names;
            })

            self.approvedGroupNames = ko.computed(function() {
                names = [];
                _.each(self.identities, function(identity) {
                    if (identity.type === 'group' && identity.approved()) {
                        names.push(identity.name);
                    }
                }, this);
                return names;
            })

            self.userFilter = ko.observable('');

            self.filteredUsers = ko.computed(function() {
                var filter = self.userFilter();
                var selected = _.filter(self.identities, function(identity) {
                    return ko.unwrap(identity.selected);
                });
                var list = []
                if (selected.length === 1) {
                    list = selected[0].users;
                    if (filter.length === 0) {
                        return list;
                    }
                }
                return _.filter(list, function(user) {
                    if (user.username.startsWith(filter)) {
                        return user
                    }
                });
            });

            self.hasIdentity = function() {
                var approved = false;
                var identity = self.selectedIdentity();
                if (identity) {
                    approved = identity.approved()
                }
                return approved
            };

            self.toggleIdentity = function() {
                var identity = self.selectedIdentity();
                if (identity) {
                    var identities = identity.type === 'user' ? self.users : self.groups;
                    if (self.hasIdentity()) {
                        identities.remove(identity.id);
                        if (identity.type === 'user') {
                            identity.approved(false);
                        } else {
                            identity.approved(false);
                            _.chain(self.identities).filter(function(id) {
                                return id.type === 'user'
                            }).each(function(user) {
                                if (_.intersection(user.group_ids, self.groups()).length === 0) { // user does not belong to any accepted groups
                                    user.approved(false);
                                    self.users.remove(user.id);
                                }
                            })
                        };
                    } else {
                        identities.push(identity.id);
                        identity.approved(true);
                        _.chain(self.identities).filter(function(id) {
                            return id.type === 'user'
                        }).each(function(user) {
                            if (_.intersection(user.group_ids, self.groups()).length > 0) {
                                user.approved(true);
                                self.users.push(user.id);
                            }
                        })
                    };
                };
            };

            self.toggleShowDetails = function() {
                self.setIdentityApproval();
                self.showDetails(!self.showDetails())
            }

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
                });
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
            self.description(source.description);
            self.startdate(source.startdate);
            self.enddate(source.enddate);
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

        _getURL: function(method) {
            return this.url;
        },

        save: function(userCallback, scope) {
            var self = this;
            var method = "POST";
            var callback = function(request, status, model) {
                if (typeof userCallback === 'function') {
                    userCallback.call(this, request, status, model);
                }
                if (status === 'success') {
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
            this.setIdentityApproval();
        }
    });
});
