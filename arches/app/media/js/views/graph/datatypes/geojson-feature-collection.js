define([
    'arches',
    'knockout',
    'bindings/color-picker'
], function (arches, ko) {
    var name = 'geojson-feature-collection-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            this.node = params;
            this.layer = params.layer;
            this.layerActivated = params.config.layerActivated;
            this.pointColor = params.config.pointColor;
            this.pointHaloColor = params.config.pointHaloColor;
            this.radius = params.config.radius;
            this.haloRadius = params.config.haloRadius;
            this.lineColor = params.config.lineColor;
            this.lineHaloColor = params.config.lineHaloColor;
            this.weight = params.config.weight;
            this.haloWeight = params.config.haloWeight;
            this.fillColor = params.config.fillColor;
            this.outlineColor = params.config.outlineColor;
            this.outlineWeight = params.config.outlineWeight;
            this.serviceURL = window.location.origin +
                arches.urls.tileserver +
                '/' + params.nodeid +
                '/{z}/{x}/{y}.pbf';
        },
        template: { require: 'text!datatype-config-templates/geojson-feature-collection' }
    });
    return name;
});
