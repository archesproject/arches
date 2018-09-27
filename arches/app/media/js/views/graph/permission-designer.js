define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/graph/permission-manager/identity-list',
    'views/graph/permission-manager/permission-settings-form'
], function($, _, ko, koMapping, arches, IdentityList, PermissionSettingsForm, data) {
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

        self.identityList = new IdentityList({
            items: ko.observableArray()
        });
        self.identityList.selectedItems.subscribe(function(item) {
            self.updatePermissions();
        });
        self.showPermissionsForm = ko.observable(false);
        self.cardTree = params.cardTree;
        self.cardList = null;

        self.selectedCards = ko.pureComputed(function() {
            return self.cardTree.selection();
        });

        self.getPermissionManagerData = function() {
            self.cardList = self.cardTree.flattenTree(ko.unwrap(self.cardTree.topCards), []);
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
                        cardList: self.cardList
                    });

                    self.showPermissionsForm(true);

                    self.permissionSettingsForm.on('save', function() {
                        self.updatePermissions();
                    });
                    self.permissionSettingsForm.on('revert', function() {
                        self.updatePermissions();
                    });
                })
                .fail(function(err) {
                    console.log(err);
                });
        };

        this.updatePermissions = function() {
            var item = self.identityList.selectedItems()[0];
            var nodegroupIds = [];

            if (item) {
                self.cardList.forEach(function(item) {
                    nodegroupIds.push(item.model.nodegroup_id());
                });
                $.ajax({
                    type: 'GET',
                    url: arches.urls.permission_data,
                    data: {'nodegroupIds': JSON.stringify(nodegroupIds), 'identityType': item.type, 'identityId': item.id},
                    success: function(res) {
                        res.forEach(function(nodegroup) {
                            var card = _.find(self.cardList, function(card) {
                                return card.model.nodegroup_id() === nodegroup.nodegroup_id;
                            });

                            if (nodegroup.perms.length === 0) {
                                nodegroup.perms = self.identityList.selectedItems()[0].default_permissions;
                            }
                            nodegroup.perms.forEach(function(perm) {
                                perm.icon = permIcons[perm.codename];
                            });
                            card.perms(nodegroup.perms);
                            card.permsLiteral(' - ' + _.pluck(nodegroup.perms, 'name').join(', '));

                            if (card.type === 'card') {
                                if (card.children.length > 0) {
                                    card.children.forEach(function(child) {
                                        if (child.type === 'node') {
                                            child.perms(nodegroup.perms);
                                        }
                                    });
                                }
                            }
                        });
                    }
                });
            }
        };
    };

    return PermissionDesignerViewModel;
    /**
    * a GraphPageView representing the graph manager page
    */
    // var graphPageView = new GraphPageView({
    //     viewModel: {
    //         identityList: identityList,
    //         groupedNodeList: groupedNodeList,
    //         permissionSettingsForm: permissionSettingsForm
    //     }
    // });
});
