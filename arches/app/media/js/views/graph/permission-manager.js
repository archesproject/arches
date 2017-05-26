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

    var groupedNodeList = new GroupedNodeList({
        cards: data.cards,
        datatypes: data.datatypes
    })
    
    var permissionSettingsForm = new PermissionSettingsForm({
        selectedUsersAndGroups: usersAndGroupsList.selectedItems,
        selectedCards: groupedNodeList.selectedItems,
        nodegroupPermissions: data.nodegroupPermissions
    })
  
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
