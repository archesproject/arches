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
                    rotate: false,
                    mouseWheelZoom:false
                }).extend([new ol.interaction.DragPan({kinetic: null})]).extend([dragAndDropInteraction]),
                target: this.el,
                view: new ol.View({
                    extent: arches.mapDefaults.extent ? arches.mapDefaults.extent.split(',') : undefined,
                    center: [arches.mapDefaults.x, arches.mapDefaults.y],
                    zoom: arches.mapDefaults.zoom,
                    minZoom: arches.mapDefaults.minZoom,
                    maxZoom: arches.mapDefaults.maxZoom
                })
            });
            
            if (this.enableSelection) {
                this.select = new ol.interaction.Select({
                    condition: ol.events.condition.click,
                    style: function(feature, resolution) {
                        var isSelectFeature = _.contains(feature.getKeys(), 'select_feature');
                        var fillOpacity = isSelectFeature ? 0.3 : 0;
                        var strokeOpacity = isSelectFeature ? 0.9 : 0;
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


            this.map.on('click', function(e) {
                var clickFeature = self.map.forEachFeatureAtPixel(e.pixel, function (feature, layer) {
                    return feature;
                });
                self.trigger('mapClicked', e, clickFeature);
            });
        },

        handleMouseMove: function(e) {
            var self = this;
            if(e.offsetX === undefined) {
                // this works in Firefox
                var xpos = e.pageX-$('#map').offset().left;
                var ypos = e.pageY-$('#map').offset().top;
            } else { 
                // works in Chrome, IE and Safari
                var xpos = e.offsetX;
                var ypos = e.offsetY;
            }
            var pixels = [xpos, ypos];
            var coords = this.map.getCoordinateFromPixel(pixels);
            var point = new ol.geom.Point(coords);
            var format = ol.coordinate.createStringXY(4);
            var overFeature = this.map.forEachFeatureAtPixel(pixels, function (feature, layer) {
                return feature;
            });
            
            coords = point.transform("EPSG:3857", "EPSG:4326").getCoordinates();
            if (coords.length > 0) {
                this.trigger('mousePositionChanged', format(coords), pixels, overFeature);
            } else {
                this.trigger('mousePositionChanged', '');
            }
        },


        handleMouseOut: function () {
            this.trigger('mousePositionChanged', '');
        }
    });
});