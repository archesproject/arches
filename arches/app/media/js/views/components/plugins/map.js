define([
    'knockout',
    'templates/views/components/plugins/map.htm',
    'views/components/widgets/map',
], function(ko, mapPluginTemplate) {
    const viewModel = function() {
        this.configJSON = {
            "zoom": 0,
            "pitch": 0,
            "basemap": "streets",
            "bearing": 0,
            "centerX": 0,
            "centerY": 0,
            "maxZoom": 20,
            "minZoom": 0,
            "defaultValue": "",
            "featureColor": "#FF0000",
            "geometryTypes": [],
            "overlayConfigs": [],
            "overlayOpacity": 0,
            "geocodeProvider": "10000000-0000-0000-0000-010000000000",
            "geocoderVisible": true,
            "defaultValueType": "",
            "featureLineWidth": 1,
            "featurePointSize": 3,
            "geocodePlaceholder": "Search"
        };
    };

    return ko.components.register('map-plugin', {
        viewModel: viewModel,
        template: mapPluginTemplate,
    });
});
