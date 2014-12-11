define([
    'jquery',
    'openlayers',
    'underscore',
    'arches',
    'layer-names'
], function($, ol, _, arches, layerNames) {
    var count = 20000;
    var features = new Array(count);
    var e = 4500000;
    for (var i = 0; i < count; ++i) {
      var coordinates = [2 * e * Math.random() - e, 2 * e * Math.random() - e];
      features[i] = new ol.Feature(new ol.geom.Point(coordinates));
    }

    var source = new ol.source.Vector({
      features: features
    });

    var clusterSource = new ol.source.Cluster({
      distance: 40,
      source: source
    });

    var styleCache = {};
    var clusters = new ol.layer.Vector({
        source: clusterSource,
        style: function(feature, resolution) {
            var size = feature.get('features').length;
            var style = styleCache[size];
            if (!style) {
              style = [new ol.style.Style({
                image: new ol.style.Circle({
                  radius: 10,
                  stroke: new ol.style.Stroke({
                    color: '#fff'
                  }),
                  fill: new ol.style.Fill({
                    color: '#3399CC'
                  })
                }),
                text: new ol.style.Text({
                  text: size.toString(),
                  fill: new ol.style.Fill({
                    color: '#fff'
                  })
                })
              })];
              styleCache[size] = style;
            }
            return style;
        }
    });

    return [{
        id: 'exampleLayer',
        name: layerNames.exampleLayer,
        icon: arches.urls.media + '',
        layer: clusters,
        onMap: true,
        active: true
    }];
});