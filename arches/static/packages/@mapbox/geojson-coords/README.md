![](http://img.shields.io/travis/mapbox/geojson-coords.svg?style=flat)

# geojson-coords

Extract coordinates from [GeoJSON](http://geojson.org/).

## install

    npm install --save geojson-coords

## api

### `coords(geojson)`

Given any valid GeoJSON object, return a single array of coordinates that
it contains. Handles any root object, collapses multidimensional coordinate arrays
and expands point coordinate arrays.

## example

```js
var geojsonCoords = require('geojson-coords');

geojsonCoords({
    "type": "GeometryCollection",
    "geometries": [
        {
            "type": "Point",
            "coordinates": [100.0, 0.0]
        },
        {
            "type": "LineString",
            "coordinates": [ [101.0, 0.0], [102.0, 1.0] ]
        }
    ]
});
// returns [[100, 0], [101, 0], [102, 1]];
