define([
    'arches',
    'jquery',
    'knockout',
    'leaflet',
    'views/components/workbench',
    'leaflet-iiif',
    'leaflet-fullscreen',
    'bindings/leaflet'
], function(arches, $, ko, L, WorkbenchViewmodel) {
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
        this.filter = ko.observable('');
        this.manifestData = ko.observable();
        this.manifestError = ko.observable();
        this.canvases = ko.pureComputed(function() {
            var manifestData = self.manifestData();
            var sequences = manifestData ? manifestData.sequences : [];
            var canvases = [];
            sequences.forEach(function(sequence) {
                if (sequence.canvases) {
                    sequence.label = getLabel(sequence);
                    sequence.canvases.forEach(function(canvas) {
                        canvas.label = getLabel(canvas);
                        if (typeof canvas.thumbnail === 'object')
                            canvas.thumbnail = canvas.thumbnail["@id"];
                        else if (canvas.images && canvas.images[0] && canvas.images[0].resource)
                            canvas.thumbnail = canvas.images[0].resource["@id"];
                        canvases.push(canvas);
                    });
                }
            });
            return canvases;
        });
        this.manifestName = ko.pureComputed(function() {
            var manifestData = self.manifestData();
            return getLabel(manifestData || {label: ''});
        });
        this.zoomToCanvas = !(params.zoom && params.center);

        var validateUrl = function(value) {
            return /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S*)?$/i.test(value);
        };

        var queryTerm;
        var limit = 10;
        this.manifestSelectConfig = {
            value: this.manifest,
            clickBubble: true,
            multiple: false,
            closeOnSlect: false,
            allowClear: true,
            ajax: {
                url: arches.urls.iiifmanifest,
                dataType: 'json',
                quietMillis: 250,
                data: function(term, page) {
                    var data = {
                        start: (page-1)*limit,
                        limit: limit
                    };
                    queryTerm = term;
                    if (term) data.query = term;
                    return data;
                },
                results: function(data, page) {
                    var results = data.results;
                    if (validateUrl(queryTerm)) results.unshift({
                        url: queryTerm,
                        label: queryTerm
                    });
                    return {
                        results: results,
                        more: data.count >= (page*limit)
                    };
                }
            },
            id: function(item) {
                return item.url;
            },
            formatResult: function(item) {
                return item.label;
            },
            formatSelection: function(item) {
                return item.label;
            },
            clear: function() {
                self.manifest('');
            },
            isEmpty: ko.computed(function() {
                return self.manifest() === '' || !self.manifest();
            }, this),
            initSelection: function() {
                return;
            }
        };

        this.getManifestData = function() {
            var manifestURL = self.manifest();
            if (manifestURL) {
                self.manifestLoading(true);
                self.manifestError(undefined);
                abortFetchManifest = new window.AbortController();
                window.fetch(manifestURL, {signal: abortFetchManifest.signal})
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

        this.activeTab.subscribe(function() {
            var map = self.map();
            if (map) setTimeout(function() {
                map.invalidateSize();
            }, 1);
        });

        if (params.showGallery === undefined) params.showGallery = true;
        this.showGallery = ko.observable(params.showGallery);
        if (!params.manifest) params.expandGallery = true;
        this.expandGallery = ko.observable(params.expandGallery);
        this.expandGallery.subscribe(function(expandGallery) {
            if (expandGallery) self.showGallery(true);
        });
        this.showGallery.subscribe(function(showGallery) {
            if (!showGallery) self.expandGallery(false);
        });

        this.toggleGallery = function() {
            self.showGallery(!self.showGallery());
        };

        this.leafletConfig = {
            center: params.center || [0, 0],
            crs: L.CRS.Simple,
            zoom: params.zoom || 0,
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
        this.map.subscribe(function(map) {
            L.control.fullscreen({
                fullscreenElement: $(map.getContainer()).closest('.workbench-card-wrapper')[0]
            }).addTo(map);
            addCanvasLayer();
        });
        this.canvas.subscribe(addCanvasLayer);

        this.selectCanvas = function(canvas) {
            var service = self.getCanvasService(canvas);
            self.zoomToCanvas = true;
            if (service) self.canvas(service);
        };

        this.canvasClick = function(canvas) {
            self.selectCanvas(canvas);
            self.expandGallery(false);
        };

        this.getCanvasService = function(canvas) {
            if (canvas.images.length > 0) return canvas.images[0].resource.service['@id'];
        };

        var updateCanvas = !self.canvas();
        this.manifestData.subscribe(function(manifestData) {
            if (updateCanvas && manifestData.sequences.length > 0) {
                var sequence = manifestData.sequences[0];
                if (sequence.canvases.length > 0) {
                    var canvas = sequence.canvases[0];
                    self.selectCanvas(canvas);
                }
            }
            updateCanvas = true;
        });

        this.toggleManifestEditor = function() {
            self.editManifest(!self.editManifest());
            if (abortFetchManifest) abortFetchManifest.abort();
        };

        this.getAnnotationCount = function() {
            return 0;
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
