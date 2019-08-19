define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'mapbox-gl',
    'mapbox-gl-geocoder',
    'text!templates/views/components/map-popup.htm',
    'bindings/mapbox-gl',
    'bindings/sortable'
], function($, _, arches, ko, mapboxgl, MapboxGeocoder, popupTemplate) {
    var viewModel = function(params) {
        var self = this;
        var geojsonSourceFactory = function() {
            return {
                "type": "geojson",
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            };
        };

        var x = params.x || arches.mapDefaultX;
        var y = params.y || arches.mapDefaultY;
        var zoom = params.zoom || arches.mapDefaultZoom;
        var bounds = params.bounds || arches.hexBinBounds;
        var sources = Object.assign({
            "resource": geojsonSourceFactory(),
            "search-results-hex": geojsonSourceFactory(),
            "search-results-hashes": geojsonSourceFactory(),
            "search-results-points": geojsonSourceFactory()
        }, arches.mapSources, params.sources);
        var mapLayers = params.mapLayers || arches.mapLayers;

        this.map = ko.isObservable(params.map) ? params.map : ko.observable();
        this.popupTemplate = popupTemplate;
        this.basemaps = [];
        this.overlays = ko.observableArray();
        this.activeBasemap = ko.observable();
        this.activeTab = ko.observable(params.activeTab);
        this.hideSidePanel = function() {
            self.activeTab(undefined);
        };
        this.activeTab.subscribe(function() {
            var map = self.map();
            if (map) setTimeout(function() { map.resize(); }, 1);
        });

        mapLayers.forEach(function(layer) {
            if (!layer.isoverlay) {
                self.basemaps.push(layer);
                if (layer.addtomap) self.activeBasemap(layer);
            }
            else {
                layer.opacity = ko.observable(layer.addtomap ? 100 : 0);
                layer.onMap = ko.pureComputed({
                    read: function() { return layer.opacity() > 0; },
                    write: function(value) {
                        layer.opacity(value ? 100 : 0);
                    }
                });
                self.overlays.push(layer);
            }
        });

        _.each(sources, function(sourceConfig) {
            if (sourceConfig.tiles) {
                sourceConfig.tiles.forEach(function(url, i) {
                    if (url.startsWith('/')) {
                        sourceConfig.tiles[i] = window.location.origin + url;
                    }
                });
            }
            if (sourceConfig.data && typeof sourceConfig.data === 'string' && sourceConfig.data.startsWith('/')) {
                sourceConfig.data = arches.urls.root + sourceConfig.data.substr(1);
            }
        });

        var multiplyStopValues = function(stops, multiplier) {
            _.each(stops, function(stop) {
                if (Array.isArray(stop[1])) {
                    multiplyStopValues(stop[1], multiplier);
                } else {
                    stop[1] = stop[1] * multiplier;
                }
            });
        };

        var updateOpacity = function(layer, val) {
            var opacityVal = Number(val) / 100.0;
            layer = JSON.parse(JSON.stringify(layer));
            if (layer.paint === undefined) {
                layer.paint = {};
            }
            _.each([
                'background',
                'fill',
                'line',
                'text',
                'icon',
                'raster',
                'circle',
                'fill-extrusion',
                'heatmap'
            ], function(opacityType) {
                var startVal = layer.paint ? layer.paint[opacityType + '-opacity'] : null;

                if (startVal) {
                    if (parseFloat(startVal)) {
                        layer.paint[opacityType + '-opacity'].base = startVal * opacityVal;
                    } else {
                        layer.paint[opacityType + '-opacity'] = JSON.parse(JSON.stringify(startVal));
                        if (startVal.base) {
                            layer.paint[opacityType + '-opacity'].base = startVal.base * opacityVal;
                        }
                        if (startVal.stops) {
                            multiplyStopValues(layer.paint[opacityType + '-opacity'].stops, opacityVal);
                        }
                    }
                } else if (layer.type === opacityType ||
                     (layer.type === 'symbol' && (opacityType === 'text' || opacityType === 'icon'))) {
                    layer.paint[opacityType + '-opacity'] = opacityVal;
                }
            }, self);
            return layer;
        };

        this.additionalLayers = params.layers;
        this.layers = ko.pureComputed(function() {
            var layers = self.activeBasemap().layer_definitions.slice(0);
            self.overlays().forEach(function(layer) {
                if (layer.onMap()) {
                    var opacity = layer.opacity();
                    layer.layer_definitions.forEach(function(layer) {
                        layers.push(updateOpacity(layer, opacity));
                    });
                }
            });
            if (this.additionalLayers) {
                layers = layers.concat(ko.unwrap(this.additionalLayers));
            }
            return layers;
        }, this);

        this.mapOptions = {
            style: {
                version: 8,
                sources: sources,
                sprite: arches.mapboxSprites,
                glyphs: arches.mapboxGlyphs,
                layers: self.layers(),
                center: [x, y],
                zoom: zoom
            },
            bounds: bounds,
            fitBoundsOptions: params.fitBoundsOptions
        };

        this.toggleTab = function(tabName) {
            if (self.activeTab() === tabName) {
                self.activeTab(null);
            } else {
                self.activeTab(tabName);
            }
        };

        this.updateLayers = function(layers) {
            var map = self.map();
            var style = map.getStyle();
            style.layers = layers;
            map.setStyle(style);
        };

        this.isFeatureClickable = function(feature) {
            return feature.properties.resourceinstanceid;
        };

        this.resourceLookup = {};
        this.getPopupData = function(feature) {
            var data = feature.properties;
            var id = data.resourceinstanceid;
            if (id) {
                if (!self.resourceLookup[id]){
                    data = _.defaults(data, {
                        'loading': true,
                        'displayname': '',
                        'graph_name': ''
                    });
                    data = ko.mapping.fromJS(data);
                    data.reportURL = arches.urls.resource_report;
                    data.editURL = arches.urls.resource_editor;

                    self.resourceLookup[id] = data;
                    $.get(arches.urls.resource_descriptors + id, function(data) {
                        data.loading = false;
                        ko.mapping.fromJS(data, self.resourceLookup[id]);
                    });
                }
                self.resourceLookup[id].feature = feature;
                self.resourceLookup[id].mapCard = self;
                return self.resourceLookup[id];
            }
        };

        this.onFeatureClick = function(feature, lngLat) {
            var map = self.map();
            self.popup = new mapboxgl.Popup()
                .setLngLat(lngLat)
                .setHTML(self.popupTemplate)
                .addTo(map);
            ko.applyBindingsToDescendants(
                self.getPopupData(feature),
                self.popup._content
            );
            map.setFeatureState(feature, { selected: true });
            self.popup.on('close', function() {
                map.setFeatureState(feature, { selected: false });
                self.popup = undefined;
            });
        };

        this.setupMap = function(map) {
            map.on('load', function() {
                map.addControl(new mapboxgl.NavigationControl(), 'top-left');
                map.addControl(new mapboxgl.FullscreenControl({
                    container: $(map.getContainer()).closest('.map-card-wrapper')[0]
                }), 'top-left');
                map.addControl(new MapboxGeocoder({
                    accessToken: mapboxgl.accessToken,
                    mapboxgl: mapboxgl,
                    placeholder: arches.geocoderPlaceHolder,
                    bbox: arches.hexBinBounds
                }), 'top-right');

                self.layers.subscribe(self.updateLayers);

                var hoverFeature;
                map.on('mousemove', function(e) {
                    if (hoverFeature) map.setFeatureState(hoverFeature, { hover: false });
                    hoverFeature = _.find(
                        map.queryRenderedFeatures(e.point),
                        self.isFeatureClickable
                    );
                    if (hoverFeature) map.setFeatureState(hoverFeature, { hover: true });
                    map.getCanvas().style.cursor = hoverFeature ? 'pointer' : '';
                });

                map.on('click', function(e) {
                    if (hoverFeature) {
                        self.onFeatureClick(hoverFeature, e.lngLat);
                    }
                });

                self.map(map);
                setTimeout(function() { map.resize(); }, 1);
            });
        };
    };
    ko.components.register('arches-map', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/map.htm'
        }
    });
    return viewModel;
});
