import arches from 'arches';


export default function(resourceId, source, sourceLayer, selectedResourceIds, visible, color) {
    color = color || "#F0C200";
    var strokecolor = "#fff";
    var minzoom = arches.mapDefaultMinZoom;
    if (selectedResourceIds && selectedResourceIds.length > 0) {
        color = [
            'match',
            ['get', 'resourceinstanceid'],
            selectedResourceIds, "#2F14A6",
            color
        ];
    }
    if (!source) return [];
    var layers = [{
        "id": "select-feature-polygon-fill",
        "type": "fill",
        "minzoom": minzoom,
        "filter": ['all',[
            "==", "$type", "Polygon"
        ], [
            "!=", "resourceinstanceid", resourceId
        ]],
        "paint": {
            "fill-color": color,
            "fill-outline-color": color,
            "fill-opacity": 0.2
        },
        "layout": {
            "visibility": visible ? "visible": "none"
        }
    },  {
        "id": "select-feature-polygon-under-stroke",
        "type": "line",
        "minzoom": minzoom,
        "filter": ['all',[
            "==", "$type", "Polygon"
        ], [
            "!=", "resourceinstanceid", resourceId
        ]],
        "layout": {
            "line-cap": "round",
            "line-join": "round",
            "visibility": visible ? "visible": "none"
        },
        "paint": {
            "line-color": strokecolor,
            "line-width": 4
        }
    }, {
        "id": "select-feature-polygon-stroke",
        "type": "line",
        "minzoom": minzoom,
        "filter": ['all',[
            "==", "$type", "Polygon"
        ], [
            "!=", "resourceinstanceid", resourceId
        ]],
        "layout": {
            "line-cap": "round",
            "line-join": "round",
            "visibility": visible ? "visible": "none"
        },
        "paint": {
            "line-color": color,
            "line-width": 2
        }
    }, {
        "id": "select-feature-line",
        "type": "line",
        "minzoom": minzoom,
        "filter": ['all',[
            "==", "$type", "LineString"
        ], [
            "!=", "resourceinstanceid", resourceId
        ]],
        "layout": {
            "line-cap": "round",
            "line-join": "round",
            "visibility": visible ? "visible": "none"
        },
        "paint": {
            "line-color": color,
            "line-width": 2
        }
    }, {
        "id": "select-feature-point-point-stroke",
        "type": "circle",
        "minzoom": minzoom,
        "filter": ['all',[
            "==", "$type", "Point"
        ], [
            "!=", "resourceinstanceid", resourceId
        ]],
        "paint": {
            "circle-radius": 6,
            "circle-opacity": 1,
            "circle-color": "#fff"
        },
        "layout": {
            "visibility": visible ? "visible": "none"
        }
    }, {
        "id": "select-feature-point",
        "type": "circle",
        "minzoom": minzoom,
        "filter": ['all',[
            "==", "$type", "Point"
        ], [
            "!=", "resourceinstanceid", resourceId
        ]],
        "paint": {
            "circle-radius": 4,
            "circle-color": color
        },
        "layout": {
            "visibility": visible ? "visible": "none"
        }
    }];
    layers.forEach(function(layer) {
        layer["source"] = source;
        if (sourceLayer) layer["source-layer"] = sourceLayer;
    });
    return layers;
};
