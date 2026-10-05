import $ from 'jquery';
import _ from 'underscore';
import Backbone from 'backbone';
import ko from 'knockout';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';

if (!ko.bindingHandlers.indeterminate) {
    ko.bindingHandlers.indeterminate = {
        update: function(element, valueAccessor) {
            element.indeterminate = !!ko.unwrap(valueAccessor());
        }
    };
}

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
        var self = this;
        this.selectedIdentities = options.selectedIdentities;
        this.identityList = options.identityList;
        this.selectedCards = options.selectedCards;
        this.permissionsByNodegroup = options.permissionsByNodegroup || ko.observable({});
        this.loading = options.loading || ko.observable(false);
        this.alert = options.alert || ko.observable();
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

        // starts unset so the "Select a Group/Account..." placeholder shows
        this.identityid = ko.observable();

        this.identityid.subscribe(function(val) {
            _.forEach(options.identityList.items(), function(item) {
                item.selected(item.combinedId === val);
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
            perm.indeterminate = ko.observable(false);
            perm.selected.subscribe(function() {
                perm.indeterminate(false);
            });
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
                    if (selected && this.noAccessPerm) {
                        this.noAccessPerm.selected(false);
                    }
                }, this);
            }
        }, this);

        this.nodegroupPermissions = ko.observableArray(options.nodegroupPermissions);

        this.canSubmit = ko.pureComputed(function() {
            return !self.loading() && self.selectedCards().length > 0 && self.selectedIdentities().length > 0;
        });

        this.selectedNodegroupIds = ko.pureComputed(function() {
            return self.selectedCards().map(function(card) {
                return card.nodegroupid || ko.unwrap(card.model.nodegroup_id);
            });
        });

        // reflect saved explicit perms whenever the identity, card selection or saved data changes
        ko.computed(function() {
            self.syncSelectedPermissions(self.selectedNodegroupIds(), self.permissionsByNodegroup());
        });
    },

    /**
    * Sets each checkbox from the saved explicit perms of the selected cards;
    * a checkbox is indeterminate when the selected cards disagree.
    */
    syncSelectedPermissions: function(nodegroupIds, permissionsByNodegroup) {
        var explicitSets = nodegroupIds.map(function(nodegroupId) {
            var data = permissionsByNodegroup[nodegroupId];
            return data ? _.pluck(data.explicit, 'codename') : [];
        });

        ko.ignoreDependencies(function() {
            this.nodegroupPermissions().forEach(function(perm) {
                var count = explicitSets.filter(function(codenames) {
                    return codenames.indexOf(perm.codename) !== -1;
                }).length;
                var allSelected = explicitSets.length > 0 && count === explicitSets.length;
                perm.selected(allSelected);
                perm.indeterminate(count > 0 && !allSelected);
            });
        }, this);
    },

    getIdentitiesPayload: function() {
        return this.selectedIdentities().map(function(identity) {
            return {
                type: identity.type,
                id: identity.id
            };
        });
    },

    getCardsPayload: function() {
        return this.selectedNodegroupIds().map(function(nodegroupid) {
            return { nodegroupid: nodegroupid };
        });
    },

    showError: function(response) {
        var json = (response && response.responseJSON) || {};
        this.alert(new AlertViewModel(
            'ep-alert-red',
            json.title || arches.translations.requestFailed.title,
            json.message || arches.translations.requestFailed.text,
            null,
            function(){}
        ));
    },

    showSuccess: function(translation) {
        this.alert(new AlertViewModel(
            'ep-alert-blue',
            translation.title,
            translation.text,
            null,
            function(){}
        ));
    },

    save: function() {
        var self = this;
        if (!this.canSubmit()) {
            return;
        }
        var postData = {
            'selectedIdentities': this.getIdentitiesPayload(),
            'selectedCards': this.getCardsPayload(),
            'selectedPermissions': _.filter(this.nodegroupPermissions(), function(perm) {
                return perm.selected();
            }).map(function(perm) {
                return {
                    codename: perm.codename
                };
            })
        };

        this.loading(true);
        $.ajax({
            type: 'POST',
            url: arches.urls.permission_data,
            data: JSON.stringify(postData)
        })
            .done(function() {
                self.showSuccess(arches.translations.graphDesignerPermissionsApplied);
                self.trigger('save');
            })
            .fail(function(response) {
                self.showError(response);
            })
            .always(function() {
                self.loading(false);
            });
    },

    revert: function() {
        var self = this;
        if (!this.canSubmit()) {
            return;
        }
        var confirm = arches.translations.graphDesignerPermissionsResetConfirm;
        this.alert(new AlertViewModel(
            'ep-alert-red',
            confirm.title,
            confirm.text,
            function(){},
            function() {
                self.reset();
            }
        ));
    },

    reset: function() {
        var self = this;
        var postData = {
            'selectedIdentities': this.getIdentitiesPayload(),
            'selectedCards': this.getCardsPayload()
        };

        this.loading(true);
        $.ajax({
            type: 'DELETE',
            url: arches.urls.permission_data,
            data: JSON.stringify(postData)
        })
            .done(function() {
                self.showSuccess(arches.translations.graphDesignerPermissionsReset);
                self.trigger('revert');
            })
            .fail(function(response) {
                self.showError(response);
            })
            .always(function() {
                self.loading(false);
            });
    }
});
export default PermissionSettingsForm;
