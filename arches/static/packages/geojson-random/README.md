# geojson-random

[![build status](https://secure.travis-ci.org/mapbox/geojson-random.png)](http://travis-ci.org/mapbox/geojson-random)

Generate random [GeoJSON](http://geojson.org/) features.

Usable in [node.js](http://nodejs.org/) and in browsers with [browserify](http://browserify.org/).

    npm install -g geojson-random
    geojson-random

## api

```js
var random = require('geojson-random');
```

### `random.point(count, bbox)`

Return `count` points wrapped in a FeatureCollection.

An optional `bbox` parameter should be an array of numbers representing
a [bbox](http://geojson.org/geojson-spec.html#bounding-boxes) in WSEN order,
and if given, the point will reside within its bounds.

### `random.position(bbox?)`

Return a single GeoJSON [Position](http://geojson.org/geojson-spec.html#positions)
as a 2-element array of numbers in longitude, latitude order.

An optional `bbox` parameter should be an array of numbers representing
a [bbox](http://geojson.org/geojson-spec.html#bounding-boxes) in WSEN order,
and if given, the position will reside within its bounds.

### `random.polygon(count, num_vertices, max_radial_length)`

Return `count` polygons wrapped in a FeatureCollection.

* `num_vertices` is default `10` and is how many coordinates each Polygon
  will contain.
* `max_radial_length` is the maximum number of decimal degrees latitude
  or longitude that a vertex can reach out of the center of the Polygon.
  Default is `10`.
