define([], function() {
    return function(resourceId, source, sourceLayer) {
        var color = "#f0c200";
        if (!source) return [];
        var layers = [{
            "id": "select-feature-polygon-fill",
            "type": "fill",
            "filter": ['all',[
                "==", "$type", "Polygon"
            ], [
                "!=", "resourceinstanceid", resourceId
            ]],
            "paint": {
                "fill-color": color,
                "fill-outline-color": color,
                "fill-opacity": 0.1
            },
            "layout": {
                "visibility": "none"
            }
        }, {
            "id": "select-feature-polygon-stroke",
            "type": "line",
            "filter": ['all',[
                "==", "$type", "Polygon"
            ], [
                "!=", "resourceinstanceid", resourceId
            ]],
            "layout": {
                "line-cap": "round",
                "line-join": "round",
                "visibility": "none"
            },
            "paint": {
                "line-color": color,
                "line-width": 2
            }
        }, {
            "id": "select-feature-line",
            "type": "line",
            "filter": ['all',[
                "==", "$type", "LineString"
            ], [
                "!=", "resourceinstanceid", resourceId
            ]],
            "layout": {
                "line-cap": "round",
                "line-join": "round",
                "visibility": "none"
            },
            "paint": {
                "line-color": color,
                "line-width": 2
            }
        }, {
            "id": "select-feature-point-point-stroke",
            "type": "circle",
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
                "visibility": "none"
            }
        }, {
            "id": "select-feature-point",
            "type": "circle",
            "filter": ['all',[
                "==", "$type", "Point"
            ], [
                "!=", "resourceinstanceid", resourceId
            ]],
            "paint": {
                "circle-radius": 3,
                "circle-color": color
            },
            "layout": {
                "visibility": "none"
            }
        }];
        layers.forEach(function(layer) {
            layer["source"] = source;
            if (sourceLayer) layer["source-layer"] = sourceLayer;
        });
        return layers;
    };
});
