define([
    'openlayers',
    'underscore',
    'arches',
    'map/layer-model'
], function(ol, _, arches, LayerModel) {
    var hexToRgb = function (hex) {
        var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    };

    return function(config, featureCallback) {
        config = _.extend({
            entitytypeid: 'all',
            vectorColor: '#808080'
        }, config);

        var layer = function () {
            var rgb = hexToRgb(config.vectorColor);
            var iconUnicode = '\uf060';
            var zIndex = 0;

            var style = function(feature, resolution) {
                var mouseOver = feature.get('mouseover');
                var shadowSize = mouseOver ? 42 : 38;
                var iconSize = mouseOver ? 37 : 33;

                var styles = [new ol.style.Style({
                    text: new ol.style.Text({
                        text: iconUnicode,
                        font: 'normal ' + iconSize + 'px octicons',
                        offsetX: 5,
                        offsetY: -5,
                        textBaseline: 'Bottom',
                        fill: new ol.style.Fill({
                            color: 'rgba(126,126,126,0.3)',
                        })
                    }),
                    zIndex: mouseOver ? zIndex*1000000000: zIndex
                }), new ol.style.Style({
                    text: new ol.style.Text({
                        text: iconUnicode,
                        font: 'normal ' + iconSize + 'px octicons',
                        stroke: new ol.style.Stroke({
                            // color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',1)',
                            color: 'white',
                            width: 3
                        }),
                        textBaseline: 'Bottom',
                        fill: new ol.style.Fill({
                            color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.9)',
                        })
                    }),
                    zIndex: mouseOver ? zIndex*2000000000 : zIndex+1
                })];

                zIndex += 2;

                return styles;
            };

            var source = new ol.source.GeoJSON({
                projection: 'EPSG:3857',
                url: arches.urls.map_markers + config.entitytypeid
            });

            if (typeof featureCallback === 'function') {
                var loadListener = source.on('change', function(e) {
                    if (source.getState() == 'ready') {
                        featureCallback(source.getFeatures());
                        ol.Observable.unByKey(loadListener);
                    }
                });
            }

            var vectorLayer = new ol.layer.Vector({
                maxResolution: arches.mapDefaults.cluster_min,
                source: source,
                style: style
            });

            var clusterSource = new ol.source.Cluster({
                distance: 40,
                source: source
            });

            var styleCache = {};

            var clusterStyle = function(feature, resolution) {
                var size = feature.get('features').length;
                var mouseOver = feature.get('mouseover');
                var shadowSize = mouseOver ? 42 : 38;
                var iconSize = mouseOver ? 37 : 33;
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

                return [new ol.style.Style({
                    image: new ol.style.Circle({
                        radius: radius,
                        stroke: new ol.style.Stroke({
                            color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.4)',
                            width: radius
                        }),
                        fill: new ol.style.Fill({
                            color: 'rgba(' + rgb.r + ',' + rgb.g + ',' + rgb.b + ',0.8)',
                        })
                    }),
                    text: new ol.style.Text({
                        text: size.toString(),
                        fill: new ol.style.Fill({
                            color: '#fff'
                        })
                    })
                })];
            };

            var clusterLayer = new ol.layer.Vector({
                source: clusterSource,
                style: clusterStyle
            });

            return new ol.layer.Group({
                layers: [
                    clusterLayer
                ]
            });
        };

        return new LayerModel(_.extend({
                layer: layer,
                onMap: true
            }, config)
        );
    };
});