import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import arches from 'arches';
import geojsonFeatureCollectionDatatypeTemplate from 'templates/views/components/datatypes/geojson-feature-collection.htm';
import 'bindings/color-picker';
import 'bindings/mapbox-gl';
import 'bindings/codemirror';
import 'bindings/key-events-click';
import 'codemirror/mode/javascript/javascript';
import 'bindings/ckeditor';
import 'views/components/icon-selector';


var name = 'geojson-feature-collection-datatype-config';
const viewModel = function(params) {
    var self = this;
        
    this.node = params;
    this.config = params.config;
    this.graph = params.graph;
    this.layer = params.layer;
    this.search = params.search;

    if (this.search) {
        var filter = params.filterValue();
        this.op = ko.observable(filter.op || '~');
        this.node = params.node;
        this.searchValue = ko.observable(filter.val || '');
        this.filterValue = ko.computed(function() {
            return {
                op: self.op(),
                val: self.searchValue()
            };
        }).extend({ throttle: 750 });
        params.filterValue(this.filterValue());
        this.filterValue.subscribe(function(val) {
            params.filterValue(val);
        });
    } else {
        let haloWeightValue = self.config.haloWeight();
        let outlineWeightValue = self.config.outlineWeight();
        let weightValue = self.config.weight();
        let haloRadiusValue = self.config.haloRadius();
        let radiusValue = self.config.radius();
        let clusterDistanceValue = self.config.clusterDistance();
        let clusterMaxZoomValue = self.config.clusterMaxZoom();
        let clusterMinPointsValue = self.config.clusterMinPoints();
        let simplificationValue = self.config.simplification();
        if (this.layer) {
            this.permissions = params.permissions;
            this.iconFilter = ko.observable('');
            this.icons = ko.computed(function() {
                return _.filter(params.icons, function(icon) {
                    return icon.name.indexOf(self.iconFilter()) >= 0;
                });
            });
            if (!this.config.layerIcon()){
                this.config.layerIcon(this.layer.icon);
            }
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
                        haloWeightValue = self.config.haloWeight();
                        if (haloWeightValue === "") {
                            haloWeightValue = 4;
                        } else {
                            (haloWeightValue = Number(haloWeightValue));
                        }
                        layer.paint["line-width"] = haloWeightValue;
                        layer.paint["line-color"] = self.config.lineHaloColor();                    
                        break;

                    case "resources-line-" + params.nodeid:
                        weightValue = self.config.weight();
                        if (weightValue === "") {
                            weightValue = 4;
                        } else {
                            (weightValue = Number(weightValue));
                        }
                        layer.paint["line-width"] = weightValue;
                        layer.paint["line-color"] = self.config.lineColor();
                        break;

                    case "resources-poly-outline-" + params.nodeid:
                        outlineWeightValue = self.config.outlineWeight();
                        if (outlineWeightValue === "") {
                            outlineWeightValue = 2;
                        } else {
                            (outlineWeightValue = Number(outlineWeightValue));
                        }
                        layer.paint["line-width"] = outlineWeightValue;
                        layer.paint["line-color"] = self.config.outlineColor();
                        break;

                    case "resources-point-halo-" + params.nodeid:
                        haloRadiusValue = self.config.haloRadius();
                        if (haloRadiusValue === "") {
                            haloRadiusValue = 4;
                        } else {
                            (haloRadiusValue = Number(haloRadiusValue));
                        }    
                        layer.paint["circle-radius"] = haloRadiusValue;

                    case "resources-cluster-point-halo-" + params.nodeid:
                        layer.paint["circle-color"] = self.config.pointHaloColor();
                        break;

                    case "resources-point-" + params.nodeid:
                        radiusValue = self.config.radius();
                        if (radiusValue === "") {
                            radiusValue = 2;
                        } else {
                            (radiusValue = Number(radiusValue));
                        }
                        layer.paint["circle-radius"] = radiusValue;

                    case "resources-cluster-point-" + params.nodeid:
                        clusterDistanceValue = self.config.clusterDistance();
                        if (clusterDistanceValue === "") {
                            clusterDistanceValue = 20;
                        } else {
                            (clusterDistanceValue = Number(clusterDistanceValue));
                        }
                        clusterMaxZoomValue = self.config.clusterMaxZoom();
                        if (clusterMaxZoomValue === "") {
                            clusterMaxZoomValue = 5;
                        } else {
                            (clusterMaxZoomValue = Number(clusterMaxZoomValue));
                        }
                        clusterMinPointsValue = self.config.clusterMinPoints();
                        if (clusterMinPointsValue === "") {
                            clusterMinPointsValue = 3;
                        } else {
                            (clusterMinPointsValue = Number(clusterMinPointsValue));
                        }
                        simplificationValue = self.config.simplification();
                        if (simplificationValue === "") {
                            simplificationValue = 0.3;
                        } else {
                            (simplificationValue = Number(simplificationValue));
                        }
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
                self.config.haloWeight(haloWeightValue);
                self.config.weight(weightValue);
                self.config.outlineWeight(outlineWeightValue);
                self.config.haloRadius(haloRadiusValue);
                self.config.radius(radiusValue);
                self.config.clusterDistance(clusterDistanceValue);
                self.config.clusterMaxZoom(clusterMaxZoomValue);
                self.config.clusterMinPoints(clusterMinPointsValue);
                self.config.simplification(simplificationValue);
                self.loading(true);
                self.node.save(function() {
                    self.loading(false);
                });
            };
        }
    }
};

ko.components.register(name, {
    viewModel: viewModel,
    template: geojsonFeatureCollectionDatatypeTemplate,
});

export default name;
