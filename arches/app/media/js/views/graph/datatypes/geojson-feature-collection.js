define([
    'arches',
    'knockout',
    'bindings/color-picker'
], function (arches, ko) {
    var name = 'geojson-feature-collection-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            this.layerActivated = params.config.layerActivated;
            this.mainColor = params.config.mainColor;
            this.haloColor = params.config.haloColor;
        },
        template: { require: 'text!datatype-config-templates/geojson-feature-collection' }
    });
    return name;
});
