![](http://img.shields.io/travis/mapbox/geojson-extent.svg?style=flat)

# geojson-extent

Compute an extent given a GeoJSON object.

## install

    npm install --save geojson-extent

## example

[Live example with Mapbox Static Map API](https://www.mapbox.com/mapbox.js/example/v1.0.0/static-map-from-geojson-with-geo-viewport/)

```js
var geojsonExtent = require('geojson-extent');

geojsonExtent({ type: 'Point', coordinates: [0, 0] }); // returns 0,0,0,0 extent
```

## bin

Provides a binary that takes GeoJSON as stdin and returns a JSON stringified
array of extent data.

```sh
$ npm install -g geojson-extent
$ geojson-extent < file.geojson
```

Given an argument of `leaflet`, this will return Leaflet-formatted data instead.

```sh
$ geojson-extent leaflet < file.geojson
```

## api

### `extent(geojson)`

Given any valid GeoJSON object, return bounds in the form `[WSEN]`.
Invalid objects will return `null`.

### `extent.polygon(geojson)`

Given any valid GeoJSON object, return bounds in the form of a GeoJSON polygon object.
Invalid objects will return `null`.

### `extent.bboxify(geojson)`

Add [bounding boxes](http://geojson.org/geojson-spec.html#bounding-boxes) to all
appropriate GeoJSON objects - Feature, FeatureCollection, and Geometry.
