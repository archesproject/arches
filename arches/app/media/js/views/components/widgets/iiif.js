define([
    'knockout',
    'underscore',
    'viewmodels/widget',
    'leaflet',
    'knockout-mapping',
    'uuid',
    'arches',
    'leaflet-iiif',
    'leaflet-draw',
    'leaflet-draw-local',
    'bindings/leaflet'
], function(ko, _, WidgetViewModel, L, koMapping, uuid, arches) {
    return ko.components.register('iiif-widget', {
        viewModel: function(params) {
            var self = this;
            var canvasLayer = null;
            params.configKeys = ['nameLabel', 'placeholder', 'typeLabel'];
            WidgetViewModel.apply(this, [params]);

            this.displayValue = ko.computed(function() {
                var val = ko.unwrap(self.value);
                if (!val) {
                    return val;
                }
                return val.manifestLabel;
            });

            var features = self.value.features ? koMapping.toJS(self.value.features) : [];
            var ignoreFeatureClick = false;
            this.hoverData = ko.observable(null);
            this.clickData = ko.observable(null);
            this.clickName = ko.pureComputed({
                read: function() {
                    return self.clickData() ? self.clickData().name : '';
                },
                write: function(val) {
                    if (self.clickData()) {
                        self.clickData().name = val;
                        updateFeatures();
                    }
                },
                owner: this
            });
            this.clickType = ko.pureComputed({
                read: function() {
                    return self.clickData() ? self.clickData().type : null;
                },
                write: function(val) {
                    if (self.clickData()) {
                        self.clickData().type = val;
                        updateFeatures();
                    }
                },
                owner: this
            });
            this.hoverType = ko.pureComputed(function() {
                return self.hoverData() ? self.hoverData().type : null;
            });
            this.popupData = ko.computed(function() {
                var hoverData = self.hoverData();
                return hoverData ? hoverData : self.clickData();
            });

            var highlightedFeature;
            var highlightedFeatureStyle;
            var largeIcon = new L.Icon.Default();
            largeIcon.options.iconSize = [33, 54]
            largeIcon.options.iconAnchor = [16, 54]
            largeIcon.options.shadowSize =  [54, 54];
            var highlightFeature = function(layer) {
                highlightedFeatureStyle = _.clone(layer.options);
                if (highlightedFeatureStyle.icon) {
                    layer.setIcon(largeIcon);
                } else {
                    layer.setStyle({
                        weight: 7,
                        color: '#2a3fff',
                        fillOpacity: 0.7
                    });

                    if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                        layer.bringToFront();
                    }
                }

                highlightedFeature = layer;
            };

            this.clickData.subscribe(function(clickData) {
                if (highlightedFeature) {
                    if (highlightedFeatureStyle.icon) {
                        highlightedFeature.setIcon(highlightedFeatureStyle.icon);
                    } else {
                        highlightedFeature.setStyle(highlightedFeatureStyle);
                    }
                    highlightedFeature = null;
                    highlightedFeatureStyle = null;
                }
            });

            var addLayerListeners = function(layer) {
                layer.on({
                    mouseover: function(e) {
                        self.hoverData(layer.feature.properties);
                    },
                    mouseout: function(e) {
                        self.hoverData(null);
                    },
                    click: function(e) {
                        if (!ignoreFeatureClick) {
                            self.clickData(layer.feature.properties);
                            highlightFeature(layer);
                        }
                    }
                });
            }
            var drawnItems = new L.geoJson({
                type: 'FeatureCollection',
                features: features
            }, {
                onEachFeature: function(feature, layer) {
                    addLayerListeners(layer)
                }
            });
            var drawControl = new L.Control.Draw({
                edit: {
                    featureGroup: drawnItems
                },
                draw: {
                    circle: false
                }
            });

            this.expandControls = ko.observable(false);

            var manifestId;
            var canvasId;
            if (self.value.manifestId !== undefined) {
                manifestId = ko.unwrap(self.value.manifestId);
            }
            if (self.value.canvasId !== undefined) {
                canvasId = ko.unwrap(self.value.canvasId);
            }
            this.selectedManifest = ko.observable(null);
            this.selectedCanvas = ko.observable(null);
            var updateSelections = function(manifest) {
                var selectedCanvas;
                var selectedManifest;
                if (manifest.data()['@id'] === manifestId) {
                    selectedManifest = manifest;
                    _.find(manifest.data().sequences, function(sequence) {
                        var canvas = _.find(sequence.canvases, function(canvas) {
                            return canvas['@id'] === canvasId;
                        });
                        if (canvas) {
                            selectedCanvas = canvas;
                        }
                        return canvas;
                    });
                }
                if (selectedManifest) {
                    self.selectedManifest(selectedManifest);
                }
                if (selectedCanvas) {
                    self.selectedCanvas(selectedCanvas);
                }
            }
            _.each(arches.iiifManifests, function(manifest) {
                if (!manifest.data) {
                    manifest.data = ko.observable(null);
                    $.get(manifest.url, function(data) {
                        manifest.data(data);
                    });
                }
                if (manifest.data()) {
                    updateSelections(manifest);
                } else {
                    manifest.data.subscribe(function() {
                        updateSelections(manifest);
                    })
                }
            });
            this.manifests = ko.observableArray(arches.iiifManifests);

            var updateFeatures = function() {
                var features = drawnItems.toGeoJSON().features;
                if (self.value.features !== undefined) {
                    self.value.features(features);
                } else {
                    var value = self.value();
                    if (!value) {
                        value = {
                            canvasId: null,
                            canvasLabel: null,
                            manifestId: null,
                            manifestLabel: null,
                            attribution: null,
                            url: null
                        };
                    }
                    value.features = features;
                    self.value(value)
                }
            }
            this.map = null;
            this.mapConfig = {
                center: [0, 0],
                crs: L.CRS.Simple,
                zoom: 0,
                afterRender: function(map) {
                    var url;
                    var attribution;
                    if (self.value.url !== undefined) {
                        url = ko.unwrap(self.value.url);
                    }
                    if (self.value.attribution !== undefined) {
                        attribution = ko.unwrap(self.value.manifestLabel) + ', ' +
                            ko.unwrap(self.value.canvasLabel) + ', ' +
                            ko.unwrap(self.value.attribution);
                    }
                    self.map = map;
                    self.map.addLayer(drawnItems);
                    map.on('preclick', function(e) {
                        self.clickData(null);
                    });

                    if (url) {
                        canvasLayer = L.tileLayer.iiif(
                            url, {
                                attribution: attribution
                            }
                        ).addTo(self.map);
                    }

                    if (self.state !== 'report') {
                        self.map.addControl(drawControl);
                        map.on('draw:deletestart', function(e) {
                            ignoreFeatureClick = true;
                        });
                        map.on('draw:deletestop', function(e) {
                            ignoreFeatureClick = false;
                        })
                    } else {
                        self.map.addLayer(drawnItems);
                    }

                    self.map.on(L.Draw.Event.CREATED, function(e) {
                        var type = e.layerType
                        var layer = e.layer;
                        layer.feature = {
                            type: "Feature",
                            properties: {
                                id: uuid.generate(),
                                name: '',
                                type: null
                            }
                        };

                        addLayerListeners(layer);

                        drawnItems.addLayer(layer);

                        updateFeatures()
                    });
                    self.map.on(L.Draw.Event.EDITED, updateFeatures);
                    self.map.on(L.Draw.Event.DELETED, updateFeatures);

                    self.expanded.subscribe(function () {
                        _.defer(function () {
                            self.map.invalidateSize();
                        }, 500);
                    });
                }
            };

            this.selectedCanvas.subscribe(function(canvas) {
                var url;
                var manifest = self.selectedManifest() ? self.selectedManifest().data() : {
                    '@id': null,
                    'label': null,
                    'attribution': null
                };
                if (self.map && canvasLayer && self.map.hasLayer(canvasLayer)) {
                    self.map.removeLayer(canvasLayer);
                    canvasLayer = null;
                }
                if (canvas) {
                    if (canvas.images.length > 0) {
                        url = canvas.images[0].resource.service['@id'] + '/info.json';
                    }
                    if (self.map) {
                        self.map.removeLayer(drawnItems);
                        if (canvas.images.length > 0) {
                            canvasLayer = L.tileLayer.iiif(
                                canvas.images[0].resource.service['@id'] + '/info.json', {
                                    attribution: manifest['label'] + ', ' + canvas['label'] + ', ' + manifest['attribution']
                                }
                            ).addTo(self.map);
                        }
                        self.map.addLayer(drawnItems);
                    }
                } else {
                    canvas = {
                        '@id': null,
                        'label': null
                    };
                    url = null;
                }
                if (self.value.canvasId !== undefined) {
                    self.value.canvasId(canvas['@id']);
                    self.value.canvasLabel(canvas['label']);
                    self.value.manifestId(manifest['@id']);
                    self.value.manifestLabel(manifest['label']);
                    self.value.attribution(manifest['attribution']);
                    self.value.url(url);
                    self.value.features(drawnItems.toGeoJSON().features);
                } else {
                    var value = self.value();
                    if (canvas['@id']) {
                        if (!value) {
                            value = {};
                        }
                        value.canvasId = canvas['@id'];
                        value.canvasLabel = canvas['label'];
                        value.manifestId = manifest['@id'];
                        value.manifestLabel = manifest['label'];
                        value.attribution = manifest['attribution'];
                        value.url = url;
                        value.features = drawnItems.toGeoJSON().features;
                    }
                    self.value(value)
                }
            });

            if (this.form) {
                this.form.on('after-update', function(req, tile) {
                    self.clickData(null);
                    if (!ko.unwrap(self.value)) {
                        drawnItems.clearLayers();
                        self.selectedManifest(null);
                        self.selectedCanvas(null);
                    }
                });
                this.form.on('tile-reset', function(tile) {
                    self.clickData(null);
                    drawnItems.clearLayers();
                    var features = self.value.features ? koMapping.toJS(self.value.features) : [];
                    drawnItems.addData({
                        type: 'FeatureCollection',
                        features: features
                    });
                    var manifestId;
                    var canvasId;
                    if (self.value.manifestId !== undefined) {
                        manifestId = ko.unwrap(self.value.manifestId);
                    }
                    if (self.value.canvasId !== undefined) {
                        canvasId = ko.unwrap(self.value.canvasId);
                    }
                    var selectedManifest = _.find(self.manifests(), function(manifest) {
                        return manifest.data()['@id'] === manifestId
                    });
                    var selectedCanvas = null;
                    if (selectedManifest) {
                        _.find(selectedManifest.data().sequences, function(sequence) {
                            var canvas = _.find(sequence.canvases, function(canvas) {
                                return canvas['@id'] === canvasId;
                            });
                            if (canvas) {
                                selectedCanvas = canvas;
                            }
                            return canvas;
                        });
                    }
                    var currentCanvasId = self.selectedCanvas() ? self.selectedCanvas()['@id'] : null;
                    var selectedCanvasId = selectedCanvas ? selectedCanvas['@id'] : null;
                    if (currentCanvasId !== selectedCanvasId) {
                        self.selectedCanvas(selectedCanvas);
                    }
                    self.selectedManifest(selectedManifest);
                });
            }
        },
        template: {
            require: 'text!widget-templates/iiif'
        }
    });
});
