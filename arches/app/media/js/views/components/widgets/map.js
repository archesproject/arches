define([
    'arches',
    'underscore',
    'knockout',
    'viewmodels/widget',
    'viewmodels/map-editor',
    'bindings/chosen',
    'bindings/codemirror',
    'codemirror/mode/javascript/javascript'
], function(arches, _, ko, WidgetViewModel, MapEditorViewModel) {
    var viewModel = function(params) {
        this.context = params.type;
        this.zoomConfigOpen = ko.observable(false);
        this.positionConfigOpen = ko.observable(false);
        this.geocoderConfigOpen = ko.observable(false);
        this.resourcePropertiesConfigOpen = ko.observable(false);
        this.defaultValueConfigOpen = ko.observable(false);
        this.geocodingProviders = arches.geocodingProviders;
        this.defaultValueOptions = [
            {
                "name": "",
                "defaultOptionid": 0,
                "value": ""
            },
            {
                "name": "Drawn Location",
                "defaultOptionid": 1,
                "value": "Drawn Location"
            },
            {
                "name": "Current Device Location",
                "defaultOptionid": 2,
                "value": "Current Device Location"
            }
        ];

        params.configKeys = [
            'zoom',
            'centerX',
            'centerY',
            'geocodeProvider',
            'basemap',
            'geometryTypes',
            'pitch',
            'bearing',
            'geocodePlaceholder',
            'geocoderVisible',
            'minZoom',
            'maxZoom',
            'featureColor',
            'featurePointSize',
            'featureLineWidth',
            'featureEditingDisabled',
            'overlayConfigs',
            'overlayOpacity',
            'mapControlsHidden',
            'defaultValueType',
            'defaultValue'
        ];

        WidgetViewModel.apply(this, [params]);

        if (!this.geocodeProvider()) {
            this.geocodeProvider(arches.geocoderDefault);
        }

        this.geocodeProviderDetails = ko.mapping.fromJS(_.findWhere(this.geocodingProviders, {
            'geocoderid': this.geocodeProvider()
        }));

        this.geocodeProvider.subscribe(function(geocoderid) {
            if (geocoderid) {
                var provider = _.findWhere(this.geocodingProviders, {
                    'geocoderid': geocoderid
                });
                this.geocodeProviderDetails.api_key(provider.api_key);
                this.geocodeProviderDetails.component(provider.component);
            }
        }, this);

        if (params.widget) params.widgets = [params.widget];

        MapEditorViewModel.apply(this, [params]);
    };
    ko.components.register('map-widget', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/widgets/map.htm'
        }
    });
    return viewModel;
});
