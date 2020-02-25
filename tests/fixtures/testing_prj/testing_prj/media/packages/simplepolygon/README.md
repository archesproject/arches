# simplepolygon

Takes a complex (i.e. self-intersecting) GeoJSON polygon, and breaks it down into its composite simple, non-self-intersecting one-ring polygons.

The algorithm is based on a thesis submitted by Lavanya Subramaniam: *Subramaniam, Lavanya. Partition of a Non-simple Polygon Into Simple Polygons. Diss. University of South Alabama, 2003*, which can be found [here](http://www.cis.southalabama.edu/~hain/general/Theses/Subramaniam_thesis.pdf) and features a `C/C++` implementation for polygons with one self-intersecting ring.

Here, the algorithm was implemented in `JavaScript`, and was extended to work with GeoJSON polygons, in the sense that it can handle outer *and* inner rings self- and cross-intersecting.

## How to use it

Install Node.js, then simply use the node package manager 'npm' to

```bash
npm install simplepolygon
```

In your javascript, you can then use simplepolygon like so:

```javascript
var simplepolygon = require('simplepolygon')

var poly = {
"type": "Feature",
 "geometry": {
   "type": "Polygon",
   "coordinates": [[[0,0],[2,0],[0,2],[2,2],[0,0]]]
 }
};
var result = simplepolygon(poly)
```

The **input** feature is a GeoJSON polygon which may be non-conform the [Simple Features standard](https://en.wikipedia.org/wiki/Simple_Features) in the sense that it's inner and outer rings may cross-intersect or self-intersect, that the outer ring must not contain the optional inner rings and that the winding number must not be positive for the outer and negative for the inner rings.

The **output** is a FeatureCollection containing the simple, non-self-intersecting one-ring polygon features that the complex polygon is composed of. These simple polygons have properties such as their parent polygon, winding number and net winding number.

In the above example, the output will be a FeatureCollection of two polygons, one with coordinates `[[[0,0],[2,0],[1,1],[0,0]]]`, parent -1, winding 1 and net winding 1, and one with coordinates `[[[1,1],[0,2],[2,2],[1,1]]]`, parent -1, winding -1 and net winding -1.

Another example input and output is shown below.
![](/example.png?raw=true)  

## How the algorithm works

This algorithm employs the notion of intersections and pseudo-vertices as outlined in the article.

**Intersections** are either vertices of an input ring (*ring-vertex-intersection*) or a self- or cross-intersection of those ring(s) (*self-intersection*).

**Pseudo-vertices** are a concepts that occur at an intersection: when two edges cross, one pseudo-vertex is formed by the first edge going up to and until the intersection vertex and the second edge going out from the intersection. A second pseudo vertex is formed reciprocally. Two such *intersection-pseudo-vertices* are depicted below.
![](/intersectionPseudoVertices.png?raw=true)  

Also, at each input ring vertices one pseudo-vertex (*ring-pseudo-vertex*) is created by one egde going in and the other going out.

This algorithm walks from intersections to intersection over (rings and) edges in their original direction, and while walking traces simple, non-self-intersecting one-ring polygons by storing the vertices along the way. This is possible since each intersection is first taught (using the pseudo-vertices) which is the next one given the incoming walking edge. When walking, the algorithm also stores where it has walked (since we must only walk over each (part of an) edge once), and keeps track of intersections that are new and from where another walk (and hence simple polygon) could be initiated. The resulting simple, one-ring polygons cover all input edges exactly once and don't self- or cross-intersect (but can touch at intersections). Hence, they form a set of nested rings.

### Some notes on the algorithm:

- We will talk about rings (arrays of `[x,y]`) and polygons (array of rings). The GeoJSON spec requires rings to be non-self- and non-cross-intersecting, but here the input rings can self- and cross-intersect (inter and intra ring). The output rings can't, since they are conform the spec. Therefore will talk about *input rings* or simply *rings* (non-conform), *output rings* (conform) and more generally *simple, non-self or cross-intersecting rings* (conform)
- We say that a polygon self-intersects when it's rings either self-intersect of cross-intersect
- Edges are oriented from their first to their second ring vertex. Hence, ring `i` edge `j` goes from vertex `j` to `j+1`. This direction or orientation of an edge is kept unchanged during the algorithm. We will only walk along this direction
- We use the terms *ring edge*, *ring vertex*, *self-intersection vertex*, *intersection* (which includes *ring-vertex-intersection* and *self-intersection*) and *pseudo-vertex* (which includes *ring-pseudo-vertex* and *intersection-pseudo-vertex*)
- At an intersection of two edges, two pseudo-vertices (intersection-pseudo-vertices) are one intersection (self-intersection) is present
- At a ring vertex, one pseudo-vertex (ring-pseudo-vertex) and one intersection (ring-intersection) is present
- A pseudo-vertex has an incoming and outgoing (crossing) edge
- The following objects are stored and passed by the index in the list between brackets: intersections (`isectList`) and pseudo-vertices (`pseudoVtxListByRingAndEdge`)
- The algorithm checks if the input has no non-unique vertices. This is mainly to prevent self-intersecting input polygons such as `[[0,0],[2,0],[1,1],[0,2],[1,3],[2,2],[1,1],[0,0]]`, whose self-intersections would not be detected. As such, many polygons which are non-simple, by the OGC definition, for other reasons then self-intersection, will not be allowed. An exception includes polygons with spikes or cuts such as `[[0, 0], [2, 0], [0, 2], [4, 2], [2, 2], [0, 0]]`, who are currently allowed and treated correctly, but make the output non-simple (by OGC definition). This could be prevented by checking for vertices on other edges.
- The resulting component polygons are one-ring and simple (in the sense that their ring does not contain self-intersections) and two component simple polygons are either disjoint, touching in one or multiple vertices, or one fully encloses the other
- This algorithm takes GeoJSON as input, be was developed for a euclidean (and not geodesic) setting. If used in a geodesic setting, the most important consideration to make is the computation of intersection points (which is practice is only an issue of the line segments are relatively long). Further we also note that winding numbers for area's larger than half of the globe are sometimes treated specially. All other concepts of this algorithm (convex angles, direction, ...) can be ported to a geodesic setting without problems.
- Since v1.1.1, spatial indexes are used in the underlying computation of edge intersections and throughout the algorithm, to dramatically speed up the computations in case of large polygons

### Differences with the original article

This code differs from the algorithm and nomenclature of the article it is inspired on in the following way:

- The code was written based on the article text, and not ported directly from the enclosed C/C++ code
- This implementation expanded the algorithm to polygons containing inner and outer rings
- No constructors are used, except `PseudoVtx` and `Isect`
- Some variables are named differently: `edges` is called `LineSegments` in the article, `ringAndEdgeOut` is  `l`, `PseudoVtx` is `nVtx`, `Isect` is `intersection`, `nxtIsectAlongEdgeIn` is `index`, `ringAndEdge1` and `ringAndEdge2` are `origin1` and `origin2`, `pseudoVtxListByRingAndEdge` is `polygonEdgeArray`, `isectList` is `intersectionList` and `isectQueue` is `intersectioQueue`
- `pseudoVtxListByRingAndEdge` contains the ring vertex at its end as the last item, and not the ring vertex at its start as the first item
- `winding` is not implemented as a property of an intersection, but as its own queue
