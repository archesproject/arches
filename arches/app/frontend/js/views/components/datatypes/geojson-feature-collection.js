define([
    'jquery',
    'arches',
    'knockout',
    'underscore',
    'bindings/color-picker',
    'bindings/mapbox-gl',
    'bindings/codemirror',
    'codemirror/mode/javascript/javascript',
    'bindings/ckeditor'
], function($, arches, ko, _) {
    var name = 'geojson-feature-collection-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this;
            this.node = params;
            this.config = params.config;
            this.graph = params.graph;
            this.layer = params.layer;
            if (this.layer) {
                this.permissions = params.permissions;
                this.iconFilter = ko.observable('');
                this.icons = ko.computed(function() {
                    return _.filter(params.icons, function(icon) {
                        return icon.name.indexOf(self.iconFilter()) >= 0;
                    });
                });
                this.count = params.mapSource.count;
                this.loading = params.loading || ko.observable(false);
                var overlays = JSON.parse(this.layer.layer_definitions);
                var getDisplayLayers = function() {
                    var displayLayers = overlays;
                    if (self.config.advancedStyling()) {
                        var advancedStyle = self.config.advancedStyle();
                        try {
                            displayLayers = JSON.parse(advancedStyle);
                        }
                        catch (e) {
                            displayLayers = [];
                        }
                    }
                    if (params.mapSource.count > 0) {
                        _.each(displayLayers, function(layer){
                            layer["source-layer"] = params.nodeid;
                        });
                    }
                    return displayLayers;
                };
                if (params.mapSource.count === 0) {
                    _.each(overlays, function(overlay){
                        delete overlay["source-layer"];
                    });
                }
                this.selectedBasemapName = ko.observable('');
                var mapLayers = $.extend(true, {}, arches.mapLayers);
                this.basemaps = _.filter(mapLayers, function(layer) {
                    return !layer.isoverlay;
                });
                this.basemaps.forEach(function(basemap) {
                    basemap.select = function(){
                        self.selectedBasemapName(basemap.name);
                    };
                });
                var defaultBasemap = _.find(this.basemaps, function(basemap) {
                    return basemap.addtomap;
                });
                if (!defaultBasemap) {
                    defaultBasemap = this.basemaps[0];
                }
                if (defaultBasemap) {
                    this.selectedBasemapName(defaultBasemap.name);
                }
                var getBasemapLayers = function() {
                    return _.filter(self.basemaps, function(layer) {
                        return layer.name === self.selectedBasemapName();
                    }).reduce(function(layers, layer) {
                        return layers.concat(layer.layer_definitions);
                    }, []);
                };
                var sources = $.extend(true, {}, arches.mapSources);
                sources[params.mapSource.name] = JSON.parse(params.mapSource.source);
                _.each(sources, function(sourceConfig, name) {
                    if (sourceConfig.tiles) {
                        sourceConfig.tiles.forEach(function(url, i) {
                            if (url.startsWith('/')) {
                                sourceConfig.tiles[i] = window.location.origin + url;
                            }
                        });
                    }
                });

                var displayLayers = getDisplayLayers();
                var basemapLayers = getBasemapLayers();
                this.mapStyle = {
                    "version": 8,
                    "name": "Basic",
                    "metadata": {
                        "mapbox:autocomposite": true,
                        "mapbox:type": "template"
                    },
                    "sources": sources,
                    "sprite": "mapbox://sprites/mapbox/basic-v9",
                    "glyphs": "mapbox://fonts/mapbox/{fontstack}/{range}.pbf",
                    "layers": basemapLayers.concat(displayLayers)
                };
                this.zoom = ko.observable(arches.mapDefaultZoom);
                this.minZoom = ko.observable(arches.mapDefaultMinZoom);
                this.maxZoom = ko.observable(arches.mapDefaultMaxZoom);
                this.centerX = ko.observable(arches.mapDefaultX);
                this.centerY = ko.observable(arches.mapDefaultY);
                this.pitch = ko.observable(0);
                this.bearing = ko.observable(0);

                this.serviceURL = window.location.origin +
                    arches.urls.mvt(params.nodeid);

                this.map = null;
                this.setupMap = function(map) {
                    this.map = map;
                    if (this.node.layer.bounds) {
                        var bounds = [
                            [
                                this.node.layer.bounds.top_left.lon,
                                this.node.layer.bounds.bottom_right.lat
                            ],
                            [
                                this.node.layer.bounds.bottom_right.lon,
                                this.node.layer.bounds.top_left.lat
                            ]
                        ];
                        _.defer(function() {
                            map.fitBounds(bounds, {
                                padding: 20
                            });
                        }, 1);
                    }
                };

                var updateMapStyle = function() {
                    _.each(overlays, function(layer) {
                        switch (layer.id) {
                        case "resources-fill-" + params.nodeid:
                            layer.paint["fill-color"] = self.config.fillColor();
                            break;
                        case "resources-line-halo-" + params.nodeid:
                            layer.paint["line-width"] = parseInt(self.config.haloWeight());
                            if (!(self.config.haloWeight() > 0)) { layer.paint["line-width"] = 1; }
                            self.config.haloWeight(layer.paint["line-width"]);
                            layer.paint["line-color"] = self.config.lineHaloColor();
                            break;
                        case "resources-line-" + params.nodeid:
                            layer.paint["line-width"] = parseInt(self.config.weight());
                            if (!(self.config.weight() > 0)) { layer.paint["line-width"] = 1; }
                            self.config.weight(layer.paint["line-width"]);
                            layer.paint["line-color"] = self.config.lineColor();
                            break;
                        case "resources-poly-outline-" + params.nodeid:
                            layer.paint["line-width"] = parseInt(self.config.outlineWeight());
                            if (!(self.config.outlineWeight() > 0)) { layer.paint["line-width"] = 1; }
                            self.config.outlineWeight(layer.paint["line-width"]);
                            layer.paint["line-color"] = self.config.outlineColor();
                            break;
                        case "resources-point-halo-" + params.nodeid:
                            layer.paint["circle-radius"] = parseInt(self.config.haloRadius());
                            if (!(self.config.haloRadius() > 0)) { layer.paint["circle-radius"] = 1; }
                            self.config.haloRadius(layer.paint["circle-radius"]);
                        case "resources-cluster-point-halo-" + params.nodeid:
                            layer.paint["circle-color"] = self.config.pointHaloColor();
                            break;
                        case "resources-point-" + params.nodeid:
                            layer.paint["circle-radius"] = parseInt(self.config.radius());
                            if (!(self.config.radius() > 0)) { layer.paint["circle-radius"] = 1; }
                            self.config.radius(layer.paint["circle-radius"]);
                        case "resources-cluster-point-" + params.nodeid:
                            layer.paint["circle-color"] = self.config.pointColor();
                            break;
                        default:

                        }
                    });
                    var displayLayers = getDisplayLayers();
                    var basemapLayers = getBasemapLayers();
                    self.mapStyle.layers = basemapLayers.concat(displayLayers);
                    self.map.setStyle(self.mapStyle);
                };

                this.node.json.subscribe(updateMapStyle);
                this.selectedBasemapName.subscribe(updateMapStyle);

                this.config.advancedStyling.subscribe(function(value) {
                    if (value && !self.config.advancedStyle()) {
                        self.config.advancedStyle(JSON.stringify(overlays, null, '\t'));
                    }
                });

                this.saveNode = function() {
                    self.loading(true);
                    self.node.save(function() {
                        self.loading(false);
                    });
                };
            }
        },
        template: { require: 'text!datatype-config-templates/geojson-feature-collection' }
    });
    return name;
});
