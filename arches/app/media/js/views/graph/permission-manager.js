require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view', 
    'views/graph/permission-manager/users-and-groups-list',
    'views/graph/permission-manager/grouped-node-list',
    'views/graph/permission-manager/permission-settings-form',
    'permission-manager-data'
], function($, _, ko, arches, GraphPageView, UsersAndGroupsList, GroupedNodeList, PermissionSettingsForm, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */

    var usersAndGroupsList = new UsersAndGroupsList({
        items: ko.observableArray(data.usersAndGroups)
    })
    usersAndGroupsList.selectedItems.subscribe(function(item){
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
        selectedUsersAndGroups: usersAndGroupsList.selectedItems,
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
        var item = usersAndGroupsList.selectedItems()[0];
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
                    res.perms.forEach(function(nodegroup){
                        var card = _.find(groupedNodeList.items(), function(card){
                            return card.nodegroup === nodegroup.nodegroup_id;
                        });
                        var perms = _.pluck(nodegroup.perms.local, 'name');
                        card.perm(perms.join(', '));                        
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
            usersAndGroupsList: usersAndGroupsList,
            groupedNodeList: groupedNodeList,
            permissionSettingsForm: permissionSettingsForm
        }
    });

});
