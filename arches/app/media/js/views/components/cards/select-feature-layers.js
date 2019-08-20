define([], function() {
    return function(resourceId, source, sourceLayer, areaSelectColor) {
        if (!source) return [];
        if (!areaSelectColor) areaSelectColor = "#f0c200";
        if (!sourceLayer) sourceLayer = source;
        return [{
            "id": "select-feature-polygon-fill",
            "type": "fill",
            "filter": ['all',[
                "==", "$type", "Polygon"
            ], [
                "!=", "resourceinstanceid", resourceId
            ]],
            "paint": {
                "fill-color": areaSelectColor,
                "fill-outline-color": areaSelectColor,
                "fill-opacity": 0.1
            },
            "source": source,
            "source-layer": sourceLayer,
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
                "line-color": areaSelectColor,
                "line-width": 2
            },
            "source": source,
            "source-layer": sourceLayer
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
                "line-color": areaSelectColor,
                "line-width": 2
            },
            "source": source,
            "source-layer": sourceLayer
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
            "source": source,
            "source-layer": sourceLayer,
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
                "circle-radius": 5,
                "circle-color": areaSelectColor
            },
            "source": source,
            "source-layer": sourceLayer,
            "layout": {
                "visibility": "none"
            }
        }];
    };
});
