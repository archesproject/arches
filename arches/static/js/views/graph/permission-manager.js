require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'views/graph/graph-page-view',
    'views/graph/permission-manager/identity-list',
    'views/graph/permission-manager/grouped-node-list',
    'views/graph/permission-manager/permission-settings-form',
    'permission-manager-data'
], function($, _, ko, koMapping, arches, GraphPageView, IdentityList, GroupedNodeList, PermissionSettingsForm, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */

    var perm_icons = {
        'no_access_to_nodegroup': 'ion-close',
        'read_nodegroup': 'ion-ios-book',
        'write_nodegroup': 'ion-edit',
        'delete_nodegroup': 'ion-android-delete'
    }

    data.identities.forEach(function(identity){
        identity.permsLiteral = ' - ' + _.pluck(identity.default_permissions, 'name').join(', ');
    });
    var identityList = new IdentityList({
        items: ko.observableArray(data.identities)
    })
    identityList.selectedItems.subscribe(function(item){
        updatePermissions();
    })


    var groupedNodeList = new GroupedNodeList({
        cards: data.cards,
        datatypes: data.datatypes
    })
    groupedNodeList.items().forEach(function(item){
        item.perms = ko.observableArray();
        item.permsLiteral = ko.observable('');
        item.children.forEach(function(child){
            child.perms = ko.observableArray();
            child.permsLiteral = ko.observable('');
        });
    });

    data.nodegroupPermissions.forEach(function(perm){
        perm.icon = perm_icons[perm.codename];
    });

    var permissionSettingsForm = new PermissionSettingsForm({
        selectedIdentities: identityList.selectedItems,
        selectedCards: groupedNodeList.selectedItems,
        nodegroupPermissions: data.nodegroupPermissions
    })
    permissionSettingsForm.on('save', function(){
        updatePermissions();
    });
    permissionSettingsForm.on('revert', function(){
        updatePermissions();
    })


    var updatePermissions = function(){
        var item = identityList.selectedItems()[0];
        var nodegroupIds = [];

        if(item){
            groupedNodeList.items().forEach(function(item){
                nodegroupIds.push(item.nodegroup);
            });
            $.ajax({
                type: 'GET',
                url: arches.urls.permission_data,
                data: {'nodegroupIds': JSON.stringify(nodegroupIds), 'identityType': item.type, 'identityId': item.id},
                success: function(res){
                    res.forEach(function(nodegroup){
                        var card = _.find(groupedNodeList.items(), function(card){
                            return card.nodegroup === nodegroup.nodegroup_id;
                        });

                        if (nodegroup.perms.length === 0){
                            nodegroup.perms = identityList.selectedItems()[0].default_permissions;
                        }
                        nodegroup.perms.forEach(function(perm){
                            perm.icon = perm_icons[perm.codename];
                        });
                        card.perms(nodegroup.perms);
                        card.permsLiteral(' - ' + _.pluck(nodegroup.perms, 'name').join(', '));

                        if (card.type === 'card') {
                            if (card.children.length > 0) {
                                card.children.forEach(function(child){
                                    if (child.type === 'node') {
                                        child.perms(nodegroup.perms);
                                    }
                                })
                            }
                        }
                    })
                },
                complete: function () {
                    //self.loading(false);
                }
            });
        }

    }

    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: {
            identityList: identityList,
            groupedNodeList: groupedNodeList,
            permissionSettingsForm: permissionSettingsForm
        }
    });

});
