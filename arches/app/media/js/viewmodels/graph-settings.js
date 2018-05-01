define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'bindings/color-picker',
    'arches',
    'bindings/chosen'
], function ($, _, ko, koMapping, colorPicker, arches) {
    var GraphSettingsViewModel = function(params) {

        var self = this;
        var resourceJSON;

        self.resource_data = ko.observableArray([]);
        self.relatable_resources = ko.computed(function () {
            resourceJSON = JSON.stringify(self.resource_data());
            return _.each(self.resource_data(), function (resource) {
                resource.isRelatable = ko.observable(resource.is_relatable);
            });
        })

        var srcJSON = JSON.stringify(koMapping.toJS(params.graph));

        self.graph = params.graph;

        self.node = params.node
        self.graph.name.subscribe(function(val){
            self.node().name(val);
        })

        var ontologyClass = params.node().ontologyclass;

        self.jsonData = ko.computed(function() {
            var relatableResourceIds = _.filter(self.resource_data(), function(resource){
                return resource.isRelatable();
            }).map(function(resource){
                return resource.id
            });
            if (self.graph.ontology_id() === undefined) {
                self.graph.ontology_id(null);
            }
            return JSON.stringify({
                graph: koMapping.toJS(self.graph),
                relatable_resource_ids: relatableResourceIds,
                ontology_class: ontologyClass()
            });
        });
        self.jsonCache = ko.observable(self.jsonData());

        var dirty = ko.computed(function () {
            var dirty = self.jsonData() !== self.jsonCache();
            return dirty
        });

        self.dirty = dirty;

        self.icon_data = ko.observableArray([]);
        self.iconFilter = params.iconFilter;
        self.icons = ko.computed(function () {
            return _.filter(self.icon_data(), function (icon) {
                return icon.name.indexOf(self.iconFilter()) >= 0;
            });
        });

        self.ontologies = params.ontologies;
        self.ontologyClass = ontologyClass;
        self.ontologyClasses = ko.computed(function () {
            return _.filter(params.ontologyClasses(), function (ontologyClass) {
                ontologyClass.display = ontologyClass.source;
                return ontologyClass.ontology_id === self.graph.ontology_id();
            });
        });

        self.save = function () {
            self.contentLoading(true);
            $.ajax({
                type: "POST",
                url: arches.urls.new_graph_settings(self.graph.graphid()),
                data: self.jsonData()})
                .done(function(response) {
                    self.jsonCache(self.jsonData());
                    self.node()._node(JSON.stringify(self.node()))
                })
                .fail(function(response) {
                    console.log('there was an error saving the settings', response)
                })
                .always(function(){
                    self.contentLoading(false);
                })
        };

        self.reset = function () {
            var graph = self.graph;
            _.each(JSON.parse(srcJSON), function(value, key) {
                if (ko.isObservable(graph[key])) {
                    graph[key](value);
                };
            });
            JSON.parse(resourceJSON).forEach(function(jsonResource) {
                var resource = _.find(self.resource_data(), function (resource) {
                    return resource.id === jsonResource.id;
                });
                resource.isRelatable(jsonResource.is_relatable);
            });
            self.jsonCache(self.jsonData());
            self.node()._node(JSON.stringify(self.node()))
        };

    };
    return GraphSettingsViewModel;
});
