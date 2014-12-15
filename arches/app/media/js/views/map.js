define([
    'jquery',
    'backbone',
    'underscore',
    'openlayers',
    'arches',
    'map/base-layers',
    'bootstrap'
], function($, Backbone, _, ol, arches, baseLayers) {
    return Backbone.View.extend({
        events: {
            'mousemove': 'handleMouseMove',
            'mouseout': 'handleMouseOut'
        },

        overlays: [],
        initialize: function(options) {
            var self = this;
            var projection = ol.proj.get('EPSG:3857');
            var layers = [];
            var dragAndDropInteraction = new ol.interaction.DragAndDrop({
                formatConstructors: [
                    ol.format.GPX,
                    ol.format.GeoJSON,
                    ol.format.IGC,
                    ol.format.KML,
                    ol.format.TopoJSON
                ]
            });

            _.extend(this, _.pick(options, 'overlays'));

            this.baseLayers = baseLayers;

            _.each(this.baseLayers, function(baseLayer) {
                layers.push(baseLayer.layer);
            });
            _.each(this.overlays, function(overlay) {
                layers.push(overlay);
            });

            dragAndDropInteraction.on('addfeatures', function(event) {
                var vectorSource = new ol.source.Vector({
                    features: event.features,
                    projection: event.projection
                });
                var vectorLayer = new ol.layer.Vector({
                    source: vectorSource,
                    style: new ol.style.Style({
                            fill: new ol.style.Fill({
                                color: 'rgba(92, 184, 92, 0.5)'
                            }),
                            stroke: new ol.style.Stroke({
                                color: '#0ff',
                                width: 1
                            })
                    })
                });
                self.map.addLayer(vectorLayer);
                var view = self.map.getView();
                view.fitExtent(vectorSource.getExtent(), (self.map.getSize()));
                self.trigger('layerDropped', vectorLayer, event.file.name);
            });

            this.map = new ol.Map({
                layers: layers,
                interactions: ol.interaction.defaults({
                    altShiftDragRotate: false,
                    dragPan: false,
                    rotate: false
                }).extend([new ol.interaction.DragPan({kinetic: null})]).extend([dragAndDropInteraction]),
                target: this.el,
                view: new ol.View({
                    center: [arches.mapDefaults.x, arches.mapDefaults.y],
                    zoom: arches.mapDefaults.zoom
                })
            });

            this.map.on('moveend', function () {
                var view = self.map.getView();
                var extent = view.calculateExtent(self.map.getSize());
                self.trigger('viewChanged', view.getZoom(), extent);
            });
        },

        handleMouseMove: function(e) {
            var coords = this.map.getCoordinateFromPixel([e.offsetX, e.offsetY]);
            var point = new ol.geom.Point(coords);
            var format = ol.coordinate.createStringXY(4);
            coords = point.transform("EPSG:3857", "EPSG:4326").getCoordinates();
            this.trigger('mousePositionChanged', format(coords));
        },

        handleMouseOut: function () {
            this.trigger('mousePositionChanged', '');
        }
    });
});
