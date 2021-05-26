define([
    'arches',
    'jquery',
    'knockout',
    'knockout-mapping',
    'leaflet',
    'views/components/workbench',
    'text!templates/views/components/iiif-popup.htm',
    'leaflet-iiif',
    'leaflet-fullscreen',
    'bindings/select2-query',
    'bindings/leaflet'
], function(arches, $, ko, koMapping, L, WorkbenchViewmodel, iiifPopup) {
    var Foo = function(params) {

    };
    ko.components.register('foo', {
        viewModel: Foo,
        template: '<div></div>'
    });
    return Foo;
});
