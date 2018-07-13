require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/graph/permission-manager/identity-list',
    'views/graph/permission-manager/permission-settings-form'
], function($, _, ko, koMapping, arches, IdentityList, PermissionSettingsForm, data) {
    var permIcons = {
        'no_access_to_nodegroup': 'ion-close',
        'read_nodegroup': 'ion-ios-book',
        'write_nodegroup': 'ion-edit',
        'delete_nodegroup': 'ion-android-delete'
    };

    var identityList = new IdentityList({
        items: ko.observableArray()
    });
    identityList.selectedItems.subscribe(function(item) {
        updatePermissions();
    });

    var groupedNodeList = {items: ko.observableArray()};

    $.ajax({
        url: arches.urls.permission_manager_data
    })
        .done(function(data) {
            data.identities.forEach(function(identity) {
                identity.permsLiteral = ' - ' + _.pluck(identity.default_permissions, 'name').join(', ');
            });
            identityList.items(data.identities);
            data.permissions.forEach(function(perm) {
                perm.icon = permIcons[perm.codename];
            });

            var permissionSettingsForm = new PermissionSettingsForm({
                identityList: identityList,
                selectedIdentities: identityList.selectedItems,
                selectedCards: ko.observableArray(),
                nodegroupPermissions: data.permissions
            });

            permissionSettingsForm.on('save', function() {
                updatePermissions();
            });
            permissionSettingsForm.on('revert', function() {
                updatePermissions();
            });

        })
        .fail(function(err) {
            console.log(err);
        });

    var updatePermissions = function() {
        var item = identityList.selectedItems()[0];
        var nodegroupIds = [];

        if (item) {
            groupedNodeList.items().forEach(function(item) {
                nodegroupIds.push(item.nodegroup);
            });
            $.ajax({
                type: 'GET',
                url: arches.urls.permission_data,
                data: {'nodegroupIds': JSON.stringify(nodegroupIds), 'identityType': item.type, 'identityId': item.id},
                success: function(res) {
                    res.forEach(function(nodegroup) {
                        var card = _.find(groupedNodeList.items(), function(card) {
                            return card.nodegroup === nodegroup.nodegroup_id;
                        });

                        if (nodegroup.perms.length === 0) {
                            nodegroup.perms = identityList.selectedItems()[0].default_permissions;
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
                },
                complete: function() {
                    // self.loading(false);
                }
            });
        }
    };


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
