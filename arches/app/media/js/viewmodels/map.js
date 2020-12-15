define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'knockout-mapping',
    'mapbox-gl',
    'mapbox-gl-geocoder',
    'text!templates/views/components/map-popup.htm'
], function($, _, arches, ko, koMapping, mapboxgl, MapboxGeocoder, popupTemplate) {
    var viewModel = function(params) {
        var self = this;
        var geojsonSourceFactory = function() {
            return {
                "type": "geojson",
                "generateId": true,
                "data": {
                    "type": "FeatureCollection",
                    "features": []
                }
            };
        };

        var x = ko.unwrap(params.x) ? params.x : arches.mapDefaultX;
        var y = ko.unwrap(params.y) ? params.y : arches.mapDefaultY;
        var bounds = ko.unwrap(params.bounds) ? params.bounds : arches.hexBinBounds;
        var zoom = ko.unwrap(params.zoom) ? params.zoom : arches.mapDefaultZoom;
        var minZoom = arches.mapDefaultMinZoom;
        var maxZoom = arches.mapDefaultMaxZoom;
        var sources = Object.assign({
            "resource": geojsonSourceFactory(),
            "search-results-hex": geojsonSourceFactory(),
            "search-results-hashes": geojsonSourceFactory(),
            "search-results-points": geojsonSourceFactory()
        }, arches.mapSources, params.sources);
        var mapLayers = params.mapLayers || arches.mapLayers;

        this.map = ko.isObservable(params.map) ? params.map : ko.observable();
        this.popupTemplate = popupTemplate;
        this.basemaps = params.basemaps || [];
        this.overlays = params.overlaysObservable || ko.observableArray();
        this.activeBasemap = params.activeBasemap || ko.observable();
        this.activeTab = ko.observable(params.activeTab);
        this.hideSidePanel = function() {
            self.activeTab(undefined);
        };
        this.activeTab.subscribe(function() {
            var map = self.map();
            if (map && map.getStyle()) setTimeout(function() { map.resize(); }, 1);
        });

        mapLayers.forEach(function(layer) {
            if (!layer.isoverlay) {
                if (!params.basemaps) self.basemaps.push(layer);
                if (layer.addtomap && !params.activeBasemap) self.activeBasemap(layer);
            }
            else if (!params.overlaysObservable) {
                if (layer.searchonly && !params.search) return;
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
            var layers = [];
            self.overlays().forEach(function(layer) {
                if (layer.onMap()) {
                    var opacity = layer.opacity();
                    layers = layer.layer_definitions.map(function(layer) {
                        return updateOpacity(layer, opacity);
                    }).concat(layers);
                }
            });
            layers = self.activeBasemap().layer_definitions.slice(0).concat(layers);
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
                center: [
                    parseFloat(ko.unwrap(x)),
                    parseFloat(ko.unwrap(y))
                ],
                zoom: parseFloat(ko.unwrap(zoom)),
            },
            maxZoom: maxZoom,
            minZoom: minZoom,
        };
        if (!params.usePosition) {
            this.mapOptions.bounds = bounds;
            this.mapOptions.fitBoundsOptions = params.fitBoundsOptions;
        }

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
            if (style) {
                style.layers = layers;
                map.setStyle(style);
            }
        };

        this.isFeatureClickable = function(feature) {
            return feature.properties.resourceinstanceid;
        };

        this.expandSidePanel = function() {
            return false;
        };

        this.resourceLookup = {};
        this.getPopupData = function(feature) {
            var data = feature.properties;
            var id = data.resourceinstanceid;
            data.showEditButton = false;
            if (id) {
                if (!self.resourceLookup[id]){
                    data = _.defaults(data, {
                        'loading': true,
                        'displayname': '',
                        'graph_name': '',
                        'map_popup': ''
                    });
                    if (data.permissions) {
                        try {
                            data.permissions = JSON.parse(ko.unwrap(data.permissions));
                        } catch (err) {
                            data.permissions = koMapping.toJS(ko.unwrap(data.permissions));
                        }
                        if (data.permissions.users_without_edit_perm.indexOf(ko.unwrap(self.userid)) === -1) {
                            data.showEditButton = true;
                        }
                    }
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
            } else {
                data.resourceinstanceid = ko.observable(false);
                data.loading = ko.observable(false);
                data.feature = feature;
                data.mapCard = self;
                return data;
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
            if (map.getStyle() && feature.id) map.setFeatureState(feature, { selected: true });
            self.popup.on('close', function() {
                if (map.getStyle() && feature.id) map.setFeatureState(feature, { selected: false });
                self.popup = undefined;
            });
        };

        this.setupMap = function(map) {
            map.on('load', function() {
                map.addControl(new mapboxgl.NavigationControl(), 'top-left');
                map.addControl(new mapboxgl.FullscreenControl({
                    container: $(map.getContainer()).closest('.workbench-card-wrapper')[0]
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
                    var style = map.getStyle();
                    if (hoverFeature && hoverFeature.id && style) map.setFeatureState(hoverFeature, { hover: false });
                    hoverFeature = _.find(
                        map.queryRenderedFeatures(e.point),
                        self.isFeatureClickable
                    );
                    if (hoverFeature && hoverFeature.id && style) map.setFeatureState(hoverFeature, { hover: true });

                    map.getCanvas().style.cursor = hoverFeature ? 'pointer' : '';
                    if (self.map().draw_mode) {
                        var crosshairModes = [
                            "draw_point",
                            "draw_line_string",
                            "draw_polygon",
                        ];
                        map.getCanvas().style.cursor = crosshairModes.includes(self.map().draw_mode) ? "crosshair" : "";
                    }
                });

                map.draw_mode = null;

                map.on('click', function(e) {
                    if (hoverFeature) {
                        self.onFeatureClick(hoverFeature, e.lngLat);
                    }
                });

                self.map(map);
                if (params.fitBounds){
                    var padding = 40;
                    var activeTab = self.activeTab();
                    var options = {
                        padding: {
                            top: padding,
                            left: padding + (activeTab ? 200: 0),
                            bottom: padding,
                            right: padding + (activeTab ? 200: 0)
                        },
                        animate: false
                    };
                    var bounds = params.fitBounds();
                    if (bounds) {
                        map.fitBounds(bounds, options);
                    } else {
                        var fitBounds = params.fitBounds.subscribe(function(bounds) {
                            map.fitBounds(bounds, options);
                            fitBounds.dispose();
                        });
                    }
                }
                setTimeout(function() { map.resize(); }, 1);

                if (ko.isObservable(zoom)) {
                    map.on('zoomend', function() {
                        zoom(map.getZoom());
                    });
                    zoom.subscribe(function(level) {
                        level = parseFloat(level);
                        if (level) map.setZoom(level);
                    });
                }

                if (ko.isObservable(x)) {
                    map.on('dragend', function() {
                        var center = map.getCenter();
                        x(center.lng);
                    });
                    x.subscribe(function(lng) {
                        var center = map.getCenter();
                        lng = parseFloat(lng);
                        if (lng) {
                            center.lng = lng;
                            map.setCenter(center);
                        }
                    });
                }

                if (ko.isObservable(y)) {
                    map.on('dragend', function() {
                        var center = map.getCenter();
                        y(center.lat);
                    });
                    y.subscribe(function(lat) {
                        var center = map.getCenter();
                        lat = parseFloat(lat);
                        if (lat) {
                            center.lat = lat;
                            map.setCenter(center);
                        }
                    });
                }
            });
        };
    };
    return viewModel;
});
