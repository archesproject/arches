define([
    'jquery',
    'underscore',
    'knockout',
    'viewmodels/map',
    'templates/views/components/map.htm',
    'bindings/mapbox-gl',
    'bindings/sortable',
    'bindings/key-events-click',
], function($, _, ko, MapViewModel, mapTemplate) {
    ko.components.register('arches-map', {
        viewModel: MapViewModel,
        template: mapTemplate,
    });
    return MapViewModel;
});
