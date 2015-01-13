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
        enableSelection: true,
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

            _.extend(this, _.pick(options, 'overlays', 'enableSelection'));

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
            
            if (this.enableSelection) {
                this.select = new ol.interaction.Select({
                    condition: ol.events.condition.click,
                    style: function(feature, resolution) {
                        var fillOpacity = self.isFeatureSelectable(feature) ? 0.3 : 0;
                        var strokeOpacity = self.isFeatureSelectable(feature) ? 0.9 : 0;
                        return [new ol.style.Style({
                            fill: new ol.style.Fill({
                                color: 'rgba(0, 255, 255, ' + fillOpacity + ')'
                            }),
                            stroke: new ol.style.Stroke({
                                color: 'rgba(0, 255, 255, ' + strokeOpacity + ')',
                                width: 3
                            }),
                            image: new ol.style.Circle({
                                radius: 10,
                                fill: new ol.style.Fill({
                                    color: 'rgba(0, 255, 255, ' + fillOpacity + ')'
                                }),
                                stroke: new ol.style.Stroke({
                                    color: 'rgba(0, 255, 255, ' + strokeOpacity + ')',
                                    width: 3
                                })
                            })
                        })];
                    }
                });

                this.map.addInteraction(this.select);
            }

            this.map.on('moveend', function () {
                var view = self.map.getView();
                var extent = view.calculateExtent(self.map.getSize());
                self.trigger('viewChanged', view.getZoom(), extent);
            });

            this.select.getFeatures().on('change:length', function(e) {
                if (e.target.getArray().length !== 0) {
                    var feature = e.target.item(0);
                    var isClustered = _.contains(feature.getKeys(), "features");
                    if (isClustered) {
                        var extent = feature.getGeometry().getExtent();
                        _.each(feature.get("features"), function (feature) {
                            featureExtent = feature.getGeometry().getExtent()
                            if (_.contains(feature.getKeys(), 'extent')) {
                                featureExtent = ol.extent.applyTransform(feature.get('extent'), ol.proj.getTransform('EPSG:4326', 'EPSG:3857'));
                            }
                            extent = ol.extent.extend(extent, featureExtent);
                        });
                        self.map.getView().fitExtent(extent, (self.map.getSize()));
                        _.defer(function () {
                            self.select.getFeatures().clear()
                        });
                    }
                }
            });
        },

        handleMouseMove: function(e) {
            var self = this;
            var pixels = [e.offsetX, e.offsetY];
            var coords = this.map.getCoordinateFromPixel(pixels);
            var point = new ol.geom.Point(coords);
            var format = ol.coordinate.createStringXY(4);
            var overFeature = this.map.forEachFeatureAtPixel(pixels, function (feature, layer) {
                return self.isFeatureSelectable(feature);
            });
            var cursorStyle = overFeature ? "pointer" : "";
            if (this.enableSelection) {
                this.$el.css("cursor", cursorStyle);
            }
            coords = point.transform("EPSG:3857", "EPSG:4326").getCoordinates();
            if (coords.length > 0) {
                this.trigger('mousePositionChanged', format(coords));
            }
        },

        handleMouseOut: function () {
            this.trigger('mousePositionChanged', '');
        },

        isFeatureSelectable: function (feature) {
            var keys = feature.getKeys();
            return (_.contains(keys, 'features') || _.contains(keys, 'entitytypeid'));
        }
    });
});