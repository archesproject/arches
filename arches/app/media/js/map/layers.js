define([
    'jquery',
    'openlayers',
    'underscore',
    'arches',
    'layer-names'
], function($, ol, _, arches, layerNames) {
    var createDemoLayer = function () {
      var fillColor = '#'+Math.floor(Math.random()*16777215).toString(16);
      var count = 200;
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

      return new ol.layer.Vector({
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
                      color: fillColor
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
    }
    

    return [
      {
          id: 'exampleLayer',
          name: layerNames.exampleLayer,
          description: 'Lorem ipsum dolor si amet...',
          categories: ['test', 'example'],
          icon: arches.urls.media + '',
          layer: createDemoLayer(),
          onMap: true
      },
      {
          id: 'exampleLayer2',
          name: layerNames.exampleLayer + " 2",
          description: 'Lorem ipsum dolor si amet...',
          categories: ['test', 'example'],
          icon: arches.urls.media + '',
          layer: createDemoLayer(),
          onMap: true
      },
      {
          id: 'exampleLayer3',
          name: layerNames.exampleLayer + " 3",
          description: 'Lorem ipsum dolor si amet...',
          categories: ['test', 'example'],
          icon: arches.urls.media + '',
          layer: createDemoLayer(),
          onMap: false
      },
      {
          id: 'exampleLayer4',
          name: layerNames.exampleLayer + " 4",
          description: 'Lorem ipsum dolor si amet...',
          categories: ['test', 'example'],
          icon: arches.urls.media + '',
          layer: createDemoLayer(),
          onMap: false
      }
    ];
});