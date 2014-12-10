define([
    'jquery',
    'openlayers',
    'underscore',
    'arches'
], function($, ol, _, arches) {
    var bingLayers = [{
            id: 'Road',
            name: 'Streets',
            icon: ''
        },
        {
            id: 'AerialWithLabels',
            name: 'Streets',
            icon: ''
        },
        {
            id: 'ordnanceSurvey',
            name: 'Streets',
            icon: ''
        }];

    _.each(bingLayers, function(layer) {
        layer.layer = new ol.layer.Tile({
            visible: false,
            preload: Infinity,
            source: new ol.source.BingMaps({
                key: arches.bingKey,
                imagerySet: layer.id
            })
        });
    })

    //set default map style to Roads
    bingLayers[0].layer.setVisible(true);

    return bingLayers
});