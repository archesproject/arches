define([
    'jquery',
    'openlayers',
    'underscore',
    'arches',
    'map/layer-model',
    'utils',
    'plugins/supercluster/supercluster' 
], function($, ol, _, arches, LayerModel, utils, supercluster) {
    return function(config, featureCallback) {
        config = _.extend({
            entitytypeid: 'all',
            vectorColor: '#808080'
        }, config);

        var layer = function () {
            var rgb = utils.hexToRgb(config.vectorColor);
            var zIndex = 0;
            var styleCache = {};
            var hasData = false;

            var style = function(feature, resolution) {
                var mouseOver = feature.get('mouseover');
                var text = '1 ' + mouseOver;

                if (!feature.get('arches_marker')) {
                    feature.set('arches_marker', true);
                }

                if (styleCache[text]) {
                    return styleCache[text];
                }
                
                var iconSize = mouseOver ? 38 : 32;

                var styles = [new ol.style.Style({
                    text: new ol.style.Text({
                        text: arches.resourceMarker.icon,
                        font: 'normal ' + iconSize + 'px ' + arches.resourceMarker.font,
                        offsetX: 5,
                        offsetY: ((iconSize/2)*-1)-5,
                        fill: new ol.style.Fill({
                            color: 'rgba(126,126,126,0)',
                        })
                    }),
                    zIndex: mouseOver ? zIndex*1000000000: zIndex
                }), new ol.style.Style({
                    text: new ol.style.Text({
                        text: arches.resourceMarker.icon,
                        font: 'normal ' + iconSize + 'px ' + arches.resourceMarker.font,
                        offsetY: (iconSize/2)*-1,
                        stroke: new ol.style.Stroke({
                            color: 'white',
                            width: 3
                        }),
                        fill: new ol.style.Fill({
                            color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.9)',
                        })
                    }),
                    zIndex: mouseOver ? zIndex*2000000000 : zIndex+1
                })];

                zIndex += 2;

                styleCache[text] = styles;
                return styles;
            };

            var layerConfig = {
                format: new ol.format.GeoJSON()
            };
            
            var geojson_array;
            var spatial_index = supercluster({
                radius: 100,
                maxZoom: 16
            })

            if (config.entitytypeid !== null) {
                layerConfig.url = arches.urls.map_markers + config.entitytypeid;
                
                //fetch the raw geojson data and act on it
                $.ajax({
                    url: layerConfig.url,
                    success: function (result) {
                        //load features into supercluster index
                        spatial_index.load(result.features)
                        hasData = true;
                        
                        //trigger an initial clustering pass
                        if(initialExtent && initialZoom) {
                            clusterLayer.updateClusters(initialExtent, initialZoom)
                        }
                        
                        if(typeof(featureCallback) === 'function') {
                            featureCallback(result.features);
                            geojson_array = result;
                        }
                        $('.map-loading').hide();
                    },
                    error: function (jqxhr, status, err) {
                        console.error('error fetching geojson features', err);
                    }
                })
            }
            

            $('.map-loading').show();

            var clusterStyle = function(feature, resolution) {
                if(feature.get('features')) {
                    var size = feature.get('features').length;
                } else if (feature.get('point_count')) {
                    var size = feature.get('point_count');
                } else {
                    var size = 1;
                }
                var mouseOver = feature.get('mouseover');
                var text = size + ' ' + mouseOver;

                if (!feature.get('arches_cluster')) {
                    feature.set('arches_cluster', true);
                }

                if (styleCache[text]) {
                    return styleCache[text];
                }

                var radius = mouseOver ? 12 : 10;

                if (size === 1) {
                    return style(feature, resolution);
                }

                if (size > 200) {
                    radius = mouseOver ? 20 : 18;
                } else if (size > 150) {
                    radius = mouseOver ? 18 : 16;
                } else if (size > 100) {
                    radius = mouseOver ? 16 : 14;
                } else if (size > 50) {
                    radius = mouseOver ? 14 : 12;
                }

                var styles = [new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: radius,
                        stroke: new ol.style.Stroke({
                            color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.4)',
                            width: radius
                        }),
                        fill: new ol.style.Fill({
                            color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0)',
                        })
                    }),
                    text: new ol.style.Text({
                        text: size.toString(),
                        fill: new ol.style.Fill({
                            color: '#fff'
                        })
                    })
                })];
                styleCache[text] = styles;
                return styles;
            };

            var superClusterSource = new ol.source.Vector()

            var clusterLayer = new ol.layer.Vector({
                source: superClusterSource,
                style: clusterStyle
            });

            clusterLayer.geojson_data = geojson_array;

            initialExtent = null;
            initialZoom = null;

            clusterLayer.updateClusters = function (extentOl, zoom) {
                var extentLatLng = ol.proj.transformExtent(extentOl, 'EPSG:3857', 'EPSG:4326');
                if(hasData) {
                    var clusters = spatial_index.getClusters(extentLatLng, zoom)
                    
                    var clusterFeatures = _.map(clusters, function (cluster) {
                        //project to map coordinates
                        var coords = ol.proj.transform(cluster.geometry.coordinates, 'EPSG:4326', 'EPSG:3857');
                        var f = new ol.Feature(new ol.geom.Point(
                            coords
                        ));
                        f.setProperties(cluster.properties);
                        if(cluster.id) {
                            f.setId(cluster.id);
                        }
                        return f;
                    }.bind(this));
                    
                    clusterLayer.getSource().clear();
                    clusterLayer.getSource().addFeatures(clusterFeatures);
                } else {
                    // store the zoom and extent to cluster when the data has loaded
                    initialExtent = extentOl;
                    initialZoom = zoom;
                }
                
            }

            // clusterLayer.vectorSource = source;
            clusterLayer.set('is_arches_layer', true);

            return clusterLayer;
        };

        return new LayerModel(_.extend({
                layer: layer,
                onMap: true,
                isArchesLayer: true,
            }, config)
        );
    };
});
