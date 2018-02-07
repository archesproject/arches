# MarchingSquaresJS

A JavaScript implementation of the [Marching Squares](https://en.wikipedia.org/wiki/Marching_squares) algorithm
featuring IsoContour and IsoBand computation.

The source code of this module is available through [github](https://github.com/RaumZeit/MarchingSquares.js)

### INSTALL

This module uses the [Universal Module Definition (UMD)](https://github.com/umdjs/umd) API for
JavaScript modules. Thus, it is easy to run the implementations on the server, the client, or
elsewhere.

##### Using Node:

```javascript
var MarchingSquaresJS = require('./marchingsquares.js');
```

The above code creates an object `MarchingSquaresJS` with two function attributes:

```javascript
MarchingSquaresJS = {
    isoContours : function(data, threshold, options){},
    isoBands : function(data, minV, bandwidth, options){}
};
```

It is possible to require only one of the implementations, `isoContours` or `isoBands`,
by requiring the correpsonding implementation directly, e.g.:

```javascript
var MarchingSquaresJS = require('./marchingsquares-isobands.js');
```

This creates the same object as before but without bound `isoContours` function.

##### Using AMD (e.g RequireJS):

The MarchingSquaresJS module should work perfectly fine through the Asynchronous Module
Definition (AMD) API. This enables easy integration with module loaders such as
[RequireJS](https://github.com/requirejs/requirejs)

Similar to the usage in Node, you can either `require` all the impementations
```javascript
var MarchingSquaresJS = require('./marchingsquares');
```
or just a single one
```javascript
var MarchingSquaresJS = require('./marchingsquares-isobands');
```

to retrieve an object with `isoContours` and/or `isoBands` function attributes:


```javascript
MarchingSquaresJS = {
    isoContours : function(data, threshold, options){},
    isoBands : function(data, minV, bandwidth, options){}
};
```

See also `example/index_require.html` for using MarchingSquaresJS with AMD

##### Using as browser global:

Download the [minified Iso Bands](https://raw.githubusercontent.com/RaumZeit/MarchingSquares.js/master/marchingsquares-isobands.min.js)
and/or the [minified Iso Contours](https://raw.githubusercontent.com/RaumZeit/MarchingSquares.js/master/marchingsquares-isocontours.min.js)
implementation, and include them in a script tag.

```html
<script src="marchingsquares-isocontours.min.js"></script>
<script src="marchingsquares-isobands.min.js"></script>
```

This will expose a global variable named `MarchingSquaresJS` with two function
attributes:

```javascript
MarchingSquaresJS = {
    isoContours : function(data, threshold, options){},
    isoBands : function(data, minV, bandwidth, options){}
};
```

Again, it is possible to omit one of the script tags to load only one of the implementations.


### Usage

For both implementations, `isoContours` and `isoBands`, the input data must be formatted as a
regular 2-dimensional grid.

#### Isocontours parameters
The `data` parameter denotes the gridded input data.
The `threshold` parameter denotes the threshold of value that will be encompassed by the iso-contour.
The optional parameter `options` may be used to chane the behavior of this function (See below)

#### IsoBands parameters
The `data` parameter denotes the gridded input data.
The `lowerBand` parameter denotes the the lowest value that will be encompassed by this iso-band, while
the `bandWidth` parameter denotes what range of values it will cover. The iso-band shown below should contain all values between `lowerBand` and `upperBand`.
The optional parameter `options` may be used to chane the behavior of this function (See below)

```javascript
var data = [
    [18, 13, 10,  9, 10, 13, 18],
    [13,  8,  5,  4,  5,  8, 13],
    [10,  5,  2,  1,  2,  5, 10],
    [ 9,  4,  1, 12,  1,  4,  9],
    [10,  5,  2,  1,  2,  5, 10],
    [13,  8,  5,  4,  5,  8, 13],
    [18, 13, 10,  9, 10, 13, 18],
    [18, 13, 10,  9, 10, 13, 18]
];

var bandWidth = upperBand - lowerBand;
var band = MarchingSquaresJS.isoBands(data, lowerBand, bandWidth, options);
```

The return value, `band`, is an array of closed polygons which includes all the point of the grid with values between the limiting isolines:

```text
[Array[21], Array[5]]
  0: Array[21]
  1: Array[5]
    0: Array[2]
      0: 2.3181818181818183
      1: 3
      length: 2
      __proto__: Array[0]
    1: Array[2]
      0: 3
      1: 2.3181818181818183
      length: 2
      __proto__: Array[0]
    2: Array[2]
    3: Array[2]
    4: Array[2]
    length: 5
    __proto__: Array[0]
  length: 2
  __proto__: Array[0]
```

##### Options

The object has the following fields:

`successCallback`: *function* - called at the end of the process with the band array passed as argument; default `null`.

`verbose`: *bool* - logs info messages before each major step of the algorithm; default `false`.

`polygons`: *bool* - if `true` the function returns a list of path coordinates for individual polygons within each grid cell, if `false` returns a list of path coordinates representing the outline of connected polygons. Default `false`.


----

Copyright (c) 2015, 2015 Ronny Lorenz <ronny@tbi.univie.ac.at>
