define([
    'jquery',
    'underscore',
    'arches',
    'knockout',
    'knockout-mapping',
    'text!templates/views/components/map-popup.htm'
], function($, _, arches, ko, koMapping, popupTemplate) {
    const viewModel = function(params) {

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


        this.mapEventHandler = function(eventName,additionalParam,data,event){
            if(event.type=="click" || (event.type=="keyup" && (event.which==13 || event.keyCode==13))){
                var parent;
                var provisionalEdit;
                switch (eventName){
                case "toggle tab":
                    data.toggleTab(additionalParam);
                    break;
                case "hide side panel":
                    data.hideSidePanel();
                    break;
                case "active basemap":
                    additionalParam.activeBasemap(data);
                    break;
                case "overlay":
                    data.onMap(!data.onMap());
                    data.updateParent(additionalParam);
                    break;
                case "select features":
                    if(data.mapCard.isSelectable([data.feature])){
                        data.selectFeature([data.feature]);
                    }
                    break;
                case "open editing":
                    window.open(data.editURL + data.resourceinstanceid);
                    break;
                case "reset provisional edits":
                    data.provisionalTileViewModel.resetAuthoritative();
                    break;
                case "delete provisional edits":
                    data.provisionalTileViewModel.deleteAllProvisionalEdits();
                    break;
                case "select provisional edit":
                    parent = additionalParam[0];
                    provisionalEdit = additionalParam[1];
                    parent.provisionalTileViewModel.selectProvisionalEdit(provisionalEdit);
                    break;
                case "reject provisional edit":
                    parent = additionalParam[0];
                    provisionalEdit = additionalParam[1];
                    parent.provisionalTileViewModel.rejectProvisionalEdit(provisionalEdit);
                    break;
                case "clear features":
                    data.geoJSONString(undefined);
                    break;
                case "update features":
                    data.updateGeoJSON();
                    break;
                case "toggle help":
                    data.card.model.get('helpactive')(additionalParam);
                    break;
                case "show geojson errors":
                    additionalParam[0].featureLookup[additionalParam[1]].dropErrors([]);
                    break;
                case "feature item":
                    additionalParam.fitFeatures([data]);
                    break;
                case "edit feature":
                    additionalParam.editFeature(data);
                    break;
                case "delete feature":
                    additionalParam.deleteFeature(data);
                    break;
                case "edit geojson":
                    additionalParam[0].editGeoJSON(additionalParam[0].featureLookup[additionalParam[1]].features(), additionalParam[1]);
                    break;
                case "edit coordinates":
                    additionalParam.coordinateEditing(true);
                    break;
                case "add buffer":
                    additionalParam[0].bufferNodeId(additionalParam[1]);
                    break;
                case "zoom to all":
                    additionalParam[0].fitFeatures(self.featureLookup[additionalParam[1]].features());
                    break;
                case "delete tile":
                    data.deleteTile();
                    break;
                case "reset tile":
                    additionalParam.reset();
                    break;
                case "save tile":
                    data.saveTile();
                    break;
                case "add card":
                    if (additionalParam.isWritable && !data.preview) {
                        data.updateTiles();
                        data.saveTile();
                    }

                }
            }
        };

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
        this.getPopupData = function(features) {
            const popupFeatures = features.map(feature => {
                var data = feature.properties;
                var id = data.resourceinstanceid;
                data.showEditButton = self.canEdit;
                const descriptionProperties = ['displayname', 'graph_name', 'map_popup'];
                if (id) {
                    if (!self.resourceLookup[id]){
                        data = _.defaults(data, {
                            'loading': true,
                            'displayname': '',
                            'graph_name': '',
                            'map_popup': '',
                            'feature': feature,
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
                        descriptionProperties.forEach(prop => data[prop] = ko.observable(data[prop]));
                        data.reportURL = arches.urls.resource_report;
                        data.editURL = arches.urls.resource_editor;
                        self.resourceLookup[id] = data;
                        $.get(arches.urls.resource_descriptors + id, function(data) {
                            data.loading = false;
                            descriptionProperties.forEach(prop => self.resourceLookup[id][prop](data[prop]));
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
            });

            const unique = [];
            const uniquePopupFeatures = popupFeatures.filter(feature => {
                feature.active = ko.observable(false);
                if (!unique.includes(feature)) {
                    unique.push(feature);
                    return true;
                }
            });
            uniquePopupFeatures[0].active(true);

            return {
                popupFeatures: uniquePopupFeatures,
                loading: ko.observable(false),
                activeFeature: uniquePopupFeatures[0],
                advanceFeature: function(direction) {
                    const map = self.map();
                    const activeFeatureIndex = uniquePopupFeatures.findIndex(feature => feature.active());
                    let activeFeature;
                    uniquePopupFeatures[activeFeatureIndex].active(false);
                    if (direction==='right') {
                        if (activeFeatureIndex + 1 >= uniquePopupFeatures.length) {
                            activeFeature = uniquePopupFeatures[0];
                        } else {
                            activeFeature = uniquePopupFeatures[activeFeatureIndex + 1];
                        }
                    } else {
                        if (activeFeatureIndex == 0) {
                            activeFeature = uniquePopupFeatures[uniquePopupFeatures.length - 1];
                        } else {
                            activeFeature = uniquePopupFeatures[activeFeatureIndex - 1];
                        }
                    }
                    activeFeature.active(true);
                    if (map.getStyle()) {
                        uniquePopupFeatures.forEach(feature=>{
                            const featureId = feature.feature.id;
                            if (featureId) {
                                if (featureId === activeFeature.feature.id) {
                                    map.setFeatureState(activeFeature.feature, { hover: true });
                                } else {
                                    map.setFeatureState(feature.feature, { hover: false });
                                }
                            }
                        });
                    }
                }
            };
        };

        this.popupTemplate = popupTemplate;

        this.onFeatureClick = function(features, lngLat, MapboxGl) {
            const map = self.map();
            const mapStyle = map.getStyle();
            self.popup = new MapboxGl.Popup()
                .setLngLat(lngLat)
                .setHTML(self.popupTemplate)
                .addTo(map);
            ko.applyBindingsToDescendants(
                self.getPopupData(features),
                self.popup._content
            );
            features.forEach(feature=>{
                if (mapStyle && feature.id) map.setFeatureState(feature, { selected: true });
                self.popup.on('close', function() {
                    if (mapStyle && feature.id) {
                        map.setFeatureState(feature, { selected: false });
                        map.setFeatureState(feature, { hover: false });
                    }
                    self.popup = undefined;
                });
            });
        };

        this.setupMap = function(map) {
            map.on('load', function() {
                require(['mapbox-gl', 'mapbox-gl-geocoder'], function(MapboxGl, MapboxGeocoder) {
                    map.addControl(new MapboxGl.NavigationControl(), 'top-left');
                    map.addControl(new MapboxGl.FullscreenControl({
                        container: $(map.getContainer()).closest('.workbench-card-wrapper')[0]
                    }), 'top-left');
                    map.addControl(new MapboxGeocoder({
                        accessToken: MapboxGl.accessToken,
                        mapboxgl: MapboxGl,
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
                        const popupFeatures = _.filter(
                            map.queryRenderedFeatures(e.point),
                            self.isFeatureClickable
                        );
                        if (popupFeatures.length) {
                            self.onFeatureClick(popupFeatures, e.lngLat, MapboxGl);
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
            });
        };
    };
    return viewModel;
});
