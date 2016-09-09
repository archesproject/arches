require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/graph/graph-page-view',
    'form-settings-data'
], function($, _, ko, koMapping, PageView, data) {
    /**
    * prep data for models
    */
    // var srcJSON = JSON.stringify(data.form);

    /**
    * setting up page view model
    */
    // var srcJSON = JSON.stringify(data.form);

    /**
    * setting up page view model
    */
    var iconFilter = {}//ko.observable('');
    // var jsonData = ko.computed(function() {
    //     var relatableResourceIds = _.filter(data.resources, function(resource){
    //         return resource.isRelatable();
    //     }).map(function(resource){
    //         return resource.id
    //     });
    //     // if (graph.ontology_id() === undefined) {
    //     //     graph.ontology_id(null);
    //     // }
    //     return JSON.stringify({
    //         // graph: koMapping.toJS(graph),
    //         relatable_resource_ids: relatableResourceIds,
    //         ontology_class: ontologyClass()
    //     });
    // });
    // var jsonCache = ko.observable(jsonData());
    // var dirty = ko.computed(function () {
    //     return jsonData() !== jsonCache();
    // });
    var viewModel = {
        // dirty: dirty,
        iconFilter: iconFilter,
        icons: [1,2]
    };

    /**
    * a GraphPageView representing the graph settings page
    */
    // var pageView = new PageView({
    //     viewModel: viewModel
    // });
});
