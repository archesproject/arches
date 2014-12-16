define([
    'jquery',
    'openlayers',
    'underscore',
    'arches'
], function($, ol, _, arches) {
    var baseLayers = arches.bingLayers;

    _.each(baseLayers, function(layer) {
        layer.layer = new ol.layer.Tile({
            visible: false,
            preload: Infinity,
            source: new ol.source.BingMaps({
                key: arches.bingKey,
                imagerySet: layer.id
            })
        });
    });

    //set default map style to Roads
    baseLayers[0].layer.setVisible(true);

    baseLayers.push({
        id: 'osm',
        name: 'OpenStreetMap',
        icon: arches.urls.media + 'img/map/google_streets.jpg',
        layer: new ol.layer.Tile({
          source: new ol.source.OSM(),
          visible: false
        })
    });

    return baseLayers;
});