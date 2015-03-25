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

    // baseLayers.push({
    //     id: 'examplemap',
    //     name: 'Example Basemap',
    //     icon: arches.urls.media + 'img/map/an_example.png',
    //     layer: new ol.layer.Tile({
    //         visible: false,
    //         source: new ol.source.XYZ({
    //             url: 'http://otile1.mqcdn.com/tiles/1.0.0/map/{z}/{x}/{y}.png'
    //         })
    //     })
    // });

    return baseLayers;
});