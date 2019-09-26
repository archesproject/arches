define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'viewmodels/map',
    'bindings/mapbox-gl',
    'bindings/sortable'
], function($, _, arches, ko, MapViewModel) {
    ko.components.register('arches-map', {
        viewModel: MapViewModel,
        template: {
            require: 'text!templates/views/components/map.htm'
        }
    });
    return MapViewModel;
});
