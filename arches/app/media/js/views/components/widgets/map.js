define([
    'arches',
    'underscore',
    'knockout',
    'knockout-mapping',
    'viewmodels/widget',
    'viewmodels/map-editor',
    'bindings/chosen',
    'bindings/codemirror',
    'select2',
    'bindings/select2v4',
    'bindings/fadeVisible',
    'bindings/mapbox-gl',
    'bindings/chosen',
    'bindings/color-picker',
    'geocoder-templates'
], function(arches, _, ko, koMapping, WidgetViewModel, MapEditorViewModel) {
    var viewModel = function(params) {
        this.context = params.type;

        this.summaryDetails = [];
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
            'basemap',
            'overlayConfigs',
            'zoom',
            'centerX',
            'centerY',
            'geometryTypes',
            'defaultValueType',
            'defaultValue'
        ];

        WidgetViewModel.apply(this, [params]);

        this.geometryTypeList = ko.computed({
            read: function() {
                var geometryTypes = this.geometryTypes() || [];
                return geometryTypes.map(function(type) {
                    return ko.unwrap(type.id);
                });
            },
            write: function(value) {
                this.geometryTypes(value.map(function(type) {
                    return {
                        id: type,
                        text: type
                    };
                }));
            },
            owner: this
        });

        this.displayValue = ko.computed(function() {
            var value = koMapping.toJS(this.value);
            if (!value || !value.features) {
                return 0;
            }
            return value.features.length;
        }, this);

        if (params.widget) {
            params.widgets = [params.widget];
        }

        if (ko.unwrap(this.value) !== null) {
            this.summaryDetails = koMapping.toJS(this.value).features || [];
        }

        if (this.centerX() == 0 && this.centerY() == 0 && this.zoom() == 0) {
            this.centerX(arches.mapDefaultX);
            this.centerY(arches.mapDefaultY);
            this.zoom(arches.mapDefaultZoom);
        }

        params.basemap = this.basemap;
        params.overlayConfigs = this.overlayConfigs;
        params.zoom = this.zoom;
        params.x = this.centerX;
        params.y = this.centerY;
        params.usePosition = true;
        params.inWidget = true;

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
