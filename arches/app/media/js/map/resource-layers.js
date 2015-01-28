define([
        'openlayers',
        'underscore',
        'knockout',
        'arches',
        'resource-layer-info',
        'map/resource-layer-model'
], function(ol, _, ko, arches, resourceLayerInfo, ResourceLayerModel) {
        var resourceFeatures = ko.observableArray();
        var layers = [];

        _.each(resourceLayerInfo, function (item, entitytypeid) {
            item.entitytypeid = entitytypeid;
            layers.push(new ResourceLayerModel(item, function(features) {
                resourceFeatures(resourceFeatures().concat(features));
            }));
        });

        return {
            layers: layers,
            features: resourceFeatures
        };
});