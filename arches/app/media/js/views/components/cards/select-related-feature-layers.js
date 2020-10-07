define([], function() {
    return function(source, sourceLayer, selectedResourceIds, visible, color, nodeids, filteredNodeids, hoverId) {
        color = color || "#F0C200";
        hoverId = hoverId;
        var selectionColor = "#427AFF";
        var hoverColor = "#ff0000";
        var colorPalette = [ "#A4DB6E", "#F0C200", "#fdb462", "#22ff33", "#D29EFF"]
        var createColorExpressions = function(defaultColor, colorPalette){
            if (nodeids) {
                var colorExpressions = ['case'];
                nodeids.forEach(function(nodeid, i) {
                    colorExpressions.push(['==', ['get', 'nodeid'], nodeid])
                    if (i <= colorPalette.length) {
                        colorExpressions.push(colorPalette[i]);
                    } else {
                        colorExpressions.push(colorPalette[Math.floor(Math.random() * Math.floor(colorPalette.length))]);
                    }
                });
                colorExpressions.push(color)
                return colorExpressions;
            } else {
                return defaultColor;
            }
        } 
        color = createColorExpressions(color, colorPalette);
        var nodeFilter = ["!=", "resourceinstanceid", "x"] // just a placeholder if there are no filerNodeids
        if (filteredNodeids && nodeids.length > 1) {
            var nodeFilter = filteredNodeids.map(id => ["==", "nodeid", id])
            nodeFilter.splice(0, 0, 'any');
        }
        var strokecolor = "#fff";
        var overviewzoom = 11;
        var minzoom = 15;
        if (selectedResourceIds && selectedResourceIds.length > 0) {
            color = ['match', ['get', 'resourceinstanceid'], selectedResourceIds, selectionColor, color
            ];
        }
        if (hoverId) {
            color = ['match', ['get', 'resourceinstanceid'], hoverId, hoverColor, color
            ];
        }
        if (!source) return [];
        var layers = [{
            "id": "select-feature-polygon-fill",
            "type": "fill",
            "minzoom": overviewzoom,
            "filter": ['all',[
                "==", "$type", "Polygon"
                ], nodeFilter
            ],
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
            ], nodeFilter],
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
            "minzoom": overviewzoom,
            "filter": ['all',[
                "==", "$type", "Polygon"
            ], nodeFilter],
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
            ], nodeFilter],
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
            "filter": ['all',
                ["==", "$type", "Point"]
            ],
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
            ], nodeFilter],
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
});
