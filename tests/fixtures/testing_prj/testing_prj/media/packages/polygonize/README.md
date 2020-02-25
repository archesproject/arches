# Polygonize

[![Build Status](https://travis-ci.org/NickCis/polygonize.svg?branch=master)](https://travis-ci.org/NickCis/polygonize)

Polygonizes a set of Geometrys which contain linework that represents the edges of a planar graph. It's basically an implementation of [GEOS's Polygonizer](https://github.com/echoz/xlibspatialite/blob/master/geos/include/geos/operation/polygonize/Polygonizer.h).

Although, the algorithm is the same as GEOS, it isn't a literal transcription of the C++ source code. It was rewriten in order to get a more javascript like code.

## JSDoc

```javascript
/**
 * Polygonizes {@link LineString|(Multi)LineString(s)} into {@link Polygons}.
 *
 * Implementation of GEOSPolygonize function (`geos::operation::polygonize::Polygonizer`).
 *
 * Polygonizes a set of lines that represents edges in a planar graph. Edges must be correctly
 * noded, i.e., they must only meet at their endpoints.
 *
 * The implementation correctly handles:
 *
 * - Dangles: edges which have one or both ends which are not incident on another edge endpoint.
 * - Cut Edges (bridges): edges that are connected at both ends but which do not form part of a polygon.
 *
 * @name polygonize
 * @param {FeatureCollection|Geometry|Feature<LineString|MultiLineString>} geoJson Lines in order to polygonize
 * @returns {FeatureCollection<Polygon>} Polygons created
 * @throws {Error} if geoJson is invalid.
 */
```

## Example

This example is the test found in [`test/in/complex.geojson`](https://github.com/NickCis/polygonize/blob/master/test/in/complex.geojson).


```javascript
const polygonize = require('polygonize'),
    fs = require('fs'),
    input = JSON.parse(fs.readFileSync('./test/in/complex.geojson'));

console.log(JSON.stringify(polygonize(input)));
```

The [input](https://github.com/NickCis/polygonize/blob/master/test/in/complex.geojson) as GeoJson LineString:

![](https://cloud.githubusercontent.com/assets/174561/26525683/c30957de-4335-11e7-8eb9-bf72f268efb8.png)

Turned into [polygons](https://github.com/NickCis/polygonize/blob/master/test/out/complex.geojson):

![](https://cloud.githubusercontent.com/assets/174561/26525695/24f5270c-4336-11e7-9b62-60db8c0c9a28.png)


## Documentation

Polygonizes [(Multi)LineString(s)](http://geojson.org/geojson-spec.html#linestring) into [Polygons](Polygons).

Implementation of GEOSPolygonize function (`geos::operation::polygonize::Polygonizer`).

Polygonizes a set of lines that represents edges in a planar graph. Edges must be correctly noded, i.e., they must only meet at their endpoints.

The implementation correctly handles:

-   Dangles: edges which have one or both ends which are not incident on another edge endpoint.
-   Cut Edges (bridges): edges that are connected at both ends but which do not form part of a polygon.

**Parameters**

-   `geojson` **([FeatureCollection](http://geojson.org/geojson-spec.html#feature-collection-objects) \| [Geometry](http://geojson.org/geojson-spec.html#geometry) \| [Feature](http://geojson.org/geojson-spec.html#feature-objects)&lt;([LineString](http://geojson.org/geojson-spec.html#linestring) \| [MultiLineString](http://geojson.org/geojson-spec.html#multilinestring))>)** Lines in order to polygonize


-   Throws **[Error](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error)** if geoJson is invalid.

Returns **[FeatureCollection](http://geojson.org/geojson-spec.html#feature-collection-objects)&lt;[Polygon](http://geojson.org/geojson-spec.html#polygon)>** Polygons created

### Installation

Install this module individually:

```sh
$ npm install polygonize
```
