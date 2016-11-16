define(function() {
      var getDrawStyles = function(resource)
        {
          return [
            {
              "id": "gl-draw-point-active",
              "type": "circle",
              "filter": ["all", ["!=", "meta", "vertex"],
                  ["==", "$type", "Point"],
                  ["!=", "mode", "static"]
              ],
              "paint": {
                  "circle-radius": 5,
                  "circle-color": "#FFF"
              },
              "interactive": true
          }, {
              "id": "gl-draw-point",
              "type": "circle",
              "layout": {},
              "filter": ["all", ["!in", "$type", "LineString", "Polygon"],
                  ["!=", "mode", "static"]
              ],
              "paint": {
                  "circle-radius": resource.pointsize,
                  "circle-color": resource.color,
                  "circle-opacity": 0.8
              },
              "interactive": true
          }, {
              "id": "gl-draw-line",
              "type": "line",
              "filter": ["all", ["==", "$type", "LineString"],
                  ["!=", "mode", "static"]
              ],
              "layout": {
                  "line-cap": "round",
                  "line-join": "round"
              },
              "paint": {
                  "line-color": resource.color,
                  // "line-dasharray": [0.2, 2],
                  "line-width": resource.linewidth
              },
              "interactive": true
          }, {
              "id": "gl-draw-polygon-fill",
              "type": "fill",
              "filter": ["all", ["==", "$type", "Polygon"],
                  ["!=", "mode", "static"]
              ],
              "paint": {
                  "fill-color": resource.color,
                  "fill-outline-color": resource.color,
                  "fill-opacity": 0.1
              },
              "interactive": true
          }, {
              "id": "gl-draw-polygon-stroke-active",
              "type": "line",
              "filter": ["all", ["==", "$type", "Polygon"],
                  ["!=", "mode", "static"]
              ],
              "layout": {
                  "line-cap": "round",
                  "line-join": "round"
              },
              "paint": {
                  "line-color": resource.color,
                  // "line-dasharray": [0.2, 2],
                  "line-width": resource.linewidth
              },
              "interactive": true
          }, {
              "id": "gl-draw-polygon-and-line-vertex-halo-active",
              "type": "circle",
              "filter": ["all", ["==", "meta", "vertex"],
                  ["==", "$type", "Point"],
                  ["!=", "mode", "static"]
              ],
              "paint": {
                  "circle-radius": 5,
                  "circle-color": "#FFF"
              },
              "interactive": true
          }, {
              "id": "gl-draw-polygon-and-line-vertex-active",
              "type": "circle",
              "filter": ["all", ["==", "meta", "vertex"],
                  ["==", "$type", "Point"],
                  ["!=", "mode", "static"]
              ],
              "paint": {
                  "circle-radius": 3,
                  "circle-color": resource.color,
              },
              "interactive": true
          }, {
              "id": "gl-draw-polygon-and-line-midpoint-halo-active",
              "type": "circle",
              "filter": ["all", ["==", "meta", "midpoint"],
                  ["==", "$type", "Point"],
                  ["!=", "mode", "static"]
              ],
              "paint": {
                  "circle-radius": 4,
                  "circle-color": "#FFF"
              },
              "interactive": true
          }, {
              "id": "gl-draw-polygon-and-line-midpoint-active",
              "type": "circle",
              "filter": ["all", ["==", "meta", "midpoint"],
                  ["==", "$type", "Point"],
                  ["!=", "mode", "static"]
              ],
              "paint": {
                  "circle-radius": 2,
                  "circle-color": resource.color,
              },
              "interactive": true
          }, {
              "id": "gl-draw-line-static",
              "type": "line",
              "filter": ["all", ["==", "$type", "LineString"],
                  ["==", "mode", "active"]
              ],
              "layout": {
                  "line-cap": "round",
                  "line-join": "round"
              },
              "paint": {
                  "line-color": "#000",
                  "line-width": resource.linewidth
              },
              "interactive": true
          }
        ];
       }

      return {getDrawStyles: getDrawStyles};
});
