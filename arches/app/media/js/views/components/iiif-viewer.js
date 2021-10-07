define([
    'arches',
    'jquery',
    'knockout',
    'knockout-mapping',
    'leaflet',
    'views/components/workbench',
    'text!templates/views/components/iiif-popup.htm',
    'leaflet-iiif',
    'leaflet-fullscreen',
    'bindings/select2-query',
    'bindings/leaflet'
], function(arches, $, ko, koMapping, L, WorkbenchViewmodel, iiifPopup) {
    var IIIFViewerViewmodel = function(params) {
        var self = this;
        var abortFetchManifest;
        this.getManifestDataValue = function(object, property, returnFirstVal) {
            var val = object[property];
            if (Array.isArray(val) && returnFirstVal) val = object[property][0]["@value"];
            return val;
        };

        this.map = ko.observable();
        this.manifest = ko.observable(params.manifest);
        this.editManifest = ko.observable(!params.manifest);
        this.canvas = ko.observable(params.canvas);
        this.manifestLoading = ko.observable();
        this.filter = ko.observable('');
        this.manifestData = ko.observable();
        this.manifestError = ko.observable();
        this.manifestName = ko.observable();
        this.manifestDescription = ko.observable();
        this.manifestAttribution = ko.observable();
        this.manifestLogo = ko.observable();
        this.manifestMetadata = koMapping.fromJS([]);
        this.canvasLabel = ko.observable();
        this.zoomToCanvas = !(params.zoom && params.center);
        this.annotationNodes = ko.observableArray();

        this.buildAnnotationNodes = params.buildAnnotationNodes || function(json) {
            self.annotationNodes(
                json.map(function(node) {
                    var annotations = ko.observableArray();
                    var updateAnnotations = function() {
                        var canvas = self.canvas();
                        if (canvas) {
                            window.fetch(arches.urls.iiifannotations + '?canvas=' + canvas + '&nodeid=' + node.nodeid)
                                .then(function(response) {
                                    return response.json();
                                })
                                .then(function(json) {
                                    json.features.forEach(function(feature) {
                                        feature.properties.graphName = node['graph_name'];
                                    });
                                    annotations(json.features);
                                });
                        }
                    };
                    self.canvas.subscribe(updateAnnotations);
                    updateAnnotations();
                    return {
                        name: node['graph_name'] + ' - ' + node.name,
                        icon: node.icon,
                        active: ko.observable(false),
                        opacity: ko.observable(100),
                        annotations: annotations
                    };
                })
            );
        };

        window.fetch(arches.urls.iiifannotationnodes)
            .then(function(response) {
                return response.json();
            })
            .then(self.buildAnnotationNodes);

        var annotationLayer = ko.computed(function() {
            var annotationFeatures = [];
            self.annotationNodes().forEach(function(node) {
                if (node.active()) {
                    var annotations = node.annotations();
                    if (params.tile && params.tile.tileid) {
                        annotations = annotations.filter(function(annotation) {
                            return annotation.properties.tileId !== params.tile.tileid;
                        });
                    }
                    annotations.forEach(function(annotation) {
                        annotation.properties.opacityModifier = node.opacity();
                    });
                    annotationFeatures = annotations.concat(annotationFeatures);
                }
            });
            return L.geoJson({
                type: 'FeatureCollection',
                features: annotationFeatures
            }, {
                pointToLayer: function(feature, latlng) {
                    var modifier = feature.properties.opacityModifier / 100;
                    var style = {
                        color: feature.properties.color,
                        fillColor: feature.properties.fillColor,
                        weight: feature.properties.weight,
                        radius: feature.properties.radius,
                        opacity: (feature.properties.opacity * modifier),
                        fillOpacity: (feature.properties.fillOpacity * modifier)
                    };
                    return L.circleMarker(latlng, style);
                },
                style: function(feature) {
                    var modifier = feature.properties.opacityModifier / 100;
                    var style = {
                        color: feature.properties.color,
                        fillColor: feature.properties.fillColor,
                        weight: feature.properties.weight,
                        radius: feature.properties.radius,
                        opacity: (feature.properties.opacity * modifier),
                        fillOpacity: (feature.properties.fillOpacity * modifier)
                    };
                    return style;
                },
                onEachFeature: function(feature, layer) {
                    if (params.onEachFeature) {
                        params.onEachFeature(feature, layer);
                    }
                    else {
                        var popup = L.popup({
                            closeButton: false,
                            maxWidth: 349
                        })
                            .setContent(iiifPopup)
                            .on('add', function() {
                                var popupData = {
                                    'closePopup': function() {
                                        popup.remove();
                                    },
                                    'name': ko.observable(''),
                                    'description': ko.observable(''),
                                    'graphName': feature.properties.graphName,
                                    'resourceinstanceid': feature.properties.resourceId,
                                    'reportURL': arches.urls.resource_report
                                };
                                window.fetch(arches.urls.resource_descriptors + popupData.resourceinstanceid)
                                    .then(function(response) {
                                        return response.json();
                                    })
                                    .then(function(descriptors) {
                                        popupData.name(descriptors.displayname);
                                        popupData.description(descriptors['map_popup']);
                                    });
                                var popupElement = popup.getElement()
                                    .querySelector('.mapboxgl-popup-content');
                                ko.applyBindingsToDescendants(popupData, popupElement);
                            });
                        layer.bindPopup(popup);
                    }
                }
            });
        });
        var annotationFeatureGroup = new L.FeatureGroup();

        annotationLayer.subscribe(function(newAnnotationLayer) {
            var map = self.map();
            if (map) {
                annotationFeatureGroup.clearLayers();
                annotationFeatureGroup.addLayer(newAnnotationLayer);
            }
        });

        this.canvases = ko.pureComputed(function() {
            var manifestData = self.manifestData();
            var sequences = manifestData ? manifestData.sequences : [];
            var canvases = [];
            sequences.forEach(function(sequence) {
                if (sequence.canvases) {
                    sequence.label = self.getManifestDataValue(sequence, 'label', true);
                    sequence.canvases.forEach(function(canvas) {
                        canvas.label = self.getManifestDataValue(canvas, 'label', true);
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

        var validateUrl = function(value) {
            return /^(?:(?:(?:https?|ftp):)?\/\/)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-*)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S*)?$/i.test(value);
        };

        var queryTerm;
        var limit = 10;
        this.manifestSelectConfig = {
            value: this.manifest,
            clickBubble: true,
            multiple: false,
            closeOnSelect: false,
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
            map.addLayer(annotationFeatureGroup);
        });
        this.canvas.subscribe(addCanvasLayer);

        this.selectCanvas = function(canvas) {
            var service = self.getCanvasService(canvas);
            self.zoomToCanvas = true;
            if (service) self.canvas(service);

            self.origCanvasLabel = self.getManifestDataValue(canvas, 'label', true);
            self.canvasLabel(self.getManifestDataValue(canvas, 'label', true));
        };

        this.canvasClick = function(canvas) {
            self.selectCanvas(canvas);
            self.expandGallery(false);
        };

        this.getCanvasService = function(canvas) {
            if (canvas.images.length > 0) return canvas.images[0].resource.service['@id'];
        };

        this.updateCanvas = !self.canvas();
        this.manifestData.subscribe(function(manifestData) {
            if (manifestData) {
                if (manifestData.sequences.length > 0) {
                    var sequence = manifestData.sequences[0];
                    var canvasIndex = 0;
                    if (sequence.canvases.length > 0) {
                        if (!self.updateCanvas) {
                            canvasIndex = sequence.canvases.findIndex(function(c){return c.images[0].resource.service['@id'] === self.canvas();});
                        }
                        var canvas = sequence.canvases[canvasIndex];
                        self.selectCanvas(canvas);
                    }    
                }
                self.updateCanvas = true;
                self.origManifestName = self.getManifestDataValue(manifestData, 'label', true);
                self.manifestName(self.origManifestName);
                self.origManifestDescription = self.getManifestDataValue(manifestData, 'description', true);
                self.manifestDescription(self.origManifestDescription);
                self.origManifestAttribution = self.getManifestDataValue(manifestData, 'attribution', true);
                self.manifestAttribution(self.origManifestAttribution);
                self.origManifestLogo = self.getManifestDataValue(manifestData, 'logo', true);
                self.manifestLogo(self.origManifestLogo);
                self.origManifestMetadata = koMapping.toJSON(self.getManifestDataValue(manifestData, 'metadata'));
                self.manifestMetadata.removeAll();
                self.getManifestDataValue(manifestData, 'metadata').forEach(function(entry){
                    self.manifestMetadata.push(koMapping.fromJS(entry));
                });
            }
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
