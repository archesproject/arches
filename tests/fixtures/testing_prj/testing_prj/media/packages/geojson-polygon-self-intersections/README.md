# geojson-polygon-self-intersections

A very simple script to compute all self-intersections in a GeoJSON polygon.

According to the [Simple Features standard](https://en.wikipedia.org/wiki/Simple_Features), polygons may not self-intersect. GeoJSON, however, doesn't care about this. You can use this tool to check for self-intersections, list them or use them in some way.

This tool uses the [rbush](https://github.com/mourner/rbush) spatial index by default to speed up the detection of intersections. This is especially useful when are many edges but only few intersections. If you prefer, you can opt-out using an input parameter (see below) and it will perform a brute-force search for intersections instead. This might be preferable in case of few edges, as it allows you to avoid some overhead.

# Usage

Get Node.js, then

```bash
npm install geojson-polygon-self-intersections
```

and use it like so:

```javascript
var gpsi = require('geojson-polygon-self-intersections');

// poly = {type: "Feature", geometry: {type: "Polygon", coordinates: [[[1, 10], [11, 13], ...]]}}

var isects = gpsi(poly);

// isects = {type: "Feature", geometry: {type: "MultiPoint", coordinates: [[5, 8], [7, 3], ...]}}
```

Where `poly` is a GeoJSON Polygon, and `isects` is a GeoJSON MultiPoint.

Alternatively, you can use a filter function to specify the output. You have access to the following data per point:

- [x,y] intersection coordinates: `isect`
- ring index of the first edge: `ring0`
- edge index of the first edge: `edge0`
- [x,y] of the start point of the first edge: `start0`
- [x,y] of the end point of the first edge: `end0`
- fractional distance of the intersection on the first edge: `frac0`
- idem for the second edge: `ring1`, `edge1`, `start1`, `end1`, `frac1`
- boolean indicating if the intersection is unique: `unique`

Finally, you can pass an option object to control the behaviour of the algorithm.
The following options are supported:

|Option|Description|
|------|-----------|
| `useSpatialIndex` | Whether a spatial index should be used to filter for possible intersections. Default: `true` |
| `reportVertexOnVertex` | If the same vertex (or almost the same vertex) appears more than once in the input, should this be reported as an intersection? Default: `false`|
| `reportVertexOnEdge` | If a vertex lies (almost) exactly on an edge segment, should this be reported as an intersection? Default: `false` |
| `epsilon` | It is almost never a good idea to compare floating point numbers for identity. Therefor, if we say "the same vertex" or "exactly on an edge segment", we need to define how "close" is "close enough". Note that the value is *not* used as an euclidian distance but always relative to the length of some edge segment. Default: `0`|

Together, this may look like so:

```javascript
var options = {
  useSpatialIndex:false
};
var isects = gpsi(poly, function filterFn(isect, ring0, edge0, start0, end0, frac0, ring1, edge1, start1, end1, frac1, unique){return [isect, frac0, frac1];}, options);

// isects = [[[5, 8], 0.4856, 0.1865]], [[[7, 3], 0.3985, 0.9658]], ...]
```
For backwards compatibility, if you pass anything other than an object, it will be interpreted as the value of the
`useSpatialIndex`-option.
