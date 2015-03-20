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
        id: 'labasemap',
        name: 'LA County Basemap',
        icon: arches.urls.media + 'img/map/la_county.png',
        layer: new ol.layer.Tile({
            visible: false,
            source: new ol.source.XYZ({
                url: 'http://egis3.lacounty.gov/arcgis/rest/services/LACounty_Cache/LACounty_Base/MapServer/tile/{z}/{y}/{x}'
            })
        })
    });

    return baseLayers;
});