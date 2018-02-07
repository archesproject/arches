# grid-to-matrix

[![Build Status](https://travis-ci.org/stebogit/grid-to-matrix.svg?branch=master)](https://travis-ci.org/stebogit/grid-to-matrix)
[![npm version](https://badge.fury.io/js/grid-to-matrix.svg)](https://badge.fury.io/js/grid-to-matrix)
[![MIT licensed](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/stebogit/grid-to-matrix/blob/master/LICENSE)

Takes a [Point](http://geojson.org/geojson-spec.html#point) grid and returns a correspondent matrix of the `property` values

**Parameters**

- `grid` \[**[FeatureCollection](http://geojson.org/geojson-spec.html#feature-collection-objects)&lt;[Point](http://geojson.org/geojson-spec.html#point)>**] grid of points
- `property` \[**[string](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/String)**] the property name in `grid` from which the matrix values will be pulled (optional, default `elevation`)

- `flip` \[**[boolean](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Boolean)**] returns the matrix upside-down (optional, default `false`)

**Returns**
 
Matrix \[**[Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)<Array<<[number](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number)>>**] of the `grid` points `property` values

### Installation

**npm**

```sh
$ npm install grid-to-matrix
```

**browser (ES5)**

```html
<script src="https://unpkg.com/grid-to-matrix@1.1.0/dist/grid-to-matrix.min.js"></script>
```

### Quickstart

```javascript
  var pointGrid = require('@turf/point-grid');
  var gridToMatrix = require('grid-to-matrix');
  
  var extent = [-70.823364, -33.553984, -70.473175, -33.302986];
  var cellSize = 3;
  var grid = pointGrid(extent, cellSize);
  // add a random elevation property to each point between 0 and 60
  for (var i = 0; i < grid.features.length; i++) {
    grid.features[i].properties.elevation = (Math.random() * 60);
  }
  
  gridToMatrix(grid);
  // =[
  //    [ 1, 13, 20,  9, 10, 13, 18],
  //    [34,  8,  0,  4,  5,  8, 13],
  //    [10,  5,  2,  1,  2,  5, 24],
  //    [ 0,  4, 56, 19,  0,  4,  9],
  //    [10,  5,  2, 12,  2,  5, 10],
  //    [57,  8,  5,  4,  5,  0, 57],
  //    [ 3, 13,  0,  9,  5, 13, 35],
  //    [18, 13, 10,  9, 78, 13, 18]
  //  ]
```

