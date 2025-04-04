import $ from 'jquery';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import L from 'leaflet';
import arches from 'arches';
import WorkbenchViewmodel from 'views/components/workbench';
import iiifPopup from 'templates/views/components/iiif-popup.htm';
import iiifViewerTemplate from 'templates/views/components/iiif-viewer.htm';
import selectWooUtils from 'select-woo-src/utils';
import selectWooArrayAdapter from 'select-woo-src/data/array';
import 'leaflet-iiif';
import 'leaflet-fullscreen';
import 'leaflet-side-by-side';
import 'bindings/select2-query';
import 'bindings/leaflet';


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
    this.compareMode = ko.observable(false);
    this.primaryCanvas = ko.observable();
    this.canvasObject = ko.observable();
    this.secondaryCanvasObject = ko.observable();
    this.secondaryCanvas = ko.observable();
    this.compareInstruction = ko.observable();
    this.primaryTilesLoaded = ko.observable(false);
    this.secondaryTilesLoaded = ko.observable(false);
    this.selectPrimaryPanel = ko.observable(true);
    this.secondaryLabel = ko.observable();
    this.imageToolSelector = ko.observable(this.canvas());
    this.floatingLocation = ko.observable("left");
    this.showImageModifiers = ko.observable(false);
    this.renderContext = ko.observable(params.renderContext);
    this.showModeSelector = ko.observable(true);
    this.primaryLayerLoaded = true;
    this.secondaryLayerLoaded = true;
    let primaryPanelFilters;
    let secondaryPanelFilters;
    const layers = [];
    const secondaryLayers = [];
    const cachedAnnotations = {};
    this.origCanvasLabel = ko.observable();

    this.selectPrimaryPanel.subscribe((value) => {
        // if true, primary panel is being selected
        if(value){
            this.imageToolSelector(this.canvas());
            self.origCanvasLabel(self.canvasObject().label);
            self.canvasLabel(self.canvasObject().label);
            // preserve state of secondary filters, if secondaryCanvas is set
            if(self.secondaryCanvas()) {
                secondaryPanelFilters = self.canvasFilterObject();
                if(primaryPanelFilters) {
                    self.brightness(primaryPanelFilters.brightness);
                    self.saturation(primaryPanelFilters.saturation);
                    self.contrast(primaryPanelFilters.contrast);
                    self.greyscale(primaryPanelFilters.greyscale);
                }
            }
        } else {
            this.imageToolSelector(this.secondaryCanvas());
            primaryPanelFilters = self.canvasFilterObject();
            self.origCanvasLabel(self.secondaryCanvasObject()?.label);
            self.canvasLabel(self.secondaryCanvasObject()?.label);
            if(secondaryPanelFilters) {
                self.brightness(secondaryPanelFilters.brightness);
                self.saturation(secondaryPanelFilters.saturation);
                self.contrast(secondaryPanelFilters.contrast);
                self.greyscale(secondaryPanelFilters.greyscale);
            } else {
                self.brightness(100);
                self.saturation(100);
                self.contrast(100);
                self.greyscale(false);
            }
        }
    });

    this.imageToolSelector.subscribe((value) => {
        if(this.selectPrimaryPanel() && this.canvas() !== this.imageToolSelector()){
            this.canvas(this.imageToolSelector());
        } else if (!this.selectPrimaryPanel() && this.secondaryCanvas() !== this.imageToolSelector()){
            this.secondaryCanvas(this.imageToolSelector());
        }
    });

    this.compareMode.subscribe((mode) => {
        if(!mode){
            const map = self.map();

            if(secondaryCanvasLayer && map.hasLayer(secondaryCanvasLayer)){
                try {
                    map.removeLayer(secondaryCanvasLayer);
                } catch(e){
                    // ignore/smother if remove layer fails
                }
            }

            if(sideBySideControl && sideBySideControl?._map){
                map.removeControl(sideBySideControl);
            }

            self.secondaryCanvas(undefined);
            self.secondaryLabel(undefined);
            self.showImageModifiers(false);
            self.selectPrimaryPanel(true);
        } else {
            self.selectPrimaryPanel(false);
            self.canvasClick(self.canvasObject());
            self.selectPrimaryPanel(true);
        }
    });

    this.panelRadio = ko.pureComputed(() => {
        if(!this.compareMode()){
            return "single";
        } else {
            return "double";
        }
    });

    this.showLogo = ko.pureComputed(() => {
        const imageExtenstion = ["bmp", "gif", "jpeg", "jpg", "png", "svg", "tif", "tiff", "webp"]
        return !!imageExtenstion.find((ext) => self.manifestLogo().endsWith(ext))
    });

    this.buildAnnotationNodes = params.buildAnnotationNodes || function(json) {
        self.annotationNodes(
            json.map((node) => {
                const annotations = ko.observableArray();
                const updateAnnotations = async function() {
                    var canvas = self.canvas();
                    if (canvas) {
                        const annotationsUrl = arches.urls.iiifannotations + '?canvas=' + canvas + '&nodeid=' + node.nodeid;
                        if(!cachedAnnotations[annotationsUrl]){
                            const response = await window.fetch(annotationsUrl);

                            const jsonResponse = await response.json();
                            cachedAnnotations[annotationsUrl] = jsonResponse;
                        }
                        const annotation = cachedAnnotations[annotationsUrl];

                        annotation.features.forEach(function(feature) {
                            feature.properties.graphName = node['graph_name'];
                        });
                        annotations(annotation.features);

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
                                'reportURL': arches.urls.resource_report,
                                'translations': arches.translations
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
                    canvas.id = self.getCanvasService(canvas);
                    canvas.text = canvas.label;
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
        closeOnSelect: true,
        allowClear: true,
        placeholder: arches.translations.selectAManifest,
        ajax: {
            url: arches.urls.iiifmanifest,
            dataType: 'json',
            quietMillis: 250,
            data: function(requestParams) {
                let term = requestParams.term || '';
                let page = requestParams.page || 1;
                var data = {
                    start: (page-1)*limit,
                    limit: limit
                };
                queryTerm = term;
                if (term) data.query = term;
                return data;
            },
            processResults: function(data) {
                var results = data.results;
                if (validateUrl(queryTerm)) results.unshift({
                    url: queryTerm,
                    label: queryTerm
                });
                results.forEach((item) => {
                    item.id = item.url;
                });
                return {
                    "results": results,
                    "pagination": {
                        "more": data.more
                    }
                };
            }
        },
        templateResult: function(item) {
            return item.label;
        },
        templateSelection: function(item) {
            return item.label;
        }
    };

    var CustomDataAdapterClass = function(){
        return {};
    };

    var CustomDataAdapter = selectWooUtils.Decorate(selectWooArrayAdapter, CustomDataAdapterClass);
    CustomDataAdapter.prototype.current = function(callback){
        const canvasObj = self.canvases().find(canvas => self.getCanvasService(canvas) == this.options.options.value());
        callback([canvasObj]);
    };
    CustomDataAdapter.prototype.query = function(params, callback){
        // self.canvases.subscribe(function(canvases){
        //     callback({"results": canvases});
        // });
        callback({"results": self.canvases()});
    };

    const splitSelectConfig = {
        clickBubble: true,
        multiple: false,
        closeOnSelect: true,
        allowClear: false,
        dataAdapter: CustomDataAdapter,
        dropdownCssClass: "split-controls-drop",
        templateResult: function(item) {
            if(item.loading){
                return "";
            }
            return $(`<div class="image"><img src="${item.thumbnail}" height="50"/></div><div class="title">${item.label}</div>`); 
        },
        templateSelection: function(item) {
            return item?.label;
        }
    };

    this.rightSideSelectConfig = {
        ...splitSelectConfig,
        value: this.secondaryCanvas
    };

    this.leftSideSelectConfig = {
        ...splitSelectConfig,
        value: this.canvas
    };
    
    this.imageToolConfig = {
        ...splitSelectConfig,
        value: this.imageToolSelector
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
        if (expandGallery) { 
            self.compareMode(false);
            self.showGallery(true);
        }
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

    this.imagePropertyUpdate = (location, viewmodel, event) => {
        if(self.floatingLocation() == location || !self.showImageModifiers()){
            self.showImageModifiers(!self.showImageModifiers());
        }
        self.floatingLocation(location);
        if(self.floatingLocation() == "left") {
            self.selectPrimaryPanel(true);
        } else {
            self.selectPrimaryPanel(false);
        }

    };

    this.fileUpdate = (...params) => {
        console.log(params);
    };

    let canvasLayer;
    let secondaryCanvasLayer;
    let sideBySideControl;
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

    this.canvasFilterObject = ko.pureComputed(() => {
        const brightness = self.brightness();
        const contrast = self.contrast();
        const saturation = self.saturation();
        const greyscale = self.greyscale();

        return { brightness, contrast, saturation, greyscale };
    });

    var updateCanvasLayerFilter = function() {
        var filter = self.canvasFilter();
        var map = self.map();
        let layer;
        if (map) {
            if(self.selectPrimaryPanel()){
                layer = map.getPane('tilePane').querySelector('.iiif-layer-primary');
            } else {
                layer = map.getPane('tilePane').querySelector('.iiif-layer-secondary');
            }
            if(layer && layer !== null){
                layer.style.filter = filter;
            }
        }
    };
    this.canvasFilter.subscribe(updateCanvasLayerFilter);

    this.resetImageSettings = function() {
        self.brightness(100);
        self.contrast(100);
        self.saturation(100);
        self.greyscale(false);
    };

    const zoomToBounds = (map, layer) => {
        var initialZoom = layer._getInitialZoom(map.getSize());
        var imageSize = layer._imageSizes[initialZoom];
        var sw = map.options.crs.pointToLatLng(L.point(0, imageSize.y), initialZoom);
        var ne = map.options.crs.pointToLatLng(L.point(imageSize.x, 0), initialZoom);
        var bounds = L.latLngBounds(sw, ne);
        map.fitBounds(bounds);
    };

    const loadComparison = () => {
        const map = self.map();
        if(map && canvasLayer.getContainer() && secondaryCanvasLayer?.getContainer() /*self.primaryLayerLoaded && self.secondaryLayerLoaded*/){
            // remove the control if it's been added to the map already  
            if(self.zoomToCanvas){
                zoomToBounds(map, canvasLayer);
                //map.fitBounds(canvasLayer.getBounds())
                self.zoomToCanvas = false;
            }
            // add the control back, comparing the appropriate layers
            if(!sideBySideControl){
                sideBySideControl = L.control.sideBySide(canvasLayer, secondaryCanvasLayer);
            } else {
                sideBySideControl.setLeftLayers(canvasLayer);
                sideBySideControl.setRightLayers(secondaryCanvasLayer);
            }

            if(!sideBySideControl?._map) {
                sideBySideControl.addTo(map);
            }
        }
    };

    var updatePrimaryCanvasLayer = function() {
        const map = self.map();
        const canvas = self.canvas();

        if(self.selectPrimaryPanel() && canvas && canvas != self.imageToolSelector()){
            self.imageToolSelector(canvas);
        }

        if (map && canvas) {
            if (canvasLayer && map.hasLayer(canvasLayer)) {
                try {
                    map.removeLayer(canvasLayer);
                } catch(e){
                    // ignore/smother if remove layer fails
                }
                canvasLayer = undefined;
            }
            if (canvas) {
                const layerInfoUrl = canvas + '/info.json';
                canvasLayer = getLayer(layerInfoUrl, layers);

                if(!canvasLayer){
                    canvasLayer = L.tileLayer.iiif(layerInfoUrl, {
                        fitBounds: false,
                        className: "iiif-layer-primary"
                    });

                    canvasLayer.on('load', () => {
                        if(self.compareMode()){
                            loadComparison();
                        } else if (!self.compareMode() && self.zoomToCanvas && canvasLayer){
                            zoomToBounds(map, canvasLayer);
                            self.zoomToCanvas = false;
                        }
                    });

                    layers.push(canvasLayer);
                }
                canvasLayer.addTo(map);
                updateCanvasLayerFilter();

            }
        }
    };

    const getLayer = (url, layers) => {
        const match = layers.filter(layer => layer._infoUrl == url);
        if(match.length > 0){
            return match[0];
        }
    };

    const updateSecondaryCanvasLayer = () => {
        const map = self.map();
        const primaryCanvas = self.canvas();
        const secondaryCanvas = self.secondaryCanvas();
        if(secondaryCanvas && secondaryCanvas != self.imageToolSelector()){
            self.selectPrimaryPanel(false);
            self.imageToolSelector(secondaryCanvas);
        }

        if (map && primaryCanvas && secondaryCanvas) {
            if(secondaryCanvasLayer && map.hasLayer(secondaryCanvasLayer)) {
                try {
                    map.removeLayer(secondaryCanvasLayer);
                } catch(e){
                    // ignore/smother if remove layer fails
                }
                secondaryCanvasLayer = undefined;
            }

            const layerInfoUrl = secondaryCanvas + '/info.json';
            secondaryCanvasLayer = getLayer(layerInfoUrl, secondaryLayers);

            if(!secondaryCanvasLayer){
                secondaryCanvasLayer = L.tileLayer.iiif(layerInfoUrl, {
                    fitBounds: false,
                    className: "iiif-layer-secondary"
                });

                secondaryCanvasLayer.on('load', () => {
                    if(self.compareMode()){
                        loadComparison();
                    }
                });

                secondaryLayers.push(secondaryCanvasLayer);
            }
            secondaryCanvasLayer.addTo(map);
            
            updateCanvasLayerFilter();
        }
    };

    this.map.subscribe(function(map) {
        L.control.fullscreen({
            fullscreenElement: $(map.getContainer()).closest('.workbench-card-wrapper')[0]
        }).addTo(map);
        updatePrimaryCanvasLayer();
        map.addLayer(annotationFeatureGroup);
    });
    this.canvas.subscribe(updatePrimaryCanvasLayer);
    this.secondaryCanvas.subscribe(updateSecondaryCanvasLayer);

    this.setSecondaryCanvas = (canvas) => {
        const service = self.getCanvasService(canvas);
        if(service){
            self.secondaryCanvas(service);
        }
    };

    this.selectCanvas = function(canvas) {
        
        const service = self.getCanvasService(canvas);

        if (service && self.selectPrimaryPanel()) {
            self.canvas(service);
            self.canvasObject(canvas);
            self.canvasLabel(self.getManifestDataValue(canvas, 'label', true));
        } else {
            self.secondaryCanvas(service);
            self.secondaryCanvasObject(canvas);
            self.canvasLabel(self.getManifestDataValue(canvas, 'label', true));
        }
        self.origCanvasLabel(self.canvasLabel());
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

                    self.secondaryCanvasLayer = undefined;
                    self.canvasLayer = undefined;
                    const service = self.getCanvasService(canvas);
                    self.zoomToCanvas = true;
                    self.canvas(service);
                    self.canvasObject(canvas);

                    if(self.compareMode()){
                        self.secondaryCanvas(service);
                        self.secondaryCanvasObject(canvas);
                    }
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
    template: iiifViewerTemplate,
});
export default IIIFViewerViewmodel;
