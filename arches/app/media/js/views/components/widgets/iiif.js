define([
    'underscore',
    'leaflet',
    'knockout',
    'knockout-mapping',
    'viewmodels/widget',
    'views/components/iiif-annotation',
    'geojson-extent',
    'leaflet-fullscreen'
], function(_, L, ko, koMapping, WidgetViewModel, IIIFAnnotationViewmodel, geojsonExtent) {
    return ko.components.register('iiif-widget', {
        viewModel: function(params) {
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
                                    return L.circleMarker(latlng, {
                                        color: feature.properties.color,
                                        fillColor: feature.properties.fillColor,
                                        weight: feature.properties.weight,
                                        radius: feature.properties.radius,
                                        opacity: feature.properties.opacity,
                                        fillOpacity: feature.properties.fillOpacity
                                    });
                                },
                                style: function(feature) {
                                    return {
                                        color: feature.properties.color,
                                        fillColor: feature.properties.fillColor,
                                        weight: feature.properties.weight,
                                        radius: feature.properties.radius,
                                        opacity: feature.properties.opacity,
                                        fillOpacity: feature.properties.fillOpacity
                                    };
                                }
                            }));
                            L.control.fullscreen().addTo(map);
                            setTimeout(function() {
                                if (features.length === 1 && features[0].geometry.type === 'Point') {
                                    var coords = features[0].geometry.coordinates;
                                    map.panTo([coords[1], coords[0]]);
                                } else {
                                    map.fitBounds([
                                        [extent[1], extent[0]],
                                        [extent[3], extent[2]]
                                    ]);
                                }
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
        },
        template: { require: 'text!templates/views/components/widgets/iiif.htm' }
    });
});
