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
        initialize: function() {
            var projection = ol.proj.get('EPSG:3857');

            this.baseLayers = baseLayers;

            var layers = [];

            _.each(this.baseLayers, function(baseLayer) {
                layers.push(baseLayer.layer);
            });

            var dragAndDropInteraction = new ol.interaction.DragAndDrop({
                formatConstructors: [
                    ol.format.GPX,
                    ol.format.GeoJSON,
                    ol.format.IGC,
                    ol.format.KML,
                    ol.format.TopoJSON
                ]
            });

            dragAndDropInteraction.on('addfeatures', function(event) {
                var vectorSource = new ol.source.Vector({
                    features: event.features,
                    projection: event.projection
                });
                map.getLayers().push(new ol.layer.Vector({
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
                }));
                var view = map.getView();
                view.fitExtent(vectorSource.getExtent(), (map.getSize()));
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
        }
    });
});
