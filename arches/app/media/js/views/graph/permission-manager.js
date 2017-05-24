require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/graph/graph-page-view', 
    'views/graph/permission-manager/users-and-groups-list',
    'permission-manager-data'
], function($, _, ko, arches, GraphPageView, UsersAndGroupsList, data) {
    /**
    * set up the page view model with the graph model and related sub views
    */

    var viewModel = {
        usersAndGroupsList: new UsersAndGroupsList({
            items: ko.observableArray(data.usersAndGroups)
        })
    };
  
    /**
    * a GraphPageView representing the graph manager page
    */
    var graphPageView = new GraphPageView({
        viewModel: viewModel
    });

});
