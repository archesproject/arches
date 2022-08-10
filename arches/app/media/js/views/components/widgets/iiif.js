define([
    'underscore',
    'leaflet',
    'knockout',
    'knockout-mapping',
    'viewmodels/widget',
    'views/components/iiif-annotation',
    'geojson-extent',
    'templates/views/components/widgets/iiif.htm',
    'leaflet-fullscreen',
], function(_, L, ko, koMapping, WidgetViewModel, IIIFAnnotationViewmodel, geojsonExtent, iiifWidgetTemplate) {
    const viewModel = function(params) {
        var self = this;

         
        params.configKeys = ['defaultManifest'];
        WidgetViewModel.apply(this, [params]);

        if (params.widget) params.widgets = [params.widget];
        if (!params.manifest) params.manifest = this.defaultManifest();

        IIIFAnnotationViewmodel.apply(this, [params]);

        if (params.state === 'report') {
            this.canvasConfigs = [];
            var canvases = {};
            var value = koMapping.toJS(params.value);
            if (value && value.features) {
                value.features.forEach(function(feature) {
                    if (!canvases[feature.properties.canvas]) canvases[feature.properties.canvas] = [];
                    canvases[feature.properties.canvas].push(feature);
                });
            }
            _.forEach(canvases, function(features, canvas) {
                self.canvasConfigs.push({
                    center: [0, 0],
                    crs: L.CRS.Simple,
                    zoom:  0,
                    afterRender: function(map) {
                        L.tileLayer.iiif(canvas + '/info.json').addTo(map);
                        var featureCollection = {
                            type: 'FeatureCollection',
                            features: features
                        };
                        var extent = geojsonExtent(featureCollection);
                        map.addLayer(L.geoJson(featureCollection, {
                            pointToLayer: function(feature, latlng) {
                                return L.circleMarker(latlng, feature.properties);
                            },
                            style: function(feature) {
                                return feature.properties;
                            }
                        }));
                        L.control.fullscreen().addTo(map);
                        setTimeout(function() {
                            map.fitBounds([
                                [extent[1]-1, extent[0]-1],
                                [extent[3]+1, extent[2]+1]
                            ]);
                        }, 250);
                    }
                });
            });
        }

        this.manifest.subscribe(function(manifest) {
            if (manifest !== self.defaultManifest())
                self.defaultManifest(manifest);
        });

        this.defaultManifest.subscribe(function(manifest) {
            if (manifest !== self.manifest())
                self.manifest(manifest);
        });

        this.displayValue = ko.computed(function() {
            var value = koMapping.toJS(this.value);
            if (!value || !value.features) {
                return 0;
            }
            return value.features.length;
        }, this);    
    };

    return ko.components.register('iiif-widget', {
        viewModel: viewModel,
        template: iiifWidgetTemplate,
    });
});
