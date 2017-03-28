define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'leaflet',
    'knockout-mapping',
    'arches',
    'leaflet-iiif',
    'leaflet-draw',
    'bindings/leaflet'
], function (ko, _, WidgetViewModel, L, koMapping, arches) {
    return ko.components.register('iiif-widget', {
        viewModel: function(params) {
            var self = this;
            var canvasLayer = null;
            var drawnItems = new L.FeatureGroup();
            params.configKeys = [];
            WidgetViewModel.apply(this, [params]);

            this.expandControls = ko.observable(false);

            _.each(arches.iiifManifests, function (manifest) {
                manifest.data = ko.observable(null);
                $.get(manifest.url, function(data) {
                    manifest.data(data);
                });
            });
            this.manifests = ko.observableArray(arches.iiifManifests);
            this.selectedManifest = ko.observable(null);
            if (this.value.canvas) {
                this.selectedCanvas = ko.observable(koMapping.toJS(this.value.canvas));
            } else {
                this.selectedCanvas = ko.observable(null);
            }

            console.log(this.selectedCanvas())

            this.map = null;
            this.mapConfig = {
                center: [0, 0],
                crs: L.CRS.Simple,
                zoom: 0,
                afterRender: function (map) {
                    var canvas = self.selectedCanvas();
                    self.map = map;
                    self.map.addLayer(drawnItems);

                    if (canvas && canvas.images.length > 0) {
                        canvasLayer = L.tileLayer.iiif(
                            canvas.images[0].resource.service['@id'] + '/info.json'
                        ).addTo(self.map);
                    }

                    var drawControl = new L.Control.Draw({
                        edit: {
                            featureGroup: drawnItems
                        }
                    });

                    self.map.addControl(drawControl);

                    self.map.on(L.Draw.Event.CREATED, function(e) {
                        var type = e.layerType
                        var layer = e.layer;

                        drawnItems.addLayer(layer);
                    });
                }
            };

            this.selectedCanvas.subscribe(function(canvas) {
                if (self.map) {
                    self.map.removeLayer(drawnItems);
                    if (canvasLayer) {
                        self.map.removeLayer(canvasLayer);
                        canvasLayer = null;
                    }
                    if (canvas.images.length > 0) {
                        canvasLayer = L.tileLayer.iiif(
                            canvas.images[0].resource.service['@id'] + '/info.json'
                        ).addTo(self.map);
                    }
                    self.map.addLayer(drawnItems);
                }
                if (self.value.canvas !== undefined) {
                    _.each(canvas, function(val, key) {
                        self.value.canvas[key](val);
                    });
                } else {
                    self.value({
                        canvas: canvas
                    })
                }
            });
        },
        template: { require: 'text!widget-templates/iiif' }
    });
});
