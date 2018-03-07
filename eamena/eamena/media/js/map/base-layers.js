define([
    'jquery',
    'openlayers',
    'underscore',
    'arches'
//     'gmjs',
//     'map/ol3gm'
], function($, ol, _, arches) {
    var baseLayers = arches.bingLayers;
    var editor = arches.editor;
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
    baseLayers[0].layer.setVisible(true);
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
    if (editor === true) {
        baseLayers.push({
            id: 'DG',
            name: 'Digital Globe',
            icon: arches.urls.media + 'img/map/DigitalGlobe.jpg',
            layer: new ol.layer.Tile({
                visible: false,
                source: new ol.source.XYZ({
                    url: 'http://api.tiles.mapbox.com/v4/digitalglobe.nal0mpda/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoiZGlnaXRhbGdsb2JlIiwiYSI6ImNpdmFzc3ZsNTAwd20yenBiaWxuZzdjaHQifQ.Zirx4s_vruVlBq-UgIyKEw'
                })
            })
        });
        baseLayers.push({
            id: 'DARE',
            name: 'DARE/Pelagios',
            icon: arches.urls.media + 'img/map/Pelagios.png',
            layer: new ol.layer.Tile({
                visible: false,
                source: new ol.source.XYZ({
                    url: 'http://pelagios.org/tilesets/imperium/{z}/{x}/{y}.png'
                })
            })
        });
    }
        
    return baseLayers;
});