require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view', 
    'views/graph/permission-manager/identity-list',
    'views/graph/permission-manager/grouped-node-list',
    'views/graph/permission-manager/permission-settings-form',
    'permission-manager-data'
], function($, _, ko, arches, GraphPageView, IdentityList, GroupedNodeList, PermissionSettingsForm, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */

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
        item.perm = ko.observable();
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
                data: {'nodegroupIds': JSON.stringify(nodegroupIds), 'userOrGroupType': item.type, 'userOrGroupId': item.id},
                success: function(res){
                    //self.options(res.results);
                    console.log(res);
                    res.forEach(function(nodegroup){
                        var card = _.find(groupedNodeList.items(), function(card){
                            return card.nodegroup === nodegroup.nodegroup_id;
                        });
                        var perms = _.pluck(nodegroup.perms, 'name');
                        if (perms.length > 0){
                            card.perm(perms.join(', '));                        
                        }else{
                            card.perm('Default (' + identityList.selectedItems()[0].default_permissions_list + ')');
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
