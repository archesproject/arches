define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'bindings/leaflet-iiif'
], function (ko, _, WidgetViewModel) {
    return ko.components.register('iiif-widget', {
        viewModel: function(params) {
            params.configKeys = [];
            WidgetViewModel.apply(this, [params]);
        },
        template: { require: 'text!widget-templates/iiif' }
    });
});
