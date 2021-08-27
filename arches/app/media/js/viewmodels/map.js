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

        this.activeTab = ko.observable(ko.unwrap(params.activeTab));
        this.canEdit = params.userCanEditResources;
        this.canRead = params.userCanReadResources;

        var boundingOptions = {
            padding: {
                top: 40,
                left: 40 + (self.activeTab() ? 200: 0),
                bottom: 40,
                right: 40 + (self.activeTab() ? 200: 0)
            },
            animate: false
        };

        this.map = ko.isObservable(params.map) ? params.map : ko.observable();
        this.map.subscribe(function(map) {
            self.setupMap(map);

            if (ko.unwrap(params.x) && ko.unwrap(params.y)) {
                var center = map.getCenter();
            
                lng = parseFloat(params.x());
                lat = parseFloat(params.y());
                
                if (lng) { center.lng = lng; }
                if (lat) { center.lat = lat; }
    
                map.setCenter(center);
            }

            if (ko.unwrap(params.zoom)) {
                map.setZoom(ko.unwrap(params.zoom));
            }

            if (ko.unwrap(params.bounds)) {
                map.fitBounds(ko.unwrap(params.bounds), boundingOptions);
            }

        });

        this.bounds = ko.observable(ko.unwrap(params.bounds) || arches.hexBinBounds);
        this.bounds.subscribe(function(bounds) {
            if (bounds && self.map()) {
                self.map().fitBounds(bounds, boundingOptions);
            }

            if (ko.isObservable(params.fitBounds) && params.fitBounds() !== bounds){
                params.fitBounds(bounds);
            }
        });

        this.centerX = ko.observable(ko.unwrap(params.x) || arches.mapDefaultX);
        this.centerX.subscribe(function(lng) {
            if (lng && self.map()) {
                var center = self.map().getCenter();
                center.lng = lng;
            
                self.map().setCenter(center);
            }
            if (ko.isObservable(params.x) && params.x() !== lng) {
                params.x(lng);
            }
        });

        this.centerY = ko.observable(ko.unwrap(params.y) || arches.mapDefaultY);
        this.centerY.subscribe(function(lat) {
            if (lat && self.map()) {
                var center = self.map().getCenter();
                center.lat = lat;
            
                self.map().setCenter(center);
            }
            if (ko.isObservable(params.y) && params.y() !== lat) {
                params.y(lat);
            }
        });
        
        this.zoom = ko.observable(ko.unwrap(params.zoom) || arches.mapDefaultZoom);
        this.zoom.subscribe(function(level) {
            if (level && self.map()) { self.map().setZoom(level) };

            if (ko.isObservable(params.zoom) && params.zoom() !== level) {
                params.zoom(level);
            }
        });

        this.overlayConfigs = ko.observableArray(ko.unwrap(params.overlayConfigs));
        this.overlayConfigs.subscribe(function(overlayConfigs) {
            if (ko.isObservable(params.overlayConfigs)) {
                params.overlayConfigs(overlayConfigs)
            }
        })
        
        this.activeBasemap = ko.observable();  // params.basemap is a string, activeBasemap is a map. Cannot initialize from params.
        this.activeBasemap.subscribe(function(basemap) {
            if (ko.isObservable(params.basemap) && params.basemap() !== basemap.name) {
                params.basemap(basemap.name);
            }
        });

        var sources = Object.assign({
            "resource": geojsonSourceFactory(),
            "search-results-hex": geojsonSourceFactory(),
            "search-results-hashes": geojsonSourceFactory(),
            "search-results-points": geojsonSourceFactory()
        }, arches.mapSources, params.sources);
        
        this.basemaps = params.basemaps || [];
        this.overlays = params.overlaysObservable || ko.observableArray();
        
        var mapLayers = params.mapLayers || arches.mapLayers;
        mapLayers.forEach(function(layer) {
            if (!layer.isoverlay) {
                if (!params.basemaps) self.basemaps.push(layer);
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
                
                layer.updateParent = function(parent) {
                    if (self.overlayConfigs.indexOf(layer.maplayerid) === -1) {
                        self.overlayConfigs.push(layer.maplayerid)
                        layer.opacity(100)
                    } else {
                        self.overlayConfigs.remove(layer.maplayerid);
                        layer.opacity(0)
                    }
                    
                    if (parent !== self) {
                        parent.overlayConfigs(self.overlayConfigs())

                        if (params.inWidget) {
                            try {
                                parent.overlays.valueHasMutated();
                            } catch(e) {
                                console.log(e);
                            }
                        }
                    }
                };

                self.overlays.push(layer);
            }
        });
        
        if (!self.activeBasemap()) {
            var basemap = ko.unwrap(self.basemaps).find(function(basemap) {
                return ko.unwrap(params.basemap) === basemap.name;
            });

            if (!basemap && params.config) {
                basemap = ko.unwrap(self.basemaps).find(function(basemap) {
                    return params.config().basemap === basemap.name;
                });
            }

            if (!basemap) {
                basemap = ko.unwrap(self.basemaps).find(function(basemap) {
                    return basemap.addtomap;
                });
            }

            self.activeBasemap(basemap);
        }

        for (var overlay of self.overlays()) {
            if (
                ko.unwrap(self.overlayConfigs) && self.overlayConfigs.indexOf(overlay.maplayerid) > -1
                || params.search && overlay.addtomap
            ) {
                overlay.opacity(100);
            } else {
                overlay.opacity(0);
            }
        }

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
            if (ko.unwrap(self.activeBasemap)) {
                layers = ko.unwrap(self.activeBasemap).layer_definitions.slice(0).concat(layers);
            }
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
                    parseFloat(self.centerX()),
                    parseFloat(self.centerY()),
                ],
                zoom: parseFloat(self.zoom()),
            },
            maxZoom: arches.mapDefaultMaxZoom,
            minZoom: arches.mapDefaultMinZoom,
        };
        if (!params.usePosition) {
            this.mapOptions.bounds = self.bounds;
            this.mapOptions.fitBoundsOptions = params.fitBoundsOptions;
        }

        this.hideSidePanel = function() {
            self.activeTab(undefined);
        };

        this.toggleTab = function(tabName) {
            if (self.activeTab() === tabName) {
                self.activeTab(null);
            } else {
                self.activeTab(tabName);
            }
        };

        this.updateLayers = function(layers) {
            var style = self.map().getStyle();

            if (style) {
                style.layers = self.draw ? layers.concat(self.draw.options.styles) : layers;
                self.map().setStyle(style);
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
            data.showEditButton = self.canEdit;
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
                        if (data.permissions.users_without_edit_perm.indexOf(ko.unwrap(self.userid)) > 0) {
                            data.showEditButton = false;
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

        this.popupTemplate = popupTemplate;
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

                map.on('zoomend', function() {
                    self.zoom(
                        parseFloat(map.getZoom())
                    );
                });

                map.on('dragend', function() {
                    var center = map.getCenter();
                    
                    self.centerX(parseFloat(center.lng));
                    self.centerY(parseFloat(center.lat));
                });

                self.map(map);
            });
        };
    };
    return viewModel;
});
