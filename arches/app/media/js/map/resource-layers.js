define([
        'openlayers',
        'underscore',
        'knockout',
        'arches',
        'layer-info',
        'map/resource-layer-model'
], function(ol, _, ko, arches, layerInfo, ResourceLayerModel) {
        var resourceFeatures = ko.observableArray();
        var layers = [];

        _.each(layerInfo, function (item, entitytypeid) {
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