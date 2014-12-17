define([
    'jquery',
    'openlayers',
    'underscore',
    'arches',
    'layer-info'
], function($, ol, _, arches, layerInfo) {
    var layers = [];

    _.each(layerInfo, function (item, entitytypeid) {
      var color = '#'+Math.floor(Math.random()*16777215).toString(16);

      var style = new ol.style.Style({
        fill: new ol.style.Fill({
          color: item.vectorColor
        }),
        stroke: new ol.style.Stroke({
          color: item.vectorColor,
          width: 1
        }),
        image: new ol.style.Circle({
          radius: 5,
          stroke: new ol.style.Stroke({
            color: '#fff'
          }),
          fill: new ol.style.Fill({
            color: item.vectorColor
          })
        })
      });

      var pointSource = new ol.source.Vector({
        features: []
      });

      var source = new ol.source.GeoJSON({
        projection: 'EPSG:3857',
        url: 'resources/layers/' + entitytypeid + '/'
      });

      source.on('addfeature', function (e) {
        var feature = e.feature;
        if (e.feature.getGeometry().getType() === 'Polygon') {
          feature = feature.clone();
          feature.setGeometry(feature.getGeometry().getInteriorPoint());
        }
        pointSource.addFeature(feature);
      });


      var vectorLayer = new ol.layer.Vector({
        maxResolution: arches.mapDefaults.cluster_min,
        source: source,
        style: style
      });

      var clusterSource = new ol.source.Cluster({
        distance: 40,
        source: pointSource
      });

      var styleCache = {};

      var clusterStyle = function(feature, resolution) {
          var size = feature.get('features').length;
          var style = [new ol.style.Style({
            fill: new ol.style.Fill({
              color: item.vectorColor
            }),
            stroke: new ol.style.Stroke({
              color: item.vectorColor,
              width: 1
            }),
            image: new ol.style.Circle({
              radius: 10,
              stroke: new ol.style.Stroke({
                color: '#fff'
              }),
              fill: new ol.style.Fill({
                color: item.vectorColor
              })
            }),
            text: new ol.style.Text({
              text: size.toString(),
              fill: new ol.style.Fill({
                color: '#fff'
              })
            })
          })];
          return style;
      };

      var clusterLayer = new ol.layer.Vector({
        minResolution: arches.mapDefaults.cluster_min,
        source: clusterSource,
        style: clusterStyle
      });

      var layerGroup = new ol.layer.Group({
        layers: [
          vectorLayer,
          clusterLayer
        ]
      });

      var layerModel = _.extend({
        layer: layerGroup,
        onMap: true
      }, layerInfo[entitytypeid]);

      layers.push(layerModel);
    });

    return layers;
});