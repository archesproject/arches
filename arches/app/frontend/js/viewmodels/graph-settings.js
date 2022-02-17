define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'bindings/color-picker',
    'viewmodels/alert-json',
    'arches',
    'bindings/chosen'
], function($, _, ko, koMapping, colorPicker, JsonErrorAlertViewModel, arches) {
    var GraphSettingsViewModel = function(params) {

        var self = this;

        self.resource_data = ko.observableArray([]);
        self.relatable_resources = ko.computed(function() {
            return _.each(self.resource_data(), function(resource) {
                resource.isRelatable = ko.observable(resource.is_relatable);
            });
        });

        self.designerViewModel = params.designerViewModel;
        self.graph = params.graph;
        self.graph.name.subscribe(function(val){
            self.graph.root.name(val);
            self.rootnode.name(val);
        });
        self.graph.root.datatype.subscribe(function(val){
            self.rootnode.datatype(val);
        });

        self.graphModel = params.graphModel;
        self.rootnode = self.graphModel.get('root');
        self.nodes = self.graphModel.get('nodes');

        self.nodeCount = ko.computed(function(){
            return self.nodes().length;
        });

        var ontologyClass = self.rootnode.ontologyclass;
        var ontologyClassFriendlyName = self.rootnode.ontologyclass_friendlyname;

        self.jsonData = ko.computed(function() {
            var relatableResourceIds = _.filter(self.resource_data(), function(resource){
                return resource.isRelatable();
            }).map(function(resource){
                return resource.id;
            });
            if (self.graph.ontology_id() === undefined) {
                self.graph.ontology_id(null);
            }
            self.graph.root.config = koMapping.toJS(self.rootnode.config);
            return JSON.stringify({
                graph: koMapping.toJS(self.graph),
                relatable_resource_ids: relatableResourceIds,
                ontology_class: ontologyClass(),
            });
        }).extend({deferred: true});

        self.jsonCache = ko.observable(self.jsonData());

        var dirty = ko.computed(function() {
            var dirty = self.jsonData() !== self.jsonCache();
            return dirty;
        });

        self.dirty = dirty;

        self.icon_data = ko.observableArray([]);
        self.iconFilter = params.iconFilter;
        self.icons = ko.computed(function() {
            return _.filter(self.icon_data(), function(icon) {
                return icon.name.indexOf(self.iconFilter()) >= 0;
            });
        });

        self.ontologies = params.ontologies;
        self.ontologyClass = ontologyClass;
        self.ontologyClassFriendlyName = ontologyClassFriendlyName;
        self.ontologyClasses = ko.computed(function() {
            return _.filter(params.ontologyClasses(), function(ontologyClass) {
                ontologyClass.display = ontologyClass.source;
                return ontologyClass.ontology_id === self.graph.ontology_id();
            });
        });

        self.save = function() {
            self.contentLoading(true);
            $.ajax({
                type: "POST",
                url: arches.urls.graph_settings(self.graph.graphid()),
                data: self.jsonData()})
                .done(function(response) {
                    self.jsonCache(self.jsonData());
                    self.rootnode._node(JSON.stringify(self.rootnode));
                })
                .fail(function(response) {
                    self.designerViewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                })
                .always(function(){
                    self.contentLoading(false);
                });
        };

        self.reset = function() {
            var graph = self.graph;
            var src = JSON.parse(self.jsonCache());
            ko.mapping.fromJS(src.graph, graph);
            self.ontologyClass(src.graph.root.ontologyclass);
            self.relatable_resources().forEach(function(resource) {
                if (_.contains(src.relatable_resource_ids, resource.id)){
                    resource.isRelatable(true);
                } else {
                    resource.isRelatable(false);
                }
            });
            self.jsonCache(self.jsonData());
            self.rootnode._node(JSON.stringify(self.rootnode));
            if (params.onReset && typeof params.onReset === 'function') {
                params.onReset();
            }
        };

    };
    return GraphSettingsViewModel;
});
