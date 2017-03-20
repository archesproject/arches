require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/graph/graph-page-view',
    'graph-settings-data',
    'bindings/color-picker'
], function($, _, ko, koMapping, PageView, data) {
    /**
    * prep data for models
    */
    var resourceJSON = JSON.stringify(data.resources);
    data.resources.forEach(function(resource) {
        resource.isRelatable = ko.observable(resource.is_relatable);
    });
    var srcJSON = JSON.stringify(data.graph);

    /**
    * setting up page view model
    */
    var graph = koMapping.fromJS(data.graph);
    var iconFilter = ko.observable('');
    var ontologyClass = ko.observable(data.node.ontologyclass);
    var jsonData = ko.computed(function() {
        var relatableResourceIds = _.filter(data.resources, function(resource){
            return resource.isRelatable();
        }).map(function(resource){
            return resource.id
        });
        if (graph.ontology_id() === undefined) {
            graph.ontology_id(null);
        }
        return JSON.stringify({
            graph: koMapping.toJS(graph),
            relatable_resource_ids: relatableResourceIds,
            ontology_class: ontologyClass()
        });
    });
    var jsonCache = ko.observable(jsonData());
    var dirty = ko.computed(function () {
        return jsonData() !== jsonCache();
    });
    var viewModel = {
        dirty: dirty,
        iconFilter: iconFilter,
        icons: ko.computed(function () {
            return _.filter(data.icons, function (icon) {
                return icon.name.indexOf(iconFilter()) >= 0;
            });
        }),
        graph: graph,
        relatable_resources: data.resources,
        ontologies: data.ontologies,
        ontologyClass: ontologyClass,
        ontologyClasses: ko.computed(function () {
            return _.filter(data.ontologyClasses, function (ontologyClass) {
                return ontologyClass.ontology_id === graph.ontology_id();
            });
        }),
        save: function () {
            pageView.viewModel.loading(true);
            $.ajax({
                type: "POST",
                url: '',
                data: jsonData(),
                success: function(response) {
                    jsonCache(jsonData());
                    pageView.viewModel.loading(false);
                },
                error: function(response) {
                    pageView.viewModel.loading(false);
                }
            });
        },
        reset: function () {
            _.each(JSON.parse(srcJSON), function(value, key) {
                graph[key](value);
            });
            JSON.parse(resourceJSON).forEach(function(jsonResource) {
                var resource = _.find(data.resources, function (resource) {
                    return resource.id === jsonResource.id;
                });
                resource.isRelatable(jsonResource.is_relatable);
            });
            jsonCache(jsonData());
        }
    };

    /**
    * a GraphPageView representing the graph settings page
    */
    var pageView = new PageView({
        viewModel: viewModel
    });
    var self = this;

    var updatePageViewGraph = function(pageView, prop){
      return function(e){
        var graph = _.findWhere(pageView.viewModel.allGraphs(), {graphid: pageView.viewModel.graphid()})
        graph[prop](e);
      }
    }
    viewModel.graph.name.subscribe(updatePageViewGraph(pageView, 'name'))
    viewModel.graph.iconclass.subscribe(updatePageViewGraph(pageView, 'iconclass'))
});
