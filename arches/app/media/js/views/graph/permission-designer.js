import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';
import IdentityList from 'views/graph/permission-manager/identity-list';
import PermissionSettingsForm from 'views/graph/permission-manager/permission-settings-form';


    /**
    * A viewmodel for managing nodegroup permissions
    *
    * @constructor
    * @name PermissionDesignerViewModel
    *
    * @param  {string} params - a configuration object
    */

    var PermissionDesignerViewModel = function(params) {
        var self = this;
        var permIcons = {
            'no_access_to_nodegroup': 'ion-close',
            'read_nodegroup': 'ion-ios-book',
            'write_nodegroup': 'ion-edit',
            'delete_nodegroup': 'ion-android-delete'
        };

        self.alert = params.alert || ko.observable();
        self.identityList = new IdentityList({
            items: ko.observableArray()
        });
        var currentIdentity;
        self.identityList.selectedItems.subscribe(function(items) {
            if (items[0] !== currentIdentity) {
                currentIdentity = items[0];
                self.updatePermissions();
            }
        });
        var requestCount = 0;
        self.showPermissionsForm = ko.observable(false);
        self.loading = ko.observable(false);
        self.cardTree = params.cardTree;
        self.cardList = null;
        // nodegroup_id -> {explicit, effective, source} for the selected identity
        self.permissionsByNodegroup = ko.observable({});

        self.selectedCards = ko.pureComputed(function() {
            return self.cardTree.selection();
        });

        var showError = function(responseJSON, fallback) {
            var json = responseJSON || {};
            self.alert(new AlertViewModel(
                'ep-alert-red',
                json.title || fallback.title,
                json.message || fallback.text,
                null,
                function(){}
            ));
        };

        var describeSource = function(source) {
            if (!source || source === 'default') {
                return arches.translations.permissionsSourceDefault;
            }
            if (source.indexOf('group:') === 0) {
                return arches.translations.permissionsSourceGroup + ' ' + source.slice('group:'.length);
            }
            return arches.translations.permissionsSourceExplicit;
        };

        self.getPermissionManagerData = function() {
            self.cardList = self.cardTree.flattenTree(ko.unwrap(self.cardTree.topCards), []);
            self.loading(true);
            $.ajax({
                url: arches.urls.permission_manager_data
            })
                .done(function(data) {
                    data.identities.forEach(function(identity) {
                        identity.permsLiteral = ' - ' + _.pluck(identity.default_permissions, 'name').join(', ');
                    });
                    self.identityList.items(data.identities);
                    data.permissions.forEach(function(perm) {
                        perm.icon = permIcons[perm.codename];
                    });

                    self.permissionSettingsForm = new PermissionSettingsForm({
                        identityList: self.identityList,
                        selectedIdentities: self.identityList.selectedItems,
                        selectedCards: self.selectedCards,
                        nodegroupPermissions: data.permissions,
                        cardList: self.cardList,
                        permissionsByNodegroup: self.permissionsByNodegroup,
                        loading: self.loading,
                        alert: self.alert
                    });

                    self.showPermissionsForm(true);

                    self.permissionSettingsForm.on('save', function() {
                        self.updatePermissions();
                    });
                    self.permissionSettingsForm.on('revert', function() {
                        self.updatePermissions();
                    });
                })
                .fail(function(response) {
                    showError(response.responseJSON, arches.translations.graphDesignerPermissionsLoadError);
                })
                .always(function() {
                    self.loading(false);
                });
        };

        var setCardPerms = function(card, perms, literal) {
            card.perms(perms);
            card.permsLiteral(literal);
            if (card.type === 'card' && card.children && card.children.length > 0) {
                card.children.forEach(function(child) {
                    if (child.type === 'node' && child.perms) {
                        child.perms(perms);
                    }
                });
            }
        };

        this.updatePermissions = function() {
            var identity = self.identityList.selectedItems()[0];

            if (!identity || !self.cardList) {
                requestCount++;
                self.loading(false);
                self.permissionsByNodegroup({});
                (self.cardList || []).forEach(function(card) {
                    setCardPerms(card, [], '');
                });
                return;
            }

            var nodegroupIds = self.cardList.map(function(card) {
                return card.model.nodegroup_id();
            });

            var request = ++requestCount;
            self.permissionsByNodegroup({});
            self.loading(true);
            $.ajax({
                type: 'GET',
                url: arches.urls.permission_data,
                data: {'nodegroupIds': JSON.stringify(nodegroupIds), 'identityType': identity.type, 'identityId': identity.id}
            })
                .done(function(res) {
                    // ignore responses superseded by a later identity selection
                    if (request !== requestCount) {
                        return;
                    }
                    var byNodegroup = {};
                    res.forEach(function(nodegroup) {
                        byNodegroup[nodegroup.nodegroup_id] = nodegroup;
                        var card = _.find(self.cardList, function(card) {
                            return card.model.nodegroup_id() === nodegroup.nodegroup_id;
                        });
                        if (!card) {
                            return;
                        }

                        var inherited = nodegroup.explicit.length === 0;
                        var sourceLabel = describeSource(nodegroup.source);
                        var perms = nodegroup.effective.map(function(perm) {
                            return {
                                codename: perm.codename,
                                name: perm.name,
                                icon: permIcons[perm.codename],
                                inherited: inherited,
                                title: perm.name + ' (' + sourceLabel + ')'
                            };
                        });
                        var literal = ' - ' + _.pluck(perms, 'name').join(', ') + ' (' + sourceLabel + ')';
                        setCardPerms(card, perms, literal);
                    });
                    self.permissionsByNodegroup(byNodegroup);
                })
                .fail(function(response) {
                    if (request === requestCount) {
                        showError(response.responseJSON, arches.translations.graphDesignerPermissionsLoadError);
                    }
                })
                .always(function() {
                    if (request === requestCount) {
                        self.loading(false);
                    }
                });
        };
    };

    export default PermissionDesignerViewModel;
