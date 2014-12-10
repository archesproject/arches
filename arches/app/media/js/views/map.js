define([
    'jquery',
    'backbone',
    'openlayers',
    'arches',
    'bootstrap'
], function($, Backbone, ol, arches) {
    return Backbone.View.extend({
        initialize: function() {
            var projection = ol.proj.get('EPSG:3857');

            var styles = [
                'Road',
                'AerialWithLabels',
                'ordnanceSurvey'
            ];

            var layers = [];
            var i, ii;
            for (i = 0, ii = styles.length; i < ii; ++i) {
                layers.push(new ol.layer.Tile({
                    visible: false,
                    preload: Infinity,
                    source: new ol.source.BingMaps({
                        key: arches.bingKey,
                        imagerySet: styles[i]
                    })
                }));
            }

            //set default map style to Roads
            layers[0].setVisible(true);

            //set up basemap display selection
            $(".basemap").click(function (){ 

                var basemap = $(this).attr('id');

                //iterate through the set of layers.  Set the layer visibilty to "true" for the 
                //layer that matches the user's selection
                var i, ii;
                for (i = 0, ii = layers.length; i < ii; ++i) {
                    layers[i].setVisible(styles[i] == basemap);
                }

                //close panel
                $("#inventory-home").click();

                //keep page from re-loading
                return false;

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
