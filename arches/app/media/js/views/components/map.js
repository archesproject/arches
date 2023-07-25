define([
    'jquery',
    'underscore',
    'knockout',
    'viewmodels/map',
    'templates/views/components/map.htm',
    'bindings/mapbox-gl',
    'bindings/sortable',
    'utils/aria',
], function($, _, ko, MapViewModel, mapTemplate, ariaUtils) {
    ko.components.register('arches-map', {
        viewModel: MapViewModel,
        template: mapTemplate,
        toggleAriaExpanded: ariaUtils.toggleAriaExpanded,
    });
    return MapViewModel;
});
