define([
    'arches',
    'knockout',
    'underscore',
    'bindings/color-picker',
    'bindings/mapbox-gl'
], function (arches, ko, _) {
    var name = 'geojson-feature-collection-datatype-config';
    ko.components.register(name, {
        viewModel: function(params) {
            var self = this
            this.node = params;
            this.config = params.config;
            this.graph = params.graph;
            this.layer = params.layer;
            var overlays = JSON.parse(this.layer.layer_definitions);
            _.each(overlays, function(overlay){
                delete overlay["source-layer"];
            })
            var basemapLayers = _.filter(arches.mapLayers, function(layer) {
                return layer.name === 'streets';
            }).reduce(function(layers, layer) {
                return layers.concat(layer.layer_definitions);
            }, []);
            var sources = $.extend(true, {}, arches.mapSources);
            sources[params.mapSource.name] = JSON.parse(params.mapSource.source);

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
                "layers": basemapLayers.concat(overlays)
            };
            this.zoom = ko.observable(0);
            this.minZoom = ko.observable(0);
            this.maxZoom = ko.observable(20);
            this.centerX = ko.observable(-80);
            this.centerY = ko.observable(0);
            this.pitch = ko.observable(0);
            this.bearing = ko.observable(0);

            this.serviceURL = window.location.origin +
                arches.urls.tileserver +
                '/' + params.nodeid +
                '/{z}/{x}/{y}.pbf';

            this.map = null;
            this.setupMap = function(map) {
                this.map = map;
            }

            this.node.json.subscribe(function () {
                _.each(overlays, function(layer) {
                    switch (layer.id) {
                        case "resources-fill-" + params.nodeid:
                            layer.paint["fill-color"] = self.config.fillColor()
                            break;
                        case "resources-line-halo-" + params.nodeid:
                            layer.paint["line-width"] = parseInt(self.config.haloWeight());
                            layer.paint["line-color"] = self.config.lineHaloColor();
                            break;
                        case "resources-line-" + params.nodeid:
                            layer.paint["line-width"] = parseInt(self.config.weight());
                            layer.paint["line-color"] = self.config.lineColor();
                            break;
                        case "resources-poly-outline-" + params.nodeid:
                            layer.paint["line-width"] = parseInt(self.config.outlineWeight());
                            layer.paint["line-color"] = self.config.outlineColor();
                            break;
                        case "resources-point-halo-" + params.nodeid:
                            layer.paint["circle-radius"] = parseInt(self.config.haloRadius());
                        case "resources-cluster-point-halo-" + params.nodeid:
                            layer.paint["circle-color"] = self.config.pointHaloColor();
                            break;
                        case "resources-point-" + params.nodeid:
                            layer.paint["circle-radius"] = parseInt(self.config.radius());
                        case "resources-cluster-point-" + params.nodeid:
                            layer.paint["circle-color"] = self.config.pointColor();
                            break;
                        case "resources-cluster-count-" + params.nodeid:
                            break;
                        default:

                    }
                });;
                self.map.setStyle(self.mapStyle);
            })
        },
        template: { require: 'text!datatype-config-templates/geojson-feature-collection' }
    });
    return name;
});
