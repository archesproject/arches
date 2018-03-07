define([
    'jquery',
    'openlayers',
    'underscore',
    'arches',
    'gmjs',
    'map/ol3gm'
], function($, ol, _, arches, gmjs, olgm) {
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

    //set default map style to Aerial
    baseLayers[1].layer.setVisible(true);
    baseLayers.push({
        id: 'DG',
        name: 'Digital Globe',
        icon: arches.urls.media + 'img/map/google_satellite.jpg',
        layer: new ol.layer.Tile({
            visible: false,
            source: new ol.source.XYZ({
                url: 'http://api.tiles.mapbox.com/v4/digitalglobe.nal0mpda/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNpdmFzc3ZsNTAwd20yenBiaWxuZzdjaHQifQ.Zirx4s_vruVlBq-UgIyKEw'
            })
        })
    });

    return baseLayers;
});