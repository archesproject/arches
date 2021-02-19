define([
    'jquery',
    'arches',
    'knockout',
    'mapbox-gl',
    'viewmodels/external-resource-data-preview',
    'text!templates/views/components/cards/external-resource-data-preview-popup.htm'
], function($, arches, ko, mapboxgl, ExternalResourceDataPreview, popupTemplate) {
    /* 
        Used to connect the external-resource-data-preview component 
        with the related-resources-map-card
    */ 
    var viewModel = function(params) {
        var self = this;

        params.popupTemplate = popupTemplate;
        self.popupTemplate = popupTemplate;
        console.log("THER THER", self, params, ko.unwrap(params.fileData))
        

        this.map = params.map;
        this.fileData = ko.observable();
        this.fileData.subscribe(function(fileData) {
            if (!ko.unwrap(params.fileData)) {

                params.fileData(fileData)
            }

            var bounds = new mapboxgl.LngLatBounds();

            fileData.forEach(function(fileDatum) {
                fileDatum.data.forEach(function(parsedRow) {
                    if (parsedRow.location_data) {
                        parsedRow.location_data.features.forEach(function(feature) {
                            feature.id = parsedRow.row_id;
                            self.draw.add(feature);
                            bounds.extend(feature.geometry.coordinates);
                        });
                    }
                });
            });

            self.map().fitBounds(
                bounds, 
                { 
                    padding: { top: 120, right: 540, bottom: 120, left: 120 },
                    linear: true,
                }
            );
        });

        self.map.subscribe(function(map) {
            if (!self.draw && params.draw) {
                self.draw = params.draw;
            }

            map.on('click', function(e) {
                var hoverFeature = _.find(
                    map.queryRenderedFeatures(e.point),
                    function(feature) { return feature.properties.id; }
                );
                
                if (hoverFeature) {
                    hoverFeature.id = hoverFeature.properties.id;

                    var featureData = self.fileData().reduce(function(acc, fileDatum) {
                        acc = fileDatum.data.find(function(parsedRow) {
                            return parsedRow.row_id === hoverFeature.id;
                        });

                        return acc;
                    }, null)

                    self.popup = new mapboxgl.Popup()
                        .setLngLat(e.lngLat)
                        .setHTML(self.popupTemplate)
                        .addTo(map);
                    ko.applyBindingsToDescendants(
                        featureData,
                        self.popup._content
                    );

                    if (map.getStyle()) {
                        map.setFeatureState(hoverFeature, { selected: true });
                    }

                    self.popup.on('close', function() {
                        if (map.getStyle()) map.setFeatureState(hoverFeature, { selected: false });
                        self.popup = undefined;
                    });
                }
            });
        });
    }

    ko.components.register('external-resource-data-preview-map', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/cards/related-resources-map.htm'
        }
    });

    return viewModel;
});
