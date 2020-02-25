[![Build Status](https://secure.travis-ci.org/mapbox/geojsonhint.svg?branch=master)](http://travis-ci.org/mapbox/geojsonhint) [![Coverage Status](https://coveralls.io/repos/mapbox/geojsonhint/badge.svg)](https://coveralls.io/r/mapbox/geojsonhint)

# geojsonhint: complete, fast, standards-based validation for geojson

A [lint](https://en.wikipedia.org/wiki/Lint_%28software%29) tool for the [GeoJSON](https://tools.ietf.org/html/rfc7946)
standard. geojsonhint is written _to the standard_, with no missing or additional
opinions about structure.

Thanks to `jsonlint-lines`, GeoJSON that is also not valid [JSON](http://json.org/)
can return informative, line-oriented parsing errors.

## Specification

The basis of this tool is the published [GeoJSON](https://tools.ietf.org/html/rfc7946) specification.

## API

`errors = geojsonhint.hint(string or object, options)`

Lint a file, given as a string or object. This call detects all aberrations from
the GeoJSON standards and returns them as an array of errors. An example of the output:

```json
[{
  "message": "\"features\" property should be an array, but is an object instead",
  "line": 1
}]
```

The options argument is optional. It has these options:

`noDuplicateMembers`.

By default, geojsonhint will treat repeated properties as an error: you can
set noDuplicateMembers to false to allow them. For instance:

```js
geojsonhint.hint('{"type":"invalid","type":"Feature","properties":{},"geometry":null}', {
    noDuplicateMembers: false
});
```

The repeated `type` property in this input will be ignored with the option,
and flagged without it.


`precisionWarning`.

GeoJSON [now recommends six decimal places of accuracy](https://tools.ietf.org/html/rfc7946#section-11.2)
for coordinates (Section 11.2). This option adds a warning message when coordinates
contain over 6 decimal places of accuracy, up to 10 coordinates before the warning
message is truncated for performance.

```js
geojsonhint.hint('{ "type": "Point", "coordinates": [100.0000000001, 5.0000000001] }', {
    precisionWarning: false
});
```

With this option enabled, geojsonhint will produce these warnings:

```js
[{
  line: 1,
  level: 'message',
  message: 'precision of coordinates should be reduced'
}, {
  line: 1,
  level: 'message',
  message: 'precision of coordinates should be reduced'
}]
```

Without this option, this input will pass without errors.

## Line Numbers

Note that the GeoJSON can be given as a **string or as an object**. Here's how
to choose which input to use:

* `string` inputs receive **line numbers for each error**. These make errors
  easier to track down if the GeoJSON is hand-written.
* `object` inputs don't have line numbers but are evaluated faster, by up to 10x.
  GeoJSONHint is _very fast already_ so unless you have identified it as a
  bottleneck in your application, don't [prematurely optimize](http://c2.com/cgi/wiki?PrematureOptimization) based
  on this fact.

If you're really trying to save space and don't care about JSON validity errors -
only GeoJSON errors - you can `require('geojsonhint/lib/object')` to get a version
of this library that bypasses jsonlint-lines and provides only the object
interface.

## use it

**npm** (node.js, browserify, webpack, etc)

    npm install --save @mapbox/geojsonhint

**CDN / script tag**

Hit this URL to resolve to the latest pinned version.

    https://unpkg.com/@mapbox/geojsonhint@latest/geojsonhint.js

## As a command-line utility

Install:

    npm install -g @mapbox/geojsonhint

```
➟ geojsonhint
Usage: geojsonhint FILE.geojson

Options:
  --json  output json-formatted data for hints
```

```
➟ geojsonhint test.geojson
line 9, each element in a position must be a number
```

## Development

* Tests: `npm test`
* Building the browser version: `npm run build`

## See Also

* [geojsonhint online](https://www.mapbox.com/geojsonhint/)
* [grunt-geojsonhint](https://github.com/jieter/grunt-geojsonhint) does it as a Grunt task
* [geojsonlint.com](http://geojsonlint.com/) does this server-side
* [GeoJSON-Validation](https://github.com/craveprogramminginc/GeoJSON-Validation) is another node module for this.
* [geojson-assert](https://github.com/calvinmetcalf/geojson-assert) does it in assertion tests
* [geojsonlint](https://github.com/ropenscilabs/geojsonlint) does it in an R package
