define([
    'jquery',
    'underscore',
    'backbone',
    'knockout',
    'arches',
], function($, _, Backbone, ko, arches) {
    var PermissionSettingsForm = Backbone.View.extend({
        /**
        * A backbone view representing a card component form
        * @augments Backbone.View
        * @constructor
        * @name PermissionSettingsForm
        */

        /**
        * Initializes the view with optional parameters
        * @memberof PermissionSettingsForm.prototype
        * @param {boolean} options.selection - the selected item, either a {@link CardModel} or a {@link NodeModel}
        */
        initialize: function(options) {
            this.selectedIdentities = options.selectedIdentities;
            this.identityList = options.identityList;
            this.selectedCards = options.selectedCards;
            this.noAccessPerm = undefined;
            this.whiteListPerms = [];
            this.groupedNodeList = options.groupedNodeList;

            this.groups = ko.utils.arrayFilter(this.identityList.items(), function(identity) {
                return identity.type === 'group';
            });

            this.groups = _.forEach(this.groups, function(group) {
                group.combinedId = 'group-' + group.id;
            });

            this.users = ko.utils.arrayFilter(this.identityList.items(), function(identity) {
                return identity.type === 'user';
            });

            this.users = _.forEach(this.users, function(user) {
                user.combinedId = 'user-' + user.id;
            });

            this.identityid = ko.observable(this.groups[0]);

            this.identityid.subscribe(function(val) {
                _.forEach(options.identityList.items(), function(item) {
                    if (item.combinedId != val) {
                        item.selected(false);
                    }
                    else {
                        item.selected(true);
                    }
                });
            });

            this.groupedIdentities = ko.observable({
                groups: [
                    { name: 'Groups', items: this.groups },
                    { name: 'Accounts', items: this.users }
                ]
            });

            options.nodegroupPermissions.forEach(function(perm) {
                perm.selected = ko.observable(false);
                if (perm.codename === 'no_access_to_nodegroup') {
                    this.noAccessPerm = perm;
                    perm.selected.subscribe(function(selected) {
                        if (selected) {
                            this.whiteListPerms.forEach(function(perm) {
                                perm.selected(false);
                            }, this);
                        }
                    }, this);
                } else {
                    this.whiteListPerms.push(perm);
                    perm.selected.subscribe(function(selected) {
                        if (selected) {
                            this.noAccessPerm.selected(false);
                        }
                    }, this);
                }
            }, this);

            this.nodegroupPermissions = ko.observableArray(options.nodegroupPermissions);
        },

        save: function() {
            var self = this;
            var postData = {
                'selectedIdentities': this.selectedIdentities().map(function(identity) {
                    return {
                        type: identity.type,
                        id: identity.id
                    };
                }),
                'selectedCards': this.selectedCards().map(function(card) {
                    return {
                        nodegroupid: card.nodegroupid
                    };
                }),
                'selectedPermissions': _.filter(this.nodegroupPermissions(), function(perm) {
                    return perm.selected();
                }).map(function(perm) {
                    return {
                        codename: perm.codename
                    };
                })
            };

            $.ajax({
                type: 'POST',
                url: arches.urls.permission_data,
                data: JSON.stringify(postData),
                success: function(res) {
                    self.trigger('save');
                    self.clearUserPermissionCache();
                }
            });
        },

        revert: function() {
            var self = this;
            var postData = {
                'selectedIdentities': this.selectedIdentities(),
                'selectedCards': this.selectedCards()
            };

            $.ajax({
                type: 'DELETE',
                url: arches.urls.permission_data,
                data: JSON.stringify(postData),
                success: function(res) {
                    self.clearUserPermissionCache();
                    self.trigger('revert');
                }
            });
        },

        clearUserPermissionCache: function() {
            return $.ajax({
                type: 'POST',
                url: arches.urls.clear_user_permission_cache,
            });
        }
    });
    return PermissionSettingsForm;
});
