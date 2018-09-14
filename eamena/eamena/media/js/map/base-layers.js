define([
    'jquery',
    'openlayers',
    'underscore',
    'arches'
//     'gmjs',
//     'map/ol3gm'
], function($, ol, _, arches) {
    var baseLayers = [];
//     _.each(baseLayers, function(layer) {
//         layer.layer = new ol.layer.Tile({
//             visible: false,
//             preload: Infinity,
//             source: new ol.source.BingMaps({
//                 key: arches.bingKey,
//                 imagerySet: layer.id
//             })
//         });
//     });


    baseLayers.push({
        id: 'GM',
        name: 'Google Hybrid',
        icon: arches.urls.media + 'img/map/Google.png',
        layer: new ol.layer.Tile({
            visible: false,
            source: new ol.source.XYZ({
                url: 'http://mt0.google.com/vt/lyrs=y&hl=en&x={x}&y={y}&z={z}&s=Ga'
            })
        })
    });

     //set default map style to Google Hybrid
    baseLayers[0].layer.setVisible(true);       
    return baseLayers;
});