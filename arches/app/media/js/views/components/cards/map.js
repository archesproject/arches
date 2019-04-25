define([
    'arches',
    'knockout',
    'viewmodels/card-component'
], function(arches, ko, CardComponentViewModel) {
    return ko.components.register('map-card', {
        viewModel: function(params) {
            var layers = [];
            arches.mapLayers.forEach(function(layer) {
                if (layer.addtomap) {
                    layers = layers.concat(layer.layer_definitions);
                }
            });
            this.mapStyle = {
                "version": 8,
                "sources": arches.mapSources,
                "sprite": arches.mapboxSprites,
                "glyphs": arches.mapboxGlyphs,
                "layers": layers
            };
            this.activeTab = ko.observable();

            CardComponentViewModel.apply(this, [params]);
        },
        template: {
            require: 'text!templates/views/components/cards/map.htm'
        }
    });
});
