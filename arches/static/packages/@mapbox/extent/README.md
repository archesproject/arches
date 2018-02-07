[![Build Status](https://travis-ci.org/mapbox/extent.svg)](https://travis-ci.org/mapbox/extent)

# extent

A simple geographical extent.

## api

### `extent()`

Create a new extent object

### `extent([w, s, e, n])`

Create a new extent object, given bounds as an array.

### `extent.include([lon, lat])`

Expand the extent to include a lon, lat point.

### `extent.union([w, s, e, n] or other extent)`

Expand the extent to include another extent.

### `extent.equals([w, s, e, n] or other extent)`

Whether this extent is exactly equal to another.

### `extent.bbox()`

Get the extent's value. `null` if no points have
been included yet. Order is `[WSEN]` to match the [GeoJSON](http://geojson.org/)
standard.

### `extent.center()`

Get the centerpoint of the extent as a `[longitude, latitude]` array.

### `extent.polygon()`

Get the extent as a [GeoJSON](http://geojson.org/) Polygon geometry object.

### `extent.contains([lon, lat])`

Returns `true` if this extent contains the given point, and false if not. Points
on the boundary of the extent are considered to be contained. If the extent is
invalid, returns `null`.

### `extent.contains()`

Returns a function that evaluates whether points are contained in the extent -
same behavior as `.contains([lon, lat])`. This pre-compiles the function with the
current extent values, yielding a roughly 3x speedup.
