require([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'views/graph-page-view',
    'graph-settings-data'
], function($, _, ko, koMapping, PageView, data) {
    var resourceJSON = JSON.stringify(data.resources);
    data.resources.forEach(function(resource) {
        resource.isRelatable = ko.observable(resource.is_relatable);
    });
    var srcJSON = JSON.stringify(data.metadata);
    var metadata = koMapping.fromJS(data.metadata);
    var iconFilter = ko.observable('');
    var viewModel = {
        iconFilter: iconFilter,
        icons: ko.computed(function () {
            return _.filter(data.icons, function (icon) {
                return icon.name.indexOf(iconFilter()) >= 0;
            });
        }),
        metadata: metadata,
        resources: data.resources,
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
            var relatableResourceIds = _.filter(data.resources, function(resource){
                return resource.isRelatable();
            }).map(function(resource){
                return resource.id
            })
            $.ajax({
                type: "POST",
                url: '',
                data: JSON.stringify({
                    metadata: koMapping.toJS(metadata),
                    relatable_resource_ids: relatableResourceIds
                }),
                success: function(response) {
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
        }
    };

    var pageView = new PageView({
        viewModel: viewModel
    });
});
