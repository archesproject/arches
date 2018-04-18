define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'bindings/color-picker',
    'models/node',
    'arches',
    'bindings/chosen'
], function ($, _, ko, koMapping, colorPicker, NodeModel, arches) {
    var GraphSettingsViewModel = function(params) {

        var self = this;
        self.resource_data = ko.observableArray([]);
        self.relatable_resources = ko.computed(function () {
            return _.each(self.resource_data(), function (resource) {
                resource.isRelatable = ko.observable(resource.is_relatable);
            });
        })

        var resourceJSON = JSON.stringify(self.relatable_resources);
        var srcJSON = JSON.stringify(koMapping.toJS(params.graph));

        self.graph = params.graph;

        self.graph.ontology_id.subscribe(function(val){
            console.log(val);
        })

        var ontologyClass = params.node.ontologyclass;
        var topNode = _.filter(self.graph.nodes(), function(node) {
                        if (node.istopnode() === true) {
                            return node
                        }
                        })[0];

        var rootNodeColor = ko.observable('rgba(233,112,111,0.8)')
        if (_.has(ko.unwrap(topNode.config),'fillColor')) {
            rootNodeColor = ko.unwrap(topNode.config).fillColor
        } else {
            topNode.config = ko.observable({fillColor:rootNodeColor});
        }
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
            return self.jsonData() !== self.jsonCache();
        });

        self.rootNodeColor = rootNodeColor;
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
                var resource = _.find(self.resource_data, function (resource) {
                    return resource.id === jsonResource.id;
                });
                resource.isRelatable(jsonResource.is_relatable);
            });
            self.jsonCache(self.jsonData());
        };

    };
    return GraphSettingsViewModel;
});
