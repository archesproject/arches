define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'leaflet',
    'arches',
    'leaflet-iiif',
    'leaflet-draw',
    'bindings/leaflet'
], function (ko, _, WidgetViewModel, L, arches) {
    return ko.components.register('iiif-widget', {
        viewModel: function(params) {
            var self = this;
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
            this.selectedCanvas = ko.observable(null);
            this.map = null;
            var canvasLayer = null;
            var drawnItems = new L.FeatureGroup();
            this.mapConfig = {
                center: [0, 0],
                crs: L.CRS.Simple,
                zoom: 0,
                afterRender: function (map) {
                    self.map = map;
                    self.map.addLayer(drawnItems);

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
            })
        },
        template: { require: 'text!widget-templates/iiif' }
    });
});
