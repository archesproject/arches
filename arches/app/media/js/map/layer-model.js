define([
    'underscore',
], function(_) {
    return function(config) {
        var layerModel = {
                layer: null,
                id: _.uniqueId('layer_'),
                icon: "",
                name: "",
                description: "",
                categories: [],
                onMap: false,
                iconColor: "#FFFFFF",
                infoContent: null,
                isArchesLayer: false
            };
        _.extend(layerModel, config);
        return layerModel;
    };
});