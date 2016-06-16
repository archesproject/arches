require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/graph-page-view',
    'graph-settings-data'
], function($, _, ko, koMapping, PageView, data) {
    /**
    * prep data for models
    */
    var resourceJSON = JSON.stringify(data.resources);
    data.resources.forEach(function(resource) {
        resource.isRelatable = ko.observable(resource.is_relatable);
    });
    var srcJSON = JSON.stringify(data.metadata);

    /**
    * setting up page view model
    */
    var metadata = koMapping.fromJS(data.metadata);
    var iconFilter = ko.observable('');
    var ontologyClass = ko.observable(data.node.ontologyclass);
    var jsonData = ko.computed(function() {
        var relatableResourceIds = _.filter(data.resources, function(resource){
            return resource.isRelatable();
        }).map(function(resource){
            return resource.id
        });
        if (metadata.ontology_id() === undefined) {
            metadata.ontology_id(null);
        }
        return JSON.stringify({
            metadata: koMapping.toJS(metadata),
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
        metadata: metadata,
        resources: data.resources,
        ontologies: data.ontologies,
        ontologyClass: ontologyClass,
        ontologyClasses: ko.computed(function () {
            return _.filter(data.ontologyClasses, function (ontologyClass) {
                return ontologyClass.ontology_id === metadata.ontology_id();
            });
        }),
        isResource: ko.computed({
            read: function() {
                return metadata.isresource().toString();
            },
            write: function(value) {
                metadata.isresource(value === "true");
            }
        }),
        isActive: ko.computed({
            read: function() {
                return metadata.isactive().toString();
            },
            write: function(value) {
                metadata.isactive(value === "true");
            }
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
                failure: function(response) {
                    pageView.viewModel.loading(false);
                }
            });
        },
        reset: function () {
            _.each(JSON.parse(srcJSON), function(value, key) {
                metadata[key](value);
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
});
