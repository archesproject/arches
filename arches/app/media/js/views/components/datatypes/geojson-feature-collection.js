define([
    'jquery',
    'arches',
    'knockout',
    'underscore',
    'bindings/color-picker',
    'bindings/mapbox-gl',
    'bindings/codemirror',
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
                    console.log("update map style has been run")
                    _.each(overlays, function(layer) {
                        switch (layer.id) {
                        case "resources-fill-" + params.nodeid:
                            layer.paint["fill-color"] = self.config.fillColor();
                            break;
                        case "resources-line-halo-" + params.nodeid:
                            halo_weight_value = self.config.haloWeight();
                            //if empty string or combination of int+str convert to default
                            if(halo_weight_value === ""){halo_weight_value = 4} 
                            else (halo_weight_value = Number(halo_weight_value));
                            layer.paint["line-width"] = halo_weight_value
                            layer.paint["line-color"] = self.config.lineHaloColor();
                            break;
                        case "resources-line-" + params.nodeid:
                            weight_value = self.config.weight();
                            if(weight_value === ""){weight_value = 2} 
                            else (weight_value = Number(weight_value));
                            layer.paint["line-width"] = weight_value;
                            layer.paint["line-color"] = self.config.lineColor();
                            break;
                        case "resources-poly-outline-" + params.nodeid:
                            outline_weight_value = self.config.outlineWeight();
                            if(outline_weight_value === ""){outline_weight_value = 2} 
                            else (outline_weight_value = Number(outline_weight_value));
                            layer.paint["line-width"] = outline_weight_value;
                            layer.paint["line-color"] = self.config.outlineColor();
                            break;
                        case "resources-point-halo-" + params.nodeid:
                            halo_radius_value = self.config.haloRadius();
                            if(halo_radius_value === ""){halo_radius_value = 4} 
                            else (halo_radius_value = Number(halo_radius_value));    
                            layer.paint["circle-radius"] = halo_radius_value                        
                        case "resources-cluster-point-halo-" + params.nodeid:
                            layer.paint["circle-color"] = self.config.pointHaloColor();
                            break;
                        case "resources-point-" + params.nodeid:
                            radius_value = self.config.radius();
                            if(radius_value === ""){radius_value = 2} 
                            else (radius_value = Number(radius_value));   
                            layer.paint["circle-radius"] = radius_value;
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
                    // do saving of config values at end to avoid double save button issue
                    self.config.haloWeight(halo_weight_value)
                    self.config.weight(weight_value)
                    self.config.outlineWeight(outline_weight_value)
                    self.config.haloRadius(halo_radius_value)
                    self.config.radius(radius_value)

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
