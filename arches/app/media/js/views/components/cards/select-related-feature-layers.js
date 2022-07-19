define([], function() {
    return function(source, sourceLayer, selectedResourceIds, visible, color, nodeids, filteredNodeids, hoverId, selectedLayerConfig) {

        var layerConfig = selectedLayerConfig;
        color = color || layerConfig.defaultcolor;
        var selectionColor = layerConfig.selectioncolor;
        var hoverColor = layerConfig.hovercolor;
        var colorPalette = layerConfig.colorpalette;

        var createColorExpressions = function(defaultColor, colorPalette){
            if (nodeids) {
                var colorExpressions = ['case'];
                nodeids.forEach(function(nodeid, i) {
                    colorExpressions.push(['==', ['get', 'nodeid'], nodeid]);
                    if (i <= colorPalette.length) {
                        colorExpressions.push(colorPalette[i]);
                    } else {
                        colorExpressions.push(colorPalette[Math.floor(Math.random() * Math.floor(colorPalette.length))]);
                    }
                });
                colorExpressions.push(color);
                return colorExpressions;
            } else {
                return defaultColor;
            }
        }; 
        color = createColorExpressions(color, colorPalette);
        var nodeFilter = ["!=", "resourceinstanceid", "x"]; // just a placeholder if there are no filterNodeids
        if (filteredNodeids && nodeids.length > 0) {
            nodeFilter = filteredNodeids.map(id => ["==", "nodeid", id]);
            nodeFilter.splice(0, 0, 'any');
        }
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
            "minzoom": layerConfig.minzoom,
            "filter": ['all',[
                "==", "$type", "Polygon"
            ], nodeFilter
            ],
            "paint": {
                "fill-color": color,
                "fill-outline-color": color,
                "fill-opacity": layerConfig.fillopacity
            },
            "layout": {
                "visibility": visible ? "visible": "none"
            }
        },  {
            "id": "select-feature-polygon-under-stroke",
            "type": "line",
            "minzoom": layerConfig.minzoom,
            "filter": ['all',[
                "==", "$type", "Polygon"
            ], nodeFilter],
            "layout": {
                "line-cap": "round",
                "line-join": "round",
                "visibility": visible ? "visible": "none"
            },
            "paint": {
                "line-color": layerConfig.strokecolor,
                "line-width": layerConfig.strokelinewidth
            }
        }, {
            "id": "select-feature-polygon-stroke",
            "type": "line",
            "minzoom": layerConfig.minzoom,
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
                "line-width": layerConfig.linewidth
            }
        }, {
            "id": "select-feature-line",
            "type": "line",
            "minzoom": layerConfig.minzoom,
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
                "line-width": layerConfig.linewidth
            }
        }, {
            "id": "select-feature-point-point-stroke",
            "type": "circle",
            "minzoom": layerConfig.minzoom,
            "filter": ['all',
                ["==", "$type", "Point"]
            ],
            "paint": {
                "circle-radius": layerConfig.strokepointradius,
                "circle-opacity": layerConfig.strokepointopacity,
                "circle-color": layerConfig.strokecolor
            },
            "layout": {
                "visibility": visible ? "visible": "none"
            }
        }, {
            "id": "select-feature-point",
            "type": "circle",
            "minzoom": layerConfig.minzoom,
            "filter": ['all',[
                "==", "$type", "Point"
            ], nodeFilter],
            "paint": {
                "circle-radius": layerConfig.pointradius,
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
