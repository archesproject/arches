define([
    'knockout',
    'leaflet',
    'views/components/workbench',
    'leaflet-iiif',
    'bindings/leaflet'
], function(ko, L, WorkbenchViewmodel) {
    var IIIFViewerViewmodel = function(params) {
        var self = this;
        var abortFetchManifest;
        var getLabel = function(object) {
            var label = object.label;
            if (Array.isArray(label)) label = object.label[0]["@value"];
            return label;
        };

        this.map = ko.observable();
        this.manifest = ko.observable(params.manifest);
        this.editManifest = ko.observable(!params.manifest);
        this.canvas = ko.observable(params.canvas);
        this.manifestLoading = ko.observable();
        this.manifestData = ko.observable();
        this.manifestError = ko.observable();
        this.sequences = ko.pureComputed(function() {
            var manifestData = self.manifestData();
            var sequences = manifestData ? manifestData.sequences : [];
            sequences.forEach(function(sequence) {
                if (sequence.canvases) {
                    sequence.label = getLabel(sequence);
                    sequence.canvases.forEach(function(canvas) {
                        canvas.label = getLabel(canvas);
                        if (typeof canvas.thumbnail === 'object')
                            canvas.thumbnail = canvas.thumbnail["@id"];
                    });
                }
            });
            return sequences;
        });
        this.manifestName = ko.pureComputed(function() {
            var manifestData = self.manifestData();
            return getLabel(manifestData || {label: ''});
        });
        this.zoomToCanvas = true;
        
        this.getManifestData = function() {
            var manifestURL = self.manifest();
            if (manifestURL) {
                self.manifestLoading(true);
                self.manifestError(undefined);
                abortFetchManifest = new window.AbortController();
                fetch(manifestURL, {signal: abortFetchManifest.signal})
                    .then(function(response) {
                        return response.json();
                    })
                    .then(function(manifestData) {
                        self.manifestData(manifestData);
                        self.editManifest(false);
                    })
                    .catch(function(error) {
                        if (error.message !== "The user aborted a request.")
                            self.manifestError(error);
                    })
                    .finally(function() {
                        self.manifestLoading(false);
                        abortFetchManifest = undefined;
                    });
            }
        };
        this.getManifestData();
        
        WorkbenchViewmodel.apply(this, [params]);
        
        this.showGallery = ko.observable(true);
        
        this.toggleGallery = function() {
            self.showGallery(!self.showGallery());
        };
        
        this.leafletConfig = {
            center: [0, 0],
            crs: L.CRS.Simple,
            zoom: 0,
            afterRender: this.map
        };
        
        var canvasLayer;
        this.brightness = ko.observable(100);
        this.contrast = ko.observable(100);
        this.saturation = ko.observable(100);
        this.greyscale = ko.observable(false);
        this.canvasFilter = ko.pureComputed(function() {
            var b = self.brightness() / 100;
            var c = self.contrast() / 100;
            var s = self.saturation() / 100;
            var g = self.greyscale() ? 1 : 0;
            return 'brightness(' + b + ') contrast(' + c + ') ' +
                'saturate(' + s + ') grayscale(' + g + ')';
        });
        var updateCanvasLayerFilter = function() {
            var filter = self.canvasFilter();
            var map = self.map();
            if (map) {
                map.getContainer().querySelector('.leaflet-tile-pane').style.filter = filter;
            }
        };
        this.canvasFilter.subscribe(updateCanvasLayerFilter);
        
        this.resetImageSettings = function() {
            self.brightness(100);
            self.contrast(100);
            self.saturation(100);
            self.greyscale(false);
        };

        var addCanvasLayer = function() {
            var map = self.map();
            var canvas = self.canvas();
            if (map && canvas) {
                if (canvasLayer) {
                    map.removeLayer(canvasLayer);
                    canvasLayer = undefined;
                }
                if (canvas) {
                    canvasLayer = L.tileLayer.iiif(canvas + '/info.json', {
                        fitBounds: self.zoomToCanvas
                    });
                    canvasLayer.addTo(map);
                    updateCanvasLayerFilter();
                }
            }
            self.zoomToCanvas = false;
        };
        this.map.subscribe(addCanvasLayer);
        this.canvas.subscribe(addCanvasLayer);
        
        this.selectCanvas = function(canvas) {
            var service = self.getCanvasService(canvas);
            self.zoomToCanvas = true;
            if (service) self.canvas(service);
        };
        
        this.getCanvasService = function(canvas) {
            if (canvas.images.length > 0) return canvas.images[0].resource.service['@id'];
        };
        
        this.manifestData.subscribe(function(manifestData) {
            if (!self.canvas() && manifestData.sequences.length > 0) {
                var sequence = manifestData.sequences[0];
                if (sequence.canvases.length > 0) {
                    var canvas = sequence.canvases[0];
                    self.selectCanvas(canvas);
                }
            }
        });
        
        this.toggleManifestEditor = function() {
            self.editManifest(!self.editManifest());
            if (abortFetchManifest) abortFetchManifest.abort();
        };
    };
    ko.components.register('iiif-viewer', {
        viewModel: IIIFViewerViewmodel,
        template: {
            require: 'text!templates/views/components/iiif-viewer.htm'
        }
    });
    return IIIFViewerViewmodel;
});
